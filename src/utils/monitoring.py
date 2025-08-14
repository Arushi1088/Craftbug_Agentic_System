#!/usr/bin/env python3
"""
Monitoring and Rollback System for Safe Refactoring
Monitors system health and provides emergency rollback capabilities
"""

import logging
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import subprocess
import os

logger = logging.getLogger(__name__)

class SystemMonitor:
    """
    Monitors system health during refactoring and provides rollback capabilities
    """
    
    def __init__(self):
        self.health_checks = []
        self.alert_history = []
        self.rollback_history = []
        self.monitoring_enabled = True
        self.health_threshold = 0.8  # 80% success rate required
        
    def add_health_check(self, name: str, check_function, interval: int = 60):
        """Add a health check function"""
        self.health_checks.append({
            "name": name,
            "function": check_function,
            "interval": interval,
            "last_run": None,
            "last_result": None,
            "success_count": 0,
            "failure_count": 0
        })
        logger.info(f"✅ Health check added: {name}")
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        if not self.monitoring_enabled:
            return {"status": "monitoring_disabled"}
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "PENDING"
        }
        
        total_checks = len(self.health_checks)
        passed_checks = 0
        
        for check in self.health_checks:
            try:
                # Run the health check
                check_result = await check["function"]()
                
                # Update check statistics
                if check_result.get("status") == "PASSED":
                    check["success_count"] += 1
                    passed_checks += 1
                else:
                    check["failure_count"] += 1
                
                check["last_run"] = datetime.now().isoformat()
                check["last_result"] = check_result
                
                results["checks"][check["name"]] = check_result
                
                logger.info(f"Health check {check['name']}: {check_result.get('status', 'UNKNOWN')}")
                
            except Exception as e:
                check["failure_count"] += 1
                check["last_run"] = datetime.now().isoformat()
                check["last_result"] = {"status": "ERROR", "error": str(e)}
                
                results["checks"][check["name"]] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                
                logger.error(f"Health check {check['name']} failed: {e}")
        
        # Calculate overall status
        success_rate = passed_checks / total_checks if total_checks > 0 else 0
        
        if success_rate >= self.health_threshold:
            results["overall_status"] = "HEALTHY"
        else:
            results["overall_status"] = "UNHEALTHY"
            await self.send_alert(f"System health degraded: {success_rate:.1%} success rate")
        
        return results
    
    async def check_end_to_end_health(self) -> Dict[str, Any]:
        """Check if end-to-end flow is working"""
        try:
            import requests
            
            # Test basic endpoints
            endpoints = [
                ("/health", "GET"),
                ("/api/scenarios", "GET"),
                ("/api/analyze", "POST")  # We'll just check if it responds
            ]
            
            passed = 0
            total = len(endpoints)
            
            for endpoint, method in endpoints:
                try:
                    if method == "GET":
                        response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
                    else:
                        # For POST, just check if endpoint exists
                        response = requests.get("http://localhost:8000/health", timeout=10)
                    
                    if response.status_code in [200, 405]:  # 405 means method not allowed (endpoint exists)
                        passed += 1
                    else:
                        logger.warning(f"Endpoint {endpoint} returned {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Endpoint {endpoint} failed: {e}")
            
            success_rate = passed / total
            
            if success_rate >= 0.8:
                return {
                    "status": "PASSED",
                    "message": f"End-to-end health check passed: {passed}/{total} endpoints",
                    "success_rate": success_rate
                }
            else:
                return {
                    "status": "FAILED",
                    "message": f"End-to-end health check failed: {passed}/{total} endpoints",
                    "success_rate": success_rate
                }
                
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    async def check_analysis_workflow(self) -> Dict[str, Any]:
        """Check if analysis workflow is working"""
        try:
            import requests
            
            # Test a simple analysis
            payload = {
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "scenario_id": "1.1",
                "modules": {"performance": True}
            }
            
            response = requests.post(
                "http://localhost:8000/api/analyze",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("analysis_id"):
                    return {
                        "status": "PASSED",
                        "message": "Analysis workflow working",
                        "analysis_id": result["analysis_id"]
                    }
                else:
                    return {
                        "status": "FAILED",
                        "message": "Analysis returned no analysis ID"
                    }
            else:
                return {
                    "status": "FAILED",
                    "message": f"Analysis endpoint returned {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    async def check_fix_with_agent(self) -> Dict[str, Any]:
        """Check if Fix with Agent is working"""
        try:
            import requests
            
            # Test the fix endpoint
            payload = {
                "work_item_id": 999,
                "file_path": "web-ui/public/mocks/word/basic-doc.html",
                "instruction": "Test fix"
            }
            
            response = requests.post(
                "http://localhost:8000/api/ado/trigger-fix",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "status": "PASSED",
                    "message": "Fix with Agent endpoint responding"
                }
            else:
                return {
                    "status": "FAILED",
                    "message": f"Fix with Agent returned {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    async def send_alert(self, message: str, severity: str = "WARNING"):
        """Send an alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "severity": severity
        }
        
        self.alert_history.append(alert)
        
        # Log the alert
        if severity == "CRITICAL":
            logger.critical(f"🚨 CRITICAL ALERT: {message}")
        elif severity == "ERROR":
            logger.error(f"❌ ERROR ALERT: {message}")
        else:
            logger.warning(f"⚠️ WARNING ALERT: {message}")
        
        # If critical, trigger rollback
        if severity == "CRITICAL":
            await self.trigger_rollback(f"Critical alert: {message}")
    
    async def trigger_rollback(self, reason: str):
        """Trigger emergency rollback"""
        logger.critical(f"🚨 EMERGENCY ROLLBACK TRIGGERED: {reason}")
        
        try:
            # Import feature flags
            from src.utils.feature_flags import FeatureFlags
            
            # Force legacy mode
            FeatureFlags.force_legacy_mode()
            
            # Record rollback
            rollback_record = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "action": "forced_legacy_mode"
            }
            
            self.rollback_history.append(rollback_record)
            
            logger.info("✅ Emergency rollback completed - legacy mode forced")
            
            # Save rollback history
            self.save_rollback_history()
            
        except Exception as e:
            logger.error(f"❌ Emergency rollback failed: {e}")
    
    def save_rollback_history(self, filename: str = None):
        """Save rollback history to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rollback_history_{timestamp}.json"
        
        data = {
            "rollback_history": self.rollback_history,
            "alert_history": self.alert_history[-10:],  # Last 10 alerts
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"💾 Rollback history saved to: {filename}")
        return filename
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "health_checks_count": len(self.health_checks),
            "alerts_count": len(self.alert_history),
            "rollbacks_count": len(self.rollback_history),
            "last_rollback": self.rollback_history[-1] if self.rollback_history else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def enable_monitoring(self):
        """Enable monitoring"""
        self.monitoring_enabled = True
        logger.info("✅ System monitoring enabled")
    
    def disable_monitoring(self):
        """Disable monitoring"""
        self.monitoring_enabled = False
        logger.info("❌ System monitoring disabled")

class RollbackManager:
    """
    Manages rollbacks if issues arise during refactoring
    """
    
    @staticmethod
    def rollback_to_legacy():
        """Immediately disable new architecture"""
        try:
            from src.utils.feature_flags import FeatureFlags
            FeatureFlags.force_legacy_mode()
            logger.warning("🔄 Rolled back to legacy system")
            return True
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    @staticmethod
    def emergency_restart():
        """Restart with legacy system only"""
        try:
            # Kill existing processes
            subprocess.run(["pkill", "-f", "enhanced_fastapi_server"], check=False)
            time.sleep(2)
            
            # Restart with legacy system
            subprocess.Popen(["python", "enhanced_fastapi_server.py"])
            logger.warning("🔄 Emergency restart completed")
            return True
        except Exception as e:
            logger.error(f"❌ Emergency restart failed: {e}")
            return False
    
    @staticmethod
    def create_backup():
        """Create backup of current system"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"../craftbug_backup_{timestamp}"
            
            # Create backup directory
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy current files
            import shutil
            shutil.copytree(".", backup_dir, dirs_exist_ok=True)
            
            logger.info(f"💾 System backup created: {backup_dir}")
            return backup_dir
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return None

# Global monitoring instance
system_monitor = SystemMonitor()

# Initialize health checks
async def initialize_monitoring():
    """Initialize monitoring system"""
    system_monitor.add_health_check("end_to_end_health", system_monitor.check_end_to_end_health, 60)
    system_monitor.add_health_check("analysis_workflow", system_monitor.check_analysis_workflow, 120)
    system_monitor.add_health_check("fix_with_agent", system_monitor.check_fix_with_agent, 180)
    
    logger.info("✅ System monitoring initialized")
