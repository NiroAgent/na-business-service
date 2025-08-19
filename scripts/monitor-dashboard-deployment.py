#!/usr/bin/env python3
"""
Monitor Dashboard Deployment Status
Watches for deployment completion and notifies when done
"""

import subprocess
import json
import time
from datetime import datetime

def check_issue_status(issue_number, repo):
    """Check if an issue is closed or has completion comments"""
    try:
        # Get issue details
        cmd = ['gh', 'issue', 'view', str(issue_number), '--repo', repo, '--json', 'state,comments,body']
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            # Check if closed
            if data['state'] == 'CLOSED':
                return 'completed'
            
            # Check comments for completion indicators
            comments = data.get('comments', [])
            for comment in comments:
                body = comment.get('body', '').lower()
                if any(word in body for word in ['complete', 'done', 'deployed', 'passed', 'ready']):
                    return 'likely_complete'
            
            # Check if all checkboxes are checked
            body = data.get('body', '')
            if '- [x]' in body and '- [ ]' not in body:
                return 'tasks_complete'
                
        return 'in_progress'
    except Exception as e:
        print(f"Error checking issue: {e}")
        return 'error'

def send_notification(message):
    """Send notification to user"""
    print(f"\n{'='*60}")
    print(f"[NOTIFICATION] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    print(f"\n{message}\n")
    print('='*60)
    
    # Also create a notification file
    with open('DEPLOYMENT_COMPLETE.txt', 'w') as f:
        f.write(f"DASHBOARD DEPLOYMENT STATUS\n")
        f.write(f"{'='*60}\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Status: COMPLETE\n")
        f.write(f"\n{message}\n")

def monitor_deployment():
    """Monitor deployment and testing issues"""
    
    deployment_issue = 56
    testing_issue = 57
    repo = "VisualForgeMediaV2/vf-dashboard-service"
    
    print("[MONITOR] Starting deployment monitoring...")
    print(f"[MONITOR] Tracking deployment issue #{deployment_issue}")
    print(f"[MONITOR] Tracking testing issue #{testing_issue}")
    print("[MONITOR] Checking every 30 seconds...")
    
    check_count = 0
    
    while True:
        check_count += 1
        print(f"\n[Check #{check_count}] {datetime.now().strftime('%H:%M:%S')}")
        
        # Check deployment status
        deploy_status = check_issue_status(deployment_issue, repo)
        test_status = check_issue_status(testing_issue, repo)
        
        print(f"  - Deployment: {deploy_status}")
        print(f"  - Testing: {test_status}")
        
        # Check if both are complete
        if deploy_status in ['completed', 'tasks_complete'] and test_status in ['completed', 'tasks_complete']:
            message = f"""
✅ DASHBOARD DEPLOYMENT COMPLETE!

Deployment Issue #{deployment_issue}: DONE
Testing Issue #{testing_issue}: DONE

The dashboard has been successfully:
- Deployed to the development environment
- Tested by the QA team
- Verified and ready for use

View the issues:
- Deployment: https://github.com/{repo}/issues/{deployment_issue}
- Testing: https://github.com/{repo}/issues/{testing_issue}

The dashboard team has completed the deployment and testing process.
"""
            send_notification(message)
            break
        
        # Check for partial completion
        elif deploy_status in ['completed', 'tasks_complete', 'likely_complete']:
            print("  [!] Deployment appears complete, waiting for testing...")
        
        # Wait before next check
        time.sleep(30)
    
    print("\n[MONITOR] Monitoring complete. Dashboard is deployed and tested!")

if __name__ == "__main__":
    try:
        monitor_deployment()
    except KeyboardInterrupt:
        print("\n[MONITOR] Monitoring stopped by user")
    except Exception as e:
        print(f"[ERROR] Monitoring failed: {e}")