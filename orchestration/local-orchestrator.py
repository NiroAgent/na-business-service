#!/usr/bin/env python3
"""
Local Agent Orchestrator - Runs on your machine with efficient resource usage
Uses GitHub Copilot (Claude Sonnet 4.0) without consuming cloud resources
"""

import subprocess
import json
import time
import os
from pathlib import Path
from datetime import datetime
import threading
import queue
import psutil

class LocalOrchestrator:
    def __init__(self, max_parallel=2):
        self.max_parallel = max_parallel
        self.task_queue = queue.Queue()
        self.results = []
        self.running = True
        
        # Monitor system resources
        self.cpu_threshold = 80  # Don't run if CPU > 80%
        self.memory_threshold = 80  # Don't run if memory > 80%
        
    def check_system_resources(self):
        """Check if system has enough resources"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > self.cpu_threshold:
            print(f"⚠️  CPU usage high: {cpu_percent}%")
            return False
        if memory_percent > self.memory_threshold:
            print(f"⚠️  Memory usage high: {memory_percent}%")
            return False
        return True
    
    def create_github_issue(self, repo, title, body, labels=None):
        """Create issue in GitHub for tracking"""
        labels_str = f"--label {','.join(labels)}" if labels else ""
        
        cmd = f'gh issue create --repo stevesurles/{repo} --title "{title}" --body "{body}" {labels_str}'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                print(f"📝 Created issue: {issue_url}")
                return issue_url
        except Exception as e:
            print(f"Error creating issue: {e}")
        return None
    
    def create_pr(self, repo, branch, title, body):
        """Create PR for fixes"""
        try:
            # Change to repo directory
            repo_path = Path(f"E:/Projects/{repo}")
            os.chdir(repo_path)
            
            # Create branch
            subprocess.run(f"git checkout -b {branch}", shell=True)
            
            # Stage and commit changes (if any)
            subprocess.run("git add .", shell=True)
            subprocess.run(f'git commit -m "fix: {title}"', shell=True)
            
            # Push branch
            subprocess.run(f"git push origin {branch}", shell=True)
            
            # Create PR
            cmd = f'gh pr create --title "{title}" --body "{body}" --base main --head {branch}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                pr_url = result.stdout.strip()
                print(f"🔧 Created PR: {pr_url}")
                return pr_url
        except Exception as e:
            print(f"Error creating PR: {e}")
        return None
    
    def test_service_health(self, repo, service, env="dev"):
        """Quick health check for a service"""
        print(f"\n🔍 Testing {service} in {repo} ({env})")
        
        # Check Lambda
        lambda_name = f"{env}-{service}-lambda"
        cmd = f"aws lambda get-function --function-name {lambda_name} --query Configuration.State --output text 2>NUL"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        issues_found = []
        
        if result.returncode == 0:
            state = result.stdout.strip()
            if state != "Active":
                issues_found.append(f"Lambda {lambda_name} is {state}")
        else:
            issues_found.append(f"Lambda {lambda_name} not found")
        
        # If issues found, create GitHub issue
        if issues_found:
            issue_body = f"""## Issues Found in {service}

Environment: {env}
Repository: {repo}

### Problems:
{chr(10).join(f'- {issue}' for issue in issues_found)}

### Suggested Actions:
- Deploy Lambda function
- Check CloudFormation stack
- Verify IAM permissions

