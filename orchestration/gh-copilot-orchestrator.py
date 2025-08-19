#!/usr/bin/env python3
"""
GitHub Copilot Orchestrator - Run gh copilot for each service from Projects folder
Focuses on testing and remediation with easy follow-up commands
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sys

class GHCopilotOrchestrator:
    def __init__(self):
        self.projects_dir = Path("E:/Projects")
        self.repos = {
            'NiroSubs-V2': [
                'ns-auth', 'ns-dashboard', 'ns-payments', 'ns-user', 'ns-shell'
            ],
            'VisualForgeMediaV2': [
                'vf-audio-service', 'vf-video-service', 'vf-image-service',
                'vf-text-service', 'vf-bulk-service', 'vf-dashboard-service'
            ]
        }
        self.current_session = {}
        
    def run_gh_command(self, command: str, working_dir: Path = None) -> str:
        """Execute a gh copilot command"""
        
        cwd = working_dir or self.projects_dir
        
        try:
            # Run from Projects folder
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(cwd),
                encoding='utf-8'
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {e}"
    
    def test_service(self, repo: str, service: str, environment: str = "dev") -> Dict[str, Any]:
        """Test a specific service using gh copilot"""
        
        # Build paths relative to Projects folder
        instruction_path = f"{repo}/{service}/AGENT_INSTRUCTIONS_{environment.upper()}.md"
        service_path = f"{repo}/{service}"
        
        print(f"\n{'='*60}")
        print(f"Testing: {service} ({environment})")
        print(f"Repo: {repo}")
        print(f"Instructions: {instruction_path}")
        print(f"{'='*60}")
        
        # Read the instruction file
        full_instruction_path = self.projects_dir / instruction_path
        if not full_instruction_path.exists():
            print(f"⚠️  Instruction file not found: {instruction_path}")
            return {"error": "Instruction file not found"}
        
        with open(full_instruction_path, 'r', encoding='utf-8') as f:
            instructions = f.read()
        
        # Create focused testing command
        test_prompt = f"""Based on the instructions in {instruction_path}, test and remediate the {service} service in {repo}. 
Focus only on this specific service in the {environment} environment.
Key areas: health checks, functional tests, security, performance, error handling.
Provide specific commands to test and fix issues."""
        
        # Store session info for follow-ups
        self.current_session[service] = {
            'repo': repo,
            'service': service,
            'environment': environment,
            'instruction_path': instruction_path,
            'service_path': service_path
        }
        
        # Build gh copilot suggest command
        cmd = f'gh copilot suggest "{test_prompt}"'
        
        print("🤖 Asking GitHub Copilot for testing suggestions...")
        result = self.run_gh_command(cmd)
        
        # Parse and display result
        print("\n📋 Copilot Response:")
        print(result)
        
        # Save result
        output = {
            'service': service,
            'repo': repo,
            'environment': environment,
            'timestamp': datetime.now().isoformat(),
            'instruction_path': instruction_path,
            'copilot_response': result,
            'status': 'completed'
        }
        
        # Save to file for later reference
        result_file = self.projects_dir / f"gh_copilot_results/{service}_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        result_file.parent.mkdir(exist_ok=True)
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Results saved to: {result_file}")
        
        return output
    
    def follow_up(self, service: str, command: str) -> str:
        """Send follow-up command for a specific service"""
        
        if service not in self.current_session:
            print(f"❌ No session found for {service}. Run test_service first.")
            return ""
        
        session = self.current_session[service]
        
        # Add context to follow-up
        follow_up_prompt = f"""For {service} in {session['repo']}/{session['service_path']}: {command}
