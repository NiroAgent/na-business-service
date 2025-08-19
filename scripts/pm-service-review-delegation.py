#!/usr/bin/env python3
"""
Project Manager Service Review and Delegation System
=====================================================
The PM agent reviews all service documentation and creates comprehensive
features/stories with proper task assignment to developer, devops, and test agents.
"""

import json
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class PMServiceReviewDelegation:
    """PM agent that reviews services and creates detailed stories with delegation"""
    
    def __init__(self):
        self.nirosubs_services = [
            "ns-auth",
            "ns-dashboard", 
            "ns-payments",
            "ns-user",
            "ns-shell"
        ]
        
        self.visualforge_services = [
            "vf-audio",
            "vf-video",
            "vf-image",
            "vf-text",
            "vf-bulk",
            "vf-dashboard"
        ]
        
        self.vf_dev_environment = "https://vf-dev.visualforgemedia.com"
        self.stories_created = []
        
    def create_service_review_policy(self):
        """Create a comprehensive policy for PM to review and delegate work"""
        
        policy = {
            "policy_name": "Service Review and Delegation Policy",
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "objective": "Review all services, create stories, and delegate testing work",
            
            "review_process": {
                "step_1": "Documentation Review",
                "step_2": "Completeness Assessment (currently 75%)",
                "step_3": "Gap Analysis",
                "step_4": "Story Creation",
                "step_5": "Task Assignment",
                "step_6": "Test Case Definition",
                "step_7": "Acceptance Criteria"
            },
            
            "delegation_rules": {
                "developer_agent": [
                    "Code completion for remaining 25%",
                    "API endpoint implementation",
                    "Bug fixes from testing",
                    "Documentation updates",
                    "Code review implementation"
                ],
                "devops_agent": [
                    "Environment setup (vf-dev)",
                    "CI/CD pipeline configuration",
                    "Deployment automation",
                    "Infrastructure as Code",
                    "Monitoring setup",
                    "Performance optimization"
                ],
                "qa_agent": [
                    "Test case creation from acceptance criteria",
                    "Integration testing",
                    "End-to-end testing",
                    "Performance testing",
                    "Security testing",
                    "Test automation"
                ]
            },
            
            "story_template": {
                "title": "[Service] - [Feature/Task]",
                "description": "Detailed description of what needs to be done",
                "tasks": [
                    "Specific implementation task 1",
                    "Specific implementation task 2",
                    "Testing task",
                    "Documentation task"
                ],
                "acceptance_criteria": [
                    "GIVEN a specific context",
                    "WHEN an action is performed", 
                    "THEN expected outcome occurs"
                ],
                "test_cases": [
                    "Test case derived from acceptance criteria"
                ],
                "assigned_agents": ["developer", "qa", "devops"],
                "priority": "P1",
                "estimated_hours": 8
            },
            
            "service_specific_requirements": {
                "authentication_services": {
                    "critical_tests": [
                        "Token validation",
                        "Session management",
                        "Password reset flow",
                        "MFA implementation",
                        "Rate limiting"
                    ]
                },
                "payment_services": {
                    "critical_tests": [
                        "Payment processing",
                        "Subscription management",
                        "Webhook handling",
                        "Refund processing",
                        "PCI compliance"
                    ]
                },
                "media_services": {
                    "critical_tests": [
                        "File upload/download",
                        "Processing pipeline",
                        "Format conversion",
                        "CDN integration",
                        "Storage optimization"
                    ]
                }
            }
        }
        
        # Save policy
        with open("pm-delegation-policy.json", "w") as f:
            json.dump(policy, f, indent=2)
        
        print("[OK] PM Delegation Policy created")
        return policy
    
    def generate_nirosubs_stories(self):
        """Generate comprehensive stories for NiroSubs services"""
        
        stories = []
        
        for service in self.nirosubs_services:
            # Service completion story
            stories.append({
                "title": f"[{service}] Complete Service Implementation to 100%",
                "body": f"""## Service Completion Story

### Description
The {service} service is currently 75% complete. This story covers the remaining 25% implementation, testing, and deployment to vf-dev environment.

### Current State
- Core functionality: 75% complete
- Testing coverage: Needs improvement
- Documentation: Partial
- Deployment: Not on vf-dev

### Tasks
1. **Code Completion** (Developer Agent)
   - Review existing codebase
   - Identify missing features from requirements
   - Implement remaining endpoints
   - Add error handling
   - Implement logging

2. **Testing Implementation** (QA Agent)
   - Create unit tests for all functions
   - Write integration tests
   - Implement E2E test scenarios
   - Performance testing
   - Security testing

3. **DevOps Setup** (DevOps Agent)
   - Configure CI/CD pipeline
   - Deploy to vf-dev environment
   - Set up monitoring
   - Configure auto-scaling
   - Implement health checks

4. **Documentation** (Developer Agent)
   - API documentation
   - Setup guides
   - Troubleshooting guide
   - Architecture diagram

### Acceptance Criteria
1. **GIVEN** the {service} service
   **WHEN** all endpoints are called with valid data
   **THEN** they return expected responses with <200ms latency

2. **GIVEN** the deployment pipeline
   **WHEN** code is pushed to main branch
   **THEN** it automatically deploys to vf-dev within 5 minutes

3. **GIVEN** the test suite
   **WHEN** executed
   **THEN** achieves >80% code coverage with all tests passing

4. **GIVEN** the monitoring dashboard
   **WHEN** service is running
   **THEN** displays real-time metrics and alerts on failures

### Test Cases
1. **Unit Tests**
   - Test each function with valid inputs
   - Test each function with invalid inputs
   - Test error handling
   - Test edge cases

2. **Integration Tests**
   - Test API endpoints
   - Test database operations
   - Test external service integrations
   - Test authentication/authorization

3. **E2E Tests**
   - Complete user flow testing
   - Cross-service communication
   - Load testing (100 concurrent users)
   - Failover testing

### Definition of Done
- [ ] All code implemented and reviewed
- [ ] Test coverage >80%
- [ ] Deployed to vf-dev successfully
- [ ] Documentation complete
- [ ] Performance benchmarks met
- [ ] Security scan passed
- [ ] Monitoring active

### Assigned Agents
- **Lead**: ai-developer-agent
- **Testing**: ai-qa-agent
- **Deployment**: ai-devops-agent
- **Review**: ai-project-manager-agent

### Priority: P1 (High)
### Estimated Effort: 16 hours
""",
                "labels": ["service/" + service, "priority/P1", "completion", "testing", "deployment"],
                "assignees": ["ai-developer-agent", "ai-qa-agent", "ai-devops-agent"]
            })
            
            # Testing specific story
            stories.append({
                "title": f"[{service}] Comprehensive Testing Suite Implementation",
                "body": f"""## Testing Story for {service}

### Description
Implement comprehensive testing for {service} based on acceptance criteria and achieve >80% coverage.

### Tasks
1. **Test Planning**
   - Review service documentation
   - Identify test scenarios
   - Create test matrix
   - Define test data

2. **Test Implementation**
   - Unit tests for all functions
   - Integration tests for APIs
   - E2E user journey tests
   - Performance benchmarks
   - Security vulnerability tests

3. **Test Automation**
   - Set up test framework
   - Implement CI/CD integration
   - Configure test reporting
   - Set up test data management

### Acceptance Criteria
**GIVEN** the test suite
**WHEN** executed in vf-dev environment
**THEN** all tests pass with >80% coverage

### Test Cases
{self._generate_service_specific_tests(service)}

### Assigned Agent: ai-qa-agent
### Priority: P1
""",
                "labels": ["testing", "service/" + service, "priority/P1"],
                "assignees": ["ai-qa-agent"]
            })
            
            # Deployment story
            stories.append({
                "title": f"[{service}] Deploy to vf-dev Environment",
                "body": f"""## Deployment Story for {service}

### Description
Deploy {service} to vf-dev environment with full monitoring and auto-scaling.

### Tasks
1. **Environment Setup**
   - Configure AWS resources
   - Set up RDS/DynamoDB
   - Configure secrets management
   - Set up networking

2. **Deployment Pipeline**
   - GitHub Actions workflow
   - Docker containerization
   - Kubernetes deployment
   - Blue-green deployment strategy

3. **Monitoring Setup**
   - CloudWatch dashboards
   - Application metrics
   - Log aggregation
   - Alert configuration

### Acceptance Criteria
**GIVEN** the deployment pipeline
**WHEN** triggered
**THEN** service deploys to vf-dev with zero downtime

### Test Cases
1. Deploy to vf-dev and verify health
2. Test auto-scaling under load
3. Verify monitoring alerts
4. Test rollback procedure

### Assigned Agent: ai-devops-agent
### Priority: P1
""",
                "labels": ["deployment", "service/" + service, "priority/P1", "vf-dev"],
                "assignees": ["ai-devops-agent"]
            })
        
        return stories
    
    def generate_visualforge_stories(self):
        """Generate comprehensive stories for VisualForge services"""
        
        stories = []
        
        for service in self.visualforge_services:
            # Media processing specific stories
            if service in ["vf-audio", "vf-video", "vf-image"]:
                stories.append({
                    "title": f"[{service}] Media Processing Pipeline Testing",
                    "body": f"""## Media Processing Testing Story

### Description
Complete testing of {service} media processing pipeline on vf-dev environment.

### Tasks
1. **Processing Tests**
   - Upload various file formats
   - Test conversion pipeline
   - Verify quality settings
   - Test error handling
   - Benchmark processing times

2. **Storage Tests**
   - S3 integration
   - CDN delivery
   - Cache invalidation
   - Storage optimization

3. **Performance Tests**
   - Concurrent processing (10+ files)
   - Large file handling (>1GB)
   - Memory optimization
   - CPU utilization

### Acceptance Criteria
**GIVEN** a media file
**WHEN** uploaded to {service}
**THEN** processes successfully within SLA times:
- Small files (<10MB): <30 seconds
- Medium files (10-100MB): <2 minutes  
- Large files (>100MB): <10 minutes

### Test Cases
1. Upload {self._get_media_formats(service)} formats
2. Test batch processing
3. Test webhook notifications
4. Verify CDN delivery
5. Test error recovery

### Assigned Agents
- **Testing**: ai-qa-agent
- **Performance**: ai-devops-agent
- **Implementation**: ai-developer-agent

### Priority: P1
### Environment: vf-dev
""",
                    "labels": ["media-processing", "service/" + service, "priority/P1", "vf-dev", "testing"],
                    "assignees": ["ai-qa-agent", "ai-developer-agent", "ai-devops-agent"]
                })
            
            # Standard service story
            stories.append({
                "title": f"[{service}] Complete Service Testing on vf-dev",
                "body": f"""## Service Testing Story

### Description
Complete all testing for {service} service deployed on vf-dev environment.

### Current State
- Implementation: 75% complete
- Testing: Needs comprehensive coverage
- Deployment: Required on vf-dev

### Tasks
1. **Functional Testing**
   - All API endpoints
   - Business logic validation
   - Data persistence
   - Integration points

2. **Non-Functional Testing**
   - Performance benchmarks
   - Security scanning
   - Load testing
   - Stress testing

3. **Deployment Verification**
   - Health checks
   - Monitoring setup
   - Log aggregation
   - Alert configuration

### Acceptance Criteria
1. **GIVEN** the {service} on vf-dev
   **WHEN** all test suites run
   **THEN** achieve >80% pass rate

2. **GIVEN** performance tests
   **WHEN** executed with 100 concurrent users
   **THEN** response time <500ms for 95th percentile

3. **GIVEN** security scan
   **WHEN** completed
   **THEN** no critical vulnerabilities found

### Test Cases
{self._generate_comprehensive_test_cases(service)}

### Definition of Done
- [ ] All functional tests passing
- [ ] Performance benchmarks met
- [ ] Security scan clean
- [ ] Deployed on vf-dev
- [ ] Monitoring active
- [ ] Documentation updated

### Assigned Agents
- **Lead**: ai-qa-agent
- **Support**: ai-developer-agent, ai-devops-agent
- **Review**: ai-project-manager-agent

### Priority: P1
### Estimated Effort: 12 hours
""",
                "labels": ["testing", "service/" + service, "priority/P1", "vf-dev"],
                "assignees": ["ai-qa-agent", "ai-developer-agent", "ai-devops-agent"]
            })
        
        return stories
    
    def _generate_service_specific_tests(self, service: str) -> str:
        """Generate service-specific test cases"""
        
        test_cases = {
            "ns-auth": """
1. **Authentication Tests**
   - Login with valid credentials
   - Login with invalid credentials
   - Token refresh flow
   - Logout functionality
   - Session expiry

2. **Authorization Tests**
   - Role-based access
   - Permission validation
   - Resource access control
   - Multi-tenancy isolation

3. **Security Tests**
   - SQL injection attempts
   - XSS prevention
   - CSRF protection
   - Rate limiting
   - Password complexity
""",
            "ns-payments": """
1. **Payment Processing**
   - Successful payment flow
   - Failed payment handling
   - Refund processing
   - Partial refunds
   - Currency conversion

2. **Subscription Tests**
   - Create subscription
   - Update subscription
   - Cancel subscription
   - Renewal processing
   - Trial period handling

3. **Webhook Tests**
   - Payment success webhook
   - Payment failure webhook
   - Subscription events
   - Retry logic
   - Signature validation
""",
            "ns-dashboard": """
1. **UI Tests**
   - Page load performance
   - Component rendering
   - Data visualization
   - Responsive design
   - Cross-browser compatibility

2. **Data Tests**
   - Real-time updates
   - Data accuracy
   - Filtering and sorting
   - Export functionality
   - Pagination

3. **Integration Tests**
   - API communication
   - WebSocket connections
   - State management
   - Error handling
   - Offline mode
"""
        }
        
        return test_cases.get(service, """
1. **Functional Tests**
   - CRUD operations
   - Business logic
   - Data validation
   - Error handling

2. **Integration Tests**
   - API endpoints
   - Database operations
   - External services
   - Message queues

3. **Performance Tests**
   - Load testing
   - Stress testing
   - Memory usage
   - Response times
""")
    
    def _get_media_formats(self, service: str) -> str:
        """Get media formats for testing"""
        
        formats = {
            "vf-audio": "MP3, WAV, FLAC, AAC, OGG",
            "vf-video": "MP4, AVI, MOV, MKV, WEBM",
            "vf-image": "JPEG, PNG, GIF, WEBP, TIFF, SVG"
        }
        
        return formats.get(service, "various")
    
    def _generate_comprehensive_test_cases(self, service: str) -> str:
        """Generate comprehensive test cases for a service"""
        
        return """
1. **Unit Tests** (Developer Agent)
   - Test all functions with valid inputs
   - Test all functions with invalid inputs
   - Test error handling
   - Test edge cases
   - Mock external dependencies

2. **Integration Tests** (QA Agent)
   - Test API endpoints with Postman/Newman
   - Test database transactions
   - Test service-to-service communication
   - Test message queue operations
   - Test cache operations

3. **End-to-End Tests** (QA Agent)
   - Complete user journey
   - Cross-service workflows
   - Data consistency checks
   - Transaction rollback scenarios
   - Concurrent user scenarios

4. **Performance Tests** (DevOps Agent)
   - Load testing (100 concurrent users)
   - Stress testing (find breaking point)
   - Spike testing (sudden load increase)
   - Endurance testing (24 hours)
   - Volume testing (large datasets)

5. **Security Tests** (Security Agent)
   - OWASP Top 10 vulnerabilities
   - Authentication bypass attempts
   - Authorization testing
   - Input validation testing
   - API security testing

6. **Deployment Tests** (DevOps Agent)
   - Blue-green deployment
   - Rollback procedures
   - Health check validation
   - Auto-scaling triggers
   - Disaster recovery
"""
    
    def create_pm_delegation_issue(self):
        """Create the master PM delegation issue"""
        
        issue = {
            "title": "[PM] Review All Services and Create Comprehensive Test Stories",
            "body": f"""## Project Manager Master Delegation Task

### Objective
Review documentation for all services in NiroSubsV2 and VisualForgeV2, assess completion status (currently ~75%), and create detailed stories with proper delegation to developer, DevOps, and QA agents.

### Scope
**NiroSubsV2 Services:**
{chr(10).join('- ' + s for s in self.nirosubs_services)}

**VisualForgeV2 Services:**
{chr(10).join('- ' + s for s in self.visualforge_services)}

### Deliverables
1. **Service Assessment Report**
   - Current completion percentage
   - Missing features/functionality
   - Testing coverage gaps
   - Deployment status

2. **Story Creation** (Per Service)
   - Detailed description
   - Specific tasks for each agent
   - Acceptance criteria (for test case generation)
   - Definition of done
   - Priority and effort estimation

3. **Test Strategy**
   - Test cases derived from acceptance criteria
   - Testing on vf-dev environment
   - Performance benchmarks
   - Security requirements

### Delegation Guidelines

**Developer Agent Responsibilities:**
- Complete remaining 25% implementation
- Fix bugs identified in testing
- Update documentation
- Code review and refactoring

**DevOps Agent Responsibilities:**
- Deploy all services to vf-dev environment
- Set up CI/CD pipelines
- Configure monitoring and alerts
- Performance optimization
- Infrastructure as Code

**QA Agent Responsibilities:**
- Create test cases from acceptance criteria
- Implement test automation
- Execute comprehensive test suites
- Report bugs and track resolution
- Validate deployments on vf-dev

### Success Criteria
1. All services deployed and running on vf-dev
2. Test coverage >80% for all services
3. All P1 bugs fixed
4. Documentation complete
5. Monitoring dashboards active
6. Performance benchmarks met

### Timeline
- Week 1: Service review and story creation
- Week 2-3: Implementation and testing
- Week 4: Deployment and validation

### Priority: P0 (Critical)
### Assigned: ai-project-manager-agent

**Note:** This is a master delegation task. The PM should create individual stories for each service with specific tasks and acceptance criteria that QA can use to generate test cases.
""",
            "labels": ["management/delegation", "priority/P0", "testing", "deployment", "all-services"],
            "assignee": "ai-project-manager-agent"
        }
        
        return issue
    
    def create_all_stories(self):
        """Create all stories in GitHub"""
        
        print("\n" + "="*80)
        print("CREATING SERVICE REVIEW AND TESTING STORIES")
        print("="*80)
        
        # Create PM delegation policy
        self.create_service_review_policy()
        
        # Generate all stories
        all_stories = []
        
        # Add PM master delegation issue
        all_stories.append(self.create_pm_delegation_issue())
        
        # Add NiroSubs stories
        print("\nGenerating NiroSubs stories...")
        all_stories.extend(self.generate_nirosubs_stories())
        
        # Add VisualForge stories  
        print("Generating VisualForge stories...")
        all_stories.extend(self.generate_visualforge_stories())
        
        print(f"\nTotal stories to create: {len(all_stories)}")
        
        # Create issues in GitHub
        repo = "NiroAgentV2/business-operations"
        
        for story in all_stories:
            print(f"\nCreating: {story['title']}")
            
            cmd = [
                "gh", "issue", "create",
                "--repo", repo,
                "--title", story["title"],
                "--body", story["body"]
            ]
            
            # Add labels
            for label in story.get("labels", []):
                cmd.extend(["--label", label])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    url = result.stdout.strip()
                    self.stories_created.append(url)
                    print(f"  [OK] Created: {url}")
                else:
                    print(f"  [INFO] May already exist or error: {result.stderr[:100]}")
            except Exception as e:
                print(f"  [ERROR] {e}")
        
        print(f"\n[COMPLETE] Created {len(self.stories_created)} stories")
        
        # Save summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_stories": len(all_stories),
            "created": len(self.stories_created),
            "nirosubs_services": self.nirosubs_services,
            "visualforge_services": self.visualforge_services,
            "vf_dev_environment": self.vf_dev_environment,
            "policy_file": "pm-delegation-policy.json"
        }
        
        with open("service-review-summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        return summary

def main():
    """Main entry point"""
    system = PMServiceReviewDelegation()
    summary = system.create_all_stories()
    
    print("\n" + "="*80)
    print("SERVICE REVIEW DELEGATION COMPLETE")
    print("="*80)
    
    print("\n[OK] Summary:")
    print(f"  - Total services: {len(summary['nirosubs_services']) + len(summary['visualforge_services'])}")
    print(f"  - Stories created: {summary['created']}")
    print(f"  - Target environment: {summary['vf_dev_environment']}")
    print(f"  - Policy saved: {summary['policy_file']}")
    
    print("\n[NEXT STEPS]:")
    print("1. PM agent will review all service documentation")
    print("2. PM creates detailed stories with acceptance criteria")
    print("3. QA agent generates test cases from acceptance criteria")
    print("4. Developer agent completes remaining 25% implementation")
    print("5. DevOps agent deploys everything to vf-dev")
    print("6. QA agent runs comprehensive testing on vf-dev")
    
    print("\n[INFO] All agents now have clear instructions and will work autonomously!")

if __name__ == "__main__":
    main()