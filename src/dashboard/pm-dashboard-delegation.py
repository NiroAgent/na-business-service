#!/usr/bin/env python3
"""
PM Dashboard Delegation System
==============================
Delegates dashboard improvements to another PM including:
- Tab system fixes
- Cost monitoring view
- Kill switch functionality
- All legacy dashboard components
"""

import subprocess
import json
from datetime import datetime

def create_dashboard_pm_issue():
    """Create PM delegation issue for dashboard improvements"""
    
    issue = {
        "title": "[PM-Dashboard] Complete Dashboard Implementation with All Views",
        "body": """## Dashboard PM Delegation Task

### Objective
Take ownership of the dashboard implementation, fixing the tab system and integrating all components from the old dashboard including cost monitoring and kill switch functionality.

### Current Issues
1. **Tab System Not Working**
   - Tabs are not switching properly
   - Content not loading in tabs
   - Active tab state not maintained

2. **Missing Components from Old Dashboard**
   - Cost monitoring view
   - Kill switch functionality
   - Performance metrics
   - Resource utilization graphs
   - Alert management panel
   - System health indicators

### Required Dashboard Views

#### 1. Main Dashboard Tab
- Agent status cards (14 agents)
- Real-time activity feed
- Success rate metrics
- Issue processing counter

#### 2. Cost Monitoring Tab
- **AWS Service Costs**
  - Lambda execution costs
  - Fargate container costs
  - EC2 instance costs
  - Storage costs (S3, EBS)
  - API Gateway costs
  - CloudWatch costs

- **Cost Breakdowns**
  - Per agent costs
  - Daily/weekly/monthly trends
  - Cost optimization recommendations
  - Budget alerts and thresholds
  - Forecasting next month's costs

#### 3. Kill Switch Tab
- **Emergency Controls**
  - Master kill switch (stop all agents)
  - Individual agent kill switches
  - Service-level kill switches
  - Batch job termination
  
- **Safety Features**
  - Confirmation dialogs
  - Audit logging
  - Rollback capability
  - Graceful shutdown procedures

#### 4. Performance Tab
- **Agent Performance**
  - Processing times per agent
  - Success/failure rates
  - Queue depths
  - Memory usage
  - CPU utilization

- **System Performance**
  - API response times
  - Database query performance
  - Network latency
  - Error rates

#### 5. Resource Utilization Tab
- **Infrastructure Metrics**
  - Container usage
  - Lambda concurrency
  - Database connections
  - Queue sizes
  - Cache hit rates

#### 6. Alerts & Monitoring Tab
- **Alert Management**
  - Active alerts list
  - Alert history
  - Alert configuration
  - Notification settings
  - Escalation policies

### Technical Requirements

#### Frontend Implementation
```javascript
// Tab System Fix
class TabManager {
    constructor() {
        this.tabs = ['main', 'costs', 'killswitch', 'performance', 'resources', 'alerts'];
        this.activeTab = 'main';
    }
    
    switchTab(tabId) {
        // Hide all content
        this.tabs.forEach(tab => {
            document.getElementById(`${tab}-content`).style.display = 'none';
            document.getElementById(`${tab}-tab`).classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(`${tabId}-content`).style.display = 'block';
        document.getElementById(`${tabId}-tab`).classList.add('active');
        this.activeTab = tabId;
        
        // Load tab-specific data
        this.loadTabData(tabId);
    }
    
    loadTabData(tabId) {
        switch(tabId) {
            case 'costs':
                this.loadCostData();
                break;
            case 'killswitch':
                this.loadKillSwitchControls();
                break;
            // ... other cases
        }
    }
}
```

#### Cost Monitoring Implementation
```javascript
// Cost Monitoring Module
class CostMonitor {
    async fetchCosts() {
        const response = await fetch('/api/costs');
        return response.json();
    }
    
    calculateTrends(data) {
        // Calculate daily, weekly, monthly trends
    }
    
    renderCostCharts(data) {
        // Use Chart.js or D3.js for visualization
    }
    
    setupBudgetAlerts(thresholds) {
        // Configure cost threshold alerts
    }
}
```

#### Kill Switch Implementation
```javascript
// Kill Switch Controller
class KillSwitch {
    async emergencyStop(target) {
        if (!confirm(`Stop ${target}? This action cannot be undone immediately.`)) {
            return;
        }
        
        // Log the action
        await this.logKillSwitch(target);
        
        // Execute kill command
        const response = await fetch('/api/kill', {
            method: 'POST',
            body: JSON.stringify({ target, graceful: true })
        });
        
        return response.json();
    }
    
    async stopAllAgents() {
        // Master kill switch
    }
    
    async stopAgent(agentId) {
        // Individual agent kill
    }
}
```

### Acceptance Criteria

1. **Tab System**
   - GIVEN the dashboard with multiple tabs
   - WHEN user clicks on any tab
   - THEN the corresponding content displays without errors

2. **Cost Monitoring**
   - GIVEN the cost monitoring view
   - WHEN accessed
   - THEN displays real-time AWS costs with breakdowns and trends

3. **Kill Switch**
   - GIVEN the kill switch controls
   - WHEN activated with confirmation
   - THEN stops the specified agents/services gracefully

4. **Performance Metrics**
   - GIVEN the performance tab
   - WHEN viewed
   - THEN shows real-time metrics with <5 second refresh

5. **All Legacy Components**
   - GIVEN the new dashboard
   - WHEN compared to old dashboard
   - THEN contains all previous functionality plus improvements

### Tasks for Developer Agent

1. **Fix Tab System** (Priority: P0)
   - Debug current tab switching issues
   - Implement proper state management
   - Add URL routing for tabs
   - Ensure data persistence between tab switches

2. **Implement Cost Monitoring** (Priority: P0)
   - Create AWS Cost Explorer integration
   - Build cost calculation engine
   - Design cost visualization charts
   - Add budget alert system

3. **Build Kill Switch** (Priority: P0)
   - Create emergency stop API endpoints
   - Implement confirmation dialogs
   - Add audit logging
   - Build graceful shutdown procedures

4. **Add Missing Views** (Priority: P1)
   - Performance metrics dashboard
   - Resource utilization graphs
   - Alert management panel
   - System health indicators

5. **Testing** (Priority: P1)
   - Unit tests for all components
   - Integration tests for API calls
   - E2E tests for user workflows
   - Load testing for real-time updates

### Tasks for DevOps Agent

1. **Cost API Setup**
   - Configure AWS Cost Explorer API access
   - Set up cost data aggregation
   - Implement caching for cost data

2. **Kill Switch Infrastructure**
   - Create Lambda functions for emergency stops
   - Set up IAM roles for termination permissions
   - Implement circuit breakers

3. **Monitoring Setup**
   - CloudWatch dashboard integration
   - Metrics collection pipeline
   - Alert notification system

### Tasks for QA Agent

1. **Test Tab Functionality**
   - Verify all tabs load correctly
   - Test data persistence
   - Check responsive behavior

2. **Test Cost Monitoring**
   - Validate cost calculations
   - Test threshold alerts
   - Verify data accuracy

3. **Test Kill Switch**
   - Confirm safety mechanisms
   - Test graceful shutdowns
   - Verify audit logging

### Definition of Done

- [ ] All tabs functioning correctly
- [ ] Cost monitoring displaying real-time data
- [ ] Kill switch operational with safety measures
- [ ] All legacy dashboard components integrated
- [ ] Performance metrics updating in real-time
- [ ] Tests passing with >90% coverage
- [ ] Deployed and accessible via web
- [ ] Documentation complete

### Assigned PM
**ai-project-manager-agent-2** (Dashboard Specialist)

### Priority: P0 (Critical)
### Estimated Effort: 40 hours
### Deadline: End of current sprint

### Notes
- Reference old dashboard at: [legacy-dashboard-url]
- Use existing API endpoints where available
- Ensure mobile responsiveness
- Implement dark mode support
- Add export functionality for cost reports
""",
        "labels": ["dashboard", "priority/P0", "pm-delegation", "cost-monitoring", "kill-switch"],
        "assignee": "ai-project-manager-agent"
    }
    
    # Create the issue
    repo = "NiroAgentV2/business-operations"
    
    print("\n" + "="*80)
    print("CREATING DASHBOARD PM DELEGATION ISSUE")
    print("="*80)
    
    print(f"\nCreating: {issue['title']}")
    
    cmd = [
        "gh", "issue", "create",
        "--repo", repo,
        "--title", issue["title"],
        "--body", issue["body"]
    ]
    
    # Add labels
    for label in issue.get("labels", []):
        cmd.extend(["--label", label])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"  [OK] Created: {url}")
            return url
        else:
            print(f"  [INFO] May already exist or error: {result.stderr[:100]}")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    return None

def main():
    """Main entry point"""
    url = create_dashboard_pm_issue()
    
    print("\n" + "="*80)
    print("DASHBOARD PM DELEGATION COMPLETE")
    print("="*80)
    
    print("\n[NEXT STEPS]:")
    print("1. Dashboard PM will review current implementation")
    print("2. Fix tab system issues")
    print("3. Integrate cost monitoring view")
    print("4. Implement kill switch functionality")
    print("5. Add all legacy dashboard components")
    print("6. Deploy complete dashboard with all features")
    
    print("\n[INFO] Dashboard PM now has clear requirements for full implementation!")

if __name__ == "__main__":
    main()