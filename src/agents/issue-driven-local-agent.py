#!/usr/bin/env python3
"""
Issue-Driven Local Agent System
Reads instructions from GitHub Issues, executes locally, reports back
Zero cloud costs - all execution on your machine
"""

import subprocess
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class IssueDrivenAgent:
    def __init__(self):
        self.base_dir = Path("E:/Projects")
        self.repos = ["NiroSubs-V2", "VisualForgeMediaV2", "Projects"]
        
    def get_open_issues(self, repo: str, label: str = "agent-task") -> List[Dict]:
        """Get open issues from GitHub with specific label"""
        
        print(f"\n📋 Checking issues in {repo}...")
        
        cmd = f'gh issue list --repo stevesurles/{repo} --label {label} --state open --json number,title,body,labels'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(self.base_dir)
            )
            
            if result.returncode == 0 and result.stdout:
                issues = json.loads(result.stdout)
                print(f"   Found {len(issues)} open agent tasks")
                return issues
            
        except Exception as e:
            print(f"   Error getting issues: {e}")
        
        return []
    
    def parse_issue_instructions(self, issue: Dict) -> Dict[str, Any]:
        """Parse issue body to extract instructions"""
        
        body = issue.get('body', '')
        
        instructions = {
            'issue_number': issue['number'],
            'title': issue['title'],
            'service': None,
            'environment': 'dev',
            'tasks': [],
            'sdlc_phase': None,
            'auto_fix': False
        }
        
        # Extract service name
        service_match = re.search(r'Service:\s*(\S+)', body, re.IGNORECASE)
        if service_match:
            instructions['service'] = service_match.group(1)
        
        # Extract environment
        env_match = re.search(r'Environment:\s*(\S+)', body, re.IGNORECASE)
        if env_match:
            instructions['environment'] = env_match.group(1)
        
        # Extract SDLC phase
        phase_match = re.search(r'Phase:\s*(plan|develop|test|deploy|monitor)', body, re.IGNORECASE)
        if phase_match:
            instructions['sdlc_phase'] = phase_match.group(1)
        
        # Extract tasks (bullet points)
        tasks = re.findall(r'[-*]\s+(.+)', body)
        instructions['tasks'] = tasks
        
        # Check for auto-fix flag
        if 'auto-fix' in body.lower() or 'auto-remediate' in body.lower():
            instructions['auto_fix'] = True
        
        return instructions
    
    def execute_sdlc_phase(self, phase: str, service: str, repo: str) -> Dict[str, Any]:
        """Execute SDLC phase for a service"""
        
        print(f"\n🔄 Executing {phase} phase for {service}...")
        
        results = {
            'phase': phase,
            'service': service,
            'repo': repo,
            'timestamp': datetime.now().isoformat(),
            'actions': [],
            'issues_found': [],
            'fixes_applied': []
        }
        
        service_path = self.base_dir / repo / service
        
        if phase == "plan":
            # Planning phase - analyze requirements
            prompts = [
                f"What tests should be written for {service}",
                f"What dependencies does {service} need",
                f"Security considerations for {service}"
            ]
            
        elif phase == "develop":
            # Development phase - code analysis
            prompts = [
                f"Code improvements for {service}",
                f"Refactoring suggestions for {service}",
                f"Best practices check for {service}"
            ]
            
        elif phase == "test":
            # Testing phase - run tests
            prompts = [
                f"Unit test commands for {service}",
                f"Integration test strategy for {service}",
                f"Performance test approach for {service}"
            ]
            
            # Actually run tests if available
            if service_path.exists():
                self.run_local_tests(service_path, results)
            
        elif phase == "deploy":
            # Deployment phase - prepare deployment
            prompts = [
                f"Deployment checklist for {service}",
                f"AWS Lambda deployment command for {service}",
                f"CloudFormation validation for {service}"
            ]
            
        elif phase == "monitor":
            # Monitoring phase - check health
            prompts = [
                f"Health check commands for {service}",
                f"Log analysis for {service}",
                f"Performance metrics to track for {service}"
            ]
        else:
            prompts = [f"General analysis for {service}"]
        
        # Use GitHub Copilot for analysis
        for prompt in prompts:
            try:
                suggestion = self.get_copilot_suggestion(prompt, service_path)
                if suggestion:
                    results['actions'].append({
                        'prompt': prompt,
                        'suggestion': suggestion[:500]
                    })
            except Exception as e:
                results['issues_found'].append(f"Error with {prompt}: {str(e)}")
        
        return results
    
    def get_copilot_suggestion(self, prompt: str, working_dir: Path) -> str:
        """Get suggestion from GitHub Copilot"""
        
        cmd = f'echo "1" | gh copilot suggest "{prompt}"'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(working_dir) if working_dir.exists() else str(self.base_dir),
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
                
        except subprocess.TimeoutExpired:
            return "Timeout getting suggestion"
        except Exception as e:
            return f"Error: {str(e)}"
        
        return ""
    
    def run_local_tests(self, service_path: Path, results: Dict):
        """Run actual tests locally"""
        
        # Check for package.json
        package_json = service_path / "package.json"
        if package_json.exists():
            # Try to run npm test
            try:
                test_result = subprocess.run(
                    "npm test",
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(service_path),
                    timeout=60
                )
                
                if test_result.returncode == 0:
                    results['actions'].append({
                        'action': 'npm test',
                        'status': 'passed',
                        'output': test_result.stdout[:500]
                    })
                else:
                    results['issues_found'].append('Tests failed')
                    results['actions'].append({
                        'action': 'npm test',
                        'status': 'failed',
                        'output': test_result.stderr[:500]
                    })
                    
            except subprocess.TimeoutExpired:
                results['issues_found'].append('Tests timed out')
            except Exception as e:
                results['issues_found'].append(f'Test error: {str(e)}')
    
    def update_issue_with_results(self, repo: str, issue_number: int, results: Dict):
        """Post results back to GitHub issue"""
        
        print(f"\n📝 Updating issue #{issue_number} with results...")
        
        # Format results as markdown
        comment = f"""## 🤖 Local Agent Execution Report

**Executed locally at**: {results['timestamp']}
**Phase**: {results.get('phase', 'N/A')}
**Service**: {results.get('service', 'N/A')}

### Actions Taken
"""
        
        for action in results.get('actions', []):
            if isinstance(action, dict):
                if 'prompt' in action:
                    comment += f"\n**{action['prompt']}**\n"
                    comment += f"```\n{action.get('suggestion', 'N/A')[:300]}...\n```\n"
                elif 'action' in action:
                    comment += f"\n**{action['action']}**: {action.get('status', 'N/A')}\n"
                    if 'output' in action:
                        comment += f"```\n{action['output'][:300]}...\n```\n"
        
        if results.get('issues_found'):
            comment += "\n### ⚠️ Issues Found\n"
            for issue in results['issues_found']:
                comment += f"- {issue}\n"
        
        if results.get('fixes_applied'):
            comment += "\n### ✅ Fixes Applied\n"
            for fix in results['fixes_applied']:
                comment += f"- {fix}\n"
        
        comment += "\n---\n*Executed locally by Issue-Driven Agent*"
        
        # Post comment to issue
        cmd = f'gh issue comment {issue_number} --repo stevesurles/{repo} --body "{comment}"'
        
        try:
            # Use file to avoid shell escaping issues
            comment_file = self.base_dir / "temp_comment.md"
            comment_file.write_text(comment)
            
            cmd = f'gh issue comment {issue_number} --repo stevesurles/{repo} --body-file "{comment_file}"'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Updated issue #{issue_number}")
            else:
                print(f"   ❌ Failed to update issue: {result.stderr}")
            
            # Clean up temp file
            comment_file.unlink(missing_ok=True)
            
        except Exception as e:
            print(f"   ❌ Error updating issue: {e}")
    
    def process_all_issues(self):
        """Process all open agent tasks across all repos"""
        
        print("\n" + "="*60)
        print("🚀 ISSUE-DRIVEN LOCAL AGENT")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        total_processed = 0
        
        for repo in self.repos:
            issues = self.get_open_issues(repo)
            
            for issue in issues:
                instructions = self.parse_issue_instructions(issue)
                
                print(f"\n📌 Processing: {issue['title']}")
                print(f"   Issue #{issue['number']} in {repo}")
                
                # Determine which repo contains the service
                service = instructions.get('service')
                if service:
                    if service.startswith('ns-'):
                        service_repo = 'NiroSubs-V2'
                    elif service.startswith('vf-'):
                        service_repo = 'VisualForgeMediaV2'
                    else:
                        service_repo = repo
                    
                    # Execute based on SDLC phase or tasks
                    if instructions['sdlc_phase']:
                        results = self.execute_sdlc_phase(
                            instructions['sdlc_phase'],
                            service,
                            service_repo
                        )
                    else:
                        # Execute general tasks
                        results = {
                            'service': service,
                            'timestamp': datetime.now().isoformat(),
                            'actions': [],
                            'issues_found': []
                        }
                        
                        for task in instructions['tasks']:
                            suggestion = self.get_copilot_suggestion(
                                task,
                                self.base_dir / service_repo / service
                            )
                            results['actions'].append({
                                'prompt': task,
                                'suggestion': suggestion
                            })
                    
                    # Update issue with results
                    self.update_issue_with_results(repo, issue['number'], results)
                    total_processed += 1
                    
                    # Rate limiting
                    time.sleep(5)
        
        print("\n" + "="*60)
        print(f"✅ PROCESSING COMPLETE")
        print(f"Issues processed: {total_processed}")
        print("="*60)
    
    def monitor_issues(self, interval_minutes: int = 30):
        """Monitor for new issues continuously"""
        
        print(f"\n👀 Monitoring GitHub issues every {interval_minutes} minutes...")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                self.process_all_issues()
                
                print(f"\n💤 Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n👋 Stopping monitor...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print(f"Retrying in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)

