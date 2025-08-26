"""
Performance Service for Craftbug Agentic System.
This module provides performance monitoring and optimization capabilities.
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager, contextmanager
from functools import wraps

from config.settings import get_settings


@dataclass
class PerformanceMetric:
    """Data structure for performance metrics."""
    operation: str
    duration: float
    timestamp: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceService:
    """Service for monitoring and optimizing system performance."""
    
    def __init__(self, settings=None):
        """Initialize the performance service."""
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Performance tracking
        self.metrics: List[PerformanceMetric] = []
        self.active_timers: Dict[str, float] = {}
        
        # Performance thresholds
        self.thresholds = {
            "llm_call_timeout": 30.0,  # seconds
            "image_processing_timeout": 10.0,  # seconds
            "analysis_timeout": 60.0,  # seconds
            "memory_warning_threshold": 0.8,  # 80% of available memory
        }
    
    def start_timer(self, operation: str) -> str:
        """Start a performance timer for an operation."""
        timer_id = f"{operation}_{int(time.time() * 1000)}"
        self.active_timers[timer_id] = time.time()
        return timer_id
    
    def stop_timer(self, timer_id: str, success: bool = True, metadata: Dict[str, Any] = None) -> Optional[float]:
        """Stop a performance timer and record the metric."""
        if timer_id not in self.active_timers:
            self.logger.warning(f"Timer {timer_id} not found")
            return None
        
        start_time = self.active_timers.pop(timer_id)
        duration = time.time() - start_time
        
        metric = PerformanceMetric(
            operation=timer_id.split('_')[0],
            duration=duration,
            timestamp=start_time,
            success=success,
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        
        # Log performance warnings
        if duration > self.thresholds.get(f"{metric.operation}_timeout", 30.0):
            self.logger.warning(f"Performance warning: {metric.operation} took {duration:.2f}s")
        
        return duration
    
    @contextmanager
    def timer(self, operation: str, metadata: Dict[str, Any] = None):
        """Context manager for timing operations."""
        timer_id = self.start_timer(operation)
        try:
            yield timer_id
            self.stop_timer(timer_id, success=True, metadata=metadata)
        except Exception as e:
            self.stop_timer(timer_id, success=False, metadata=metadata)
            raise
    
    @asynccontextmanager
    async def async_timer(self, operation: str, metadata: Dict[str, Any] = None):
        """Async context manager for timing operations."""
        timer_id = self.start_timer(operation)
        try:
            yield timer_id
            self.stop_timer(timer_id, success=True, metadata=metadata)
        except Exception as e:
            self.stop_timer(timer_id, success=False, metadata=metadata)
            raise
    
    def time_function(self, operation: str = None):
        """Decorator for timing function execution."""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation or func.__name__
                with self.timer(op_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def time_async_function(self, operation: str = None):
        """Decorator for timing async function execution."""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                op_name = operation or func.__name__
                async with self.async_timer(op_name):
                    return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_performance_stats(self, operation: str = None, time_window: float = None) -> Dict[str, Any]:
        """Get performance statistics for operations."""
        if not self.metrics:
            return {"total_operations": 0}
        
        # Filter metrics by operation and time window
        filtered_metrics = self.metrics
        if operation:
            filtered_metrics = [m for m in filtered_metrics if m.operation == operation]
        
        if time_window:
            cutoff_time = time.time() - time_window
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= cutoff_time]
        
        if not filtered_metrics:
            return {"total_operations": 0}
        
        # Calculate statistics
        durations = [m.duration for m in filtered_metrics]
        successful_ops = [m for m in filtered_metrics if m.success]
        failed_ops = [m for m in filtered_metrics if not m.success]
        
        stats = {
            "total_operations": len(filtered_metrics),
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "success_rate": len(successful_ops) / len(filtered_metrics) if filtered_metrics else 0,
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations),
        }
        
        # Add percentiles if we have enough data
        if len(durations) >= 10:
            sorted_durations = sorted(durations)
            stats.update({
                "p50_duration": sorted_durations[len(sorted_durations) // 2],
                "p90_duration": sorted_durations[int(len(sorted_durations) * 0.9)],
                "p95_duration": sorted_durations[int(len(sorted_durations) * 0.95)],
                "p99_duration": sorted_durations[int(len(sorted_durations) * 0.99)],
            })
        
        return stats
    
    def get_operation_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Get performance breakdown by operation type."""
        operations = {}
        
        for metric in self.metrics:
            if metric.operation not in operations:
                operations[metric.operation] = {
                    "count": 0,
                    "total_duration": 0,
                    "successful": 0,
                    "failed": 0,
                    "durations": []
                }
            
            op_stats = operations[metric.operation]
            op_stats["count"] += 1
            op_stats["total_duration"] += metric.duration
            op_stats["durations"].append(metric.duration)
            
            if metric.success:
                op_stats["successful"] += 1
            else:
                op_stats["failed"] += 1
        
        # Calculate averages and percentiles for each operation
        for op_name, op_stats in operations.items():
            durations = op_stats["durations"]
            op_stats["average_duration"] = sum(durations) / len(durations)
            op_stats["min_duration"] = min(durations)
            op_stats["max_duration"] = max(durations)
            op_stats["success_rate"] = op_stats["successful"] / op_stats["count"]
            
            if len(durations) >= 5:
                sorted_durations = sorted(durations)
                op_stats["p90_duration"] = sorted_durations[int(len(sorted_durations) * 0.9)]
            
            # Remove raw durations list to keep response clean
            del op_stats["durations"]
        
        return operations
    
    def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest operations."""
        if not self.metrics:
            return []
        
        # Group by operation and find the slowest instance of each
        operation_max_durations = {}
        for metric in self.metrics:
            if metric.operation not in operation_max_durations:
                operation_max_durations[metric.operation] = metric
            elif metric.duration > operation_max_durations[metric.operation].duration:
                operation_max_durations[metric.operation] = metric
        
        # Sort by duration and return top N
        sorted_operations = sorted(
            operation_max_durations.values(),
            key=lambda m: m.duration,
            reverse=True
        )
        
        return [
            {
                "operation": m.operation,
                "duration": m.duration,
                "timestamp": m.timestamp,
                "success": m.success,
                "metadata": m.metadata
            }
            for m in sorted_operations[:limit]
        ]
    
    def clear_metrics(self, older_than: float = None):
        """Clear performance metrics."""
        if older_than is None:
            self.metrics.clear()
            self.logger.info("All performance metrics cleared")
        else:
            cutoff_time = time.time() - older_than
            original_count = len(self.metrics)
            self.metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            cleared_count = original_count - len(self.metrics)
            self.logger.info(f"Cleared {cleared_count} old performance metrics")
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
                "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
                "percent": process.memory_percent(),
                "available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "total_mb": psutil.virtual_memory().total / 1024 / 1024,
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_performance_health(self) -> Dict[str, Any]:
        """Check overall system performance health."""
        health = {
            "status": "healthy",
            "warnings": [],
            "metrics": {}
        }
        
        # Check recent performance
        recent_stats = self.get_performance_stats(time_window=300)  # Last 5 minutes
        if recent_stats["total_operations"] > 0:
            if recent_stats["success_rate"] < 0.9:
                health["warnings"].append("Low success rate in recent operations")
                health["status"] = "warning"
            
            if recent_stats["average_duration"] > 30:
                health["warnings"].append("High average operation duration")
                health["status"] = "warning"
        
        # Check memory usage
        memory_usage = self.get_memory_usage()
        if "error" not in memory_usage:
            if memory_usage["percent"] > 80:
                health["warnings"].append("High memory usage")
                health["status"] = "warning"
        
        health["metrics"] = {
            "recent_performance": recent_stats,
            "memory_usage": memory_usage,
            "total_metrics": len(self.metrics)
        }
        
        return health
