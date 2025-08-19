#!/usr/bin/env python3
"""
Dashboard Critical Fix Agent Assignment
Creates urgent assignment for dashboard tab switching and data loading issues + Playwright tests
"""

import json
import time
from datetime import datetime
import os

def create_dashboard_agent_assignment():
    """Create critical dashboard fix assignment"""
    
    print("🚨 CREATING CRITICAL DASHBOARD AGENT ASSIGNMENT")
    print("=" * 60)
    
    # Ensure directories exist
    os.makedirs('agent_assignments', exist_ok=True)
    os.makedirs('communication_messages', exist_ok=True)
    os.makedirs('work_queue', exist_ok=True)
    
    # Dashboard agent assignment
    dashboard_assignment = {
        'agent_id': 'GPT4-Dashboard-Agent',
        'priority': 'P0-CRITICAL-URGENT',
        'title': 'Dashboard Critical Fixes + Playwright Testing',
        'description': 'Fix dashboard tab switching and data loading issues, implement Playwright test suite',
        'urgency': 'IMMEDIATE',
        'blocking_issue': True,
        'tasks': [
            {
                'task': 'Fix Dashboard Tab Switching',
                'file': 'comprehensive-tabbed-dashboard.py',
                'details': 'Debug and fix tab navigation - tabs not clickable, investigate JavaScript issues',
                'estimated_effort': '1-2 hours',
                'priority': 'P0-BLOCKING'
            },
            {
                'task': 'Fix Data Loading Issues', 
                'file': 'comprehensive-tabbed-dashboard.py',
                'details': 'Debug data not loading in dashboard, check WebSocket connections and API endpoints',
                'estimated_effort': '1-2 hours',
                'priority': 'P0-BLOCKING'
            },
            {
                'task': 'Implement Playwright Test Suite',
                'file': 'tests/dashboard_playwright_tests.py',
                'details': 'Create comprehensive Playwright tests for tab switching, data loading, and UI interactions',
                'estimated_effort': '2-3 hours',
                'priority': 'P0-CRITICAL'
            },
            {
                'task': 'Dashboard Health Monitoring',
                'file': 'dashboard_health_checker.py', 
                'details': 'Create automated health checks for dashboard functionality',
                'estimated_effort': '1 hour',
                'priority': 'P1-HIGH'
            }
        ],
        'deliverables': [
            'Working dashboard with functional tab switching',
            'Data loading properly across all tabs',
            'Comprehensive Playwright test suite',
            'Automated dashboard health monitoring',
            'Bug fix documentation and test coverage'
        ],
        'success_criteria': [
            'All dashboard tabs are clickable and functional',
            'Data loads properly in all sections',
            'Playwright tests cover all critical user flows',
            'Dashboard passes all automated health checks',
            'Real-time monitoring works correctly'
        ],
        'current_issues': [
            'Tabs not clickable - JavaScript event handling issue',
            'No data loading - potential WebSocket or API connection problem',
            'Dashboard monitoring critical for agent coordination',
            'Testing infrastructure needed for reliability'
        ],
        'context': {
            'dashboard_url': 'http://localhost:5003',
            'current_status': 'BROKEN - tabs and data loading not working',
            'impact': 'Blocking agent coordination monitoring',
            'backup_file': 'comprehensive-tabbed-dashboard-backup.py'
        }
    }
    
    # Save assignment file
    assignment_file = "agent_assignments/GPT4-Dashboard-Agent_assignment.json"
    with open(assignment_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_assignment, f, indent=2)
    
    # Create detailed instructions
    instructions = generate_dashboard_instructions(dashboard_assignment)
    instructions_file = "agent_assignments/GPT4-Dashboard-Agent_INSTRUCTIONS.md"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    # Register in communication hub
    comm_message = {
        'message_type': 'critical_agent_assignment',
        'from_agent': 'Dashboard-Crisis-Coordinator',
        'to_agent': 'GPT4-Dashboard-Agent',
        'urgency': 'CRITICAL',
        'assignment_details': {
            'title': dashboard_assignment['title'],
            'priority': dashboard_assignment['priority'],
            'blocking_issue': True,
            'current_problem': 'Dashboard tabs not working, no data loading',
            'impact': 'Cannot monitor agent coordination system',
            'estimated_fix_time': '5-8 hours total'
        },
        'context': {
            'dashboard_broken': True,
            'user_reported': True,
            'blocking_monitoring': True,
            'playwright_testing_required': True,
            'assignment_file': instructions_file
        },
        'timestamp': datetime.now().isoformat(),
        'status': 'critical_assignment'
    }
    
    comm_file = f"communication_messages/critical_dashboard_{int(time.time())}.json"
    with open(comm_file, 'w', encoding='utf-8') as f:
        json.dump(comm_message, f, indent=2)
    
    # Create work queue item
    work_item = {
        'work_type': 'critical_bug_fix',
        'title': 'CRITICAL: Dashboard Tab Switching & Data Loading Fix',
        'description': 'Dashboard completely broken - tabs not clickable, no data loading',
        'assigned_to': 'GPT4-Dashboard-Agent',
        'priority': 'P0-CRITICAL-URGENT',
        'urgency': 'IMMEDIATE',
        'blocking': True,
        'tasks': dashboard_assignment['tasks'],
        'impact': 'Blocking agent coordination monitoring',
        'user_affected': True,
        'estimated_total_effort': '5-8 hours',
        'created_at': datetime.now().isoformat(),
        'status': 'critical_assigned',
        'requires_immediate_attention': True
    }
    
    work_file = f"work_queue/CRITICAL_dashboard_fix_{int(time.time())}.json"
    with open(work_file, 'w', encoding='utf-8') as f:
        json.dump(work_item, f, indent=2)
    
    print("🚨 CRITICAL ASSIGNMENT CREATED")
    print(f"   Assignment: {assignment_file}")
    print(f"   Instructions: {instructions_file}")
    print(f"   Communication: {comm_file}")
    print(f"   Work Queue: {work_file}")
    
    return dashboard_assignment

