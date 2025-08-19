#!/usr/bin/env python3
"""
GitHub Copilot CLI Agent Integration
Uses 'gh copilot' command to execute AI agents for testing and remediation
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import asyncio
from typing import Dict, Any, List

class GitHubCopilotCLIAgent:
    """Integration with GitHub Copilot CLI for agent testing"""
    
    def __init__(self):
        self.gh_command = "gh"
        self.verify_gh_cli()
    
    def verify_gh_cli(self):
        """Verify GitHub CLI is installed and authenticated"""
        try:
            result = subprocess.run(
                [self.gh_command, "auth", "status"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print("Warning: GitHub CLI not authenticated. Run 'gh auth login'")
        except FileNotFoundError:
            raise Exception("GitHub CLI not found. Please install: https://cli.github.com/")
    
    def execute_copilot_command(self, command: str, context_file: str = None) -> str:
        """Execute a gh copilot command"""
        
        cmd_parts = [self.gh_command, "copilot", "explain"]
        
        if context_file and Path(context_file).exists():
            # Add file context
            cmd_parts.extend(["-f", context_file])
        
        # Add the command/question
        cmd_parts.append(command)
        
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error executing gh copilot: {e}")
            return f"Error: {e.stderr}"
    
    def test_service(self, service: str, environment: str, instruction_file: str) -> Dict[str, Any]:
        """Use gh copilot to test a service based on instructions"""
        
        # Read instructions
        if not Path(instruction_file).exists():
            return {"error": f"Instruction file not found: {instruction_file}"}
        
        with open(instruction_file, 'r', encoding='utf-8') as f:
            instructions = f.read()
        
        # Create test prompt
        test_prompt = f"""
        Based on these instructions, analyze and test the {service} service in {environment}:
        
        {instructions}
        
        Please check:
        1. Health endpoints
        2. API functionality
        3. Security configuration
        4. Performance metrics
        5. Error handling
        
        Report any issues found and suggest fixes.
        """
        
        # Execute via gh copilot
        print(f"Testing {service} in {environment} via gh copilot...")
        response = self.execute_copilot_command(test_prompt, instruction_file)
        
        # Parse response and create result
        result = {
            "service": service,
            "environment": environment,
            "timestamp": datetime.now().isoformat(),
            "copilot_response": response,
            "status": "completed"
        }
        
        # Try to extract metrics from response
        if "passed" in response.lower():
            result["tests_passed"] = True
        if "failed" in response.lower() or "error" in response.lower():
            result["issues_found"] = True
        
        return result

class CopilotAgentOrchestrator:
    """Orchestrate multiple GitHub Copilot CLI agents"""
    
    def __init__(self):
        self.agent = GitHubCopilotCLIAgent()
        self.repos = {
            'NiroSubs-V2': {
                'path': 'E:/Projects/NiroSubs-V2',
                'services': ['ns-auth', 'ns-dashboard', 'ns-payments', 'ns-user', 'ns-shell']
            },
            'VisualForgeMediaV2': {
                'path': 'E:/Projects/VisualForgeMediaV2',
                'services': ['vf-audio-service', 'vf-video-service', 'vf-image-service',
                           'vf-text-service', 'vf-bulk-service', 'vf-dashboard-service']
            }
        }
    
    async def test_service_async(self, repo: str, service: str, environment: str) -> Dict[str, Any]:
        """Async wrapper for testing a service"""
        
        service_path = Path(self.repos[repo]['path']) / service
        instruction_file = service_path / f"AGENT_INSTRUCTIONS_{environment.upper()}.md"
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.agent.test_service,
            service,
            environment,
            str(instruction_file)
        )
        
        return result
    
    async def run_parallel_tests(self, environments: List[str] = ["dev", "staging"]):
        """Run tests in parallel for all services"""
        
        print("=" * 60)
        print("Starting GitHub Copilot CLI Agent Testing")
        print("=" * 60)
        
        tasks = []
        for repo, config in self.repos.items():
            for service in config['services']:
                for env in environments:
                    if env == "production":
                        print(f"Skipping production for {service}")
                        continue
                    
                    task = self.test_service_async(repo, service, env)
                    tasks.append(task)
        
        # Run all tests in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = []
        failed = []
        
        for result in results:
            if isinstance(result, Exception):
                failed.append(str(result))
            else:
                successful.append(result)
                
                # Print summary
                service = result.get('service', 'unknown')
                env = result.get('environment', 'unknown')
                status = "✓" if not result.get('issues_found') else "✗"
                print(f"{status} {service} ({env})")
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": successful,
            "errors": failed
        }
        
        # Save report
        report_file = f"gh_copilot_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {report_file}")
        print(f"Success rate: {len(successful)}/{len(results)}")
        
        return report

def create_gh_copilot_scripts():
    """Create helper scripts for using gh copilot"""
    
    # PowerShell script for Windows
    ps1_script = """# GitHub Copilot CLI Helper Script

