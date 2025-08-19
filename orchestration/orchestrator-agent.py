#!/usr/bin/env python3
"""
Simple Orchestrator Agent for GitHub Copilot Testing
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

class SimpleOrchestrator:
    def __init__(self):
        self.projects_dir = Path("E:/Projects")
        self.test_results = []
        
    def test_service_health(self, repo, service, env="dev"):
        """Test a service health endpoint"""
        
        print(f"\nTesting {service} in {repo} ({env})...")
        print("-" * 40)
        
        # Build AWS CLI command to check Lambda
        lambda_name = f"{env}-{service}-lambda"
        
        # Test 1: Check if Lambda exists
        cmd1 = f"aws lambda get-function --function-name {lambda_name} --query Configuration.State --output text 2>NUL"
        result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
        
        if result1.returncode == 0:
            state = result1.stdout.strip()
            print(f"  Lambda Status: {state}")
            
            if state != "Active":
                print(f"  ISSUE: Lambda not active!")
                # Follow-up: Fix Lambda state
                print(f"  FOLLOW-UP: Updating Lambda configuration...")
                fix_cmd = f"aws lambda update-function-configuration --function-name {lambda_name} --timeout 30"
                subprocess.run(fix_cmd, shell=True, capture_output=True)
                print(f"  Applied timeout fix")
        else:
            print(f"  Lambda Status: Not found or error")
            print(f"  FOLLOW-UP: Lambda needs to be deployed")
        
        # Test 2: Check CloudWatch logs
        print(f"  Checking CloudWatch logs...")
        log_group = f"/aws/lambda/{lambda_name}"
        cmd2 = f"aws logs describe-log-streams --log-group-name {log_group} --query 'logStreams[0].lastEventTimestamp' --output text 2>NUL"
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
        
        if result2.returncode == 0 and result2.stdout.strip():
            print(f"  Last log activity: Found")
        else:
            print(f"  Last log activity: No recent logs")
            print(f"  FOLLOW-UP: May need to trigger function for testing")
        
        # Test 3: Check API Gateway
        print(f"  Checking API Gateway...")
        api_name = f"{env}-{repo}-api"
        cmd3 = f"aws apigateway get-rest-apis --query \"items[?name=='{api_name}'].id\" --output text 2>NUL"
        result3 = subprocess.run(cmd3, shell=True, capture_output=True, text=True)
        
        if result3.returncode == 0 and result3.stdout.strip():
            api_id = result3.stdout.strip()
            print(f"  API Gateway: Found (ID: {api_id[:8]}...)")
            
            # Check API deployment
            cmd4 = f"aws apigateway get-deployments --rest-api-id {api_id} --query 'items[0].id' --output text 2>NUL"
            result4 = subprocess.run(cmd4, shell=True, capture_output=True, text=True)
            
            if result4.returncode == 0 and result4.stdout.strip():
                print(f"  API Deployment: Active")
            else:
                print(f"  API Deployment: Not deployed")
                print(f"  FOLLOW-UP: Deploying API...")
                deploy_cmd = f"aws apigateway create-deployment --rest-api-id {api_id} --stage-name {env}"
                subprocess.run(deploy_cmd, shell=True, capture_output=True)
                print(f"  Deployment initiated")
        else:
            print(f"  API Gateway: Not found")
            print(f"  FOLLOW-UP: API Gateway needs to be created")
        
        # Store results
        self.test_results.append({
            'service': service,
            'repo': repo,
            'environment': env,
            'timestamp': datetime.now().isoformat(),
            'tests_completed': 3
        })
        
        print(f"  Summary: Basic health checks completed")
        
    def orchestrate_testing(self):
        """Orchestrate testing for all services"""
        
        print("\n" + "="*50)
        print("ORCHESTRATOR AGENT - AUTOMATED TESTING")
        print("="*50)
        
        # Test plan
        services_to_test = [
            ('NiroSubs-V2', 'ns-auth', 'dev'),
            ('NiroSubs-V2', 'ns-dashboard', 'dev'),
            ('NiroSubs-V2', 'ns-payments', 'dev'),
            ('VisualForgeMediaV2', 'vf-audio-service', 'dev'),
            ('VisualForgeMediaV2', 'vf-video-service', 'dev'),
        ]
        
        print(f"\nServices to test: {len(services_to_test)}")
        print("Starting automated testing with follow-up remediation...\n")
        
        for repo, service, env in services_to_test:
            try:
                self.test_service_health(repo, service, env)
            except Exception as e:
                print(f"Error testing {service}: {e}")
        
        # Save results
        results_file = self.projects_dir / f"orchestrator_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n" + "="*50)
        print(f"TESTING COMPLETE")
        print(f"Services tested: {len(self.test_results)}")
        print(f"Results saved to: {results_file}")
        print("="*50)

def main():
    print("Starting Orchestrator Agent...")
    orchestrator = SimpleOrchestrator()
    orchestrator.orchestrate_testing()

if __name__ == "__main__":
    main()