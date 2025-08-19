#!/usr/bin/env python3
"""
Batch Service Processor - Creates PM issues for all services
"""

import subprocess
import json
import time

class BatchServiceProcessor:
    """Creates documentation and SDLC structure for all services"""
    
    def __init__(self):
        self.services = {
            'NiroSubs': [
                ('ns-auth', 'Authentication and user management service'),
                ('ns-dashboard', 'Admin dashboard and analytics service'),
                ('ns-user', 'User profile and subscription management'),
                ('ns-shell', 'CLI and shell interface service')
            ],
            'VisualForge': [
                ('vf-auth-service', 'Authentication and authorization service'),
                ('vf-video-service', 'Video processing and transcoding service'),
                ('vf-image-service', 'Image processing and optimization service'),
                ('vf-audio-service', 'Audio processing and transcription service'),
                ('vf-text-service', 'Text processing and NLP service'),
                ('vf-bulk-service', 'Bulk media processing service')
            ]
        }
        self.created_issues = []
        
    def create_all_pm_issues(self):
        """Create PM issues for all services"""
        
        print("\n=== BATCH SERVICE PROCESSOR ===")
        print("Creating PM issues for all services...")
        
        # NiroSubs services
        print("\n[NIROSUBS] Creating issues for NiroSubs services...")
        for service, description in self.services['NiroSubs']:
            self.create_pm_issue(service, description, 'NiroSubs-V2')
            
        # VisualForge services  
        print("\n[VISUALFORGE] Creating issues for VisualForge services...")
        for service, description in self.services['VisualForge']:
            self.create_pm_issue(service, description, 'VisualForgeMediaV2')
            
        print(f"\n[COMPLETE] Created {len(self.created_issues)} PM issues")
        return self.created_issues
        
    def create_pm_issue(self, service: str, description: str, org: str):
        """Create a PM issue for a service"""
        
        title = f"[PM] Review {service} Documentation and Create SDLC Structure"
        
        body = f'''## Objective
Review the {service} service documentation and establish comprehensive SDLC structure with EPICs, Features, Stories, and identify bugs.

## Service Description
{description}

## Context
The {service} service is a critical component that needs proper documentation and development structure. This review should result in creating standard documentation and a complete development hierarchy.

## Requirements

### 1. Documentation Creation
Create these standard documentation files under /docs:
- **SERVICE_OVERVIEW.md** - Architecture, purpose, dependencies
- **API_SPECIFICATION.md** - Complete API documentation  
- **DATABASE_SCHEMA.md** - Database structure and relationships
- **DEPLOYMENT_GUIDE.md** - How to deploy the service
- **TESTING_GUIDE.md** - How to test the service
- **MONITORING_GUIDE.md** - Metrics, alerts, dashboards
- **SECURITY_AUDIT.md** - Security considerations and compliance
- **RUNBOOK.md** - Operational procedures and troubleshooting

### 2. Create Development Hierarchy
Create the following in {org}/{service} repo:

#### EPICs (3-5 major initiatives)
Examples:
- Performance Optimization
- Security Hardening
- Feature Expansion
- Integration Enhancement
- Scalability Improvements

#### Features (2-3 per EPIC)
Specific capabilities to implement

#### Stories (2-3 per Feature)
User-facing functionality with acceptance criteria

#### Tasks
Technical implementation items

### 3. QA Verification
After documentation is created:
- Verify all documentation is accurate
- Test all documented procedures
- Identify and log bugs:
  - P0: Critical bugs blocking production
  - P1: High priority bugs affecting functionality
  - P2: Medium priority improvements

### 4. Bug Fixes
Developer team should:
- Fix all P0 bugs immediately
- Schedule P1 bugs for current sprint
- Plan P2 bugs for next sprint

## Success Criteria
- [ ] All 8 standard documentation files created
- [ ] 3-5 EPICs created with business value
- [ ] 6-15 Features created under EPICs
- [ ] 12-30 Stories created with acceptance criteria
- [ ] QA verification complete with bugs logged
- [ ] All P0 bugs fixed with code

## Service-Specific Focus Areas

'''
        
        # Add service-specific focus areas
        if 'auth' in service.lower():
            body += '''### Authentication Focus
- OAuth2/JWT implementation
- MFA support
- Session management
- Password policies
- Account recovery
'''
        elif 'dashboard' in service.lower():
            body += '''### Dashboard Focus
- Real-time metrics
- User analytics
- Admin controls
- Report generation
- Data visualization
'''
        elif 'video' in service.lower():
            body += '''### Video Processing Focus
- Codec support
- Transcoding pipeline
- Streaming optimization
- Thumbnail generation
- Format conversion
'''
        elif 'image' in service.lower():
            body += '''### Image Processing Focus
- Format conversion
- Resize/crop operations
- Optimization algorithms
- Metadata extraction
- CDN integration
'''
        elif 'audio' in service.lower():
            body += '''### Audio Processing Focus
- Format conversion
- Transcription accuracy
- Noise reduction
- Audio enhancement
- Multi-language support
'''
        elif 'text' in service.lower():
            body += '''### Text Processing Focus
- NLP capabilities
- Language detection
- Sentiment analysis
- Entity extraction
- Translation support
'''
        elif 'bulk' in service.lower():
            body += '''### Bulk Processing Focus
- Batch job management
- Queue optimization
- Parallel processing
- Progress tracking
- Error recovery
'''
        elif 'user' in service.lower():
            body += '''### User Management Focus
- Profile management
- Subscription handling
- Preference storage
- Activity tracking
- Data privacy
'''
        
        body += f'''
## Priority: P0 (Critical)
All services need proper documentation and structure for production readiness.

## Timeline
- Documentation: 2 days
- EPIC/Feature creation: 1 day
- QA verification: 2 days
- Bug fixes: 3 days

assigned_agent: vf-manager-agent
type: project_management
service: {service}
organization: {org}
'''
        
        print(f"\n[CREATE] Creating PM issue for {service}...")
        
        cmd = [
            'gh', 'issue', 'create',
            '--repo', 'VisualForgeMediaV2/business-operations',
            '--title', title,
            '--body', body
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                issue_num = issue_url.split('/')[-1]
                print(f"   [OK] Created issue #{issue_num}: {issue_url}")
                self.created_issues.append({
                    'number': issue_num,
                    'service': service,
                    'org': org,
                    'url': issue_url
                })
                time.sleep(1)  # Rate limiting
            else:
                print(f"   [FAIL] {result.stderr}")
        except Exception as e:
            print(f"   [ERROR] {e}")
            
    def process_all_with_agents(self):
        """Process all created issues with agents"""
        
        print("\n[PROCESSING] Running agents on all issues...")
        
        for issue in self.created_issues:
            print(f"\n[AGENT] Processing {issue['service']} (Issue #{issue['number']})...")
            
            # Create issue data file
            issue_data = {
                'number': int(issue['number']),
                'title': f"[PM] Review {issue['service']} Documentation",
                'body': f"{issue['service']} documentation review",
                'labels': [{'name': 'priority-p0'}],
                'repository': {'full_name': 'VisualForgeMediaV2/business-operations'}
            }
            
            filename = f"issue_{issue['number']}.json"
            with open(f'src/agents/{filename}', 'w') as f:
                json.dump(issue_data, f)
                
            # Run enhanced PM agent
            cmd = [
                'python', 'src/agents/enhanced-pm-agent.py',
                '--process-issue', issue['number'],
                '--issue-data', f'src/agents/{filename}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   [OK] PM agent processed {issue['service']}")
            else:
                print(f"   [FAIL] PM agent failed for {issue['service']}")
                
            time.sleep(2)  # Rate limiting between services
            
    def create_summary_report(self):
        """Create a summary report of all processing"""
        
        print("\n" + "="*60)
        print("BATCH PROCESSING SUMMARY")
        print("="*60)
        
        ns_count = len([i for i in self.created_issues if i['org'] == 'NiroSubs-V2'])
        vf_count = len([i for i in self.created_issues if i['org'] == 'VisualForgeMediaV2'])
        
        print(f"\nServices Processed: {len(self.created_issues)}")
        print(f"  NiroSubs: {ns_count} services")
        print(f"  VisualForge: {vf_count} services")
        
        print("\nCreated Structure (per service):")
        print("  - 8 Documentation files")
        print("  - 3-5 EPICs")
        print("  - 6-15 Features")
        print("  - 12-30 User Stories")
        print("  - QA verification tasks")
        
        print("\nEstimated Total Created:")
        total = len(self.created_issues)
        print(f"  - Documentation files: {total * 8}")
        print(f"  - EPICs: {total * 4}")
        print(f"  - Features: {total * 10}")
        print(f"  - Stories: {total * 20}")
        print(f"  - QA tasks: {total}")
        print(f"  - Total issues: ~{total * 43}")
        
        print("\nNext Steps:")
        print("1. QA agents verify each service")
        print("2. QA creates bug reports")
        print("3. Developers fix P0 bugs")
        print("4. Deploy to production")


def main():
    """Main entry point"""
    
    processor = BatchServiceProcessor()
    
    # Create all PM issues
    processor.create_all_pm_issues()
    
    # Process with agents
    if len(processor.created_issues) > 0:
        print("\n[OPTION] Ready to process with agents")
        print("Run: python batch-service-processor.py --process")
        
        import sys
        if '--process' in sys.argv:
            processor.process_all_with_agents()
            
    # Create summary
    processor.create_summary_report()


if __name__ == '__main__':
    main()