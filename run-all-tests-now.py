#!/usr/bin/env python3
"""
Run ALL Playwright Tests Across ALL Services
Coordinator enforcing test execution and bug fixes
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class TestRunner:
    """Run and monitor all Playwright tests"""
    
    def __init__(self):
        self.base_path = "E:\\Projects"
        self.results = {}
        self.failures = []
        
        self.services = {
            "VisualForgeMediaV2": {
                "vf-dashboard-service": "mfe/tests",
                "vf-image-service": "mfe/tests",
                "vf-audio-service": "mfe/tests",
                "vf-video-service": "mfe/tests",
                "vf-text-service": "mfe/tests",
                "vf-agent-service": "tests/e2e",
                "vf-bulk-service": "mfe/tests"
            },
            "NiroSubs-V2": {
                "ns-shell": "tests",
                "ns-auth": "frontend/tests",
                "ns-dashboard": "frontend/tests",
                "ns-payments": "tests",
                "ns-user": "frontend/tests",
                "nirosubs-v2-platform/ns-auth-service": "mfe/tests",
                "nirosubs-v2-platform/ns-dashboard-service": "mfe/tests",
                "nirosubs-v2-platform/ns-payment-service": "mfe/tests"
            }
        }
        
    def run_service_tests(self, org: str, service: str, test_path: str) -> Tuple[bool, str]:
        """Run tests for a specific service"""
        service_path = Path(self.base_path) / org / service
        full_test_path = service_path / test_path
        
        if not full_test_path.exists():
            return False, f"Test path not found: {full_test_path}"
        
        print(f"\n[TESTING] {org}/{service}")
        print("-" * 50)
        
        # Check if package.json exists
        package_json = service_path / "package.json"
        if not package_json.exists():
            package_json = service_path / test_path.split('/')[0] / "package.json"
        
        if not package_json.exists():
            return False, "No package.json found"
        
        # Navigate to service directory
        os.chdir(service_path if (service_path / "package.json").exists() else service_path / test_path.split('/')[0])
        
        # Install dependencies if needed
        if not Path("node_modules").exists():
            print("Installing dependencies...")
            subprocess.run(["npm", "install"], capture_output=True)
        
        # Install Playwright browsers if needed
        print("Ensuring Playwright browsers are installed...")
        subprocess.run(["npx", "playwright", "install"], capture_output=True)
        
        # Run tests
        print(f"Running Playwright tests in {test_path}...")
        result = subprocess.run(
            ["npx", "playwright", "test", "--reporter=json"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Parse results
        if result.stdout:
            try:
                test_results = json.loads(result.stdout)
                passed = test_results.get("stats", {}).get("expected", 0)
                failed = test_results.get("stats", {}).get("unexpected", 0)
                total = passed + failed
                
                self.results[f"{org}/{service}"] = {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "status": "PASS" if failed == 0 else "FAIL"
                }
                
                if failed > 0:
                    self.failures.append({
                        "service": f"{org}/{service}",
                        "failures": failed,
                        "details": test_results.get("errors", [])
                    })
                
                return failed == 0, f"Tests: {passed}/{total} passed"
            except:
                return False, "Could not parse test results"
        
        return False, f"Test execution failed: {result.stderr}"
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("PLAYWRIGHT TEST EXECUTION REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().isoformat()}")
        print(f"Coordinator: Enforcing test execution and bug fixes\n")
        
        # Summary
        total_services = len(self.results)
        passing_services = sum(1 for r in self.results.values() if r.get("status") == "PASS")
        failing_services = total_services - passing_services
        
        print("[SUMMARY]")
        print(f"Services Tested: {total_services}")
        print(f"Services Passing: {passing_services}")
        print(f"Services Failing: {failing_services}")
        
        # Detailed Results
        print("\n[SERVICE TEST RESULTS]")
        print("-" * 50)
        for service, result in self.results.items():
            status_icon = "[PASS]" if result["status"] == "PASS" else "[FAIL]"
            print(f"{status_icon} {service:40} {result['passed']}/{result['total']} tests passing")
        
        # Failures requiring immediate attention
        if self.failures:
            print("\n[CRITICAL FAILURES - MUST FIX NOW]")
            print("-" * 50)
            for failure in self.failures:
                print(f"\n{failure['service']}: {failure['failures']} failures")
                if failure.get('details'):
                    for detail in failure['details'][:3]:  # Show first 3 errors
                        print(f"  - {detail}")
        
        # Agent Assignments
        print("\n[AGENT ASSIGNMENTS FOR BUG FIXES]")
        print("-" * 50)
        
        if failing_services > 0:
            print("ai-qa-agent: Debug and fix test failures")
            print("ai-developer-agent: Fix application bugs found by tests")
            print("ai-devops-agent: Fix infrastructure/deployment issues")
        else:
            print("All tests passing! Move to next phase of testing.")
        
        # Next Steps
        print("\n[IMMEDIATE ACTIONS REQUIRED]")
        print("-" * 50)
        if failing_services > 0:
            print("1. ALL agents must focus on fixing test failures")
            print("2. Critical services (auth, payments) take priority")
            print("3. Re-run tests after each fix")
            print("4. No deployment until all tests pass")
        else:
            print("1. Expand test coverage")
            print("2. Add integration tests")
            print("3. Performance testing")
            print("4. Security testing")
        
        print("\n" + "=" * 80)
        print("END OF TEST REPORT")
        print("=" * 80)
        
        # Save report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_services": total_services,
                "passing": passing_services,
                "failing": failing_services
            },
            "results": self.results,
            "failures": self.failures
        }
        
        with open("test_execution_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        return report_data
    
    def run_all_tests(self):
        """Run tests for all services"""
        print("[COORDINATOR] Starting comprehensive test execution")
        print("[COORDINATOR] Every service MUST be tested")
        print("[COORDINATOR] Every bug MUST be fixed\n")
        
        for org, services in self.services.items():
            for service, test_path in services.items():
                try:
                    success, message = self.run_service_tests(org, service, test_path)
                    print(f"Result: {message}\n")
                except Exception as e:
                    print(f"Error testing {org}/{service}: {e}\n")
                    self.results[f"{org}/{service}"] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "status": "ERROR",
                        "error": str(e)
                    }
        
        # Generate and display report
        self.generate_report()
        
        # Return to original directory
        os.chdir(self.base_path)

if __name__ == "__main__":
    runner = TestRunner()
    
    print("[COORDINATOR] MANDATORY TEST EXECUTION")
    print("[COORDINATOR] All developers and QA must fix failing tests")
    print("[COORDINATOR] No excuses - tests must pass!\n")
    
    runner.run_all_tests()
    
    print("\n[COORDINATOR] Test execution complete")
    print("[COORDINATOR] Report saved to test_execution_report.json")
    print("[COORDINATOR] All failing tests MUST be fixed TODAY")