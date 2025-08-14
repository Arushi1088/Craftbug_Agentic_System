#!/usr/bin/env python3
"""
Complete System Startup Script
Starts both legacy and new systems for end-to-end testing
"""

import subprocess
import time
import sys
import os
import signal
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteSystemManager:
    """Manages both legacy and new systems"""
    
    def __init__(self):
        self.legacy_process = None
        self.new_process = None
        self.processes = []
    
    def start_legacy_system(self):
        """Start legacy system on port 8000"""
        try:
            logger.info("🚀 Starting legacy system on port 8000...")
            
            # Check if legacy system is already running
            if self._check_port_in_use(8000):
                logger.info("✅ Legacy system already running on port 8000")
                return True
            
            # Start legacy system
            self.legacy_process = subprocess.Popen(
                ["python", "enhanced_fastapi_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(self.legacy_process)
            
            # Wait for startup
            time.sleep(3)
            
            if self.legacy_process.poll() is None:
                logger.info("✅ Legacy system started successfully")
                return True
            else:
                logger.error("❌ Legacy system failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start legacy system: {e}")
            return False
    
    def start_new_system(self):
        """Start new system on port 8001"""
        try:
            logger.info("🚀 Starting new system on port 8001...")
            
            # Check if new system is already running
            if self._check_port_in_use(8001):
                logger.info("✅ New system already running on port 8001")
                return True
            
            # Start new system
            self.new_process = subprocess.Popen(
                ["python", "src/api/main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(self.new_process)
            
            # Wait for startup
            time.sleep(3)
            
            if self.new_process.poll() is None:
                logger.info("✅ New system started successfully")
                return True
            else:
                logger.error("❌ New system failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start new system: {e}")
            return False
    
    def _check_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return False
        except OSError:
            return True
    
    def wait_for_systems(self, timeout: int = 30):
        """Wait for both systems to be ready"""
        logger.info("⏳ Waiting for systems to be ready...")
        
        start_time = time.time()
        legacy_ready = False
        new_ready = False
        
        while time.time() - start_time < timeout:
            # Check legacy system
            if not legacy_ready:
                try:
                    import requests
                    response = requests.get("http://localhost:8000/health", timeout=2)
                    if response.status_code == 200:
                        legacy_ready = True
                        logger.info("✅ Legacy system ready")
                except:
                    pass
            
            # Check new system
            if not new_ready:
                try:
                    import requests
                    response = requests.get("http://localhost:8001/health", timeout=2)
                    if response.status_code == 200:
                        new_ready = True
                        logger.info("✅ New system ready")
                except:
                    pass
            
            if legacy_ready and new_ready:
                logger.info("🎉 Both systems are ready!")
                return True
            
            time.sleep(1)
        
        logger.error("❌ Systems failed to start within timeout")
        return False
    
    def stop_all_systems(self):
        """Stop all running systems"""
        logger.info("🛑 Stopping all systems...")
        
        for process in self.processes:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    logger.error(f"Error stopping process: {e}")
        
        # Kill any remaining processes
        try:
            subprocess.run(["pkill", "-f", "enhanced_fastapi_server"], check=False)
            subprocess.run(["pkill", "-f", "src/api/main"], check=False)
        except Exception as e:
            logger.error(f"Error killing processes: {e}")
        
        logger.info("✅ All systems stopped")
    
    def run_complete_test(self):
        """Run complete end-to-end test"""
        try:
            logger.info("🧪 Running complete end-to-end test...")
            
            # Run the complete test
            result = subprocess.run(
                ["python", "test_complete_end_to_end_system.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("🎉 Complete end-to-end test passed!")
                return True
            else:
                logger.error(f"❌ Complete end-to-end test failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Received shutdown signal")
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.stop_all_systems()
    sys.exit(0)

def main():
    """Main function"""
    manager = CompleteSystemManager()
    signal_handler.manager = manager
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("🚀 Starting Complete Craftbug System")
        logger.info("=" * 50)
        
        # Start legacy system
        if not manager.start_legacy_system():
            logger.error("❌ Failed to start legacy system")
            return False
        
        # Start new system
        if not manager.start_new_system():
            logger.error("❌ Failed to start new system")
            return False
        
        # Wait for systems to be ready
        if not manager.wait_for_systems():
            logger.error("❌ Systems failed to start")
            return False
        
        logger.info("🎉 Complete system started successfully!")
        logger.info("📊 System Status:")
        logger.info("   Legacy System: http://localhost:8000")
        logger.info("   New System:    http://localhost:8001")
        logger.info("   Frontend:      http://localhost:8080")
        
        # Run complete test
        if manager.run_complete_test():
            logger.info("🎉 All systems working correctly!")
        else:
            logger.error("❌ Some tests failed")
        
        # Keep systems running
        logger.info("🔄 Systems will continue running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ System error: {e}")
    finally:
        manager.stop_all_systems()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
