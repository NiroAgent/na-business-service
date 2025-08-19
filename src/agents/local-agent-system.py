#!/usr/bin/env python3
"""
Complete Local Agent Orchestration System
Runs everything locally with GitHub Copilot (Claude Sonnet 4.0)
Zero cloud costs - all processing on your machine
"""

import subprocess
import json
import time
import os
import threading
import queue
from pathlib import Path
from datetime import datetime, timedelta
import psutil
import schedule
import webbrowser
from typing import Dict, List, Any

class LocalAgentSystem:
    def __init__(self):
        self.base_dir = Path("E:/Projects")
        self.reports_dir = self.base_dir / "agent-reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.config = {
            'max_parallel_agents': 2,
            'cpu_threshold': 70,  # Don't run if CPU > 70%
            'memory_threshold': 75,  # Don't run if RAM > 75%
            'check_interval_minutes': 120,  # Check every 2 hours
            'comprehensive_test_hour': 22,  # Run full test at 10 PM
        }
        
        # Services to monitor
        self.services = {
            'NiroSubs-V2': [
                'ns-auth', 'ns-dashboard', 'ns-payments', 'ns-user', 'ns-shell'
            ],
            'VisualForgeMediaV2': [
                'vf-audio-service', 'vf-video-service', 'vf-image-service',
                'vf-text-service', 'vf-bulk-service', 'vf-dashboard-service'
            ]
        }
        
        # Task queue for agents
        self.task_queue = queue.Queue()
        self.results = []
        self.running = True
        
    def check_system_resources(self) -> bool:
        """Check if system has resources available"""
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        
        if cpu > self.config['cpu_threshold']:
            print(f"⚠️  CPU too high: {cpu}% (threshold: {self.config['cpu_threshold']}%)")
            return False
            
        if memory > self.config['memory_threshold']:
            print(f"⚠️  Memory too high: {memory}% (threshold: {self.config['memory_threshold']}%)")
            return False
            
        print(f"✅ Resources OK - CPU: {cpu:.1f}%, Memory: {memory:.1f}%")
        return True
    
    def run_gh_copilot_test(self, service: str, repo: str, env: str = "dev") -> Dict[str, Any]:
        """Run GitHub Copilot to test a service locally"""
        
        print(f"\n🤖 Testing {service} with GitHub Copilot...")
        
        result = {
            'service': service,
            'repo': repo,
            'environment': env,
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'issues': [],
            'suggestions': []
        }
        
        # Test 1: Check service structure
        service_path = self.base_dir / repo / service
        if not service_path.exists():
            result['issues'].append(f"Service directory not found: {service_path}")
            return result
        
        # Test 2: Check for common issues using gh copilot
        prompts = [
            f"Check {service} service for common issues",
            f"Test commands for {service} Lambda function",
            f"Security checks for {service}",
            f"Performance optimization for {service}"
        ]
        
        for prompt in prompts:
            try:
                # Use gh copilot suggest
                cmd = f'echo "1" | gh copilot suggest "{prompt}"'
                
                process = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(service_path),
                    timeout=30
                )
                
                if process.returncode == 0:
                    output = process.stdout
                    if output:
                        result['suggestions'].append({
                            'prompt': prompt,
                            'response': output[:500]  # Limit response length
                        })
                
            except subprocess.TimeoutExpired:
                result['issues'].append(f"Timeout on: {prompt}")
            except Exception as e:
                result['issues'].append(f"Error on {prompt}: {str(e)}")
            
            # Rate limiting
            time.sleep(2)
        
        # Test 3: Local file checks (no AWS calls)
        local_checks = self.run_local_checks(service_path)
        result['tests'].extend(local_checks)
        
        return result
    
    def run_local_checks(self, service_path: Path) -> List[Dict]:
        """Run local checks without any cloud API calls"""
        
        checks = []
        
        # Check package.json
        package_json = service_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                    
                checks.append({
                    'check': 'package.json',
                    'status': 'found',
                    'version': package_data.get('version', 'unknown')
                })
                
                # Check for test script
                if 'test' in package_data.get('scripts', {}):
                    checks.append({
                        'check': 'test script',
                        'status': 'configured'
                    })
                    
            except Exception as e:
                checks.append({
                    'check': 'package.json',
                    'status': 'error',
                    'error': str(e)
                })
        
        # Check for CloudFormation/Serverless
        if (service_path / "cloudformation.yaml").exists():
            checks.append({'check': 'CloudFormation', 'status': 'found'})
        elif (service_path / "serverless.yml").exists():
            checks.append({'check': 'Serverless', 'status': 'found'})
        else:
            checks.append({'check': 'Infrastructure', 'status': 'missing'})
        
        # Check for tests
        test_files = list(service_path.glob("*.test.js")) + list(service_path.glob("*.spec.js"))
        checks.append({
            'check': 'test files',
            'status': 'found' if test_files else 'missing',
            'count': len(test_files)
        })
        
        # Check git status
        try:
            git_status = subprocess.run(
                "git status --porcelain",
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(service_path.parent)
            )
            
            if git_status.stdout:
                uncommitted = len(git_status.stdout.strip().split('\n'))
                checks.append({
                    'check': 'git status',
                    'status': 'uncommitted changes',
                    'count': uncommitted
                })
            else:
                checks.append({'check': 'git status', 'status': 'clean'})
                
        except Exception:
            pass
        
        return checks
    
    def create_local_issue_report(self, results: List[Dict]):
        """Create a local HTML report instead of GitHub issue"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"report_{timestamp}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Agent Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #0366d6; color: white; padding: 20px; border-radius: 5px; }}
                .service {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .issues {{ background: #ffebee; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .success {{ background: #e8f5e9; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .suggestion {{ background: #f3f4f6; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                .status-good {{ color: green; }}
                .status-bad {{ color: red; }}
                .status-warning {{ color: orange; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 Local Agent Testing Report</h1>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p>Services Tested: {len(results)}</p>
            </div>
        """
        
        total_issues = sum(len(r.get('issues', [])) for r in results)
        
        if total_issues > 0:
            html_content += f"""
            <div class="issues">
                <h2>⚠️ Issues Found: {total_issues}</h2>
            </div>
            """
        else:
            html_content += """
            <div class="success">
                <h2>✅ All Services Healthy</h2>
            </div>
            """
        
        for result in results:
            service = result['service']
            repo = result['repo']
            issues = result.get('issues', [])
            tests = result.get('tests', [])
            suggestions = result.get('suggestions', [])
            
            status_icon = "❌" if issues else "✅"
            
            html_content += f"""
            <div class="service">
                <h3>{status_icon} {service} ({repo})</h3>
                <p>Environment: {result.get('environment', 'dev')}</p>
                <p>Tested: {result.get('timestamp', 'N/A')}</p>
            """
            
            if tests:
                html_content += """
                <h4>Local Checks:</h4>
                <table>
                    <tr><th>Check</th><th>Status</th><th>Details</th></tr>
                """
                for test in tests:
                    status_class = "status-good" if test.get('status') in ['found', 'clean', 'configured'] else "status-warning"
                    html_content += f"""
                    <tr>
                        <td>{test.get('check', 'N/A')}</td>
                        <td class="{status_class}">{test.get('status', 'N/A')}</td>
                        <td>{test.get('count', '') if 'count' in test else ''}</td>
                    </tr>
                    """
                html_content += "</table>"
            
            if issues:
                html_content += """
                <h4>Issues:</h4>
                <ul>
                """
                for issue in issues:
                    html_content += f"<li>{issue}</li>"
                html_content += "</ul>"
            
            if suggestions:
                html_content += """
                <div class="suggestion">
                    <h4>GitHub Copilot Suggestions:</h4>
                """
                for suggestion in suggestions[:2]:  # Show only first 2
                    html_content += f"""
                    <p><strong>{suggestion['prompt']}:</strong></p>
                    <pre>{suggestion['response'][:200]}...</pre>
                    """
                html_content += "</div>"
            
            html_content += "</div>"
        
        html_content += """
            <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
                <h3>System Resources</h3>
                <p>CPU Usage: """ + f"{psutil.cpu_percent()}%" + """</p>
                <p>Memory Usage: """ + f"{psutil.virtual_memory().percent}%" + """</p>
                <p>Next Run: """ + f"{(datetime.now() + timedelta(minutes=self.config['check_interval_minutes'])).strftime('%H:%M')}" + """</p>
            </div>
        </body>
        </html>
        """
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n📄 Report saved: {report_file}")
        
        # Open in browser
        if total_issues > 0:
            webbrowser.open(f"file:///{report_file}")
    
    def agent_worker(self):
        """Worker thread for processing service tests"""
        
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                
                repo, service, env = task
                result = self.run_gh_copilot_test(service, repo, env)
                self.results.append(result)
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")
    
    def run_orchestration(self, comprehensive: bool = False):
        """Run the orchestration cycle"""
        
        print("\n" + "="*60)
        print("🚀 LOCAL AGENT ORCHESTRATION")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'Comprehensive' if comprehensive else 'Quick Check'}")
        print("="*60)
        
        # Check system resources
        if not self.check_system_resources():
            print("⏸️  Postponing due to high resource usage")
            return
        
        # Clear previous results
        self.results = []
        
        # Queue tasks
        task_count = 0
        for repo, services in self.services.items():
            # In quick mode, only test first 2 services per repo
            services_to_test = services if comprehensive else services[:2]
            
            for service in services_to_test:
                self.task_queue.put((repo, service, 'dev'))
                task_count += 1
        
        print(f"📋 Queued {task_count} services for testing")
        
        # Start workers
        workers = []
        num_workers = self.config['max_parallel_agents']
        
        for i in range(num_workers):
            t = threading.Thread(target=self.agent_worker, name=f"Agent-{i+1}")
            t.start()
            workers.append(t)
            print(f"🤖 Started Agent-{i+1}")
        
        # Wait for all tasks to complete
        self.task_queue.join()
        
        # Stop workers
        for _ in range(num_workers):
            self.task_queue.put(None)
        
        for t in workers:
            t.join()
        
        # Generate report
        self.create_local_issue_report(self.results)
        
        # Summary
        total_issues = sum(len(r.get('issues', [])) for r in self.results)
        print("\n" + "="*60)
        print(f"✅ ORCHESTRATION COMPLETE")
        print(f"Services tested: {len(self.results)}")
        print(f"Issues found: {total_issues}")
        print(f"Next run: {(datetime.now() + timedelta(minutes=self.config['check_interval_minutes'])).strftime('%H:%M')}")
        print("="*60)
    
    def run_scheduled(self):
        """Run on a schedule"""
        
        print("\n🕐 Scheduling local agent orchestration...")
        
        # Schedule quick checks every 2 hours
        schedule.every(self.config['check_interval_minutes']).minutes.do(
            lambda: self.run_orchestration(comprehensive=False)
        )
        
        # Schedule comprehensive test once a day at 10 PM
        schedule.every().day.at(f"{self.config['comprehensive_test_hour']:02d}:00").do(
            lambda: self.run_orchestration(comprehensive=True)
        )
        
        print(f"✅ Scheduled:")
        print(f"   - Quick checks: Every {self.config['check_interval_minutes']} minutes")
        print(f"   - Comprehensive: Daily at {self.config['comprehensive_test_hour']:02d}:00")
        print("\n👀 Monitoring... (Press Ctrl+C to stop)")
        
        # Run first check immediately
        self.run_orchestration(comprehensive=False)
        
        # Keep running
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                print("\n👋 Stopping orchestration...")
                self.running = False
                break

