#!/usr/bin/env python3
"""
START TESTING AGENTS NOW
Emergency launcher to get agents actually working on testing
"""

import subprocess
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

class TestingAgentLauncher:
    """Launch testing agents immediately"""
    
    def __init__(self):
        self.base_path = Path("E:/Projects")
        self.agent_path = self.base_path / "src" / "agents"
        self.processes = {}
        
        # Critical agents for testing
        self.testing_agents = {
            "qa": {
                "script": "ai-qa-agent.py",
                "args": ["--process-all", "--run-tests"],
                "description": "QA Agent - Run Playwright tests"
            },
            "developer": {
                "script": "ai-developer-agent.py", 
                "args": ["--process-all", "--fix-bugs"],
                "description": "Developer Agent - Fix bugs"
            },
            "operations": {
                "script": "ai-operations-agent.py",
                "args": ["--monitor"],
                "description": "Operations Agent - Monitor progress"
            }
        }
        
        # Check for GitHub token
        self.github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        if not self.github_token:
            print("[WARNING] No GitHub token found. Trying to read from gh config...")
            self.setup_github_token()
    
    def setup_github_token(self):
        """Try to get GitHub token from gh CLI"""
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                self.github_token = result.stdout.strip()
                os.environ['GITHUB_TOKEN'] = self.github_token
                print("[OK] GitHub token retrieved from gh CLI")
            else:
                print("[ERROR] No GitHub token available. Agents won't be able to create issues!")
        except Exception as e:
            print(f"[ERROR] Could not get GitHub token: {e}")
    
    def create_test_runner_script(self):
        """Create a script that runs Playwright tests"""
        script_content = '''#!/usr/bin/env python3
"""Auto-generated test runner for Playwright tests"""
import os
import subprocess
from pathlib import Path

def run_service_tests(service_path, test_dir="mfe/tests"):
    """Run Playwright tests for a service"""
    full_path = Path(service_path) / test_dir
    if not full_path.exists():
        return False
        
    os.chdir(service_path)
    
    # Install dependencies if needed
    if not Path("node_modules").exists():
        print(f"Installing dependencies for {service_path}...")
        subprocess.run(["npm", "install"], capture_output=True)
    
    # Run tests
    print(f"Running Playwright tests in {service_path}/{test_dir}...")
    result = subprocess.run(
        ["npx", "playwright", "test", "--reporter=list"],
        capture_output=False
    )
    
    return result.returncode == 0

# Services to test
services = [
    ("E:/Projects/VisualForgeMediaV2/vf-dashboard-service", "mfe/tests"),
    ("E:/Projects/VisualForgeMediaV2/vf-audio-service", "mfe/tests"),
    ("E:/Projects/VisualForgeMediaV2/vf-video-service", "mfe/tests"),
    ("E:/Projects/NiroSubs-V2/ns-shell", "tests")
]

print("[TEST RUNNER] Starting Playwright test execution")
for service_path, test_dir in services:
    if Path(service_path).exists():
        print(f"\\nTesting {service_path}...")
        success = run_service_tests(service_path, test_dir)
        if not success:
            print(f"[FAILED] Tests failed for {service_path}")
            # Create bug issue
            subprocess.run([
                "gh", "issue", "create",
                "--repo", "VisualForgeMediaV2/business-operations",
                "--title", f"[BUG] Test failures in {Path(service_path).name}",
                "--body", f"Playwright tests failed in {service_path}\\nRequires immediate fix",
                "--label", "bug,testing,priority/P1"
            ])
'''
        
        script_path = self.base_path / "run-tests-now.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"[CREATED] Test runner script: {script_path}")
        return script_path
    
    def start_agent(self, name, config):
        """Start a single agent process"""
        script_path = self.agent_path / config["script"]
        
        if not script_path.exists():
            print(f"[ERROR] Agent script not found: {script_path}")
            return None
        
        try:
            print(f"\n[STARTING] {config['description']}")
            print(f"  Script: {script_path}")
            print(f"  Args: {config['args']}")
            
            # Set up environment
            env = os.environ.copy()
            env['GITHUB_TOKEN'] = self.github_token or ''
            env['PYTHONPATH'] = str(self.agent_path)
            
            # Start the process
            process = subprocess.Popen(
                [sys.executable, str(script_path)] + config['args'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.agent_path)
            )
            
            self.processes[name] = process
            print(f"[OK] Started {name} agent (PID: {process.pid})")
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if still running
            if process.poll() is None:
                print(f"[RUNNING] {name} agent is active")
                return process
            else:
                stdout, stderr = process.communicate(timeout=1)
                print(f"[FAILED] {name} agent exited immediately")
                if stderr:
                    print(f"  Error: {stderr.decode()[:200]}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Failed to start {name}: {e}")
            return None
    
    def create_test_issues(self):
        """Create GitHub issues to trigger agent work"""
        print("\n[CREATING TEST ISSUES]")
        
        issues = [
            {
                "title": "[QA] Run all Playwright tests immediately",
                "body": "Run Playwright tests for ALL services and report failures",
                "labels": "agent-task,testing,priority/P0"
            },
            {
                "title": "[DEV] Fix all test failures",
                "body": "Fix any bugs found by Playwright tests",
                "labels": "agent-task,bug,priority/P0"
            },
            {
                "title": "[OPS] Monitor test execution",
                "body": "Monitor and report on test execution progress",
                "labels": "operations/monitoring,priority/P0"
            }
        ]
        
        for issue in issues:
            try:
                cmd = [
                    "gh", "issue", "create",
                    "--repo", "VisualForgeMediaV2/business-operations",
                    "--title", issue["title"],
                    "--body", issue["body"],
                    "--label", issue["labels"]
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"[OK] Created issue: {issue['title']}")
                else:
                    print(f"[FAILED] Could not create issue: {issue['title']}")
            except Exception as e:
                print(f"[ERROR] Issue creation failed: {e}")
    
    def launch_all(self):
        """Launch all testing agents"""
        print("="*80)
        print("EMERGENCY TESTING AGENT LAUNCHER")
        print("="*80)
        print(f"Time: {datetime.now().isoformat()}")
        print(f"GitHub Token: {'Available' if self.github_token else 'MISSING'}")
        
        # Create test runner script
        test_runner = self.create_test_runner_script()
        
        # Create issues to trigger work
        self.create_test_issues()
        
        # Start agents
        print("\n[STARTING AGENTS]")
        for name, config in self.testing_agents.items():
            self.start_agent(name, config)
        
        # Start test runner directly
        print("\n[STARTING TEST RUNNER]")
        try:
            test_process = subprocess.Popen(
                [sys.executable, str(test_runner)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self.processes["test_runner"] = test_process
            print(f"[OK] Test runner started (PID: {test_process.pid})")
        except Exception as e:
            print(f"[ERROR] Could not start test runner: {e}")
        
        # Summary
        print("\n" + "="*80)
        print("LAUNCH SUMMARY")
        print("="*80)
        
        running = sum(1 for p in self.processes.values() if p and p.poll() is None)
        print(f"Agents Started: {running}/{len(self.testing_agents) + 1}")
        
        if running > 0:
            print("\n[SUCCESS] Agents are now running!")
            print("Monitor their progress with: python agent-accountability-tracker.py")
            print("\nRunning Processes:")
            for name, process in self.processes.items():
                if process and process.poll() is None:
                    print(f"  - {name}: PID {process.pid}")
        else:
            print("\n[FAILURE] No agents started successfully")
            print("Check the agent scripts for errors")
        
        return running > 0

if __name__ == "__main__":
    launcher = TestingAgentLauncher()
    
    print("[COORDINATOR] Emergency launch of testing agents")
    print("[COORDINATOR] Agents MUST start working NOW\n")
    
    success = launcher.launch_all()
    
    if success:
        print("\n[COORDINATOR] Agents launched. They better start working!")
        print("[COORDINATOR] Run accountability check in 5 minutes")
    else:
        print("\n[COORDINATOR] Launch failed! Manual intervention required")
        print("[COORDINATOR] Check agent scripts and GitHub token")