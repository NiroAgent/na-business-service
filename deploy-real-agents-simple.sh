#!/bin/bash

echo "Deploying Real AI Agents to EC2 (Simple Method)..."

INSTANCE_ID="i-0af59b7036f7b0b77"

# Stop existing agents
echo "Stopping existing agents..."
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["pkill -f python3.*agent"]' \
    --output text

sleep 5

# Create enhanced QA agent with real test execution
echo "Creating enhanced QA agent..."
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
"cat > /opt/ai-agents/scripts/ai-qa-agent-enhanced.py << '\''EOF'\''
#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path

class RealAIQAAgent:
    def __init__(self):
        self.name = \"Real-AI-QA-Agent\"
        self.services = [
            \"vf-dashboard-service\",
            \"vf-audio-service\",
            \"vf-video-service\"
        ]
        self.github_token = os.getenv(\"GITHUB_TOKEN\", \"\")
        print(f\"[{self.name}] Initialized - Ready to run REAL Playwright tests\")
        
    def find_test_files(self, service):
        \"\"\"Find actual test files in the service\"\"\"
        test_dirs = [
            f\"/opt/{service}/mfe/tests\",
            f\"/home/agent/{service}/mfe/tests\",
            f\"/var/www/{service}/mfe/tests\"
        ]
        
        test_files = []
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                path = Path(test_dir)
                test_files.extend(path.glob(\"**/*.test.ts\"))
                test_files.extend(path.glob(\"**/*.spec.ts\"))
                test_files.extend(path.glob(\"**/*.test.js\"))
                test_files.extend(path.glob(\"**/*.spec.js\"))
                
        return test_files
        
    def run_real_tests(self, service):
        \"\"\"Run actual Playwright tests\"\"\"
        print(f\"[{self.name}] Finding test files for {service}...\")
        test_files = self.find_test_files(service)
        
        if not test_files:
            print(f\"[{self.name}] No test files found for {service}, checking npm scripts...\")
            # Try running via npm/yarn scripts
            service_dir = f\"/opt/{service}\"
            if os.path.exists(f\"{service_dir}/package.json\"):
                os.chdir(service_dir)
                print(f\"[{self.name}] Running: npm test\")
                result = subprocess.run([\"npm\", \"test\"], capture_output=True, text=True)
                if result.returncode != 0:
                    self.create_github_issue(service, result.stderr)
                    return False
            return True
            
        # Run each test file
        failures = []
        for test_file in test_files:
            print(f\"[{self.name}] Running test: {test_file}\")
            result = subprocess.run(
                [\"npx\", \"playwright\", \"test\", str(test_file)],
                capture_output=True,
                text=True,
                cwd=test_file.parent
            )
            
            if result.returncode != 0:
                failures.append({
                    \"file\": str(test_file),
                    \"error\": result.stderr
                })
                
        if failures:
            self.create_github_issue(service, failures)
            return False
            
        print(f\"[{self.name}] All tests passed for {service}!\")
        return True
        
    def create_github_issue(self, service, errors):
        \"\"\"Create a real GitHub issue for test failures\"\"\"
        print(f\"[{self.name}] Creating GitHub issue for {service} failures\")
        
        if not self.github_token:
            print(f\"[{self.name}] No GitHub token, logging error locally\")
            with open(f\"/opt/ai-agents/logs/{service}-failures.json\", \"w\") as f:
                json.dump({
                    \"service\": service,
                    \"timestamp\": datetime.now().isoformat(),
                    \"errors\": errors
                }, f, indent=2)
            return
            
        # Would implement GitHub API call here
        import requests
        url = \"https://api.github.com/repos/VisualForgeMediaV2/vf_agent_service/issues\"
        headers = {
            \"Authorization\": f\"token {self.github_token}\",
            \"Accept\": \"application/vnd.github.v3+json\"
        }
        
        issue_data = {
            \"title\": f\"Test Failures in {service}\",
            \"body\": f\"Test failures detected:\\n\\n{json.dumps(errors, indent=2)}\",
            \"labels\": [\"bug\", \"test-failure\", service]
        }
        
        try:
            response = requests.post(url, headers=headers, json=issue_data)
            if response.status_code == 201:
                print(f\"[{self.name}] Issue created: {response.json()['\''html_url'\'']}\")
        except Exception as e:
            print(f\"[{self.name}] Failed to create issue: {e}\")
        
    def monitor(self):
        \"\"\"Main monitoring loop\"\"\"
        print(f\"[{self.name}] Starting real test monitoring...\")
        while True:
            for service in self.services:
                try:
                    print(f\"[{self.name}] Testing {service}...\")
                    self.run_real_tests(service)
                except Exception as e:
                    print(f\"[{self.name}] Error testing {service}: {e}\")
                    
            print(f\"[{self.name}] Waiting 600 seconds before next test cycle...\")
            time.sleep(600)  # 10 minutes

if __name__ == \"__main__\":
    agent = RealAIQAAgent()
    agent.monitor()
EOF",
"chmod +x /opt/ai-agents/scripts/ai-qa-agent-enhanced.py"
]' --output text

sleep 5

# Install required packages
echo "Installing dependencies..."
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "pip3 install requests",
        "cd /opt && npm install -g playwright@latest",
        "npx playwright install chromium"
    ]' \
    --output text

sleep 10

# Start the enhanced agent
echo "Starting enhanced agents..."
START_CMD=$(aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "cd /opt/ai-agents/scripts",
        "nohup python3 ai-qa-agent-enhanced.py > /opt/ai-agents/logs/qa-enhanced.log 2>&1 &",
        "sleep 2",
        "ps aux | grep ai-qa-agent-enhanced"
    ]' \
    --query 'Command.CommandId' \
    --output text)

sleep 10

echo "Checking deployment status..."
aws ssm get-command-invocation \
    --command-id $START_CMD \
    --instance-id $INSTANCE_ID \
    --query 'StandardOutputContent' \
    --output text

echo "Enhanced real agent deployed!"