def generate_dashboard_instructions(assignment):
    """Generate detailed instructions for dashboard agent"""
    
    return f"""# 🚨 CRITICAL: Dashboard Fixes + Playwright Testing

**Agent:** GPT4-Dashboard-Agent  
**Priority:** P0-CRITICAL-URGENT  
**Assigned:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## 🔥 CRITICAL ISSUES REPORTED

### **User Problem:**
- ❌ **Dashboard tabs not clickable** - cannot switch between tabs
- ❌ **No data loading** - dashboard shows no information
- ❌ **Blocking agent monitoring** - cannot track coordination system

### **Impact:**
- **BLOCKS agent coordination monitoring**
- **PREVENTS real-time progress tracking** 
- **USER CANNOT USE DASHBOARD** at http://localhost:5003

## 🛠️ IMMEDIATE TASKS

### Task 1: Fix Tab Switching (P0-BLOCKING)
**File:** `comprehensive-tabbed-dashboard.py`  
**Problem:** Tabs are not clickable - likely JavaScript event handling issue  
**Debug Steps:**
1. Check JavaScript showTab() function in HTML template
2. Verify event listeners are properly attached
3. Test DOM element selection and event binding
4. Fix any JavaScript syntax or logic errors

### Task 2: Fix Data Loading (P0-BLOCKING)  
**File:** `comprehensive-tabbed-dashboard.py`  
**Problem:** No data appearing in dashboard sections  
**Debug Steps:**
1. Check WebSocket connections (/socket.io)
2. Verify API endpoints are responding
3. Test data retrieval functions (get_service_status, etc.)
4. Check template data binding and rendering

### Task 3: Playwright Test Suite (P0-CRITICAL)
**File:** `tests/dashboard_playwright_tests.py`  
**Requirements:**
- Install Playwright: `pip install playwright`
- Run setup: `playwright install`
- Test tab switching functionality
- Test data loading in all tabs
- Test real-time updates
- Test WebSocket connections
- Test responsive design

### Task 4: Health Monitoring (P1-HIGH)
**File:** `dashboard_health_checker.py`  
**Create:** Automated checks for dashboard functionality

## 🔍 DEBUGGING APPROACH

### 1. **Immediate Diagnosis:**
```bash
# Check if dashboard is running
curl http://localhost:5003
# Check console errors in browser
# Inspect network tab for failed requests
```

### 2. **JavaScript Tab Fix:**
- Look for showTab() function issues
- Check event.target vs this binding
- Verify DOM element IDs match JavaScript selectors

### 3. **Data Loading Fix:**
- Test individual API endpoints
- Check WebSocket connection status
- Verify data sources are available
- Test template rendering

### 4. **Playwright Testing:**
```python
# Example test structure
import pytest
from playwright.async_api import async_playwright

async def test_dashboard_tabs():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:5003')
        await page.click('#agents-tab')
        await page.wait_for_selector('#agents-content')
        await browser.close()
```

## 📁 FILES TO EXAMINE

### **Primary Files:**
- `comprehensive-tabbed-dashboard.py` - Main dashboard application
- `comprehensive-tabbed-dashboard-backup.py` - Backup copy for comparison

### **Related Files:**
- `service-progress-monitor.py` - Data source for monitoring
- `communication_messages/` - Data for agent coordination
- `work_queue/` - Data for task tracking

### **Test Files to Create:**
- `tests/dashboard_playwright_tests.py` - Main test suite
- `dashboard_health_checker.py` - Health monitoring
- `package.json` - Playwright dependencies (if needed)

## 🎯 SUCCESS CRITERIA

### **Immediate Success:**
- [ ] Dashboard tabs are clickable and switch properly
- [ ] Data loads and displays in all sections
- [ ] Real-time updates work correctly
- [ ] No JavaScript errors in browser console

### **Testing Success:**
- [ ] Playwright tests cover all critical workflows
- [ ] All tests pass consistently  
- [ ] Test suite runs automatically
- [ ] Health monitoring detects issues

### **Documentation Success:**
- [ ] Bug fixes documented
- [ ] Test coverage documented
- [ ] Dashboard usage instructions updated

## 🚀 IMMEDIATE ACTIONS

1. **FIRST:** Check dashboard at http://localhost:5003 and identify specific errors
2. **DEBUG:** Use browser developer tools to find JavaScript/network issues
3. **FIX:** Implement tab switching and data loading fixes
4. **TEST:** Create Playwright test suite to prevent regression
5. **MONITOR:** Set up health checking for ongoing reliability

## ⚡ ENVIRONMENT READY

**Working Directory:** `E:/Projects/`  
**Dashboard URL:** `http://localhost:5003`  
**Python Environment:** Configured  
**Backup Available:** `comprehensive-tabbed-dashboard-backup.py`

## 🎯 CRITICAL SUCCESS

**This is a P0-CRITICAL issue blocking our agent coordination system!**

**Fix the dashboard immediately so we can monitor our 5-agent development coordination!** 🚨

**Start with tab switching fix, then data loading, then Playwright tests!** 🚀
"""

def main():
    print("🚨 DASHBOARD CRITICAL ISSUE COORDINATOR")
    print("=" * 50)
    print("Creating urgent assignment for dashboard fixes + Playwright testing")
    print()
    
    # Create the assignment
    assignment = create_dashboard_agent_assignment()
    
    print()
    print("✅ CRITICAL DASHBOARD ASSIGNMENT CREATED")
    print()
    print("🎯 Assignment Summary:")
    print(f"   Agent: {assignment['agent_id']}")
    print(f"   Priority: {assignment['priority']}")
    print(f"   Tasks: {len(assignment['tasks'])}")
    print("   Issues: Tab switching broken, no data loading")
    print("   Testing: Playwright test suite required")
    print()
    print("📋 Next Steps:")
    print("1. GPT4-Dashboard-Agent reads INSTRUCTIONS.md")
    print("2. Debug and fix tab switching issues")
    print("3. Fix data loading problems")
    print("4. Implement comprehensive Playwright tests")
    print("5. Set up dashboard health monitoring")
    print()
    print("🚨 CRITICAL: Dashboard fix needed for agent coordination monitoring!")

if __name__ == "__main__":
    main()
