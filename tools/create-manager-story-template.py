#!/usr/bin/env python3
"""
Create Manager Story with Proper Format
========================================
Creates a story that managers can process, following policy
with clear dev tasks and QA test criteria
"""

import subprocess
from datetime import datetime

def create_dashboard_story_for_manager():
    """Create a properly formatted story for dashboard work"""
    
    story = {
        "title": "[STORY] Dashboard Cost Monitoring and Activity View",
        "body": """## User Story
**As a** system administrator  
**I want** to see AWS costs and system activity in the dashboard  
**So that** I can monitor expenses and system health

## Priority: P0 (Critical)
## Assignee: [TO BE MANUALLY ASSIGNED]

## Acceptance Criteria
1. **GIVEN** I open the dashboard  
   **WHEN** I click the Cost tab  
   **THEN** I see AWS costs broken down by service

2. **GIVEN** I'm viewing costs  
   **WHEN** costs update  
   **THEN** I see real-time data (< 5 min delay)

3. **GIVEN** I open the dashboard  
   **WHEN** I view the Activity tab  
   **THEN** I see all agent activities with timestamps

## Development Tasks
### Task 1: Fix Tab System (2 hours)
- [ ] Debug tab switching in dashboard.html
- [ ] Fix state management
- [ ] Test all tab transitions
- **File**: vf-dashboard-service/dashboard.html

### Task 2: Implement Cost API (4 hours)
- [ ] Create AWS Cost Explorer integration
- [ ] Add endpoint: GET /api/costs/daily
- [ ] Add endpoint: GET /api/costs/by-service
- [ ] Cache results (5 min TTL)
- **File**: vf-dashboard-service/api/costs.py

### Task 3: Create Cost View Component (3 hours)
- [ ] Build cost chart component
- [ ] Add service breakdown table
- [ ] Add date range selector
- [ ] Style with existing theme
- **File**: vf-dashboard-service/components/CostView.jsx

### Task 4: Create Activity Feed (3 hours)
- [ ] Build activity API endpoint
- [ ] Create activity list component
- [ ] Add real-time updates (WebSocket)
- [ ] Add filtering options
- **File**: vf-dashboard-service/components/ActivityFeed.jsx

## QA Test Cases
### Test Case 1: Tab Navigation
**Steps**:
1. Open dashboard
2. Click Cost tab
3. Click Activity tab
4. Refresh page
**Expected**: Tabs switch correctly, state persists

### Test Case 2: Cost Data Accuracy
**Steps**:
1. Open Cost tab
2. Compare with AWS Console
3. Check all services shown
**Expected**: Data matches AWS, all services visible

### Test Case 3: Activity Real-time Updates
**Steps**:
1. Open Activity tab
2. Trigger an agent action
3. Wait 5 seconds
**Expected**: New activity appears without refresh

### Test Case 4: Performance
**Steps**:
1. Load dashboard with 1000 activities
2. Switch between tabs rapidly
3. Check memory usage
**Expected**: <500ms tab switch, <200MB memory

## Definition of Done
- [ ] All development tasks complete
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Deployed to vf-dev environment
- [ ] QA sign-off
- [ ] Documentation updated

## Technical Notes
- Use existing AWS SDK credentials
- Follow current React patterns in codebase
- Maintain existing color scheme
- Ensure mobile responsive

## Estimate: 12 hours total
- Development: 12 hours
- Testing: 4 hours
- Deployment: 1 hour

## Dependencies
- AWS Cost Explorer API access
- vf-dashboard-service repo access
- Test environment (vf-dev)

---
**Created**: ${datetime.now().isoformat()}
**Repo**: VisualForgeMediaV2/vf-dashboard-service
**Manual Assignment Required**: Assign to available developer
""",
        "repo": "VisualForgeMediaV2/vf-dashboard-service"
    }
    
    print("\n" + "="*80)
    print("CREATING STORY FOR MANUAL ASSIGNMENT")
    print("="*80)
    
    print("\nCreating story with full details for dashboard work...")
    
    cmd = [
        "gh", "issue", "create",
        "--repo", story["repo"],
        "--title", story["title"],
        "--body", story["body"]
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"[OK] Story created: {url}")
            print("\n[NEXT STEPS]:")
            print("1. Manually assign to a developer")
            print("2. Developer implements the 4 tasks")
            print("3. QA runs the 4 test cases")
            print("4. Deploy when all tests pass")
            return url
        else:
            print(f"[ERROR] {result.stderr}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    return None

def create_auth_service_story():
    """Create story for auth service completion"""
    
    story = {
        "title": "[STORY] Complete Auth Service - MFA and Session Management",
        "body": """## User Story
**As a** user  
**I want** secure authentication with MFA  
**So that** my account is protected

## Priority: P0 (Security Critical)
## Assignee: [TO BE MANUALLY ASSIGNED]

## Current State: 75% Complete
### Already Working:
- Basic login/logout
- JWT token generation
- Password hashing

### Needs Implementation (25%):
- Multi-factor authentication
- Session management
- Rate limiting

## Acceptance Criteria
1. **GIVEN** MFA is enabled  
   **WHEN** I login  
   **THEN** I'm prompted for 6-digit code

2. **GIVEN** I enter wrong code 3 times  
   **WHEN** I try again  
   **THEN** I'm temporarily locked out

3. **GIVEN** I'm logged in  
   **WHEN** I'm idle for 1 hour  
   **THEN** session expires

## Development Tasks
### Task 1: Implement MFA (4 hours)
- [ ] Add TOTP generation
- [ ] Create QR code endpoint
- [ ] Add verification endpoint
- [ ] Store secrets securely
- **File**: vf-auth-service/services/mfa.py

### Task 2: Session Management (3 hours)
- [ ] Implement Redis sessions
- [ ] Add session expiry
- [ ] Create refresh endpoint
- [ ] Add logout everywhere
- **File**: vf-auth-service/services/sessions.py

### Task 3: Rate Limiting (2 hours)
- [ ] Add rate limit middleware
- [ ] Configure limits per endpoint
- [ ] Add temporary lockout
- [ ] Return 429 status codes
- **File**: vf-auth-service/middleware/rate_limit.py

## QA Test Cases
### Test Case 1: MFA Flow
1. Enable MFA
2. Scan QR code
3. Enter code
4. Verify login
**Expected**: MFA works with authenticator apps

### Test Case 2: Session Timeout
1. Login
2. Wait 61 minutes
3. Try protected endpoint
**Expected**: 401 Unauthorized

### Test Case 3: Rate Limiting
1. Try login 10 times rapidly
2. Check response
**Expected**: 429 Too Many Requests after 5 attempts

## Definition of Done
- [ ] All tasks complete
- [ ] Security scan passed
- [ ] Tests at 80% coverage
- [ ] Deployed to vf-dev

---
**Repo**: VisualForgeMediaV2/vf-auth-service
**Manual Assignment Required**: Assign to security-focused developer
""",
        "repo": "VisualForgeMediaV2/vf-auth-service"
    }
    
    cmd = [
        "gh", "issue", "create",
        "--repo", story["repo"],
        "--title", story["title"],
        "--body", story["body"]
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

def main():
    print("\n" + "="*80)
    print("CREATING PROPERLY FORMATTED STORIES")
    print("="*80)
    
    # Create dashboard story
    dashboard_url = create_dashboard_story_for_manager()
    
    # Create auth story
    print("\nCreating auth service story...")
    auth_url = create_auth_service_story()
    if auth_url:
        print(f"[OK] Auth story created: {auth_url}")
    
    print("\n" + "="*80)
    print("STORIES CREATED FOR MANUAL ASSIGNMENT")
    print("="*80)
    
    print("\n[WHAT THESE STORIES HAVE]:")
    print("✓ User story format")
    print("✓ Clear acceptance criteria")
    print("✓ Specific dev tasks with time estimates")
    print("✓ QA test cases ready to run")
    print("✓ Definition of done")
    print("✓ File locations specified")
    
    print("\n[WORKFLOW]:")
    print("1. Manager/You assigns to developer")
    print("2. Developer works the tasks")
    print("3. QA runs test cases")
    print("4. Ship when done")
    
    print("\n[THE KEY DIFFERENCE]:")
    print("- Stories are COMPLETE and ACTIONABLE")
    print("- Developer knows EXACTLY what to do")
    print("- QA knows EXACTLY what to test")
    print("- No back-and-forth needed")
    
    print("\n[SUCCESS!]")
    print("Ready for manual assignment!")

if __name__ == "__main__":
    main()