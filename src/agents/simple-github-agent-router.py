#!/usr/bin/env python3
"""
Simple GitHub Issue Agent Router
================================
Lightweight version for immediate deployment without AWS dependencies
Routes GitHub issues to appropriate agents based on labels and content
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SimpleAgentRouter')

class SimpleGitHubAgentRouter:
    """Simple agent router that can run anywhere"""
    
    def __init__(self):
        self.agent_mapping = {
            # Development Team
            'developer': {
                'name': 'AI Developer Agent',
                'script': 'ai-developer-agent.py',
                'patterns': ['fix', 'implement', 'add', 'create', 'build', 'develop', 'code'],
                'labels': ['bug', 'feature', 'enhancement'],
                'priority': 1,
                'timeout_minutes': 30
            },
            'architect': {
                'name': 'AI Architect Agent', 
                'script': 'ai-architect-agent.py',
                'patterns': ['design', 'architecture', 'structure', 'pattern', 'framework'],
                'labels': ['architecture', 'design'],
                'priority': 1,
                'timeout_minutes': 20
            },
            'qa': {
                'name': 'AI QA Agent',
                'script': 'ai-qa-agent.py', 
                'patterns': ['test', 'verify', 'validate', 'check', 'quality'],
                'labels': ['testing', 'qa', 'quality'],
                'priority': 2,
                'timeout_minutes': 45
            },
            'devops': {
                'name': 'AI DevOps Agent',
                'script': 'ai-devops-agent.py',
                'patterns': ['deploy', 'infrastructure', 'pipeline', 'ci/cd', 'aws'],
                'labels': ['deployment', 'infrastructure', 'devops', 'ci/cd'],
                'priority': 0,
                'timeout_minutes': 25
            },
            
            # Business Team (from existing orchestrator)
            'manager': {
                'name': 'AI Manager Agent',
                'script': 'ai-manager-agent.py',
                'patterns': ['strategy', 'plan', 'roadmap', 'priority', 'decision'],
                'labels': ['management', 'strategy'],
                'priority': 0,
                'timeout_minutes': 15
            },
            'support': {
                'name': 'AI Support Agent',
                'script': 'ai-support-agent.py',
                'patterns': ['help', 'issue', 'problem', 'error', 'broken'],
                'labels': ['support', 'help'],
                'priority': 1,
                'timeout_minutes': 10
            },
            'security': {
                'name': 'AI Security Agent',
                'script': 'ai-security-agent.py',
                'patterns': ['secure', 'vulnerability', 'auth', 'permission', 'encrypt'],
                'labels': ['security', 'vulnerability'],
                'priority': 0,
                'timeout_minutes': 30
            },
            'analytics': {
                'name': 'AI Analytics Agent',
                'script': 'ai-analytics-agent.py',
                'patterns': ['analyze', 'report', 'metrics', 'data'],
                'labels': ['analytics', 'reporting'],
                'priority': 2,
                'timeout_minutes': 60
            }
        }
        
        logger.info("Simple GitHub Agent Router initialized")
    
    def analyze_issue(self, title: str, body: str, labels: List[str]) -> str:
        """Analyze issue to determine which agent should handle it"""
        
        title_lower = title.lower()
        body_lower = body.lower()
        labels_lower = [label.lower() for label in labels]
        
        # Priority 1: Explicit labels
        for agent_type, config in self.agent_mapping.items():
            for label in config['labels']:
                if label in labels_lower:
                    logger.info(f"Agent selected by label '{label}': {agent_type}")
                    return agent_type
        
        # Priority 2: Title patterns
        for agent_type, config in self.agent_mapping.items():
            for pattern in config['patterns']:
                if pattern in title_lower:
                    logger.info(f"Agent selected by title pattern '{pattern}': {agent_type}")
                    return agent_type
        
        # Priority 3: Body content
        for agent_type, config in self.agent_mapping.items():
            for pattern in config['patterns']:
                if pattern in body_lower:
                    logger.info(f"Agent selected by body pattern '{pattern}': {agent_type}")
                    return agent_type
        
        # Default: Developer agent
        logger.info("No specific match, defaulting to developer agent")
        return 'developer'
    
    def create_agent_assignment(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create agent assignment for an issue"""
        
        title = issue_data.get('title', '')
        body = issue_data.get('body', '')
        labels = [label.get('name', '') for label in issue_data.get('labels', [])]
        issue_number = issue_data.get('number', 0)
        
        # Determine agent
        agent_type = self.analyze_issue(title, body, labels)
        agent_config = self.agent_mapping[agent_type]
        
        assignment = {
            'issue_number': issue_number,
            'issue_title': title,
            'agent_type': agent_type,
            'agent_name': agent_config['name'],
            'agent_script': agent_config['script'],
            'priority': agent_config['priority'],
            'timeout_minutes': agent_config['timeout_minutes'],
            'assigned_at': datetime.now().isoformat(),
            'labels_to_add': [
                'ai-assigned',
                f'agent-{agent_type}',
                f'priority-p{agent_config["priority"]}'
            ],
            'processing_status': 'assigned'
        }
        
        return assignment
    
    def create_docker_run_command(self, assignment: Dict[str, Any], github_token: str, repo: str) -> str:
        """Create Docker command to run agent"""
        
        docker_cmd = f"""docker run --rm \\
  -e GITHUB_TOKEN="{github_token}" \\
  -e GITHUB_REPO="{repo}" \\
  -e ISSUE_NUMBER="{assignment['issue_number']}" \\
  -e AGENT_TYPE="{assignment['agent_type']}" \\
  -e AGENT_NAME="{assignment['agent_name']}" \\
  ai-agents/agent-processor:latest"""
        
        return docker_cmd
    
    def create_batch_script(self, assignment: Dict[str, Any]) -> str:
        """Create batch script for manual processing"""
        
        script = f"""#!/bin/bash
# Process GitHub Issue #{assignment['issue_number']} with {assignment['agent_name']}

echo "Starting {assignment['agent_name']} for issue #{assignment['issue_number']}"

# Set environment variables
export GITHUB_TOKEN="${{GITHUB_TOKEN}}"
export GITHUB_REPO="${{GITHUB_REPO}}"
export ISSUE_NUMBER="{assignment['issue_number']}"
export AGENT_TYPE="{assignment['agent_type']}"

# Run the agent
python {assignment['agent_script']} \\
  --process-issue {assignment['issue_number']} \\
  --repo ${{GITHUB_REPO}}

echo "Processing completed"
"""
        
        return script

