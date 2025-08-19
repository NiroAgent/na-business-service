#!/usr/bin/env python3
"""
Fixed Agent Coordinator - Routes to agents that actually do work
"""

import subprocess
import json
import time
import os
from datetime import datetime

class FixedCoordinator:
    """Coordinator that uses fixed agents"""
    
    def __init__(self):
        self.repo = "VisualForgeMediaV2/business-operations"
        self.processed = set()
        
    def run_once(self):
        """Process all open issues once"""
        
        print("\n" + "="*60)
        print("FIXED AGENT COORDINATOR")
        print("="*60)
        
        # Get open issues
        result = subprocess.run([
            'gh', 'issue', 'list',
            '--repo', self.repo,
            '--state', 'open',
            '--json', 'number,title,body,labels',
            '--limit', '20'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[ERROR] Could not fetch issues: {result.stderr}")
            return
            
        issues = json.loads(result.stdout)
        print(f"Found {len(issues)} open issues\n")
        
        for issue in issues:
            self.process_issue(issue)
            
    def process_issue(self, issue):
        """Process a single issue with the right agent"""
        
        number = issue['number']
        title = issue['title']
        body = issue.get('body', '')
        
        # Skip if already processed
        if number in self.processed:
            return
            
        print("="*60)
        print(f"Processing Issue #{number}: {title}")
        
        # Determine which agent to use
        agent_script = None
        agent_name = None
        
        if '[PM]' in title or 'plan' in title.lower() or 'review' in title.lower():
            agent_script = 'fixed-pm-agent.py'
            agent_name = 'Project Manager'
        elif '[DEV]' in title or 'implement' in title.lower():
            agent_script = 'fixed-developer-agent.py'
            agent_name = 'Developer'
        elif '[QA]' in title or 'test' in title.lower():
            agent_script = 'fixed-qa-agent.py'
            agent_name = 'QA'
        elif 'security' in title.lower():
            agent_name = 'Security'
            # Use existing security agent
            agent_script = 'ai-security-agent.py'
        else:
            # Default to operations
            agent_name = 'Operations'
            agent_script = 'ai-operations-agent.py'
            
        print(f"Assigned Agent: {agent_name}")
        print("="*60)
        
        # Save issue data
        issue_file = f"issue_{number}.json"
        with open(issue_file, 'w') as f:
            json.dump(issue, f)
            
        # Run the appropriate agent
        if agent_script in ['fixed-pm-agent.py', 'fixed-developer-agent.py']:
            # Use fixed agents
            if agent_script == 'fixed-developer-agent.py':
                # Developer needs repo info
                cmd = ['python', agent_script, '--issue', str(number), '--repo', self.repo]
            else:
                cmd = ['python', agent_script, '--process-issue', str(number), '--issue-data', issue_file]
        else:
            # Use existing agents
            cmd = ['python', agent_script, '--process-issue', str(number), '--issue-data', issue_file]
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[OK] Agent {agent_name} completed successfully")
            self.processed.add(number)
            
            # Add completion comment
            self.add_completion_comment(number, agent_name)
        else:
            print(f"[ERROR] Agent {agent_name} failed: {result.stderr}")
            
    def add_completion_comment(self, issue_number, agent_name):
        """Add a comment showing agent processed the issue"""
        
        comment = f"""## Agent Processing Update

**Agent:** {agent_name}
**Status:** COMPLETED
**Timestamp:** {datetime.now().isoformat()}

The {agent_name} agent has processed this issue. Check for:
- New delegation issues created
- Implementation code added
- Test plans generated

---
*Fixed Agent Coordinator*"""
        
        subprocess.run([
            'gh', 'issue', 'comment', str(issue_number),
            '--repo', self.repo,
            '--body', comment
        ], capture_output=True)
        
    def monitor(self):
        """Run continuously"""
        
        print("[MONITOR] Starting continuous monitoring...")
        
        while True:
            try:
                self.run_once()
                print(f"\n[WAIT] Sleeping for 60 seconds...")
                time.sleep(60)
            except KeyboardInterrupt:
                print("\n[STOP] Monitoring stopped")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(60)


def main():
    """Main entry point"""
    
    import sys
    
    coordinator = FixedCoordinator()
    
    if '--monitor' in sys.argv:
        coordinator.monitor()
    else:
        coordinator.run_once()
        print("\n[COMPLETE] Fixed coordinator finished processing")


if __name__ == '__main__':
    main()