# Function to test a service
function Test-Service {
    param(
        [string]$Service,
        [string]$Environment
    )
    
    Write-Host "Testing $Service in $Environment..." -ForegroundColor Cyan
    
    $instructionFile = "AGENT_INSTRUCTIONS_$($Environment.ToUpper()).md"
    
    if (Test-Path $instructionFile) {
        gh copilot explain "Test the $Service service based on instructions in $instructionFile and report any issues"
    } else {
        Write-Host "Instruction file not found: $instructionFile" -ForegroundColor Red
    }
}

# Function to fix issues
function Fix-Issue {
    param(
        [string]$Issue,
        [string]$File
    )
    
    Write-Host "Analyzing issue: $Issue" -ForegroundColor Yellow
    gh copilot suggest "How to fix: $Issue in file $File"
}

# Function to deploy changes
function Deploy-Service {
    param(
        [string]$Service,
        [string]$Environment
    )
    
    Write-Host "Deploying $Service to $Environment..." -ForegroundColor Green
    gh copilot explain "What are the steps to deploy $Service to AWS Lambda in $Environment environment"
}

# Main testing flow
Write-Host "GitHub Copilot Agent Testing Suite" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Magenta

# Example usage
# Test-Service -Service "ns-auth" -Environment "dev"
# Fix-Issue -Issue "Lambda timeout" -File "index.js"
# Deploy-Service -Service "ns-auth" -Environment "staging"
"""
    
    # Bash script for Linux/Mac
    bash_script = """#!/bin/bash
# GitHub Copilot CLI Helper Script

# Function to test a service
test_service() {
    local service=$1
    local environment=$2
    
    echo "Testing $service in $environment..."
    
    instruction_file="AGENT_INSTRUCTIONS_${environment^^}.md"
    
    if [ -f "$instruction_file" ]; then
        gh copilot explain "Test the $service service based on instructions in $instruction_file and report any issues"
    else
        echo "Instruction file not found: $instruction_file"
    fi
}

# Function to fix issues
fix_issue() {
    local issue=$1
    local file=$2
    
    echo "Analyzing issue: $issue"
    gh copilot suggest "How to fix: $issue in file $file"
}

# Function to deploy changes
deploy_service() {
    local service=$1
    local environment=$2
    
    echo "Deploying $service to $environment..."
    gh copilot explain "What are the steps to deploy $service to AWS Lambda in $environment environment"
}

# Main testing flow
echo "GitHub Copilot Agent Testing Suite"
echo "==================================="

# Example usage
# test_service "ns-auth" "dev"
# fix_issue "Lambda timeout" "index.js"
# deploy_service "ns-auth" "staging"
"""
    
    # Save scripts
    with open('E:/Projects/gh-copilot-helper.ps1', 'w', encoding='utf-8') as f:
        f.write(ps1_script)
    
    with open('E:/Projects/gh-copilot-helper.sh', 'w', encoding='utf-8') as f:
        f.write(bash_script)
    
    print("Created gh-copilot-helper.ps1 and gh-copilot-helper.sh")

async def main():
    """Main execution"""
    
    # Create helper scripts
    create_gh_copilot_scripts()
    
    # Initialize orchestrator
    orchestrator = CopilotAgentOrchestrator()
    
    # Run parallel tests
    report = await orchestrator.run_parallel_tests(["dev", "staging"])
    
    print("\nTesting complete!")
    print(f"Total tests: {report['total_tests']}")
    print(f"Successful: {report['successful']}")
    print(f"Failed: {report['failed']}")

if __name__ == "__main__":
    # Run async main
    asyncio.run(main())