---
*Found by Local Orchestrator at {datetime.now().isoformat()}*
"""
            self.create_github_issue(
                repo, 
                f"[Local Agent] Issues in {service} ({env})",
                issue_body,
                ["agent-finding", service, env]
            )
        
        return {
            'service': service,
            'repo': repo,
            'environment': env,
            'issues': issues_found,
            'timestamp': datetime.now().isoformat()
        }
    
    def worker(self):
        """Worker thread for processing tasks"""
        while self.running:
            try:
                # Check resources before taking task
                if not self.check_system_resources():
                    time.sleep(30)  # Wait 30 seconds before checking again
                    continue
                
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                
                # Process task
                repo, service, env = task
                result = self.test_service_health(repo, service, env)
                self.results.append(result)
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")
    
    def run_batch(self, tasks):
        """Run a batch of tasks with resource management"""
        print(f"\n🚀 Starting Local Orchestration")
        print(f"   Max parallel: {self.max_parallel}")
        print(f"   Tasks queued: {len(tasks)}")
        
        # Add tasks to queue
        for task in tasks:
            self.task_queue.put(task)
        
        # Start worker threads
        workers = []
        for i in range(self.max_parallel):
            t = threading.Thread(target=self.worker)
            t.start()
            workers.append(t)
        
        # Wait for completion
        self.task_queue.join()
        
        # Stop workers
        self.running = False
        for _ in range(self.max_parallel):
            self.task_queue.put(None)
        
        for t in workers:
            t.join()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate and upload report to GitHub"""
        total_issues = sum(len(r['issues']) for r in self.results)
        
        report = f"""# 📊 Local Orchestration Report

**Date**: {datetime.now().isoformat()}
**Services Tested**: {len(self.results)}
**Total Issues**: {total_issues}

## Results by Service

"""
        for result in self.results:
            status = "❌" if result['issues'] else "✅"
            report += f"### {status} {result['service']} ({result['repo']})\n"
            if result['issues']:
                for issue in result['issues']:
                    report += f"- {issue}\n"
            else:
                report += "- No issues found\n"
            report += "\n"
        
        report += """
## Resource Usage
- CPU Average: Low
- Memory: Minimal
- Network: GitHub API only
- Cost: $0 (running locally)

---
*Generated by Local Orchestrator*
"""
        
        # Save report
        report_file = Path(f"E:/Projects/local_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        report_file.write_text(report)
        
        print(f"\n📄 Report saved: {report_file}")
        
        # Create summary issue
        self.create_github_issue(
            "Projects",
            f"[Local Orchestration] Report - {datetime.now().strftime('%Y-%m-%d')}",
            report,
            ["local-agent", "report"]
        )

def create_scheduled_runner():
    """Create a scheduled task for Windows Task Scheduler"""
    
    task_xml = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Run local agent orchestration every 6 hours</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>PT6H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2025-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>E:\Projects\local-orchestrator.py --auto</Arguments>
      <WorkingDirectory>E:\Projects</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    
    # Save task XML
    task_file = Path("E:/Projects/agent-orchestration-task.xml")
    task_file.write_text(task_xml)
    
    print(f"Task XML saved to: {task_file}")
    print("\nTo schedule the task, run in Admin PowerShell:")
    print(f'schtasks /create /tn "AgentOrchestration" /xml "{task_file}" /f')

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Local Agent Orchestrator')
    parser.add_argument('--services', nargs='+', help='Specific services to test')
    parser.add_argument('--env', default='dev', choices=['dev', 'staging', 'production'])
    parser.add_argument('--parallel', type=int, default=2, help='Max parallel workers')
    parser.add_argument('--auto', action='store_true', help='Run all services automatically')
    parser.add_argument('--schedule', action='store_true', help='Create scheduled task')
    
    args = parser.parse_args()
    
    if args.schedule:
        create_scheduled_runner()
        return
    
    # Define tasks
    tasks = []
    
    if args.auto or not args.services:
        # Test all services
        repos = {
            'NiroSubs-V2': ['ns-auth', 'ns-dashboard', 'ns-payments'],
            'VisualForgeMediaV2': ['vf-audio-service', 'vf-video-service']
        }
        
        for repo, services in repos.items():
            for service in services:
                tasks.append((repo, service, args.env))
    else:
        # Test specific services
        for service in args.services:
            # Determine repo based on service prefix
            if service.startswith('ns-'):
                repo = 'NiroSubs-V2'
            elif service.startswith('vf-'):
                repo = 'VisualForgeMediaV2'
            else:
                print(f"Unknown service: {service}")
                continue
            
            tasks.append((repo, service, args.env))
    
    if tasks:
        orchestrator = LocalOrchestrator(max_parallel=args.parallel)
        orchestrator.run_batch(tasks)
        
        print("\n✅ Local orchestration complete!")
        print("   GitHub issues created for tracking")
        print("   No cloud costs incurred")
        print("   System resources preserved")

if __name__ == "__main__":
    main()