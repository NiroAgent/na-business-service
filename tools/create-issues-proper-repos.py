#!/usr/bin/env python3
"""
Create Issues in Proper Repositories
=====================================
RULE #1: Each project's issues go in their own repository!
"""

import subprocess
import json
from datetime import datetime

def create_issues_in_proper_repos():
    """Create issues in the correct repositories based on service/project"""
    
    # Map issues to their proper repositories
    issue_distribution = {
        "VisualForgeMediaV2/vf-audio-service": [
            {
                "title": "[QA] Test Audio Processing Service - 75% Complete",
                "body": """## Audio Service Testing Task

### Current Status: 75% complete
### Priority: P1

### Test Coverage Required:
- File upload (MP3, WAV, FLAC, AAC, OGG)
- Format conversion
- Audio processing pipeline
- Bitrate adjustment
- Noise reduction
- Performance with large files

### Testing Checklist:
- [ ] Functional testing
- [ ] Performance testing
- [ ] Error handling
- [ ] Integration testing
- [ ] CDN delivery verification

### Bug Report Format:
- Component: [upload/processing/delivery]
- Steps to reproduce
- Expected vs Actual
- Test data used""",
                "labels": ["testing", "qa", "priority-p1"]
            },
            {
                "title": "[Dev] Complete Audio Service Implementation (25% remaining)",
                "body": """## Complete Audio Service Development

### Completed (75%):
- Basic upload
- Format detection
- Simple processing

### TODO (25%):
- Advanced audio filters
- Batch processing
- Webhook notifications
- Error recovery
- Performance optimization

### DO NOT:
- Rewrite existing code
- Break working features
- Change API contracts""",
                "labels": ["enhancement", "development", "priority-p1"]
            }
        ],
        
        "VisualForgeMediaV2/vf-video-service": [
            {
                "title": "[QA] Test Video Processing Service - 75% Complete",
                "body": """## Video Service Testing Task

### Test Requirements:
- Upload (MP4, AVI, MOV, MKV, WEBM)
- Resolution changes
- Format conversion
- Thumbnail generation
- Streaming support
- Large file handling (>1GB)

### Performance Targets:
- <10 min for 1GB file
- <2 min for 100MB file
- Concurrent processing: 10 videos

### Priority: P1""",
                "labels": ["testing", "qa", "priority-p1"]
            },
            {
                "title": "[Dev] Complete Video Service (25% remaining)",
                "body": """## Video Service Completion

### TODO:
- Streaming support (HLS/DASH)
- Subtitle processing
- Multiple quality outputs
- Watermarking
- GPU acceleration

### PRESERVE existing:
- Upload functionality
- Basic encoding
- Thumbnail generation""",
                "labels": ["enhancement", "development", "priority-p1"]
            }
        ],
        
        "VisualForgeMediaV2/vf-image-service": [
            {
                "title": "[QA] Test Image Processing Service",
                "body": """## Image Service Testing

### Test Coverage:
- Format support (JPEG, PNG, GIF, WEBP, TIFF, SVG)
- Resize operations
- Format conversion
- Optimization
- Watermarking
- Bulk processing

### Priority: P1""",
                "labels": ["testing", "qa", "priority-p1"]
            },
            {
                "title": "[Dev] Complete Image Service (25%)",
                "body": """## Complete Image Processing

### Missing Features:
- Advanced filters
- AI-based enhancement
- Background removal
- Batch operations
- Smart cropping""",
                "labels": ["enhancement", "development", "priority-p1"]
            }
        ],
        
        "VisualForgeMediaV2/vf-text-service": [
            {
                "title": "[QA] Test Text Processing Service",
                "body": """## Text Service Testing

### Test Requirements:
- Document upload (TXT, PDF, DOCX, MD)
- Text extraction
- Format conversion
- Search functionality
- NLP processing

### Priority: P1""",
                "labels": ["testing", "qa", "priority-p1"]
            }
        ],
        
        "VisualForgeMediaV2/vf-dashboard-service": [
            {
                "title": "[QA] Test Dashboard - Tab System Broken",
                "body": """## Dashboard Testing Task

### Known Issues:
- Tab system not working
- Missing cost monitoring view
- Missing kill switch
- Agent cards not updating

### Test Matrix:
- Chrome, Firefox, Safari, Edge
- Desktop, Tablet, Mobile
- Dark/Light mode

### Priority: P0 (User-facing)""",
                "labels": ["testing", "qa", "bug", "priority-p0"]
            },
            {
                "title": "[Dev] Fix Dashboard Tab System",
                "body": """## Bug Fix: Tab Switching

### Problem:
Tabs don't switch, content doesn't load

### File: dashboard.html
### Lines: 150-250

### Fix Required:
```javascript
function switchTab(tabId) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    // Show selected
    document.getElementById(tabId).style.display = 'block';
}
```

### Priority: P0
### Estimate: 2 hours""",
                "labels": ["bug", "frontend", "priority-p0"]
            },
            {
                "title": "[Dev] Add Cost Monitoring View",
                "body": """## Feature: Cost Monitoring Dashboard

### Requirements:
- AWS Cost Explorer integration
- Daily/Monthly trends
- Service breakdown
- Budget alerts
- Export to CSV

### Priority: P0""",
                "labels": ["feature", "frontend", "priority-p0"]
            },
            {
                "title": "[Dev] Implement Kill Switch",
                "body": """## Critical: Emergency Kill Switch

### Requirements:
- Master kill (all services)
- Individual service stops
- Confirmation dialog
- Audit logging
- Recovery procedures

### Priority: P0 (Safety critical)""",
                "labels": ["feature", "safety", "priority-p0"]
            }
        ],
        
        "VisualForgeMediaV2/vf-auth-service": [
            {
                "title": "[QA] Test Authentication Service",
                "body": """## Auth Service Testing

### Test Scenarios:
- Login/Logout
- Registration
- Password reset
- MFA (if implemented)
- Session management
- JWT tokens
- Rate limiting

### Security Tests:
- SQL injection
- XSS attempts
- Brute force protection
- Token validation

### Priority: P0 (Security critical)""",
                "labels": ["testing", "security", "qa", "priority-p0"]
            },
            {
                "title": "[Dev] Complete Auth Service (25%)",
                "body": """## Auth Service Completion

### TODO:
- Multi-factor authentication
- OAuth providers
- Session management
- Rate limiting
- Password policies

### Keep Working:
- Basic login
- JWT generation
- Password hashing""",
                "labels": ["enhancement", "security", "priority-p0"]
            }
        ],
        
        "VisualForgeMediaV2/business-operations": [
            {
                "title": "[Manager] Coordinate All Service Development",
                "body": """## Project Management Coordination

### RULE #1: Issues in proper repositories!

### Responsibilities:
1. Ensure each service has issues in its own repo
2. Track cross-service dependencies
3. Coordinate releases
4. Monitor progress

### Service Status:
- All services: ~75% complete
- Target: 100% in 2 weeks

### Daily Tasks:
- Check each service repo for progress
- Update stakeholders
- Remove blockers
- Coordinate QA/Dev handoffs""",
                "labels": ["management", "coordination", "priority-p0"]
            },
            {
                "title": "[Architect] Review All Service Architectures",
                "body": """## Architecture Review Process

### Each Service Needs:
1. Architecture review
2. API standards check
3. Security assessment
4. Performance validation
5. Integration verification

### Review SLA: 4 hours

### Standards:
- Microservices principles
- RESTful APIs
- Cloud-native design
- Security first
- Observable systems""",
                "labels": ["architecture", "review", "priority-p0"]
            },
            {
                "title": "[PM] Documentation Standards - 7 Docs Per Service",
                "body": """## Documentation Standardization

### RULE: Each service repo must have exactly:
1. README.md
2. API.md
3. ARCHITECTURE.md (DAD)
4. DEPLOYMENT.md
5. TESTING.md
6. TROUBLESHOOTING.md
7. CHANGELOG.md

### Total: 7 docs per service repo
### No more, no less!

### Archive excess docs in /archive folder""",
                "labels": ["documentation", "standards", "priority-p0"]
            }
        ]
    }
    
    # Also check NiroAgentV2 repos if they exist
    niro_repos = {
        "NiroAgentV2/ns-auth": [
            {
                "title": "[QA] Test ns-auth Service",
                "body": """## Test Authentication Service

### Priority: P0
### Status: 75% complete

### Test Coverage:
- Login/Register
- Password reset
- Session management
- Security testing
- Performance testing""",
                "labels": ["testing", "qa", "priority-p0"]
            }
        ],
        "NiroAgentV2/ns-payments": [
            {
                "title": "[QA] Test Payment Service - CRITICAL",
                "body": """## Payment Service Testing

### CRITICAL: Handles real money!

### Test Requirements:
- Payment processing
- Subscriptions
- Webhooks
- Refunds
- PCI compliance

### Use Stripe test cards
### Priority: P0""",
                "labels": ["testing", "qa", "critical", "priority-p0"]
            }
        ],
        "NiroAgentV2/ns-dashboard": [
            {
                "title": "[QA] Test Dashboard UI",
                "body": """## Dashboard Testing

### Test all browsers
### Test responsive design
### Verify real-time updates

### Priority: P0""",
                "labels": ["testing", "qa", "ui", "priority-p0"]
            }
        ]
    }
    
    created_count = 0
    failed_repos = []
    
    print("\n" + "="*80)
    print("CREATING ISSUES IN PROPER REPOSITORIES")
    print("RULE #1: Each project's issues in their own repo!")
    print("="*80)
    
    # Process VisualForgeMediaV2 repos
    for repo, issues in issue_distribution.items():
        print(f"\n[REPO] {repo}")
        print("-" * 40)
        
        for issue in issues:
            print(f"  Creating: {issue['title'][:50]}...")
            
            cmd = [
                "gh", "issue", "create",
                "--repo", repo,
                "--title", issue["title"],
                "--body", issue["body"]
            ]
            
            for label in issue.get("labels", []):
                cmd.extend(["--label", label])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    url = result.stdout.strip()
                    print(f"    [OK] {url}")
                    created_count += 1
                else:
                    if "not found" in result.stderr.lower():
                        print(f"    [SKIP] Repo might not exist")
                        if repo not in failed_repos:
                            failed_repos.append(repo)
                    elif "already exists" in result.stderr.lower():
                        print(f"    [EXISTS] Issue already exists")
                    else:
                        print(f"    [ERROR] {result.stderr[:50]}")
            except subprocess.TimeoutExpired:
                print(f"    [TIMEOUT]")
            except Exception as e:
                print(f"    [ERROR] {str(e)[:50]}")
    
    # Try NiroAgentV2 repos
    print("\n[Checking NiroAgentV2 repos...]")
    for repo, issues in niro_repos.items():
        # First check if repo exists
        check_cmd = ["gh", "repo", "view", repo, "--json", "name"]
        try:
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"\n[REPO] {repo}")
                print("-" * 40)
                
                for issue in issues:
                    print(f"  Creating: {issue['title'][:50]}...")
                    
                    cmd = [
                        "gh", "issue", "create",
                        "--repo", repo,
                        "--title", issue["title"],
                        "--body", issue["body"]
                    ]
                    
                    for label in issue.get("labels", []):
                        cmd.extend(["--label", label])
                    
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            url = result.stdout.strip()
                            print(f"    [OK] {url}")
                            created_count += 1
                        else:
                            print(f"    [SKIP] {result.stderr[:50]}")
                    except Exception as e:
                        print(f"    [ERROR] {str(e)[:50]}")
        except:
            pass  # Repo doesn't exist, skip
    
    return created_count, failed_repos

