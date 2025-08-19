#!/usr/bin/env python3
"""
Update Agent Status Tracker with Critical Dashboard Agent
"""

import json
from datetime import datetime

def update_status_tracker():
    """Add critical dashboard agent to status tracker"""
    
    # Read current status
    with open('agent_status_tracker.json', 'r') as f:
        status = json.load(f)
    
    # Add critical dashboard agent
    status['agent_status']['GPT4-Dashboard-Agent'] = {
        'status': 'critical_assigned',
        'priority': 'P0-CRITICAL-URGENT',
        'estimated_effort': '5-8 hours',
        'progress': 0,
        'tasks_completed': 0,
        'tasks_total': 4,
        'blocking_issue': True,
        'user_reported': True,
        'issue_type': 'dashboard_broken'
    }
    
    status['total_agents'] = 6
    status['overall_progress']['critical_issues'] = 1
    status['last_updated'] = datetime.now().isoformat()
    
    # Save updated status
    with open('agent_status_tracker.json', 'w') as f:
        json.dump(status, f, indent=2)
    
    print('AGENT STATUS TRACKER UPDATED')
    print('Total agents: 6 (5 original + 1 critical dashboard agent)')
    print('Critical issues: 1 (dashboard tab/data loading)')

if __name__ == "__main__":
    update_status_tracker()
