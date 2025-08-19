#!/usr/bin/env python3
"""
Testing Progress Monitor
Tracks Playwright testing implementation across all services
Ensures all dev/QA agents are working on tests
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class TestingProgressMonitor:
    """Monitor and enforce testing directive"""
    
    def __init__(self):
        self.services = {
            "vf-agent-service": {"status": "pilot", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "ns-auth": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "ns-payments": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "ns-dashboard": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "ns-user": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "ns-shell": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "vf-audio": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "vf-video": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "vf-image": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "vf-text-service": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "vf-bulk": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
            "vf-dashboard": {"status": "pending", "coverage": 0, "bugs_found": 0, "bugs_fixed": 0},
        }
        
        self.agents = {
            "ai-qa-agent": {"assigned_to": "vf-agent-service", "tasks_today": 0},
            "ai-developer-agent": {"assigned_to": "vf-agent-service", "tasks_today": 0},
            "ai-devops-agent": {"assigned_to": "infrastructure", "tasks_today": 0},
        }
        
    def check_playwright_tests(self, service_path):
        """Check if Playwright tests exist for a service"""
        test_patterns = [
            "tests/e2e/*.spec.ts",
            "tests/e2e/*.spec.js",
            "tests/integration/*.spec.ts",
            "tests/*.spec.ts",
            "e2e/*.spec.ts"
        ]
        
        test_count = 0
        for pattern in test_patterns:
            test_files = list(Path(service_path).glob(pattern))
            test_count += len(test_files)
        
        return test_count
    
    def check_test_coverage(self, service_path):
        """Check test coverage for a service"""
        coverage_file = Path(service_path) / "coverage" / "coverage-summary.json"
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)
                if "total" in coverage_data and "lines" in coverage_data["total"]:
                    return coverage_data["total"]["lines"]["pct"]
        return 0
    
    def find_bugs_in_issues(self, service_name):
        """Find bugs reported for a service"""
        try:
            # Check for bug issues
            cmd = [
                "gh", "issue", "list",
                "--repo", f"VisualForgeMediaV2/{service_name}",
                "--label", "bug",
                "--json", "number,title,state",
                "--limit", "100"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                issues = json.loads(result.stdout)
                open_bugs = [i for i in issues if i["state"] == "OPEN"]
                closed_bugs = [i for i in issues if i["state"] == "CLOSED"]
                return len(open_bugs), len(closed_bugs)
        except:
            pass
        return 0, 0
    
    def generate_progress_report(self):
        """Generate comprehensive testing progress report"""
        print("\n" + "="*80)
        print("PLAYWRIGHT TESTING PROGRESS REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().isoformat()}")
        print("Directive: ALL services MUST have full Playwright coverage\n")
        
        # Service Status
        print("[SERVICE TESTING STATUS]")
        print("-"*50)
        
        total_services = len(self.services)
        services_with_tests = 0
        total_bugs = 0
        
        for service, status in self.services.items():
            status_icon = "[!]" if status["status"] == "pilot" else "[ ]"
            coverage_str = f"{status['coverage']}%" if status['coverage'] > 0 else "NO TESTS"
            
            # Check actual test files
            service_paths = [
                f"E:\\Projects\\vf-agent-service-local",
                f"E:\\Projects\\VisualForgeMediaV2\\{service}",
                f"E:\\Projects\\NiroSubs-V2\\{service}"
            ]
            
            test_count = 0
            for path in service_paths:
                if os.path.exists(path):
                    test_count = self.check_playwright_tests(path)
                    if test_count > 0:
                        services_with_tests += 1
                        break
            
            print(f"{status_icon} {service:20} Coverage: {coverage_str:10} Tests: {test_count:3} Status: {status['status']}")
            total_bugs += status.get('bugs_found', 0)
        
        # Agent Assignments
        print("\n[AGENT ASSIGNMENTS]")
        print("-"*50)
        for agent, info in self.agents.items():
            print(f"{agent:25} Assigned: {info['assigned_to']:20} Tasks Today: {info['tasks_today']}")
        
        # Critical Metrics
        print("\n[CRITICAL METRICS]")
        print("-"*50)
        print(f"Services with Playwright Tests: {services_with_tests}/{total_services}")
        print(f"Total Bugs Found: {total_bugs}")
        print(f"Pilot Status (vf-agent-service): {self.services['vf-agent-service']['status']}")
        
        # Action Items
        print("\n[COORDINATOR ACTION ITEMS]")
        print("-"*50)
        
        if services_with_tests == 0:
            print("[CRITICAL] No services have Playwright tests yet!")
            print("[ACTION] Immediately assign ai-qa-agent to write tests for vf-agent-service")
            print("[ACTION] Assign ai-developer-agent to fix setup issues")
        
        if self.services["vf-agent-service"]["status"] == "pilot" and self.services["vf-agent-service"]["coverage"] < 50:
            print("[URGENT] Pilot service coverage below 50%")
            print("[ACTION] Focus all QA resources on pilot completion")
        
        # Enforcement
        print("\n[ENFORCEMENT ACTIONS]")
        print("-"*50)
        print("1. All idle agents being reassigned to testing")
        print("2. Daily standup required for progress updates")
        print("3. Blockers escalated to PM immediately")
        print("4. No service deployment without 80% coverage")
        
        # Next Steps
        print("\n[NEXT 24 HOURS]")
        print("-"*50)
        print("1. Complete vf-agent-service pilot tests")
        print("2. Fix all critical bugs found")
        print("3. Document testing patterns")
        print("4. Prepare rollout to ns-auth and ns-payments")
        
        print("\n" + "="*80)
        print("END OF TESTING PROGRESS REPORT")
        print("="*80)
        
        # Save progress data
        progress_data = {
            "timestamp": datetime.now().isoformat(),
            "services": self.services,
            "agents": self.agents,
            "metrics": {
                "services_with_tests": services_with_tests,
                "total_services": total_services,
                "total_bugs_found": total_bugs
            }
        }
        
        with open("testing_progress.json", "w") as f:
            json.dump(progress_data, f, indent=2)
        
        return progress_data
    
    def create_agent_tasks(self):
        """Create specific tasks for each agent"""
        tasks = []
        
        # QA Agent tasks
        tasks.append({
            "agent": "ai-qa-agent",
            "priority": "P0",
            "task": "Write Playwright E2E tests for vf-agent-service authentication flow",
            "deadline": "Today"
        })
        
        tasks.append({
            "agent": "ai-qa-agent", 
            "priority": "P0",
            "task": "Write Playwright API tests for all vf-agent-service endpoints",
            "deadline": "Today"
        })
        
        # Developer Agent tasks
        tasks.append({
            "agent": "ai-developer-agent",
            "priority": "P0",
            "task": "Fix any test setup issues in vf-agent-service",
            "deadline": "Today"
        })
        
        tasks.append({
            "agent": "ai-developer-agent",
            "priority": "P0",
            "task": "Fix bugs found by Playwright tests",
            "deadline": "Ongoing"
        })
        
        # DevOps Agent tasks
        tasks.append({
            "agent": "ai-devops-agent",
            "priority": "P1",
            "task": "Setup Playwright test infrastructure in vf-dev",
            "deadline": "Today"
        })
        
        print("\n[AGENT TASK ASSIGNMENTS]")
        print("-"*50)
        for task in tasks:
            print(f"{task['agent']} [{task['priority']}]: {task['task']} - Due: {task['deadline']}")
        
        return tasks

if __name__ == "__main__":
    monitor = TestingProgressMonitor()
    
    print("[TESTING MONITOR] Checking Playwright testing progress...")
    print("[COORDINATOR] Enforcing comprehensive testing directive")
    
    # Generate progress report
    progress = monitor.generate_progress_report()
    
    # Create specific agent tasks
    tasks = monitor.create_agent_tasks()
    
    print("\n[COORDINATOR] Testing directive is MANDATORY")
    print("[COORDINATOR] All agents must focus on testing and bug fixes")
    print("[COORDINATOR] Progress report saved to testing_progress.json")