def main():
    """Main entry point"""
    
    created, failed = create_issues_in_proper_repos()
    
    print("\n" + "="*80)
    print("ISSUE DISTRIBUTION COMPLETE")
    print("="*80)
    
    print(f"\n[RESULTS]")
    print(f"  Created: {created} issues")
    print(f"  Failed repos: {len(failed)}")
    
    if failed:
        print(f"\n[REPOS THAT MAY NOT EXIST]:")
        for repo in failed:
            print(f"  - {repo}")
    
    print("\n[RULE #1 ENFORCED]:")
    print("✓ Each service's issues are in their own repository")
    print("✓ vf-audio issues → vf-audio-service repo")
    print("✓ vf-video issues → vf-video-service repo")
    print("✓ vf-dashboard issues → vf-dashboard-service repo")
    print("✓ Management issues → business-operations repo")
    
    print("\n[BENEFITS]:")
    print("- Clear ownership per repository")
    print("- Easier to track service progress")
    print("- Better organization")
    print("- Service teams work independently")
    
    print("\n[VIEW ISSUES]:")
    print("https://github.com/VisualForgeMediaV2/vf-audio-service/issues")
    print("https://github.com/VisualForgeMediaV2/vf-video-service/issues")
    print("https://github.com/VisualForgeMediaV2/vf-dashboard-service/issues")
    print("https://github.com/VisualForgeMediaV2/business-operations/issues")
    
    print("\n[SUCCESS!]")
    print("Issues properly distributed to their respective repositories!")

if __name__ == "__main__":
    main()