#!/usr/bin/env python3
"""
Create GitHub Actions Workflow for Autonomous Agent Processing
===============================================================
Sets up GitHub Actions to automatically trigger agents when issues are created
"""

import subprocess
import base64

def create_workflow_for_repo(repo_name, service_type):
    """Create workflow file for a specific repo"""
    
    workflow_content = f"""name: Auto-Process Issues with AI Agents

on:
  issues:
    types: [opened, reopened, labeled]
  issue_comment:
    types: [created]

jobs:
  process-issue:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install requests boto3 PyGithub openai
    
    - name: Determine Agent Type
      id: agent-type
      run: |
        # Determine which agent should handle this
        if [[ "${{{{ github.event.issue.title }}}}" == *"[STORY]"* ]]; then
          echo "agent=developer" >> $GITHUB_OUTPUT
        elif [[ "${{{{ github.event.issue.title }}}}" == *"[QA]"* ]]; then
          echo "agent=qa" >> $GITHUB_OUTPUT
        elif [[ "${{{{ github.event.issue.title }}}}" == *"[BUG]"* ]]; then
          echo "agent=developer" >> $GITHUB_OUTPUT
        elif [[ "${{{{ github.event.issue.title }}}}" == *"[DEPLOY]"* ]]; then
          echo "agent=devops" >> $GITHUB_OUTPUT
        else
          echo "agent=developer" >> $GITHUB_OUTPUT
        fi
    
    - name: Process with Developer Agent
      if: steps.agent-type.outputs.agent == 'developer'
      env:
        GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
        ISSUE_NUMBER: ${{{{ github.event.issue.number }}}}
        REPO_NAME: ${{{{ github.repository }}}}
      run: |
        # Download and run the developer agent
        curl -O https://raw.githubusercontent.com/VisualForgeMediaV2/agent-scripts/main/ai-developer-agent.py
        python ai-developer-agent.py --process-issue $ISSUE_NUMBER --repo $REPO_NAME
    
    - name: Process with QA Agent
      if: steps.agent-type.outputs.agent == 'qa'
      env:
        GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
        ISSUE_NUMBER: ${{{{ github.event.issue.number }}}}
        REPO_NAME: ${{{{ github.repository }}}}
      run: |
        curl -O https://raw.githubusercontent.com/VisualForgeMediaV2/agent-scripts/main/ai-qa-agent.py
        python ai-qa-agent.py --process-issue $ISSUE_NUMBER --repo $REPO_NAME
    
    - name: Process with DevOps Agent
      if: steps.agent-type.outputs.agent == 'devops'
      env:
        GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
        ISSUE_NUMBER: ${{{{ github.event.issue.number }}}}
        REPO_NAME: ${{{{ github.repository }}}}
      run: |
        curl -O https://raw.githubusercontent.com/VisualForgeMediaV2/agent-scripts/main/ai-devops-agent.py
        python ai-devops-agent.py --process-issue $ISSUE_NUMBER --repo $REPO_NAME
    
    - name: Auto-Assign Issue
      if: always()
      uses: actions/github-script@v6
      with:
        script: |
          // Auto-assign to the bot
          await github.rest.issues.addAssignees({{
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: context.issue.number,
            assignees: ['ai-agent-bot']
          }});
          
          // Add processing label
          await github.rest.issues.addLabels({{
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: context.issue.number,
            labels: ['processing']
          }});
          
          // Comment that work has started
          await github.rest.issues.createComment({{
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: context.issue.number,
            body: '🤖 AI Agent has started processing this issue...'
          }});

# Webhook Alternative (if using webhooks instead)
webhook-processor:
  name: Process via Webhook
  runs-on: ubuntu-latest
  if: github.event_name == 'issues'
  
  steps:
  - name: Trigger Agent Webhook
    run: |
      curl -X POST ${{{{ secrets.AGENT_WEBHOOK_URL }}}} \\
        -H "Content-Type: application/json" \\
        -H "X-GitHub-Event: ${{{{ github.event_name }}}}" \\
        -d '{{
          "action": "${{{{ github.event.action }}}}",
          "issue": {{
            "number": ${{{{ github.event.issue.number }}}},
            "title": "${{{{ github.event.issue.title }}}}",
            "body": "${{{{ github.event.issue.body }}}}",
            "repo": "${{{{ github.repository }}}}"
          }}
        }}'
"""
    
    return workflow_content

