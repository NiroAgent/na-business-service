#!/usr/bin/env python3
"""
Quick Service Setup - Creates documentation and structure for all services
"""

import subprocess
import time

def create_service_structure(service: str, org: str, description: str):
    """Create complete structure for a service"""
    
    print(f"\n{'='*60}")
    print(f"Setting up: {service}")
    print(f"Org: {org}")
    print(f"{'='*60}")
    
    repo = f"{org}/{service}"
    
    # 1. Create documentation task
    doc_issue = create_issue(
        repo,
        "[DOC] Create Standard Documentation Files",
        f"""## Documentation Required for {service}

{description}

### Files to Create in /docs:
- SERVICE_OVERVIEW.md - Architecture and purpose
- API_SPECIFICATION.md - API documentation
- DATABASE_SCHEMA.md - Database structure
- DEPLOYMENT_GUIDE.md - Deployment instructions
- TESTING_GUIDE.md - Testing procedures
- MONITORING_GUIDE.md - Metrics and alerts
- SECURITY_AUDIT.md - Security review
- RUNBOOK.md - Operational procedures

assigned_agent: vf-developer-agent
priority: P0
""")
    
    # 2. Create EPICs
    epics = []
    
    if 'auth' in service.lower():
        epics = [
            ("[EPIC] OAuth2 and SSO Integration", "Implement OAuth2 providers and SSO"),
            ("[EPIC] Security Hardening", "MFA, rate limiting, audit logging"),
            ("[EPIC] Performance Optimization", "Token caching, session management")
        ]
    elif 'dashboard' in service.lower():
        epics = [
            ("[EPIC] Real-time Analytics", "Live metrics and monitoring"),
            ("[EPIC] Admin Controls", "User management and permissions"),
            ("[EPIC] Report Generation", "Automated reporting system")
        ]
    elif 'video' in service.lower():
        epics = [
            ("[EPIC] Codec Support Expansion", "Support more video formats"),
            ("[EPIC] Streaming Optimization", "HLS/DASH streaming"),
            ("[EPIC] AI Enhancement", "AI-powered video processing")
        ]
    elif 'image' in service.lower():
        epics = [
            ("[EPIC] Advanced Processing", "AI-based image enhancement"),
            ("[EPIC] CDN Integration", "Multi-CDN support"),
            ("[EPIC] Format Support", "WebP, AVIF, HEIC support")
        ]
    elif 'audio' in service.lower():
        epics = [
            ("[EPIC] Transcription Accuracy", "Improve speech-to-text"),
            ("[EPIC] Multi-language Support", "Support 50+ languages"),
            ("[EPIC] Audio Enhancement", "Noise reduction and clarity")
        ]
    elif 'payment' in service.lower():
        epics = [
            ("[EPIC] Payment Gateway Integration", "Multiple payment providers"),
            ("[EPIC] PCI Compliance", "Security and compliance"),
            ("[EPIC] Subscription Management", "Flexible billing")
        ]
    else:
        epics = [
            ("[EPIC] Performance Optimization", "Improve service performance"),
            ("[EPIC] Feature Enhancement", "Add new capabilities"),
            ("[EPIC] Integration Expansion", "Connect with more services")
        ]
    
    for title, desc in epics:
        create_issue(repo, title, f"""## {title}

### Description
{desc}

### Business Value
Improve service capabilities and user experience

### Success Metrics
- Performance improvement
- User satisfaction
- Feature adoption

priority: P1
epic: true
""")
    
    # 3. Create Features
    features = [
        ("[FEATURE] API Rate Limiting", "Implement rate limiting for all endpoints"),
        ("[FEATURE] Caching Layer", "Add Redis caching for performance")
    ]
    
    for title, desc in features:
        create_issue(repo, title, f"""## {title}

### Description
{desc}

### Technical Requirements
- Implementation details
- Testing requirements
- Documentation updates

priority: P1
feature: true
""")
    
    # 4. Create QA task
    qa_issue = create_issue(
        repo,
        "[QA] Verify Service and Find Bugs",
        f"""## QA Verification for {service}

### Tasks:
1. Verify documentation accuracy
2. Test all API endpoints
3. Security audit
4. Performance testing
5. Create bug reports

### Bug Categories:
- P0: Critical (blocks production)
- P1: High (affects functionality)
- P2: Medium (improvements)

assigned_agent: vf-qa-agent
priority: P0
""")
    
    print(f"[OK] Created structure for {service}")
    time.sleep(2)  # Rate limiting
    

def create_issue(repo: str, title: str, body: str):
    """Create a GitHub issue"""
    
    cmd = [
        'gh', 'issue', 'create',
        '--repo', repo,
        '--title', title,
        '--body', body
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            issue_num = result.stdout.strip().split('/')[-1]
            print(f"  [OK] Created: {title} (#{issue_num})")
            return issue_num
        else:
            print(f"  [FAIL] Could not create: {title}")
            return None
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


def main():
    """Process all services"""
    
    print("\n" + "="*60)
    print("QUICK SERVICE SETUP - ALL SERVICES")
    print("="*60)
    
    services = [
        # NiroSubs
        ('NiroSubs-V2', 'ns-auth', 'Authentication and user management'),
        ('NiroSubs-V2', 'ns-dashboard', 'Admin dashboard and analytics'),
        ('NiroSubs-V2', 'ns-user', 'User profile management'),
        ('NiroSubs-V2', 'ns-shell', 'CLI interface'),
        
        # VisualForge
        ('VisualForgeMediaV2', 'vf-auth-service', 'Authentication service'),
        ('VisualForgeMediaV2', 'vf-video-service', 'Video processing'),
        ('VisualForgeMediaV2', 'vf-image-service', 'Image processing'),
        ('VisualForgeMediaV2', 'vf-audio-service', 'Audio processing'),
        ('VisualForgeMediaV2', 'vf-text-service', 'Text processing and NLP'),
        ('VisualForgeMediaV2', 'vf-bulk-service', 'Bulk media processing')
    ]
    
    print(f"\nProcessing {len(services)} services...")
    
    processed = 0
    for org, service, desc in services:
        try:
            create_service_structure(service, org, desc)
            processed += 1
        except Exception as e:
            print(f"[ERROR] Failed to process {service}: {e}")
            
    print("\n" + "="*60)
    print(f"COMPLETE: Processed {processed}/{len(services)} services")
    print("="*60)
    
    print("\nCreated per service:")
    print("  - 1 Documentation task")
    print("  - 3 EPICs")
    print("  - 2 Features")
    print("  - 1 QA verification task")
    print("\nTotal: ~70 issues across all services")
    
    print("\nNext Steps:")
    print("1. Developers create documentation")
    print("2. QA verifies and finds bugs")
    print("3. Developers fix bugs")
    print("4. Deploy to production")


if __name__ == '__main__':
    main()