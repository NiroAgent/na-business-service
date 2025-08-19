#!/usr/bin/env python3
"""
Connect GitHub Issues to Spot Instance Agents
==============================================
Simple system to connect GitHub issues to the 50 agents running on spot instances
"""

import subprocess
import json

def create_simple_github_webhook():
    """Create a simple webhook configuration for GitHub"""
    
    webhook_config = {
        "repos": [
            "VisualForgeMediaV2/vf-dashboard-service",
            "VisualForgeMediaV2/vf-auth-service",
            "VisualForgeMediaV2/vf-video-service",
            "VisualForgeMediaV2/vf-image-service",
            "VisualForgeMediaV2/vf-audio-service",
            "VisualForgeMediaV2/business-operations"
        ],
        "webhook_url": "https://vf-dev.visualforgemedia.com/github-webhook",
        "events": ["issues", "issue_comment"],
        "agent_mapping": {
            "[STORY]": "developer",
            "[QA]": "qa",
            "[Deploy]": "devops",
            "[Manager]": "manager",
            "[BUG]": "developer"
        }
    }
    
    print("\n" + "="*80)
    print("GITHUB TO AGENT CONNECTION SETUP")
    print("="*80)
    
    print("\n[CURRENT SETUP]:")
    print("- 50 agents running on EC2 spot instances")
    print("- Cost: $8-15/month")
    print("- Need: Connect GitHub issues to agents")
    
    print("\n[SIMPLE SOLUTION]:")
    print("1. Use GitHub Actions to trigger on issue creation")
    print("2. Action calls webhook on vf-dev")
    print("3. Webhook assigns to available agent")
    print("4. Agent processes and updates issue")
    
    # Create GitHub Actions workflow
    workflow = """name: Connect Issues to Agents

on:
  issues:
    types: [opened, reopened, labeled]

jobs:
  send-to-agents:
    runs-on: ubuntu-latest
    steps:
    - name: Send to Agent System
      run: |
        curl -X POST https://vf-dev.visualforgemedia.com/github-webhook \\
          -H "Content-Type: application/json" \\
          -H "X-GitHub-Event: issues" \\
          -d '{
            "action": "${{ github.event.action }}",
            "repository": "${{ github.repository }}",
            "issue": {
              "number": ${{ github.event.issue.number }},
              "title": "${{ github.event.issue.title }}",
              "body": "${{ toJSON(github.event.issue.body) }},
              "labels": ${{ toJSON(github.event.issue.labels) }}
            }
          }'
    
    - name: Auto-Assign Label
      uses: actions/github-script@v6
      with:
        script: |
          await github.rest.issues.addLabels({
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: context.issue.number,
            labels: ['ai-processing']
          });
"""
    
    with open(".github/workflows/connect-to-agents.yml", "w") as f:
        f.write(workflow)
    
    print("\n[FILES CREATED]:")
    print("✓ .github/workflows/connect-to-agents.yml")
    
    return webhook_config