def create_master_issue_template():
    """Create a master issue that explains the SDLC process"""
    
    template = """# Agent SDLC Instructions

## How to Use This System

Create issues with the label `agent-task` and the local agent will:
1. Read the issue
2. Execute tests/tasks locally
3. Post results back as comments
4. All execution happens on your local machine (zero cloud costs)

## Issue Format

```markdown
Service: ns-auth
Environment: dev
Phase: test

Tasks:
- Run unit tests
- Check code coverage
- Validate security
- Performance benchmark
```

## SDLC Phases

### Phase: plan
- Analyze requirements
- Check dependencies
- Security review

### Phase: develop
- Code improvements
- Refactoring suggestions
- Best practices

### Phase: test
- Run unit tests
- Integration tests
- Performance tests

### Phase: deploy
- Deployment checklist
- AWS commands
- CloudFormation validation

### Phase: monitor
- Health checks
- Log analysis
- Performance metrics

## Examples

### Example 1: Test a Service
```
Title: Test ns-auth service
Labels: agent-task

Service: ns-auth
Phase: test
Environment: dev

- Run all unit tests
- Check test coverage
- Validate API endpoints
```

### Example 2: Full SDLC
```
Title: Complete SDLC for vf-audio-service
Labels: agent-task

Service: vf-audio-service
Phase: plan

Auto-fix: yes

- Review architecture
- Plan improvements
- Then move to develop phase
- Then test
- Then deploy checklist
```

## Automation

The local agent runs every 30 minutes and:
1. Checks for open `agent-task` issues
2. Executes instructions locally
3. Posts results as comments
4. No cloud costs!
"""
    
    # Save template
    template_file = Path("E:/Projects/AGENT_SDLC_TEMPLATE.md")
    template_file.write_text(template)
    
    print(f"✅ Created template: {template_file}")
    
    # Create the issue
    cmd = f'''gh issue create --repo stevesurles/Projects --title "📚 Agent SDLC Instructions (Pin This)" --body-file "{template_file}" --label documentation,pinned'''
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created master instruction issue: {result.stdout}")
    except Exception as e:
        print(f"Error creating issue: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Issue-Driven Local Agent')
    parser.add_argument('--monitor', action='store_true', help='Monitor continuously')
    parser.add_argument('--once', action='store_true', help='Run once')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in minutes')
    parser.add_argument('--create-template', action='store_true', help='Create instruction template')
    
    args = parser.parse_args()
    
    if args.create_template:
        create_master_issue_template()
        return
    
    agent = IssueDrivenAgent()
    
    if args.monitor:
        agent.monitor_issues(args.interval)
    elif args.once:
        agent.process_all_issues()
    else:
        print("\n🤖 Issue-Driven Local Agent")
        print("===========================")
        print("1. Process all issues once")
        print("2. Monitor continuously")
        print("3. Create instruction template")
        print("4. Exit")
        
        choice = input("\nSelect: ")
        
        if choice == '1':
            agent.process_all_issues()
        elif choice == '2':
            agent.monitor_issues()
        elif choice == '3':
            create_master_issue_template()

if __name__ == "__main__":
    main()