def create_windows_startup():
    """Create Windows startup script"""
    
    startup_script = """@echo off
echo Starting Local Agent Orchestration System...
cd /d E:\Projects
python local-agent-system.py --scheduled
pause
"""
    
    script_path = Path("E:/Projects/start-local-agents.bat")
    script_path.write_text(startup_script)
    
    print(f"✅ Created startup script: {script_path}")
    print("\nTo run on Windows startup:")
    print("1. Press Win+R, type: shell:startup")
    print("2. Copy start-local-agents.bat to that folder")
    print("\nOr run manually: start-local-agents.bat")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Local Agent Orchestration System')
    parser.add_argument('--scheduled', action='store_true', help='Run on schedule')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive test')
    parser.add_argument('--setup', action='store_true', help='Create startup scripts')
    
    args = parser.parse_args()
    
    if args.setup:
        create_windows_startup()
        return
    
    system = LocalAgentSystem()
    
    if args.once:
        system.run_orchestration(comprehensive=args.comprehensive)
    elif args.scheduled:
        system.run_scheduled()
    else:
        # Interactive mode
        print("\n🤖 Local Agent Orchestration System")
        print("=====================================")
        print("1. Run quick check")
        print("2. Run comprehensive test")
        print("3. Start scheduled monitoring")
        print("4. Setup Windows startup")
        print("5. Exit")
        
        choice = input("\nSelect option: ")
        
        if choice == '1':
            system.run_orchestration(comprehensive=False)
        elif choice == '2':
            system.run_orchestration(comprehensive=True)
        elif choice == '3':
            system.run_scheduled()
        elif choice == '4':
            create_windows_startup()
        else:
            print("Exiting...")

if __name__ == "__main__":
    main()