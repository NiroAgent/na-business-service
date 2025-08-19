#!/usr/bin/env python3
"""
Fixed Project Manager Agent - Actually Creates Delegations
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class FixedPMAgent:
    """PM Agent that actually creates delegation issues"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        
    def process_issue(self, issue_number: int, issue_data: dict):
        """Process PM issue and create actual delegations"""
        
        title = issue_data.get('title', '')
        body = issue_data.get('body', '')
        
        print(f"\n=== FIXED PM AGENT PROCESSING ===")
        print(f"Issue #{issue_number}: {title}")
        
        # Check if this is about the dashboard
        if 'dashboard' in title.lower() or 'dashboard' in body.lower():
            self.delegate_dashboard_implementation()
        elif 'review' in title.lower() or 'plan' in title.lower():
            self.create_implementation_plan(title, body)
        else:
            self.create_generic_delegation(title, body)
            
    def delegate_dashboard_implementation(self):
        """Create specific delegations for dashboard implementation"""
        
        print("\n[DELEGATION] Creating Dashboard Implementation Delegations...")
        
        # 1. Create developer task for implementation
        dev_task = {
            'repo': 'VisualForgeMediaV2/vf-dashboard-service',
            'title': '[DEV] Implement Cost Monitoring Views',
            'body': '''## Developer Task: Implement Dashboard Cost Monitoring

### Context
Implement cost monitoring and activity tracking in the dashboard per issue #8.

### Requirements
1. Fix tab switching system in dashboard
2. Create AWS Cost Explorer integration
3. Build cost visualization components
4. Add activity feed with real-time updates

### Technical Details
- Use existing AWS SDK credentials
- Follow React patterns in codebase
- Ensure mobile responsive
- Cache cost data (5 min TTL)

### Acceptance Criteria
- [ ] Tabs switch correctly without state loss
- [ ] Cost data displays with charts
- [ ] Activity feed shows agent operations
- [ ] Data updates every 5 minutes
- [ ] All tests pass

### Files to Modify
- `dashboard.html` - Fix tab system
- `api/costs.py` - Create cost endpoints
- `components/CostView.jsx` - Cost visualization
- `components/ActivityFeed.jsx` - Activity tracking

assigned_agent: vf-developer-agent
priority: P0
estimated_hours: 12
'''
        }
        
        # 2. Create QA task for testing
        qa_task = {
            'repo': 'VisualForgeMediaV2/vf-dashboard-service',
            'title': '[QA] Test Dashboard Cost Monitoring',
            'body': '''## QA Task: Test Dashboard Implementation

### Test Scope
Validate the dashboard cost monitoring and activity tracking features.

### Test Cases

#### 1. Tab Navigation
- Switch between all tabs
- Verify state persistence
- Test refresh behavior

#### 2. Cost Data Accuracy
- Compare with AWS Console
- Verify all services shown
- Check calculations

#### 3. Activity Feed
- Verify real-time updates
- Test filtering options
- Check pagination

#### 4. Performance
- Load time < 2 seconds
- Tab switch < 500ms
- Memory usage < 200MB

### Dependencies
- Development task must be complete
- Test environment access required

assigned_agent: vf-qa-agent
priority: P0
depends_on: dev_task
'''
        }
        
        # 3. Create DevOps task for deployment
        devops_task = {
            'repo': 'VisualForgeMediaV2/vf-dashboard-service',
            'title': '[DEPLOY] Deploy Dashboard Updates to vf-dev',
            'body': '''## DevOps Task: Deploy Dashboard

### Deployment Requirements
Deploy the updated dashboard with cost monitoring to vf-dev environment.

### Steps
1. Build production bundle
2. Run security scan
3. Deploy to vf-dev CloudFront
4. Verify endpoints active
5. Set up monitoring alerts

### Configuration
- Enable Cost Explorer API access
- Configure CORS for API endpoints
- Set up CloudWatch dashboards
- Configure auto-scaling

assigned_agent: vf-devops-agent
priority: P0
depends_on: qa_task
'''
        }
        
        # Actually create the issues
        for task in [dev_task, qa_task, devops_task]:
            self.create_github_issue(task)
            
    def create_github_issue(self, task: dict):
        """Actually create a GitHub issue"""
        
        repo = task['repo']
        title = task['title']
        body = task['body']
        
        print(f"\n[CREATE] Creating issue in {repo}:")
        print(f"   Title: {title}")
        
        # Use gh CLI to create the issue
        cmd = [
            'gh', 'issue', 'create',
            '--repo', repo,
            '--title', title,
            '--body', body
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                print(f"   [OK] Created: {issue_url}")
                
                # Add to tracking
                self.add_to_tracking(issue_url, task)
            else:
                print(f"   [FAIL] Failed: {result.stderr}")
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
            
    def add_to_tracking(self, issue_url: str, task: dict):
        """Add created issue to tracking system"""
        
        # Extract issue number from URL
        issue_num = issue_url.split('/')[-1]
        repo_name = task['repo'].split('/')[-1]
        
        # Update business-operations with delegation record
        tracking_comment = f"""## [DELEGATED] Delegation Created

**Repository**: {task['repo']}
**Issue**: #{issue_num}
**URL**: {issue_url}
**Type**: {task['title'].split(']')[0][1:]}
**Status**: Delegated

This task has been delegated to the appropriate agent for implementation.
"""
        
        # Add comment to original PM issue
        subprocess.run([
            'gh', 'issue', 'comment', '16',
            '--repo', 'VisualForgeMediaV2/business-operations',
            '--body', tracking_comment
        ], capture_output=True)
        
    def create_implementation_plan(self, title: str, body: str):
        """Create implementation plan with multiple delegations"""
        
        print("\n[PLAN] Creating Implementation Plan...")
        
        # Parse requirements from body
        if 'auth' in body.lower():
            service = 'vf-auth-service'
        elif 'video' in body.lower():
            service = 'vf-video-service'
        elif 'payment' in body.lower():
            service = 'ns-payments'
        else:
            service = 'vf-dashboard-service'
            
        # Create architect review first
        arch_task = {
            'repo': f'VisualForgeMediaV2/{service}',
            'title': '[ARCH] Technical Design Review',
            'body': f'''## Architecture Review Required

### Context
{body}

### Review Checklist
- [ ] API design follows REST standards
- [ ] Security considerations addressed
- [ ] Scalability requirements met
- [ ] Database schema optimized
- [ ] Error handling comprehensive

### Deliverables
- Technical design document
- API specifications
- Database schema
- Security assessment

assigned_agent: vf-architect-agent
priority: P1
'''
        }
        
        self.create_github_issue(arch_task)
        
    def create_generic_delegation(self, title: str, body: str):
        """Create generic delegation for other requests"""
        
        print("\n[GENERIC] Creating Generic Delegation...")
        
        task = {
            'repo': 'VisualForgeMediaV2/business-operations',
            'title': f'[DELEGATED] {title}',
            'body': f'''{body}

---
## Delegation Details
This task requires further analysis and delegation.

assigned_agent: vf-manager-agent
status: pending
'''
        }
        
        self.create_github_issue(task)


def main():
    """Main entry point"""
    
    # Parse arguments
    if len(sys.argv) < 3:
        print("Usage: python fixed-pm-agent.py --process-issue <num> --issue-data <file>")
        return
        
    issue_number = None
    issue_file = None
    
    for i, arg in enumerate(sys.argv):
        if arg == '--process-issue':
            issue_number = int(sys.argv[i+1])
        elif arg == '--issue-data':
            issue_file = sys.argv[i+1]
            
    if not issue_number or not issue_file:
        print("Missing required arguments")
        return
        
    # Load issue data
    with open(issue_file, 'r') as f:
        issue_data = json.load(f)
        
    # Process with fixed agent
    agent = FixedPMAgent()
    agent.process_issue(issue_number, issue_data)
    
    print("\n[COMPLETE] PM Agent Processing Complete!")
    print("Check the repositories for newly created delegation issues.")


if __name__ == '__main__':
    main()