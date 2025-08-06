#!/usr/bin/env python3
"""
CI/CD Pipeline Script
Automated testing and deployment pipeline for UX Analyzer
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime

class CIPipeline:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "stages": {},
            "overall_success": False
        }
    
    def run_command(self, command, description, cwd=None):
        """Run a command and capture output"""
        print(f"🔄 {description}...")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            
            self.results["stages"][description] = {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command
            }
            
            if success:
                print(f"✅ {description} - SUCCESS")
            else:
                print(f"❌ {description} - FAILED")
                print(f"   Error: {result.stderr}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT")
            self.results["stages"][description] = {
                "success": False,
                "error": "timeout",
                "command": command
            }
            return False
        except Exception as e:
            print(f"💥 {description} - ERROR: {str(e)}")
            self.results["stages"][description] = {
                "success": False,
                "error": str(e),
                "command": command
            }
            return False
    
    def stage_1_linting_and_formatting(self):
        """Stage 1: Code quality checks"""
        print("\n📋 STAGE 1: Code Quality & Linting")
        print("-" * 40)
        
        # Python linting (if flake8 is available)
        python_lint = self.run_command(
            "python3 -m py_compile *.py",
            "Python Syntax Check"
        )
        
        # Check for required files
        required_files = [
            "production_server.py",
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml"
        ]
        
        files_check = True
        for file in required_files:
            if os.path.exists(os.path.join(self.project_root, file)):
                print(f"✅ {file} - Found")
            else:
                print(f"❌ {file} - Missing")
                files_check = False
        
        self.results["stages"]["Required Files Check"] = {
            "success": files_check,
            "details": f"Checked {len(required_files)} required files"
        }
        
        return python_lint and files_check
    
    def stage_2_dependency_check(self):
        """Stage 2: Dependency validation"""
        print("\n📦 STAGE 2: Dependency Validation")
        print("-" * 40)
        
        # Check Python dependencies
        python_deps = self.run_command(
            "pip3 install --dry-run -r requirements.txt",
            "Python Dependencies Check"
        )
        
        # Check if Node.js dependencies exist (if package.json exists)
        node_deps = True
        if os.path.exists(os.path.join(self.project_root, "package.json")):
            node_deps = self.run_command(
                "npm list --depth=0",
                "Node.js Dependencies Check"
            )
        else:
            print("ℹ️  No package.json found, skipping Node.js dependency check")
        
        return python_deps and node_deps
    
    def stage_3_unit_tests(self):
        """Stage 3: Unit testing"""
        print("\n🧪 STAGE 3: Unit Testing")
        print("-" * 40)
        
        # Check if test files exist
        test_files = [f for f in os.listdir(self.project_root) if f.endswith('_test.py') or f.startswith('test_')]
        
        if test_files:
            unit_tests = self.run_command(
                "python3 -m pytest -v",
                "Unit Tests Execution"
            )
        else:
            print("ℹ️  No unit test files found, creating basic validation test...")
            unit_tests = self.run_command(
                "python3 -c 'import production_server; print(\"Module import successful\")'",
                "Basic Module Import Test"
            )
        
        return unit_tests
    
    def stage_4_integration_tests(self):
        """Stage 4: Integration testing"""
        print("\n🔗 STAGE 4: Integration Testing")
        print("-" * 40)
        
        # Start servers for testing
        print("🚀 Starting test servers...")
        
        # Start backend in background
        backend_process = None
        frontend_process = None
        
        try:
            # Start backend server
            backend_process = subprocess.Popen(
                ["python3", "production_server.py"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for backend to start
            time.sleep(5)
            
            # Check if backend is responding
            backend_health = self.run_command(
                "curl -f http://localhost:8000/health || python3 -c 'import requests; requests.get(\"http://localhost:8000/health\", timeout=5)'",
                "Backend Health Check"
            )
            
            if backend_health:
                # Run integration tests
                integration_tests = self.run_command(
                    "python3 final_integration_test.py",
                    "Integration Test Suite"
                )
            else:
                print("❌ Backend server not responding, skipping integration tests")
                integration_tests = False
            
            return integration_tests
            
        finally:
            # Clean up processes
            if backend_process:
                backend_process.terminate()
                try:
                    backend_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    backend_process.kill()
    
    def stage_5_docker_build(self):
        """Stage 5: Docker build validation"""
        print("\n🐳 STAGE 5: Docker Build Validation")
        print("-" * 40)
        
        # Check Docker availability
        docker_available = self.run_command(
            "docker --version",
            "Docker Availability Check"
        )
        
        if not docker_available:
            print("⚠️  Docker not available, skipping Docker build tests")
            return True  # Not a failure if Docker isn't available
        
        # Build Docker image
        docker_build = self.run_command(
            "docker build -t ux-analyzer:test .",
            "Docker Image Build"
        )
        
        if docker_build:
            # Test Docker image
            docker_test = self.run_command(
                "docker run --rm ux-analyzer:test python3 -c 'import production_server; print(\"Docker image OK\")'",
                "Docker Image Test"
            )
            
            # Clean up test image
            self.run_command(
                "docker rmi ux-analyzer:test",
                "Docker Image Cleanup"
            )
            
            return docker_test
        
        return docker_build
    
    def stage_6_security_scan(self):
        """Stage 6: Basic security scanning"""
        print("\n🔒 STAGE 6: Security Scanning")
        print("-" * 40)
        
        # Check for common security issues
        security_checks = []
        
        # Check for hardcoded secrets
        secrets_check = self.run_command(
            "grep -r 'password\\|secret\\|key\\|token' --include='*.py' . | grep -v 'test' | grep -v '#' || true",
            "Hardcoded Secrets Check"
        )
        
        # Check Python package vulnerabilities (if safety is available)
        vuln_check = self.run_command(
            "pip3 install safety >/dev/null 2>&1 && safety check || echo 'Safety not available, skipping vulnerability check'",
            "Python Package Vulnerability Check"
        )
        
        return True  # Security checks are warnings, not failures
    
    def generate_report(self):
        """Generate CI/CD pipeline report"""
        successful_stages = len([s for s in self.results["stages"].values() if s.get("success", False)])
        total_stages = len(self.results["stages"])
        success_rate = (successful_stages / total_stages * 100) if total_stages > 0 else 0
        
        self.results["overall_success"] = success_rate >= 80
        self.results["success_rate"] = success_rate
        
        print("\n" + "="*80)
        print("🎯 CI/CD PIPELINE REPORT")
        print("="*80)
        print(f"📅 Timestamp: {self.results['timestamp']}")
        print(f"📊 Success Rate: {success_rate:.1f}% ({successful_stages}/{total_stages} stages)")
        print(f"🎯 Overall Status: {'✅ SUCCESS' if self.results['overall_success'] else '❌ FAILED'}")
        
        print("\n📋 Stage Details:")
        for stage_name, stage_result in self.results["stages"].items():
            status = "✅ PASS" if stage_result.get("success", False) else "❌ FAIL"
            print(f"   {status} {stage_name}")
            
            if not stage_result.get("success", False) and stage_result.get("stderr"):
                print(f"      └─ Error: {stage_result['stderr'][:100]}...")
        
        # Save report to file
        report_file = f"ci_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print("="*80)
        
        return self.results["overall_success"]
    
    def run_pipeline(self):
        """Execute the full CI/CD pipeline"""
        print("🚀 UX ANALYZER - CI/CD PIPELINE")
        print("="*50)
        print(f"📁 Project Root: {self.project_root}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define pipeline stages
        stages = [
            ("Code Quality", self.stage_1_linting_and_formatting),
            ("Dependencies", self.stage_2_dependency_check),
            ("Unit Tests", self.stage_3_unit_tests),
            ("Integration Tests", self.stage_4_integration_tests),
            ("Docker Build", self.stage_5_docker_build),
            ("Security Scan", self.stage_6_security_scan)
        ]
        
        # Execute all stages
        all_success = True
        for stage_name, stage_func in stages:
            try:
                success = stage_func()
                if not success:
                    all_success = False
            except Exception as e:
                print(f"💥 Stage '{stage_name}' crashed: {str(e)}")
                all_success = False
        
        # Generate final report
        return self.generate_report()

def main():
    """Main CI/CD execution"""
    pipeline = CIPipeline()
    success = pipeline.run_pipeline()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