Keep focus on the {session['environment']} environment."""
        
        cmd = f'gh copilot suggest "{follow_up_prompt}"'
        
        print(f"\n🔄 Follow-up for {service}: {command}")
        result = self.run_gh_command(cmd)
        print(result)
        
        return result
    
    def explain_command(self, command: str, service: str = None) -> str:
        """Explain a command, optionally in context of a service"""
        
        if service and service in self.current_session:
            session = self.current_session[service]
            print(f"\n📖 Explaining for {service} context:")
        else:
            print(f"\n📖 Explaining command:")
        
        cmd = f'gh copilot explain "{command}"'
        result = self.run_gh_command(cmd)
        print(result)
        
        return result
    
    def batch_test_services(self, environment: str = "dev", repos: List[str] = None):
        """Test multiple services in sequence"""
        
        repos_to_test = repos or list(self.repos.keys())
        results = []
        
        print(f"\n🚀 Starting batch testing for {environment} environment")
        print(f"Repos: {', '.join(repos_to_test)}")
        
        for repo in repos_to_test:
            if repo not in self.repos:
                print(f"⚠️  Unknown repo: {repo}")
                continue
                
            for service in self.repos[repo]:
                result = self.test_service(repo, service, environment)
                results.append(result)
                
                # Offer follow-up opportunity
                print(f"\n💬 Need follow-up for {service}? (Enter command or press Enter to continue)")
                follow_up_cmd = input("> ").strip()
                if follow_up_cmd:
                    self.follow_up(service, follow_up_cmd)
        
        # Generate summary report
        self.generate_report(results, environment)
        
        return results
    
    def generate_report(self, results: List[Dict], environment: str):
        """Generate testing report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'environment': environment,
            'total_services': len(results),
            'successful': sum(1 for r in results if 'error' not in r),
            'failed': sum(1 for r in results if 'error' in r),
            'services': results
        }
        
        report_file = self.projects_dir / f"gh_copilot_report_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Report Summary:")
        print(f"  Environment: {environment}")
        print(f"  Total Services: {report['total_services']}")
        print(f"  Successful: {report['successful']}")
        print(f"  Failed: {report['failed']}")
        print(f"  Report saved: {report_file}")
    
    def interactive_session(self):
        """Interactive testing session with easy follow-ups"""
        
        print("\n🎮 GitHub Copilot Interactive Testing Session")
        print("=" * 60)
        print("Commands:")
        print("  test <repo> <service> [env]  - Test a service")
        print("  follow <service> <command>   - Follow-up command")
        print("  explain <command>            - Explain a command")
        print("  batch <env> [repo]           - Batch test services")
        print("  list                         - List all services")
        print("  session                      - Show current sessions")
        print("  clear                        - Clear sessions")
        print("  exit                         - Exit")
        print("=" * 60)
        
        while True:
            try:
                cmd_input = input("\n> ").strip()
                
                if not cmd_input:
                    continue
                
                parts = cmd_input.split()
                command = parts[0].lower()
                
                if command == "exit":
                    print("👋 Goodbye!")
                    break
                
                elif command == "test":
                    if len(parts) < 3:
                        print("Usage: test <repo> <service> [env]")
                        continue
                    repo = parts[1]
                    service = parts[2]
                    env = parts[3] if len(parts) > 3 else "dev"
                    self.test_service(repo, service, env)
                
                elif command == "follow":
                    if len(parts) < 3:
                        print("Usage: follow <service> <command>")
                        continue
                    service = parts[1]
                    follow_cmd = ' '.join(parts[2:])
                    self.follow_up(service, follow_cmd)
                
                elif command == "explain":
                    if len(parts) < 2:
                        print("Usage: explain <command>")
                        continue
                    explain_cmd = ' '.join(parts[1:])
                    self.explain_command(explain_cmd)
                
                elif command == "batch":
                    if len(parts) < 2:
                        print("Usage: batch <env> [repo]")
                        continue
                    env = parts[1]
                    repos = [parts[2]] if len(parts) > 2 else None
                    self.batch_test_services(env, repos)
                
                elif command == "list":
                    print("\n📚 Available Services:")
                    for repo, services in self.repos.items():
                        print(f"\n{repo}:")
                        for service in services:
                            print(f"  - {service}")
                
                elif command == "session":
                    print("\n📁 Current Sessions:")
                    if not self.current_session:
                        print("  No active sessions")
                    else:
                        for service, info in self.current_session.items():
                            print(f"  {service}: {info['repo']} ({info['environment']})")
                
                elif command == "clear":
                    self.current_session.clear()
                    print("✅ Sessions cleared")
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"❌ Error: {e}")

