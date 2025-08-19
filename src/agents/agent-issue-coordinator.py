#!/usr/bin/env python3
"""
Agent Issue Coordinator
Assigns GitHub issues to specific AI agents and monitors their processing
"""

import os
import sys
import json
import subprocess
import asyncio
import time
from datetime import datetime
from pathlib import Path
import argparse
from typing import Dict, List, Any, Optional

class AgentIssueCoordinator:
    """Coordinates issue assignment and processing for AI agents"""
    
    def __init__(self):
        self.repo = "VisualForgeMediaV2/business-operations"
        
        # Agent assignment mapping based on labels
        self.label_to_agent = {
            "operations/monitoring": "ai-operations-agent",
            "operations/optimization": "ai-operations-agent",
            "support/quality-assurance": "ai-support-agent",
            "analytics/reporting": "ai-analytics-agent",
            "security/compliance": "ai-security-agent",
            "success/user-research": "ai-customer-success-agent",
            "finance/analysis": "ai-finance-agent",
            "marketing/": "ai-marketing-agent",
            "sales/": "ai-sales-agent",
            "management/strategic-planning": "ai-project-manager-agent",
            "management/resource-allocation": "ai-project-manager-agent",
            "management/escalation": "ai-project-manager-agent",
            "management/kpi-review": "ai-project-manager-agent"
        }
        
        # Agent status tracking
        self.agent_status = {}
        
    def get_open_issues(self):
        """Get all open issues from the repository"""
        cmd = ["gh", "issue", "list", "--state", "open",
               "--repo", self.repo,
               "--json", "number,title,labels,assignees,body",
               "--limit", "100"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Error getting issues: {e}")
            return []
    
    def assign_agent_to_issue(self, issue_number, agent_name):
        """Assign an agent to an issue using labels"""
        label = f"assigned/{agent_name}"
        cmd = ["gh", "issue", "edit", str(issue_number),
               "--repo", self.repo,
               "--add-label", label]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Assigned {agent_name} to issue #{issue_number}")
            return True
        except Exception as e:
            # Label might not exist, create it
            self.create_agent_label(agent_name)
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                return True
            except:
                print(f"Could not assign {agent_name} to issue #{issue_number}")
                return False
    
    def create_agent_label(self, agent_name):
        """Create an agent assignment label"""
        label = f"assigned/{agent_name}"
        cmd = ["gh", "label", "create", label,
               "--repo", self.repo,
               "--color", "0052cc",
               "--description", f"Assigned to {agent_name}"]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Created label: {label}")
        except:
            pass  # Label might already exist
    
    def determine_agent_for_issue(self, issue):
        """Determine which agent should handle an issue based on labels"""
        labels = [label['name'] for label in issue.get('labels', [])]
        
        # Check if already assigned
        for label in labels:
            if label.startswith("assigned/"):
                return label.replace("assigned/", "")
        
        # Determine based on operation type
        for label in labels:
            for pattern, agent in self.label_to_agent.items():
                if pattern in label:
                    return agent
        
        return None
    
    def update_issue_status(self, issue_number, status, message):
        """Update issue with processing status"""
        timestamp = datetime.now().isoformat()
        comment = f"""## Agent Processing Update

**Status:** {status}
**Timestamp:** {timestamp}

{message}

---
*Automated update from Agent Issue Coordinator*"""
        
        cmd = ["gh", "issue", "comment", str(issue_number),
               "--repo", self.repo,
               "--body", comment]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except Exception as e:
            print(f"Error updating issue: {e}")
            return False
    
    async def process_issue_with_agent(self, issue, agent_name):
        """Process an issue with the specified agent"""
        issue_number = issue['number']
        print(f"\n{'='*60}")
        print(f"Processing Issue #{issue_number}: {issue['title']}")
        print(f"Agent: {agent_name}")
        print(f"{'='*60}")
        
        # Update issue to show processing started
        self.update_issue_status(
            issue_number,
            "PROCESSING",
            f"Agent {agent_name} has started processing this issue."
        )
        
        # Check if agent script exists
        agent_script = f"{agent_name}.py"
        if not Path(agent_script).exists():
            print(f"Agent script not found: {agent_script}")
            self.update_issue_status(
                issue_number,
                "ERROR",
                f"Agent script {agent_script} not found."
            )
            return False
        
        # Run the agent with the issue data
        try:
            # Create a temporary file with issue data
            issue_file = f"issue_{issue_number}_data.json"
            with open(issue_file, 'w') as f:
                json.dump(issue, f)
            
            # Run the agent
            cmd = [sys.executable, agent_script, "--issue-file", issue_file]
            print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )
            
            if result.returncode == 0:
                print(f"Agent completed successfully")
                self.update_issue_status(
                    issue_number,
                    "COMPLETED",
                    f"Agent {agent_name} has successfully processed this issue.\n\nOutput:\n```\n{result.stdout[:500]}\n```"
                )
                
                # Add completion label
                subprocess.run(
                    ["gh", "issue", "edit", str(issue_number),
                     "--repo", self.repo,
                     "--add-label", "status/done"],
                    capture_output=True
                )
                return True
            else:
                print(f"Agent failed with return code: {result.returncode}")
                print(f"Error: {result.stderr}")
                self.update_issue_status(
                    issue_number,
                    "FAILED",
                    f"Agent {agent_name} encountered an error.\n\nError:\n```\n{result.stderr[:500]}\n```"
                )
                return False
                
        except subprocess.TimeoutExpired:
            print(f"Agent timed out")
            self.update_issue_status(
                issue_number,
                "TIMEOUT",
                f"Agent {agent_name} timed out after 60 seconds."
            )
            return False
        except Exception as e:
            print(f"Error running agent: {e}")
            self.update_issue_status(
                issue_number,
                "ERROR",
                f"Error running agent: {str(e)}"
            )
            return False
        finally:
            # Clean up temp file
            if Path(issue_file).exists():
                os.remove(issue_file)
    
    async def coordinate_all_issues(self):
        """Coordinate processing of all open issues"""
        print("\nAGENT ISSUE COORDINATOR")
        print("="*60)
        
        # Get all open issues
        issues = self.get_open_issues()
        print(f"Found {len(issues)} open issues")
        
        if not issues:
            print("No open issues to process")
            return
        
        # Process each issue
        for issue in issues:
            # Determine which agent should handle it
            agent_name = self.determine_agent_for_issue(issue)
            
            if agent_name:
                # Assign the agent if not already assigned
                labels = [label['name'] for label in issue.get('labels', [])]
                if f"assigned/{agent_name}" not in labels:
                    self.assign_agent_to_issue(issue['number'], agent_name)
                
                # Process the issue
                await self.process_issue_with_agent(issue, agent_name)
                
                # Rate limiting
                await asyncio.sleep(2)
            else:
                print(f"No agent found for issue #{issue['number']}")
        
        print("\n" + "="*60)
        print("COORDINATION COMPLETE")
        print("="*60)
    
    async def monitor_mode(self):
        """Continuously monitor for new issues"""
        print("Starting monitor mode - checking every 30 seconds")
        
        while True:
            await self.coordinate_all_issues()
            print("\nWaiting 30 seconds before next check...")
            await asyncio.sleep(30)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Agent Issue Coordinator')
    parser.add_argument('--monitor', action='store_true', 
                       help='Run in continuous monitoring mode')
    parser.add_argument('--once', action='store_true',
                       help='Process all issues once and exit')
    args = parser.parse_args()
    
    coordinator = AgentIssueCoordinator()
    
    if args.monitor:
        await coordinator.monitor_mode()
    else:
        await coordinator.coordinate_all_issues()

if __name__ == "__main__":
    asyncio.run(main())