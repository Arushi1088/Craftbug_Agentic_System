#!/usr/bin/env python3
"""
Performance Monitor for Animation Quality and Visual Performance
===============================================================

Monitors actual animation smoothness, frame rates, and visual performance
exactly as a user would experience it during Excel Web interactions.
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class PerformanceMonitor:
    """Monitor animation smoothness and visual performance"""
    
    def __init__(self):
        self.monitoring_active = False
        self.performance_data = []
        self.frame_rate_data = []
        self.animation_metrics = []
        self.system_metrics = []
        
        # Performance thresholds
        self.thresholds = {
            'doherty_threshold': 400,  # ms
            'target_frame_rate': 60,   # fps
            'minimum_frame_rate': 30,  # fps
            'max_animation_duration': 300,  # ms
            'max_cpu_usage': 80,       # percentage
            'max_memory_usage': 85     # percentage
        }
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring_active = True
        self.performance_data = []
        self.frame_rate_data = []
        self.animation_metrics = []
        self.system_metrics = []
        
        # Start system monitoring thread
        self.system_monitor_thread = threading.Thread(target=self._monitor_system_resources)
        self.system_monitor_thread.daemon = True
        self.system_monitor_thread.start()
        
        print("🚀 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        print("⏹️ Performance monitoring stopped")
    
    def record_interaction_timing(self, interaction_type: str, start_time: float, end_time: float, success: bool = True):
        """Record interaction timing for Doherty Threshold analysis"""
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        timing_data = {
            'timestamp': datetime.now().isoformat(),
            'interaction_type': interaction_type,
            'duration_ms': duration,
            'success': success,
            'doherty_compliant': duration <= self.thresholds['doherty_threshold'],
            'severity': self._calculate_timing_severity(duration)
        }
        
        self.performance_data.append(timing_data)
        
        # Log if Doherty Threshold is exceeded
        if duration > self.thresholds['doherty_threshold']:
            print(f"⚠️ Doherty Threshold exceeded: {interaction_type} took {duration:.1f}ms (threshold: {self.thresholds['doherty_threshold']}ms)")
        
        return timing_data
    
    def record_animation_metrics(self, animation_type: str, duration: float, frame_count: int, smoothness_score: float):
        """Record animation quality metrics"""
        frame_rate = frame_count / duration if duration > 0 else 0
        
        animation_data = {
            'timestamp': datetime.now().isoformat(),
            'animation_type': animation_type,
            'duration_ms': duration * 1000,
            'frame_count': frame_count,
            'frame_rate': frame_rate,
            'smoothness_score': smoothness_score,
            'performance_grade': self._calculate_animation_grade(frame_rate, smoothness_score),
            'issues': self._detect_animation_issues(frame_rate, smoothness_score, duration)
        }
        
        self.animation_metrics.append(animation_data)
        
        # Log performance issues
        if frame_rate < self.thresholds['minimum_frame_rate']:
            print(f"⚠️ Low frame rate detected: {animation_type} at {frame_rate:.1f}fps (minimum: {self.thresholds['minimum_frame_rate']}fps)")
        
        return animation_data
    
    def record_frame_rate_sample(self, frame_rate: float, timestamp: float):
        """Record frame rate sample for continuous monitoring"""
        frame_data = {
            'timestamp': timestamp,
            'frame_rate': frame_rate,
            'smooth': frame_rate >= self.thresholds['target_frame_rate'],
            'acceptable': frame_rate >= self.thresholds['minimum_frame_rate']
        }
        
        self.frame_rate_data.append(frame_data)
    
    def _monitor_system_resources(self):
        """Monitor system resources in background thread"""
        while self.monitoring_active:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                system_data = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available': memory.available,
                    'cpu_high': cpu_percent > self.thresholds['max_cpu_usage'],
                    'memory_high': memory.percent > self.thresholds['max_memory_usage']
                }
                
                self.system_metrics.append(system_data)
                
                # Log high resource usage
                if cpu_percent > self.thresholds['max_cpu_usage']:
                    print(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
                if memory.percent > self.thresholds['max_memory_usage']:
                    print(f"⚠️ High memory usage: {memory.percent:.1f}%")
                
                time.sleep(1)  # Sample every second
                
            except Exception as e:
                print(f"❌ System monitoring error: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _calculate_timing_severity(self, duration_ms: float) -> str:
        """Calculate severity based on timing"""
        if duration_ms <= self.thresholds['doherty_threshold']:
            return 'none'
        elif duration_ms <= 1000:
            return 'medium'
        else:
            return 'high'
    
    def _calculate_animation_grade(self, frame_rate: float, smoothness_score: float) -> str:
        """Calculate animation performance grade"""
        if frame_rate >= self.thresholds['target_frame_rate'] and smoothness_score >= 0.9:
            return 'A'
        elif frame_rate >= self.thresholds['minimum_frame_rate'] and smoothness_score >= 0.7:
            return 'B'
        elif frame_rate >= 20 and smoothness_score >= 0.5:
            return 'C'
        else:
            return 'D'
    
    def _detect_animation_issues(self, frame_rate: float, smoothness_score: float, duration: float) -> List[Dict]:
        """Detect animation performance issues"""
        issues = []
        
        if frame_rate < self.thresholds['minimum_frame_rate']:
            issues.append({
                'type': 'low_frame_rate',
                'severity': 'high' if frame_rate < 20 else 'medium',
                'description': f'Frame rate {frame_rate:.1f}fps below minimum {self.thresholds["minimum_frame_rate"]}fps'
            })
        
        if smoothness_score < 0.7:
            issues.append({
                'type': 'poor_smoothness',
                'severity': 'medium',
                'description': f'Animation smoothness score {smoothness_score:.2f} indicates stuttering'
            })
        
        if duration * 1000 > self.thresholds['max_animation_duration']:
            issues.append({
                'type': 'slow_animation',
                'severity': 'medium',
                'description': f'Animation duration {duration*1000:.1f}ms exceeds threshold {self.thresholds["max_animation_duration"]}ms'
            })
        
        return issues
    
    def analyze_performance_data(self) -> Dict[str, Any]:
        """Analyze collected performance data"""
        if not self.performance_data and not self.animation_metrics:
            return {'error': 'No performance data collected'}
        
        analysis = {
            'summary': {
                'total_interactions': len(self.performance_data),
                'total_animations': len(self.animation_metrics),
                'doherty_compliance_rate': 0,
                'average_frame_rate': 0,
                'performance_issues': 0
            },
            'timing_analysis': {},
            'animation_analysis': {},
            'system_analysis': {},
            'recommendations': []
        }
        
        # Analyze timing data
        if self.performance_data:
            doherty_compliant = sum(1 for data in self.performance_data if data['doherty_compliant'])
            analysis['summary']['doherty_compliance_rate'] = (doherty_compliant / len(self.performance_data)) * 100
            
            durations = [data['duration_ms'] for data in self.performance_data]
            analysis['timing_analysis'] = {
                'average_duration': sum(durations) / len(durations),
                'max_duration': max(durations),
                'min_duration': min(durations),
                'slow_interactions': [data for data in self.performance_data if not data['doherty_compliant']]
            }
        
        # Analyze animation data
        if self.animation_metrics:
            frame_rates = [data['frame_rate'] for data in self.animation_metrics]
            analysis['summary']['average_frame_rate'] = sum(frame_rates) / len(frame_rates)
            
            smoothness_scores = [data['smoothness_score'] for data in self.animation_metrics]
            analysis['animation_analysis'] = {
                'average_smoothness': sum(smoothness_scores) / len(smoothness_scores),
                'performance_grades': {
                    'A': len([data for data in self.animation_metrics if data['performance_grade'] == 'A']),
                    'B': len([data for data in self.animation_metrics if data['performance_grade'] == 'B']),
                    'C': len([data for data in self.animation_metrics if data['performance_grade'] == 'C']),
                    'D': len([data for data in self.animation_metrics if data['performance_grade'] == 'D'])
                },
                'animation_issues': [data for data in self.animation_metrics if data['issues']]
            }
        
        # Analyze system data
        if self.system_metrics:
            cpu_usage = [data['cpu_percent'] for data in self.system_metrics]
            memory_usage = [data['memory_percent'] for data in self.system_metrics]
            
            analysis['system_analysis'] = {
                'average_cpu_usage': sum(cpu_usage) / len(cpu_usage),
                'max_cpu_usage': max(cpu_usage),
                'average_memory_usage': sum(memory_usage) / len(memory_usage),
                'max_memory_usage': max(memory_usage),
                'high_resource_periods': [data for data in self.system_metrics if data['cpu_high'] or data['memory_high']]
            }
        
        # Count total performance issues
        timing_issues = len([data for data in self.performance_data if not data['doherty_compliant']])
        animation_issues = len([data for data in self.animation_metrics if data['issues']])
        system_issues = len([data for data in self.system_metrics if data['cpu_high'] or data['memory_high']])
        
        analysis['summary']['performance_issues'] = timing_issues + animation_issues + system_issues
        
        # Generate recommendations
        if analysis['summary']['doherty_compliance_rate'] < 90:
            analysis['recommendations'].append('Optimize interaction response times to meet Doherty Threshold')
        
        if analysis['summary']['average_frame_rate'] < self.thresholds['minimum_frame_rate']:
            analysis['recommendations'].append('Improve animation frame rates for smoother user experience')
        
        if analysis['system_analysis'].get('average_cpu_usage', 0) > self.thresholds['max_cpu_usage']:
            analysis['recommendations'].append('Reduce CPU usage to improve overall performance')
        
        return analysis
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        analysis = self.analyze_performance_data()
        
        report = {
            'report_type': 'Performance Analysis',
            'generated_at': datetime.now().isoformat(),
            'monitoring_duration': self._calculate_monitoring_duration(),
            'analysis': analysis,
            'performance_score': self._calculate_overall_performance_score(analysis),
            'craft_bugs': self._identify_performance_craft_bugs(analysis)
        }
        
        return report
    
    def _calculate_monitoring_duration(self) -> float:
        """Calculate total monitoring duration"""
        if not self.performance_data:
            return 0
        
        start_time = datetime.fromisoformat(self.performance_data[0]['timestamp'])
        end_time = datetime.fromisoformat(self.performance_data[-1]['timestamp'])
        return (end_time - start_time).total_seconds()
    
    def _calculate_overall_performance_score(self, analysis: Dict) -> float:
        """Calculate overall performance score (0-100)"""
        score = 100
        
        # Deduct points for timing violations
        if analysis['summary']['doherty_compliance_rate'] < 100:
            score -= (100 - analysis['summary']['doherty_compliance_rate']) * 0.3
        
        # Deduct points for animation issues
        if analysis['summary']['average_frame_rate'] < self.thresholds['target_frame_rate']:
            score -= (self.thresholds['target_frame_rate'] - analysis['summary']['average_frame_rate']) * 0.5
        
        # Deduct points for system issues
        if analysis['system_analysis'].get('average_cpu_usage', 0) > self.thresholds['max_cpu_usage']:
            score -= 10
        
        return max(0, score)
    
    def _identify_performance_craft_bugs(self, analysis: Dict) -> List[Dict]:
        """Identify performance-related Craft bugs"""
        craft_bugs = []
        
        # Timing-related Craft bugs
        if analysis['summary']['doherty_compliance_rate'] < 90:
            craft_bugs.append({
                'id': 'PERF-001',
                'title': 'Doherty Threshold Violations',
                'description': f'Only {analysis["summary"]["doherty_compliance_rate"]:.1f}% of interactions meet Doherty Threshold',
                'craft_bug_type': 'Performance UX',
                'severity': 'Orange' if analysis['summary']['doherty_compliance_rate'] < 80 else 'Yellow',
                'surface_level': 'L1',
                'user_impact': 'Medium',
                'recommended_fix': 'Optimize interaction response times to <400ms'
            })
        
        # Animation-related Craft bugs
        if analysis['summary']['average_frame_rate'] < self.thresholds['minimum_frame_rate']:
            craft_bugs.append({
                'id': 'PERF-002',
                'title': 'Low Animation Frame Rate',
                'description': f'Average frame rate {analysis["summary"]["average_frame_rate"]:.1f}fps below minimum {self.thresholds["minimum_frame_rate"]}fps',
                'craft_bug_type': 'Performance UX',
                'severity': 'Orange',
                'surface_level': 'L2',
                'user_impact': 'Medium',
                'recommended_fix': 'Optimize animations for smoother visual experience'
            })
        
        # System resource Craft bugs
        if analysis['system_analysis'].get('average_cpu_usage', 0) > self.thresholds['max_cpu_usage']:
            craft_bugs.append({
                'id': 'PERF-003',
                'title': 'High CPU Usage Impacting Performance',
                'description': f'Average CPU usage {analysis["system_analysis"]["average_cpu_usage"]:.1f}% exceeds threshold {self.thresholds["max_cpu_usage"]}%',
                'craft_bug_type': 'Performance UX',
                'severity': 'Yellow',
                'surface_level': 'L1',
                'user_impact': 'Low',
                'recommended_fix': 'Optimize resource usage to reduce CPU load'
            })
        
        return craft_bugs

# Test the performance monitor
if __name__ == "__main__":
    monitor = PerformanceMonitor()
    
    print("🚀 Performance Monitor initialized")
    print("✅ Ready for animation quality and visual performance monitoring")
    print("📊 Capabilities:")
    print("   - Doherty Threshold compliance tracking")
    print("   - Frame rate monitoring")
    print("   - Animation smoothness analysis")
    print("   - System resource monitoring")
    print("   - Performance Craft bug detection")
    print("   - Real-time performance alerts")
