#!/usr/bin/env python3
"""
Process Business Operations GitHub Issues
This script enables AI agents to process assigned issues from the business-operations repo
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
import argparse

def get_issue_details(issue_number):
    """Get details of a specific issue"""
    cmd = ["gh", "issue", "view", str(issue_number), 
           "--repo", "VisualForgeMediaV2/business-operations", 
           "--json", "title,body,labels,state,assignees"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting issue {issue_number}: {e}")
        return None

def process_issue(issue_number, agent_script):
    """Process an issue with the specified agent"""
    print(f"\nProcessing Issue #{issue_number} with {agent_script}")
    print("-" * 60)
    
    # Get issue details
    issue = get_issue_details(issue_number)
    if not issue:
        print(f"Could not retrieve issue #{issue_number}")
        return False
    
    print(f"Title: {issue['title']}")
    print(f"Labels: {', '.join([l['name'] for l in issue['labels']])}")
    
    # Check if agent script exists
    agent_path = Path(agent_script)
    if not agent_path.exists():
        print(f"Agent script not found: {agent_script}")
        return False
    
    # Import and run the agent
    try:
        # Add the script directory to path
        sys.path.insert(0, str(agent_path.parent))
        
        # Import the module
        module_name = agent_path.stem
        agent_module = __import__(module_name)
        
        # Check if the agent has a process_issue function
        if hasattr(agent_module, 'process_issue'):
            print(f"Running {module_name}.process_issue()")
            result = agent_module.process_issue(issue_number, issue)
            print(f"Agent completed: {result}")
            return result
        elif hasattr(agent_module, 'main'):
            print(f"Running {module_name}.main()")
            # Run the main function if available
            import asyncio
            if asyncio.iscoroutinefunction(agent_module.main):
                asyncio.run(agent_module.main())
            else:
                agent_module.main()
            return True
        else:
            print(f"Agent {module_name} doesn't have process_issue or main function")
            # Just import the module to run any top-level code
            print(f"Agent module {module_name} imported successfully")
            return True
            
    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Remove from path
        if str(agent_path.parent) in sys.path:
            sys.path.remove(str(agent_path.parent))

def update_issue_status(issue_number, status_message):
    """Update issue with status"""
    cmd = ["gh", "issue", "comment", str(issue_number),
           "--repo", "VisualForgeMediaV2/business-operations",
           "--body", status_message]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Updated issue #{issue_number} with status")
        return True
    except Exception as e:
        print(f"Error updating issue: {e}")
        return False

def main():
    """Main processing function"""
    parser = argparse.ArgumentParser(description='Process business operations issues')
    parser.add_argument('--issue', type=int, help='Specific issue number to process')
    parser.add_argument('--all', action='store_true', help='Process all open issues')
    args = parser.parse_args()
    
    # Mapping of issue types to agent scripts
    agent_mapping = {
        "operations/monitoring": "ai-operations-agent.py",
        "operations/optimization": "ai-operations-agent.py",
        "support/quality-assurance": "ai-support-agent.py",
        "analytics/reporting": "ai-analytics-agent.py",
        "security/compliance": "ai-security-agent.py",
        "success/user-research": "ai-customer-success-agent.py",
        "finance/analysis": "ai-finance-agent.py",
        "marketing/": "ai-marketing-agent.py",
        "sales/": "ai-sales-agent.py",
        "management/": "ai-project-manager-agent.py"
    }
    
    print("BUSINESS OPERATIONS ISSUE PROCESSOR")
    print("=" * 60)
    
    if args.issue:
        # Process specific issue
        issue = get_issue_details(args.issue)
        if issue:
            # Find appropriate agent based on labels
            agent_script = None
            for label in issue['labels']:
                label_name = label['name']
                for label_pattern, script in agent_mapping.items():
                    if label_pattern in label_name:
                        agent_script = script
                        break
                if agent_script:
                    break
            
            if agent_script:
                success = process_issue(args.issue, agent_script)
                if success:
                    status = f"[PROCESSED] Issue processed by {agent_script} at {datetime.now().isoformat()}"
                else:
                    status = f"[FAILED] Issue processing failed at {datetime.now().isoformat()}"
                update_issue_status(args.issue, status)
            else:
                print(f"No agent mapping found for issue #{args.issue}")
    
    elif args.all:
        # Process all open issues
        cmd = ["gh", "issue", "list", "--state", "open",
               "--repo", "VisualForgeMediaV2/business-operations",
               "--json", "number,labels", "--limit", "100"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            issues = json.loads(result.stdout)
            
            print(f"Found {len(issues)} open issues")
            
            for issue_data in issues:
                issue_number = issue_data['number']
                
                # Find appropriate agent
                agent_script = None
                for label in issue_data['labels']:
                    label_name = label['name']
                    for label_pattern, script in agent_mapping.items():
                        if label_pattern in label_name:
                            agent_script = script
                            break
                    if agent_script:
                        break
                
                if agent_script:
                    print(f"\nAssigning issue #{issue_number} to {agent_script}")
                    success = process_issue(issue_number, agent_script)
                    
                    if success:
                        status = f"[PROCESSED] Automatically processed by {agent_script}"
                    else:
                        status = f"[FAILED] Processing failed for {agent_script}"
                    
                    update_issue_status(issue_number, status)
                    time.sleep(2)  # Rate limiting
                else:
                    print(f"No agent for issue #{issue_number}")
                    
        except Exception as e:
            print(f"Error listing issues: {e}")
    
    else:
        print("Please specify --issue NUMBER or --all")
        print("\nCurrent open issues:")
        subprocess.run(["gh", "issue", "list", "--state", "open",
                       "--repo", "VisualForgeMediaV2/business-operations"])

if __name__ == "__main__":
    main()