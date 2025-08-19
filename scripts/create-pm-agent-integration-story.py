#!/usr/bin/env python3
"""
PM and Agent Team Integration Story Creator
Creates comprehensive GitHub issue for integrating PM and Agent team with NiroAgentV2 organization
Includes assigned field, webhook setup, and automated agent management
"""

import requests
import json
import os
from datetime import datetime, timedelta

class PMAgentIntegrationStoryCreator:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable required")
        
        self.repo = "NiroAgentV2/autonomous-business-system"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
    def create_comprehensive_integration_story(self):
        """Create the main PM and Agent Team Integration Epic"""
        
        issue_data = {
            "title": "🏗️ EPIC: PM and Agent Team Integration with NiroAgentV2 Organization",
            "body": self._get_epic_body(),
            "labels": ["epic", "integration", "pm-team", "agent-system", "high-priority"],
            "assignees": ["pm-agent", "integration-team"]  # Assign to PM agent
        }
        
        return self._create_issue(issue_data)
    
    def _get_epic_body(self):
        """Generate comprehensive epic description"""
        return f"""# 🏗️ PM and Agent Team Integration Epic

**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Organization**: NiroAgentV2
**Repository**: autonomous-business-system
**Epic Owner**: PM Agent
**Target Completion**: {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')}

## 🎯 OBJECTIVE
Integrate PM and Agent team management with NiroAgentV2 organization, ensuring proper assignment fields, GitHub webhook integration, and automated agent system coordination.

## 📋 EPIC REQUIREMENTS

### 🔧 Core Integration Components

#### 1. **GitHub Organization Setup** 
- ✅ Verify NiroAgentV2 organization access
- ✅ Ensure autonomous-business-system repository permissions
- 🔄 Add PM agent and development team to organization
- 🔄 Configure organization-level webhooks

#### 2. **Assignment Field System**
- 🔄 Add `assigned_agent` custom field to all repositories
- 🔄 Add `agent_status` field (available, assigned, processing, completed)
- 🔄 Add `priority_level` field (P0, P1, P2, P3, P4)
- 🔄 Add `estimated_completion` field
- 🔄 Add `processing_started` timestamp field

#### 3. **GitHub Webhook Integration**
- 🔄 Set up organization-level webhook for issue events
- 🔄 Configure webhook endpoint: `/webhook/github/issues`
- 🔄 Implement webhook authentication and validation
- 🔄 Create agent notification system for new issues

#### 4. **PM Agent Integration**
- 🔄 Register PM agent with NiroAgentV2 organization
- 🔄 Configure PM agent for automatic issue assignment
- 🔄 Set up PM oversight and approval workflows
- 🔄 Implement escalation protocols

#### 5. **Agent Team Management**
- 🔄 Create agent team roster in organization
- 🔄 Implement skill-based assignment algorithm
- 🔄 Set up agent availability tracking
- 🔄 Configure workload balancing

## 🛠️ TECHNICAL IMPLEMENTATION

### GitHub Actions Workflows Required:
1. **Agent Assignment Workflow** (`agent-assignment.yml`)
2. **Webhook Processing Workflow** (`webhook-processor.yml`) 
3. **PM Notification Workflow** (`pm-notifications.yml`)
4. **Agent Status Update Workflow** (`agent-status-sync.yml`)

### Custom Fields Schema:
```yaml
assigned_agent:
  type: single_select
  options: [pm-agent, dev-agent-01, dev-agent-02, qa-agent, devops-agent]
  
agent_status:
  type: single_select
  options: [available, assigned, processing, review, completed]
  
priority_level:
  type: single_select
  options: [P0-Critical, P1-High, P2-Medium, P3-Low, P4-Backlog]
  
estimated_completion:
  type: date
  
processing_started:
  type: date
```

### Webhook Endpoint Configuration:
```json
{{
  "name": "agent-system-integration",
  "events": ["issues", "issue_comment", "pull_request"],
  "config": {{
    "url": "https://api.niroagentv2.com/webhook/github/issues",
    "content_type": "json",
    "secret": "${{{{ secrets.WEBHOOK_SECRET }}}}"
  }}
}}
```

## 🏃‍♂️ IMPLEMENTATION PHASES

### Phase 1: Organization Setup (Days 1-3)
- [ ] Add team members to NiroAgentV2 organization
- [ ] Configure repository permissions and access levels
- [ ] Set up organization-level settings and policies
- [ ] Create team structure (PM Team, Dev Team, QA Team, DevOps Team)

### Phase 2: Custom Fields Implementation (Days 4-6)
- [ ] Create custom fields in all NiroAgentV2 repositories
- [ ] Update existing issues with new field structure
- [ ] Test field assignment and updates via API
- [ ] Create field management automation

### Phase 3: Webhook Integration (Days 7-9)
- [ ] Deploy webhook endpoint infrastructure
- [ ] Configure organization-level webhook
- [ ] Implement webhook event processing
- [ ] Set up agent notification system
- [ ] Test end-to-end webhook flow

### Phase 4: Agent System Integration (Days 10-12)
- [ ] Register all agents with GitHub organization
- [ ] Implement automatic assignment logic
- [ ] Configure PM oversight workflows
- [ ] Set up escalation and approval processes
- [ ] Test agent coordination and communication

### Phase 5: Testing and Validation (Days 13-14)
- [ ] End-to-end integration testing
- [ ] Load testing with multiple simultaneous assignments
- [ ] Failover and error handling validation
- [ ] Performance optimization
- [ ] Documentation and training materials

## 🚨 CRITICAL SUCCESS CRITERIA

### Must-Have Requirements:
1. **100% Assignment Coverage**: Every issue must be automatically assigned to appropriate agent
2. **Real-time Notifications**: Agents receive immediate notification of new assignments
3. **PM Oversight**: PM agent has visibility and control over all assignments
4. **Status Tracking**: Real-time status updates for all active work items
5. **Escalation Protocol**: Automatic escalation for overdue or blocked items

### Performance Requirements:
- Webhook processing: < 2 seconds
- Agent assignment: < 5 seconds
- Status updates: < 1 second
- PM dashboard refresh: < 3 seconds

## 🔗 INTEGRATION POINTS

### Existing Systems to Integrate:
- ✅ Enhanced EC2 Dashboard (enhanced-ec2-dashboard.py)
- ✅ Cost Monitoring System with Kill Switch
- ✅ Agent Orchestration System
- ✅ GitHub Issue Management
- 🔄 PM Workflow System
- 🔄 Agent Communication Hub

### New Components Required:
- GitHub Organization Webhook Handler
- Custom Fields Management API
- Agent Assignment Algorithm
- PM Oversight Dashboard
- Escalation Management System

## 📊 SUCCESS METRICS

### Key Performance Indicators:
- **Assignment Speed**: Time from issue creation to agent assignment
- **Resolution Rate**: Percentage of issues resolved within SLA
- **Agent Utilization**: Even distribution of work across team
- **PM Efficiency**: Time saved on manual assignment and tracking
- **System Reliability**: Uptime and error rates

### Monitoring Dashboard Metrics:
- Active assignments per agent
- Average resolution time by priority
- PM approval/rejection rates
- Webhook processing success rate
- System health and performance metrics

## 🔒 SECURITY CONSIDERATIONS

### Authentication & Authorization:
- GitHub token management and rotation
- Webhook secret validation
- Agent access control and permissions
- PM privilege escalation controls
- Audit logging for all assignments

### Data Protection:
- Secure transmission of webhook payloads
- Encrypted storage of sensitive agent data
- GDPR compliance for user data
- Backup and disaster recovery procedures

## 📚 DOCUMENTATION DELIVERABLES

1. **PM Integration Guide**: Complete setup and usage instructions
2. **Agent Onboarding Manual**: How to register and configure new agents
3. **Webhook Configuration Guide**: Technical implementation details
4. **Troubleshooting Playbook**: Common issues and resolution steps
5. **API Documentation**: Complete API reference for custom fields and webhooks

## 🔄 POST-IMPLEMENTATION

### Continuous Improvement:
- Monthly performance reviews
- Agent feedback collection and analysis
- PM efficiency optimization
- System capacity planning
- Feature enhancement roadmap

### Maintenance Schedule:
- Weekly health checks
- Monthly security reviews
- Quarterly performance optimization
- Annual system architecture review

---

## 🚀 IMMEDIATE NEXT STEPS

1. **PM Agent**: Review and approve integration plan
2. **DevOps Team**: Begin organization setup and permissions
3. **Development Team**: Start custom fields implementation
4. **QA Team**: Prepare test scenarios and validation criteria
5. **Integration Team**: Begin webhook endpoint development

## 📞 ESCALATION PATH

- **L1**: Development Team Lead
- **L2**: PM Agent
- **L3**: Architecture Review Board
- **L4**: CTO/Technical Director

---

**Epic Status**: 🔄 In Planning
**Next Review**: {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}
**Risk Level**: Medium (Integration complexity)
**Business Impact**: High (Enables full automation)"""

    def create_supporting_stories(self):
        """Create detailed implementation stories"""
        
        stories = [
            {
                "title": "🔧 Setup NiroAgentV2 Organization Custom Fields",
                "labels": ["feature", "github-integration", "custom-fields"],
                "body": self._get_custom_fields_story()
            },
            {
                "title": "🔗 Implement GitHub Webhook for Agent Assignment",
                "labels": ["feature", "webhook", "automation"],
                "body": self._get_webhook_story()
            },
            {
                "title": "👥 Configure PM Agent Integration",
                "labels": ["feature", "pm-integration", "agent-system"],
                "body": self._get_pm_integration_story()
            },
            {
                "title": "🤖 Setup Agent Team Management System",
                "labels": ["feature", "agent-management", "team-coordination"],
                "body": self._get_agent_management_story()
            },
            {
                "title": "🧪 Integration Testing and Validation",
                "labels": ["testing", "qa", "validation"],
                "body": self._get_testing_story()
            }
        ]
        
        created_issues = []
        for story in stories:
            story["assignees"] = ["pm-agent"]  # Assign all stories to PM
            issue = self._create_issue(story)
            if issue:
                created_issues.append(issue)
                
        return created_issues
    
    def _get_custom_fields_story(self):
        """Custom fields implementation story"""
        return f"""# 🔧 Setup NiroAgentV2 Organization Custom Fields

## 📋 Story Description
Implement custom fields across all NiroAgentV2 repositories to enable automated agent assignment and tracking.

## 🎯 Acceptance Criteria
- [ ] Create `assigned_agent` field with agent dropdown options
- [ ] Create `agent_status` field with status options
- [ ] Create `priority_level` field with P0-P4 options
- [ ] Create `estimated_completion` date field
- [ ] Create `processing_started` timestamp field
- [ ] Apply fields to all organization repositories
- [ ] Test field updates via GitHub API
- [ ] Create field management automation script

## 🛠️ Technical Requirements
- Use GitHub CLI and API for field creation
- Implement field validation and constraints
- Create bulk update capabilities
- Add error handling and rollback procedures

## 📊 Definition of Done
- All required fields created and tested
- Fields applied to existing issues
- API automation working correctly
- Documentation completed

**Estimated Effort**: 2 days
**Priority**: P1 - High
**Dependencies**: Organization access setup"""

    def _get_webhook_story(self):
        """Webhook implementation story"""
        return f"""# 🔗 Implement GitHub Webhook for Agent Assignment

## 📋 Story Description
Create comprehensive webhook system to automatically process GitHub issues and trigger agent assignment workflows.

## 🎯 Acceptance Criteria
- [ ] Deploy webhook endpoint infrastructure
- [ ] Configure organization-level webhook in NiroAgentV2
- [ ] Implement webhook signature validation
- [ ] Create issue event processing logic
- [ ] Set up agent notification system
- [ ] Add error handling and retry mechanisms
- [ ] Implement webhook monitoring and alerting
- [ ] Test end-to-end webhook flow

## 🛠️ Technical Requirements
- Secure webhook endpoint with authentication
- Event processing for issues, comments, and PRs
- Integration with existing agent orchestration system
- Real-time notification delivery
- Comprehensive logging and monitoring

## 🔒 Security Requirements
- Webhook secret validation
- Rate limiting and DDoS protection
- Secure communication channels
- Access control and authorization

## 📊 Definition of Done
- Webhook endpoint deployed and configured
- Organization webhook successfully created
- All event types processed correctly
- Agent notifications working
- Security measures validated

**Estimated Effort**: 3 days
**Priority**: P1 - High
**Dependencies**: Custom fields implementation"""

    def _get_pm_integration_story(self):
        """PM integration story"""
        return f"""# 👥 Configure PM Agent Integration

## 📋 Story Description
Integrate PM agent with NiroAgentV2 organization for oversight, approval workflows, and automated project management.

## 🎯 Acceptance Criteria
- [ ] Register PM agent with organization
- [ ] Configure PM oversight dashboard
- [ ] Implement approval workflow system
- [ ] Set up escalation protocols
- [ ] Create PM notification preferences
- [ ] Add assignment review and modification capabilities
- [ ] Implement workload balancing oversight
- [ ] Test PM agent coordination

## 🛠️ Technical Requirements
- PM agent authentication and authorization
- Integration with existing dashboard system
- Approval workflow automation
- Escalation logic and notifications
- Performance monitoring and reporting

## 👤 PM Capabilities Required
- View all active assignments
- Modify agent assignments
- Approve/reject assignment recommendations
- Set priority overrides
- Monitor team performance
- Handle escalations

## 📊 Definition of Done
- PM agent fully integrated
- Oversight capabilities working
- Approval workflows tested
- Escalation procedures validated
- Performance monitoring active

**Estimated Effort**: 2 days
**Priority**: P1 - High
**Dependencies**: Webhook system, custom fields"""

    def _get_agent_management_story(self):
        """Agent management story"""
        return f"""# 🤖 Setup Agent Team Management System

## 📋 Story Description
Create comprehensive agent team management system for skill-based assignment, availability tracking, and workload balancing.

## 🎯 Acceptance Criteria
- [ ] Create agent team roster in organization
- [ ] Implement skill-based assignment algorithm
- [ ] Set up agent availability tracking
- [ ] Configure workload balancing system
- [ ] Add agent performance monitoring
- [ ] Create agent onboarding automation
- [ ] Implement agent status synchronization
- [ ] Test multi-agent coordination

## 🛠️ Technical Requirements
- Agent registration and profile management
- Skill matching and assignment algorithms
- Real-time availability tracking
- Load balancing and queue management
- Performance metrics and reporting
- Integration with existing agent orchestration

## 🤖 Agent Capabilities
- Automatic assignment based on skills
- Real-time status updates
- Workload balancing
- Performance tracking
- Escalation handling
- Cross-agent communication

## 📊 Definition of Done
- All agents registered and configured
- Assignment algorithm working correctly
- Availability tracking accurate
- Workload properly balanced
- Performance monitoring active

**Estimated Effort**: 3 days
**Priority**: P1 - High
**Dependencies**: PM integration, webhook system"""

    def _get_testing_story(self):
        """Testing and validation story"""
        return f"""# 🧪 Integration Testing and Validation

## 📋 Story Description
Comprehensive testing of PM and Agent team integration to ensure reliability, performance, and security.

## 🎯 Acceptance Criteria
- [ ] End-to-end integration testing
- [ ] Load testing with multiple assignments
- [ ] Failover and error handling validation
- [ ] Security testing and penetration testing
- [ ] Performance optimization
- [ ] User acceptance testing with PM
- [ ] Documentation and training completion
- [ ] Production readiness validation

## 🧪 Test Scenarios
- New issue creation and assignment
- Agent status updates and notifications
- PM approval and override workflows
- System overload and recovery
- Webhook failure and retry
- Security breach attempts
- Performance under high load

## 📊 Performance Targets
- Webhook processing: < 2 seconds
- Agent assignment: < 5 seconds
- Status updates: < 1 second
- 99.9% uptime requirement
- Zero data loss tolerance

## 📋 Test Deliverables
- Comprehensive test plan
- Automated test suite
- Performance benchmarks
- Security audit report
- User training materials
- Production deployment checklist

## 📊 Definition of Done
- All tests passing
- Performance targets met
- Security validated
- PM training completed
- Production deployment approved

**Estimated Effort**: 2 days
**Priority**: P1 - High
**Dependencies**: All previous stories completed"""

    def _create_issue(self, issue_data):
        """Create GitHub issue via API"""
        url = f"https://api.github.com/repos/{self.repo}/issues"
        
        try:
            response = requests.post(url, headers=self.headers, json=issue_data)
            response.raise_for_status()
            
            issue = response.json()
            print(f"✅ Created issue #{issue['number']}: {issue['title']}")
            print(f"   URL: {issue['html_url']}")
            return issue
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to create issue: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            return None

def main():
    """Main execution function"""
    print("🏗️ Creating PM and Agent Team Integration Stories...")
    print("=" * 60)
    
    try:
        creator = PMAgentIntegrationStoryCreator()
        
        # Create main epic
        print("\n📋 Creating Epic: PM and Agent Team Integration...")
        epic = creator.create_comprehensive_integration_story()
        
        if epic:
            print(f"\n🎯 Epic created successfully!")
            print(f"Epic URL: {epic['html_url']}")
            
            # Create supporting stories
            print("\n📝 Creating supporting implementation stories...")
            stories = creator.create_supporting_stories()
            
            print(f"\n🎉 Created {len(stories)} supporting stories!")
            print("\n📊 Summary:")
            print(f"   Epic: #{epic['number']}")
            for i, story in enumerate(stories, 1):
                if story:
                    print(f"   Story {i}: #{story['number']}")
            
            print(f"\n🔗 All issues created in repository: {creator.repo}")
            print("✅ PM and Agent Team Integration stories are ready!")
            
        else:
            print("❌ Failed to create epic")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