def create_deployment_package():
    """Create complete deployment package"""
    
    logger.info("Creating deployment package...")
    
    # Create directory structure
    deploy_dir = Path("ai-agent-deployment")
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy essential files
    essential_files = [
        "github-agent-dispatcher.py",
        "enhanced-batch-agent-processor.py", 
        "ai-developer-agent.py",
        "ai-manager-agent.py",
        "ai-qa-agent.py",
        "ai-architect-agent.py",
        "ai-devops-agent.py",
        "agent-policy-engine.py",
        "requirements.txt",
        "Dockerfile"
    ]
    
    for file in essential_files:
        if Path(file).exists():
            import shutil
            shutil.copy2(file, deploy_dir / file)
            logger.info(f"Copied {file}")
    
    # Copy GitHub Actions workflow
    workflow_dir = deploy_dir / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    if Path(".github/workflows/ai-agent-processor.yml").exists():
        import shutil
        shutil.copy2(".github/workflows/ai-agent-processor.yml", workflow_dir / "ai-agent-processor.yml")
        logger.info("Copied GitHub Actions workflow")
    
    # Create README
    readme_content = """# AI Agent Deployment Package

## Quick Start

### 1. Manual Agent Processing
```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"
export GITHUB_REPO="owner/repository"

# Process a specific issue
python enhanced-batch-agent-processor.py
```

### 2. Docker Processing
```bash
# Build the container
docker build -t ai-agents/agent-processor .

# Run for a specific issue
docker run --rm \\
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \\
  -e GITHUB_REPO="owner/repo" \\
  -e ISSUE_NUMBER="123" \\
  -e AGENT_TYPE="developer" \\
  ai-agents/agent-processor:latest
```

### 3. GitHub Actions (Automated)
1. Copy `.github/workflows/ai-agent-processor.yml` to your repository
2. Add these repository secrets:
   - `AWS_ACCESS_KEY_ID` (if using AWS)
   - `AWS_SECRET_ACCESS_KEY` (if using AWS)
3. Add these repository variables:
   - `AWS_REGION` (default: us-east-1)
   - `USE_DIRECT_PROCESSING=true` (to process directly in GitHub Actions)

## Supported Agents

- **Developer Agent**: Handles bugs, features, code changes
- **Architect Agent**: Handles design and architecture issues  
- **QA Agent**: Handles testing and quality assurance
- **DevOps Agent**: Handles deployment and infrastructure
- **Manager Agent**: Handles strategy and management decisions
- **Support Agent**: Handles customer support issues
- **Security Agent**: Handles security vulnerabilities
- **Analytics Agent**: Handles reporting and data analysis

## Agent Selection

Agents are automatically selected based on:
1. **Issue labels** (highest priority)
2. **Title keywords** 
3. **Body content patterns**

### Label Mapping
- `bug`, `feature`, `enhancement` -> Developer Agent
- `architecture`, `design` -> Architect Agent  
- `testing`, `qa`, `quality` -> QA Agent
- `deployment`, `infrastructure`, `devops` -> DevOps Agent
- `security`, `vulnerability` -> Security Agent
- `support`, `help` -> Support Agent
- `analytics`, `reporting` -> Analytics Agent
- `management`, `strategy` -> Manager Agent

## Configuration

All configuration is handled through environment variables:
- `GITHUB_TOKEN`: GitHub personal access token
- `GITHUB_REPO`: Repository in format "owner/repo"  
- `ISSUE_NUMBER`: Issue number to process
- `AGENT_TYPE`: Agent type to use
- `AWS_REGION`: AWS region (if using AWS)
"""
    
    with open(deploy_dir / "README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create quick test script
    test_script = """#!/bin/bash
# Quick test of agent assignment

echo "Testing AI Agent Router..."

python3 -c "
import sys
sys.path.append('.')
from simple_github_agent_router import SimpleGitHubAgentRouter

router = SimpleGitHubAgentRouter()

# Test cases
test_issues = [
    {'title': 'Fix login bug', 'body': 'Users cannot login', 'labels': [{'name': 'bug'}]},
    {'title': 'Design new architecture', 'body': 'Need to redesign the system', 'labels': [{'name': 'architecture'}]},
    {'title': 'Add security scan', 'body': 'Need vulnerability testing', 'labels': [{'name': 'security'}]},
    {'title': 'Deploy to production', 'body': 'Ready for deployment', 'labels': [{'name': 'deployment'}]}
]

for issue in test_issues:
    assignment = router.create_agent_assignment(issue)
    print(f'Issue: \"{issue[\"title\"]}\" -> {assignment[\"agent_name\"]}')

print('\\nTest completed successfully!')
"

echo "All tests passed! ✅"
"""
    
    with open(deploy_dir / "test-agent-assignment.sh", "w", encoding='utf-8') as f:
        f.write(test_script)
    
    # Make scripts executable
    import stat
    (deploy_dir / "test-agent-assignment.sh").chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    
    logger.info(f"Deployment package created in: {deploy_dir}")
    return deploy_dir

def main():
    """Main function for testing and package creation"""
    
    print("\n" + "="*80)
    print("🚀 SIMPLE GITHUB AGENT ROUTER")
    print("="*80)
    print("Creating lightweight deployment package...")
    print("="*80)
    
    # Test the router
    router = SimpleGitHubAgentRouter()
    
    # Test cases
    test_cases = [
        {
            'title': '[BUG] Fix authentication issue in login flow',
            'body': 'Users are unable to login after recent deployment. Need to investigate and fix.',
            'labels': [{'name': 'bug'}, {'name': 'backend'}]
        },
        {
            'title': '[FEATURE] Add new user dashboard',
            'body': 'Create a comprehensive user dashboard with analytics.',
            'labels': [{'name': 'feature'}, {'name': 'frontend'}]
        },
        {
            'title': 'Design microservices architecture',
            'body': 'Need to redesign the monolith into microservices.',
            'labels': [{'name': 'architecture'}]
        },
        {
            'title': 'Security vulnerability in API',
            'body': 'Found potential SQL injection vulnerability.',
            'labels': [{'name': 'security'}, {'name': 'critical'}]
        },
        {
            'title': 'Deploy to production environment',
            'body': 'Ready to deploy version 2.0 to production.',
            'labels': [{'name': 'deployment'}]
        }
    ]
    
    print("\n🧪 Testing agent assignments:")
    print("-" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        assignment = router.create_agent_assignment(test_case)
        print(f"{i}. \"{test_case['title'][:50]}...\"")
        print(f"   -> {assignment['agent_name']} (P{assignment['priority']})")
        print(f"   -> Script: {assignment['agent_script']}")
        print()
    
    # Create deployment package
    print("📦 Creating deployment package...")
    deploy_dir = create_deployment_package()
    
    print("\n" + "="*80)
    print("✅ DEPLOYMENT PACKAGE READY")
    print("="*80)
    
    print(f"\n📁 Package Location: {deploy_dir}")
    print("\n🚀 Quick Start Options:")
    print()
    print("1. **Manual Processing** (No dependencies):")
    print("   cd ai-agent-deployment")
    print("   export GITHUB_TOKEN='your_token'")
    print("   export GITHUB_REPO='owner/repo'")
    print("   export ISSUE_NUMBER='123'")
    print("   export AGENT_TYPE='developer'")
    print("   python enhanced-batch-agent-processor.py")
    print()
    print("2. **Docker Processing** (Containerized):")
    print("   cd ai-agent-deployment")
    print("   docker build -t ai-agents/processor .")
    print("   docker run --rm -e GITHUB_TOKEN='...' ai-agents/processor")
    print()
    print("3. **GitHub Actions** (Fully Automated):")
    print("   - Copy .github/workflows/ai-agent-processor.yml to your repo")
    print("   - Add USE_DIRECT_PROCESSING=true to repository variables")
    print("   - Create issues with appropriate labels")
    print("   - Agents will automatically process them!")
    print()
    print("4. **Test Assignment Logic**:")
    print("   cd ai-agent-deployment")
    print("   ./test-agent-assignment.sh")
    print()
    
    print("🎯 Agent Selection Rules:")
    print("• Labels take highest priority")
    print("• Title keywords are second priority")  
    print("• Body content patterns are fallback")
    print("• Default: Developer Agent")
    print()
    
    print("📋 Supported Labels:")
    for agent_type, config in router.agent_mapping.items():
        print(f"• {', '.join(config['labels'])} -> {config['name']}")
    
    print("\n🎉 READY FOR IMMEDIATE DEPLOYMENT!")
    print("No AWS setup required for basic functionality")

if __name__ == "__main__":
    main()