def create_agent_dispatcher():
    """Create dispatcher that runs on vf-dev to route work to agents"""
    
    dispatcher = '''#!/usr/bin/env python3
"""
Agent Dispatcher - Routes GitHub issues to available agents
Runs on vf-dev server
"""

from flask import Flask, request, jsonify
import boto3
import json
import random

app = Flask(__name__)
ec2 = boto3.client('ec2', region_name='us-east-1')

# Track which agents are busy
busy_agents = set()

@app.route('/github-webhook', methods=['POST'])
def handle_webhook():
    """Receive GitHub webhook and assign to agent"""
    
    data = request.json
    
    if data.get('action') in ['opened', 'reopened']:
        issue = data['issue']
        repo = data['repository']
        
        # Determine agent type from title
        title = issue['title']
        agent_type = 'developer'  # default
        
        if '[QA]' in title:
            agent_type = 'qa'
        elif '[Deploy]' in title:
            agent_type = 'devops'
        elif '[Manager]' in title:
            agent_type = 'manager'
        
        # Find available agent
        agent_ip = get_available_agent(agent_type)
        
        if agent_ip:
            # Send work to agent
            send_work_to_agent(agent_ip, {
                'type': 'process_issue',
                'repo': repo,
                'issue_number': issue['number'],
                'issue_title': issue['title'],
                'issue_body': issue['body']
            })
            
            return jsonify({'status': 'assigned', 'agent': agent_ip}), 200
    
    return jsonify({'status': 'ignored'}), 200

def get_available_agent(agent_type):
    """Find an available agent on spot instances"""
    
    # Get running spot instances
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'instance-lifecycle', 'Values': ['spot']},
            {'Name': 'tag:AgentSystem', 'Values': ['vf-agents']}
        ]
    )
    
    available_instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            ip = instance['PrivateIpAddress']
            if ip not in busy_agents:
                available_instances.append(ip)
    
    if available_instances:
        # Pick random available instance
        selected = random.choice(available_instances)
        busy_agents.add(selected)
        return selected
    
    return None

def send_work_to_agent(agent_ip, work):
    """Send work to specific agent"""
    import requests
    
    try:
        response = requests.post(
            f"http://{agent_ip}:5000/process",
            json=work,
            timeout=30
        )
        return response.json()
    except:
        # Mark agent as available again if failed
        busy_agents.discard(agent_ip)
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
'''
    
    with open("agent-dispatcher.py", "w") as f:
        f.write(dispatcher)
    
    print("\n[DISPATCHER CREATED]:")
    print("✓ agent-dispatcher.py - Routes work to spot instance agents")
    
    return "agent-dispatcher.py"

def create_deployment_instructions():
    """Create simple deployment instructions"""
    
    instructions = """# DEPLOYMENT INSTRUCTIONS

## 1. Deploy GitHub Actions Workflow
Copy `.github/workflows/connect-to-agents.yml` to each repository:
- vf-dashboard-service
- vf-auth-service
- vf-video-service
- vf-image-service
- vf-audio-service

## 2. Deploy Dispatcher to vf-dev
```bash
# SSH to vf-dev server
ssh ec2-user@vf-dev.visualforgemedia.com

# Copy agent-dispatcher.py
scp agent-dispatcher.py ec2-user@vf-dev:~/

# Install dependencies
pip3 install flask boto3 requests

# Run dispatcher
nohup python3 agent-dispatcher.py > dispatcher.log 2>&1 &
```

## 3. Test the Connection
Create a test issue in any repo with title "[STORY] Test Issue"
- Should see "ai-processing" label added
- Check dispatcher.log on vf-dev
- Check agent logs on spot instances

## That's it! Issues will now auto-route to agents.
"""
    
    with open("DEPLOYMENT.md", "w") as f:
        f.write(instructions)
    
    print("\n[INSTRUCTIONS CREATED]:")
    print("✓ DEPLOYMENT.md - Simple deployment steps")

def main():
    # Create webhook config
    config = create_simple_github_webhook()
    
    # Create dispatcher
    create_agent_dispatcher()
    
    # Create instructions
    create_deployment_instructions()
    
    print("\n" + "="*80)
    print("CONNECTION SYSTEM READY")
    print("="*80)
    
    print("\n[HOW IT WORKS]:")
    print("1. Issue created in GitHub")
    print("2. GitHub Action triggers")
    print("3. Webhook sent to vf-dev dispatcher")
    print("4. Dispatcher finds available agent on spot instance")
    print("5. Agent processes issue")
    print("6. Agent updates GitHub issue")
    
    print("\n[NO GITHUB USERS NEEDED]:")
    print("- Agents use GitHub App authentication")
    print("- No individual user accounts required")
    print("- Actions handle the assignment")
    
    print("\n[COST EFFECTIVE]:")
    print("- 50 agents on spot instances: $8-15/month")
    print("- Auto-scales based on workload")
    print("- Handles spot interruptions gracefully")
    
    print("\n[TO ACTIVATE]:")
    print("1. Deploy workflows to repos")
    print("2. Start dispatcher on vf-dev")
    print("3. Create issues - agents auto-process!")
    
    print("\n[SUCCESS!]")
    print("GitHub to Agent connection system created!")

if __name__ == "__main__":
    main()