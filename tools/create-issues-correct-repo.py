#!/usr/bin/env python3
"""
Create Issues in Correct Repository
====================================
Creates all the delegated issues in VisualForgeMediaV2/business-operations
"""

import subprocess
import json
from datetime import datetime

def create_all_issues():
    """Create all the delegated issues in the correct repository"""
    
    repo = "VisualForgeMediaV2/business-operations"
    
    issues_to_create = [
        {
            "title": "[Manager] Coordinate Full System Migration to WSL/Linux Environment",
            "body": """## Management Directive: System Migration Project

### Executive Summary
Our autonomous business system is experiencing critical Unicode encoding failures on Windows. Coordinate migration to WSL/Linux.

### Priority: P0 (CRITICAL)
### Deadline: 8 hours

### Team Assembly & Delegation Required:
- IT Infrastructure Agent - WSL setup
- DevOps Agent - Service configuration  
- QA Agent - Migration validation
- Developer Agent - Code adaptation

### Success Criteria
- All agents running on Linux
- Unicode fully functional
- Zero data loss
- Performance improved""",
            "labels": ["management", "migration", "priority-p0"]
        },
        {
            "title": "[Manager] Organize and Standardize All Documentation",
            "body": """## Documentation Cleanup Project

### Current Problem
- 300+ random documents scattered
- No clear structure
- Difficult to maintain

### Target State
- 7 documents per service
- 8 documents per repository root
- Total: ~99 organized documents

### Standard Documents Per Service:
1. README.md
2. API.md
3. ARCHITECTURE.md (DAD)
4. DEPLOYMENT.md
5. TESTING.md
6. TROUBLESHOOTING.md
7. CHANGELOG.md

### Deadline: 2 weeks""",
            "labels": ["documentation", "cleanup", "priority-p0"]
        },
        {
            "title": "[PM-Dashboard] Complete Dashboard Implementation with All Views",
            "body": """## Dashboard Completion Task

### Current Issues
- Tab system not working
- Missing cost monitoring view
- Missing kill switch functionality

### Required Implementation:
1. Fix tab switching
2. Add cost monitoring with AWS Cost Explorer
3. Implement emergency kill switch
4. Add all legacy dashboard components
5. Performance metrics view
6. Resource utilization graphs

### Priority: P0
### Estimate: 40 hours""",
            "labels": ["dashboard", "frontend", "priority-p0"]
        },
        {
            "title": "[PM-Chat] Test Voice/Text Chat Interface Across All Platforms",
            "body": """## Chat Interface Testing Project

### Platforms to Test:
- Web (all browsers)
- Mobile (iOS/Android)
- Desktop (Windows/macOS/Linux)

### Test Coverage Required:
- Text messaging functionality
- Voice recording/playback
- Cross-platform synchronization
- Performance under load
- Accessibility compliance

### Priority: P0
### Estimate: 60 hours""",
            "labels": ["testing", "chat", "cross-platform", "priority-p0"]
        },
        {
            "title": "[Architect] Review All Features/Stories Before Implementation",
            "body": """## Architectural Review Process

### Requirement
ALL stories must be reviewed by architect before implementation.

### Review Criteria:
- Microservices principles
- Security standards
- Performance requirements
- Cloud-native design
- API standards

### Enforcement:
- No implementation without approval
- Technical guidance required
- Standards compliance mandatory

### SLA: 4-hour review time""",
            "labels": ["architecture", "review", "standards", "priority-p0"]
        },
        {
            "title": "[QA-1] Test ns-auth Authentication Service",
            "body": """## Testing Task: ns-auth Service

### Service Status: 75% complete
### Environment: vf-dev

### Test Scope:
1. Functional testing (login, register, password reset)
2. Security testing (SQL injection, XSS, rate limiting)
3. Performance testing (100 concurrent users)
4. Integration testing (database, Redis, email)

### Deliverables:
- Test report
- Bug reports
- Performance metrics
- Security vulnerabilities

### Priority: P0""",
            "labels": ["testing", "qa", "ns-auth", "priority-p0"]
        },
        {
            "title": "[QA-2] Test Dashboard UI Cross-Browser",
            "body": """## Dashboard Testing Task

### Browsers: Chrome, Firefox, Safari, Edge
### Devices: Desktop, Tablet, Mobile

### Known Issues to Verify:
- Tab system broken
- Agent cards not updating
- WebSocket disconnections

### Test Coverage:
- Browser compatibility
- Responsive design
- Performance metrics
- Accessibility

### Priority: P0""",
            "labels": ["testing", "qa", "dashboard", "ui", "priority-p0"]
        },
        {
            "title": "[QA-3] Test Payment Service End-to-End",
            "body": """## Payment Service Testing

### CRITICAL: This service handles money!

### Test Requirements:
- Payment processing flow
- Subscription management
- Webhook handling
- Refund processing
- Security (PCI compliance)
- Performance under load

### Test with Stripe test cards
### Priority: P0 (Critical)""",
            "labels": ["testing", "qa", "payments", "critical", "priority-p0"]
        },
        {
            "title": "[QA-4] Test VisualForge Media Processing Services",
            "body": """## Media Processing Testing

### Services: vf-audio, vf-video, vf-image
### Status: 75% complete each

### Test Coverage:
- File upload (all formats)
- Processing pipeline
- CDN delivery
- Error handling
- Performance (large files)
- Bulk processing

### Priority: P1""",
            "labels": ["testing", "qa", "media", "visualforge", "priority-p1"]
        },
        {
            "title": "[Dev Guidelines] DO NOT Break Existing Code - Services 75% Complete",
            "body": """## CRITICAL DEVELOPER GUIDELINES

### Services are Already 75% Complete!

### DO NOT:
- Rewrite existing working code
- Change architecture without approval
- Delete functionality
- Modify database schemas

### DO:
- Fix bugs found by QA
- Complete remaining 25%
- Test before committing
- Preserve backward compatibility

### Workflow:
1. QA tests and finds bugs
2. Developers fix (not rewrite)
3. Complete missing features
4. QA retests

### Priority: P0 - MANDATORY""",
            "labels": ["guidelines", "developer", "critical", "priority-p0"]
        },
        {
            "title": "[Dev-1] Fix Dashboard Tab System",
            "body": """## Bug Fix: Dashboard Tabs Not Working

### Problem:
Tabs don't switch properly, content doesn't load

### Location:
File: dashboard.html
Lines: 150-250

### Required Fix:
- Hide all tabs before showing selected
- Maintain active state
- Persist selection in localStorage

### Priority: P0
### Estimate: 2 hours""",
            "labels": ["bug", "dashboard", "frontend", "priority-p0"]
        },
        {
            "title": "[Dev-2] Implement Cost Monitoring API",
            "body": """## Feature: AWS Cost Monitoring

### Requirements:
- Connect to AWS Cost Explorer
- Daily cost trends
- Service breakdown
- Cost forecasting
- Budget alerts

### API Endpoints:
- GET /api/costs/daily
- GET /api/costs/services
- GET /api/costs/forecast

### Priority: P0
### Estimate: 4 hours""",
            "labels": ["feature", "api", "backend", "priority-p0"]
        },
        {
            "title": "[Dev-3] Implement Emergency Kill Switch",
            "body": """## Critical Feature: Kill Switch

### Requirements:
- Stop all agents immediately
- Stop specific services
- Graceful shutdown option
- Audit logging
- Two-factor confirmation

### Safety Features:
- Confirmation dialogs
- Rollback capability
- Audit trail

### Priority: P0
### Estimate: 6 hours""",
            "labels": ["feature", "safety", "critical", "priority-p0"]
        }
    ]
    
    created_count = 0
    
    print("\n" + "="*80)
    print(f"CREATING ISSUES IN {repo}")
    print("="*80)
    
    for issue in issues_to_create:
        print(f"\nCreating: {issue['title'][:60]}...")
        
        # Prepare command
        cmd = [
            "gh", "issue", "create",
            "--repo", repo,
            "--title", issue["title"],
            "--body", issue["body"]
        ]
        
        # Add labels if they exist
        for label in issue.get("labels", []):
            cmd.extend(["--label", label])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                url = result.stdout.strip()
                print(f"  [OK] Created: {url}")
                created_count += 1
            else:
                error_msg = result.stderr.strip()
                if "already exists" in error_msg.lower():
                    print(f"  [SKIP] Already exists")
                else:
                    print(f"  [ERROR] {error_msg[:100]}")
        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] Command took too long")
        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
    
    print("\n" + "="*80)
    print("ISSUE CREATION COMPLETE")
    print("="*80)
    print(f"\nCreated {created_count} new issues in {repo}")
    
    # List all issues to verify
    print("\nVerifying issues in repository...")
    try:
        cmd = ["gh", "issue", "list", "--repo", repo, "--limit", "20", "--json", "number,title"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            issues = json.loads(result.stdout)
            print(f"Total issues in repo: {len(issues)}")
            print("\nRecent issues:")
            for issue in issues[:5]:
                print(f"  #{issue['number']}: {issue['title'][:60]}...")
    except Exception as e:
        print(f"Could not list issues: {e}")
    
    return created_count

def main():
    """Main entry point"""
    count = create_all_issues()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    print(f"\n[RESULT] Created {count} issues in VisualForgeMediaV2/business-operations")
    
    print("\n[NEXT STEPS]:")
    print("1. Managers coordinate their assigned projects")
    print("2. QA agents start testing existing code")
    print("3. Developers wait for bug reports")
    print("4. Architects review all stories")
    
    print("\n[VIEW ISSUES]:")
    print("https://github.com/VisualForgeMediaV2/business-operations/issues")
    
    print("\n[SUCCESS!]")
    print("Issues are now in the correct repository!")

if __name__ == "__main__":
    main()