def create_quick_test_scripts():
    """Create quick test scripts for common scenarios"""
    
    # PowerShell script
    ps1_script = '''# Quick GitHub Copilot Testing Script

param(
    [string]$Repo = "NiroSubs-V2",
    [string]$Service = "ns-auth",
    [string]$Environment = "dev"
)

Write-Host "🧪 Testing $Service in $Repo ($Environment)" -ForegroundColor Cyan

# Navigate to Projects folder
Set-Location "E:\Projects"

# Build instruction path
$instructionPath = "$Repo\$Service\AGENT_INSTRUCTIONS_$($Environment.ToUpper()).md"

# Test command
$testPrompt = "Test and remediate $Service in $Repo using instructions at $instructionPath. Focus on health checks, functional tests, security, and performance."

# Run gh copilot
Write-Host "🤖 Running GitHub Copilot..." -ForegroundColor Yellow
gh copilot suggest "$testPrompt"

# Offer follow-up
Write-Host "`n💬 Need a follow-up command? (Enter command or press Enter to skip)" -ForegroundColor Green
$followUp = Read-Host ">"
if ($followUp) {
    gh copilot suggest "For $Service in $Repo: $followUp"
}
'''
    
    # Bash script
    bash_script = '''#!/bin/bash
# Quick GitHub Copilot Testing Script

REPO=${1:-"NiroSubs-V2"}
SERVICE=${2:-"ns-auth"}
ENVIRONMENT=${3:-"dev"}

echo "🧪 Testing $SERVICE in $REPO ($ENVIRONMENT)"

# Navigate to Projects folder
cd /e/Projects || cd E:/Projects

# Build instruction path
INSTRUCTION_PATH="$REPO/$SERVICE/AGENT_INSTRUCTIONS_${ENVIRONMENT^^}.md"

# Test command
TEST_PROMPT="Test and remediate $SERVICE in $REPO using instructions at $INSTRUCTION_PATH. Focus on health checks, functional tests, security, and performance."

# Run gh copilot
echo "🤖 Running GitHub Copilot..."
gh copilot suggest "$TEST_PROMPT"

# Offer follow-up
echo ""
echo "💬 Need a follow-up command? (Enter command or press Enter to skip)"
read -p "> " FOLLOW_UP
if [ ! -z "$FOLLOW_UP" ]; then
    gh copilot suggest "For $SERVICE in $REPO: $FOLLOW_UP"
fi
'''
    
    with open('E:/Projects/gh-test-service.ps1', 'w', encoding='utf-8') as f:
        f.write(ps1_script)
    
    with open('E:/Projects/gh-test-service.sh', 'w', encoding='utf-8') as f:
        f.write(bash_script)
    
    print("Created: gh-test-service.ps1 and gh-test-service.sh")

def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Copilot Testing Orchestrator')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Start interactive session')
    parser.add_argument('--test', nargs=3, metavar=('REPO', 'SERVICE', 'ENV'),
                       help='Test a specific service')
    parser.add_argument('--batch', metavar='ENV', 
                       help='Batch test all services in environment')
    parser.add_argument('--create-scripts', action='store_true',
                       help='Create quick test scripts')
    
    args = parser.parse_args()
    
    orchestrator = GHCopilotOrchestrator()
    
    if args.create_scripts:
        create_quick_test_scripts()
        return
    
    if args.interactive:
        orchestrator.interactive_session()
    elif args.test:
        repo, service, env = args.test
        orchestrator.test_service(repo, service, env)
    elif args.batch:
        orchestrator.batch_test_services(args.batch)
    else:
        # Default: interactive mode
        orchestrator.interactive_session()

if __name__ == "__main__":
    main()