def deploy_workflow_to_repo(repo_name):
    """Deploy workflow file to a repository"""
    
    workflow = create_workflow_for_repo(repo_name, "service")
    
    # Create the workflow file in the repo
    workflow_path = ".github/workflows/ai-agent-processor.yml"
    
    print(f"Creating workflow for {repo_name}...")
    
    # First, check if .github/workflows exists
    check_cmd = f"gh api repos/{repo_name}/contents/.github/workflows"
    result = subprocess.run(check_cmd.split(), capture_output=True)
    
    if result.returncode != 0:
        # Create .github/workflows directory
        print(f"  Creating .github/workflows directory...")
    
    # Create or update the workflow file
    workflow_b64 = base64.b64encode(workflow.encode()).decode()
    
    create_cmd = f"""gh api repos/{repo_name}/contents/{workflow_path} \
        -X PUT \
        -f message="Add AI agent auto-processing workflow" \
        -f content={workflow_b64}"""
    
    try:
        result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [OK] Workflow created")
            return True
        else:
            # Try to get existing file SHA and update
            get_cmd = f"gh api repos/{repo_name}/contents/{workflow_path}"
            get_result = subprocess.run(get_cmd.split(), capture_output=True, text=True)
            if get_result.returncode == 0:
                import json
                file_data = json.loads(get_result.stdout)
                sha = file_data.get('sha')
                
                update_cmd = f"""gh api repos/{repo_name}/contents/{workflow_path} \
                    -X PUT \
                    -f message="Update AI agent workflow" \
                    -f content={workflow_b64} \
                    -f sha={sha}"""
                
                result = subprocess.run(update_cmd, shell=True, capture_output=True)
                if result.returncode == 0:
                    print(f"  [OK] Workflow updated")
                    return True
            
            print(f"  [ERROR] Could not create workflow: {result.stderr[:100]}")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    return False

def create_simple_webhook_processor():
    """Create a simple webhook processor that can run on AWS Lambda or server"""
    
    webhook_code = '''import json
import subprocess
import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def process_webhook():
    """Process GitHub webhook and trigger appropriate agent"""
    
    payload = request.json
    
    if payload.get('action') in ['opened', 'reopened']:
        issue = payload['issue']
        repo = payload['repository']['full_name']
        
        # Determine agent type from title
        title = issue['title']
        if '[STORY]' in title or '[Dev]' in title:
            agent = 'ai-developer-agent.py'
        elif '[QA]' in title:
            agent = 'ai-qa-agent.py'
        elif '[Deploy]' in title:
            agent = 'ai-devops-agent.py'
        else:
            agent = 'ai-developer-agent.py'
        
        # Trigger the agent
        cmd = f"python {agent} --process-issue {issue['number']} --repo {repo}"
        subprocess.run(cmd.split(), capture_output=True)
        
        return {'status': 'processing'}, 200
    
    return {'status': 'ignored'}, 200

if __name__ == '__main__':
    app.run(port=5000)
'''
    
    with open("webhook_processor.py", "w") as f:
        f.write(webhook_code)
    
    print("[OK] Created webhook_processor.py")

def main():
    print("\n" + "="*80)
    print("SETTING UP AUTONOMOUS AGENT PROCESSING")
    print("="*80)
    
    repos_to_setup = [
        "VisualForgeMediaV2/vf-dashboard-service",
        "VisualForgeMediaV2/vf-auth-service",
        "VisualForgeMediaV2/vf-video-service",
        "VisualForgeMediaV2/vf-image-service",
        "VisualForgeMediaV2/vf-audio-service",
        "VisualForgeMediaV2/vf-text-service",
    ]
    
    print("\n[GITHUB ACTIONS SETUP]")
    print("Creating workflow files for automatic agent triggering...")
    
    # Save a sample workflow locally
    with open("ai-agent-workflow.yml", "w") as f:
        f.write(create_workflow_for_repo("sample-repo", "service"))
    print("[OK] Created sample workflow: ai-agent-workflow.yml")
    
    print("\n[WORKFLOW FEATURES]:")
    print("✓ Triggers on issue creation")
    print("✓ Determines agent type from title")
    print("✓ Runs appropriate agent")
    print("✓ Auto-assigns to AI bot")
    print("✓ Adds processing label")
    print("✓ Comments on issue")
    
    print("\n[TO DEPLOY TO REPOS]:")
    for repo in repos_to_setup:
        print(f"  {repo}")
    
    print("\n[MANUAL SETUP REQUIRED]:")
    print("1. Add OPENAI_API_KEY secret to each repo")
    print("2. Create ai-agent-bot user (or use existing bot)")
    print("3. Upload agent scripts to agent-scripts repo")
    print("4. Copy ai-agent-workflow.yml to each repo's .github/workflows/")
    
    print("\n[WEBHOOK ALTERNATIVE]:")
    create_simple_webhook_processor()
    print("Deploy webhook_processor.py to server/Lambda")
    print("Configure GitHub webhook to point to endpoint")
    
    print("\n[NEXT STEPS]:")
    print("1. Choose: GitHub Actions or Webhooks")
    print("2. Deploy the workflow/webhook")
    print("3. Test with an issue")
    print("4. Agents will auto-process!")
    
    print("\n[SUCCESS!]")
    print("Automation setup ready for deployment!")

if __name__ == "__main__":
    main()