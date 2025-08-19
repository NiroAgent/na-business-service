#!/usr/bin/env python3
"""
Create PM and Agent Integration Epic - Manual GitHub Issue Creation
Creates the main epic for PM and Agent team integration with NiroAgentV2
"""

import subprocess
import json
from datetime import datetime, timedelta

def create_pm_agent_integration_epic():
    """Create the main epic for PM and Agent integration"""
    
    title = "🏗️ EPIC: PM and Agent Team Integration with NiroAgentV2 Organization"
    
    body = f"""# 🏗️ PM and Agent Team Integration Epic

**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Organization**: NiroAgentV2
**Repository**: autonomous-business-system
**Epic Owner**: PM Agent
**Target Completion**: {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')}

## 🎯 OBJECTIVE
Integrate PM and Agent team management with NiroAgentV2 organization, ensuring proper assignment fields, GitHub webhook integration, and automated agent system coordination.

## 🚀 IMMEDIATE REQUIREMENTS

### ✅ COMPONENTS ALREADY CREATED:
- GitHub Action Workflow (`.github/workflows/agent-assignment.yml`)
- Webhook Handler (`github-webhook-handler.py`) 
- Integration Setup Guide (`pm-agent-integration-setup.py`)
- Story Creator (`create-pm-agent-integration-story.py`)

### 🔄 IMPLEMENTATION NEEDED:

#### 1. **GitHub Organization Setup**
- Add PM agent and development team to NiroAgentV2 organization
- Configure team structure (PM Team, Dev Team, QA Team, DevOps Team)
- Set up organization-level permissions and policies

#### 2. **Custom Fields Implementation**
```bash
# Required custom fields for all repositories:
- assigned_agent: [pm-agent, frontend-agent, backend-agent, devops-agent, qa-agent, security-agent]
- agent_status: [available, assigned, processing, review, completed]
- priority_level: [P0-Critical, P1-High, P2-Medium, P3-Low, P4-Backlog]
- estimated_completion: date
- processing_started: timestamp
```

#### 3. **Webhook Integration**
- Deploy webhook handler to production endpoint
- Configure organization-level webhook: `/webhook/github`
- Set up real-time agent notification system
- Integrate with existing Enhanced EC2 Dashboard

#### 4. **Agent Assignment System**
- **Automatic Assignment**: Based on issue content and agent skills
- **Workload Balancing**: Even distribution across team
- **PM Oversight**: Review, modify, and approve assignments
- **Performance Monitoring**: < 5 second assignment time

## 🤖 INTELLIGENT ASSIGNMENT ALGORITHM

### Skill-Based Matching:
- **PM Agent**: epic, planning, coordination, management, oversight
- **Frontend Agent**: ui, ux, react, dashboard, frontend, javascript
- **Backend Agent**: api, database, server, backend, python, flask
- **DevOps Agent**: deployment, infrastructure, aws, docker, kubernetes
- **QA Agent**: testing, qa, quality, validation, bug, test
- **Security Agent**: security, auth, encryption, vulnerability
- **Integration Agent**: webhook, api, integration, automation

### Priority Calculation:
- **P0-Critical**: urgent, critical, emergency keywords → PM escalation
- **P1-High**: high, important keywords → PM notification
- **P2-Medium**: Default priority → Standard assignment
- **P3-Low**: low, minor keywords → Lower priority queue
- **P4-Backlog**: backlog label → Future planning

## 🔄 INTEGRATION WITH EXISTING SYSTEMS

### ✅ Already Integrated:
- Enhanced EC2 Dashboard with cost monitoring and kill switch
- Agent orchestration system with 50 specialized agents
- GitHub issue management and tracking
- Cost protection with 3%/5% alert thresholds

### 🔄 To Be Integrated:
- PM workflow system with automated oversight
- Agent communication hub with real-time coordination
- Performance monitoring and reporting dashboard
- Escalation management for overdue items

## 📊 SUCCESS METRICS & MONITORING

### Key Performance Indicators:
- **Assignment Speed**: < 5 seconds from issue creation to agent assignment
- **Resolution Rate**: 95% of issues resolved within estimated timeframe
- **Agent Utilization**: Even distribution with max 20% variance
- **PM Efficiency**: 80% reduction in manual assignment time
- **System Reliability**: 99.9% uptime for assignment system

### Dashboard Integration:
- Real-time assignment status updates
- Agent workload visualization
- PM oversight and approval interface
- Performance metrics and trends
- Cost monitoring integration

## 🔒 SECURITY & COMPLIANCE

### Authentication & Authorization:
- GitHub webhook signature validation with rotating secrets
- Secure token management for API access
- Agent access control with role-based permissions
- PM privilege escalation controls and audit logging

### Data Protection:
- Encrypted transmission of all webhook payloads
- Secure storage of agent assignment data
- GDPR compliance for user data handling
- Backup and disaster recovery procedures

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Organization Setup (Days 1-3)
- [ ] Add team members to NiroAgentV2 organization
- [ ] Configure repository permissions and team structure
- [ ] Set up organization-level policies and settings

### Phase 2: Custom Fields & Webhook (Days 4-6)
- [ ] Create and test custom fields across all repositories
- [ ] Deploy webhook handler to production infrastructure
- [ ] Configure organization-level webhook integration

### Phase 3: Agent System Integration (Days 7-10)
- [ ] Integrate assignment system with existing dashboard
- [ ] Test automated assignment and workload balancing
- [ ] Implement PM oversight and approval workflows

### Phase 4: Testing & Validation (Days 11-14)
- [ ] Comprehensive end-to-end integration testing
- [ ] Load testing with multiple simultaneous assignments
- [ ] Security validation and performance optimization
- [ ] PM training and system validation

## 📞 ESCALATION & OWNERSHIP

### Assignment Ownership:
- **PM Agent**: Epic oversight, approval workflows, team coordination
- **DevOps Team**: Infrastructure deployment, webhook configuration
- **Development Team**: Dashboard integration, API development
- **QA Team**: Testing scenarios, validation criteria
- **Integration Team**: System coordination, troubleshooting

### Escalation Path:
- **L1**: Development Team Lead
- **L2**: PM Agent  
- **L3**: Architecture Review Board
- **L4**: CTO/Technical Director

## 🎯 IMMEDIATE NEXT STEPS

1. **PM Agent**: Review and approve this epic plan
2. **DevOps Team**: Begin organization setup and webhook deployment
3. **Development Team**: Start custom fields implementation
4. **QA Team**: Prepare comprehensive test scenarios
5. **All Teams**: Schedule training and validation sessions

## 📋 ACCEPTANCE CRITERIA

### Must-Have Requirements:
- ✅ 100% automatic assignment coverage for all new issues
- ✅ Real-time PM oversight with approval/modification capabilities
- ✅ Agent workload balancing with performance monitoring
- ✅ Integration with existing Enhanced EC2 Dashboard
- ✅ < 5 second assignment time with 99.9% reliability

### Nice-to-Have Features:
- Advanced analytics and reporting dashboard
- Predictive assignment based on historical performance
- Cross-repository assignment coordination
- Advanced escalation rules and automation

---

## 🔄 STATUS & TIMELINE

**Current Status**: 🔄 Ready for Implementation
**Epic Owner**: PM Agent
**Priority**: P1 - High (Critical for team automation)
**Estimated Timeline**: 14 days
**Business Impact**: High (Enables full autonomous operation)
**Risk Level**: Medium (Integration complexity)

**Next Review**: {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}
**Dependencies**: GitHub organization access, production webhook deployment

---

**Epic Assignment**: @pm-agent
**Supporting Team**: @dev-team @qa-team @devops-team
**Stakeholders**: @architecture-review-board @cto

🎉 **Ready for PM Review and Approval!**"""

    try:
        # Create the issue using GitHub CLI
        result = subprocess.run([
            'gh', 'issue', 'create',
            '--repo', 'NiroAgentV2/autonomous-business-system',
            '--title', title,
            '--body', body,
            '--label', 'epic',
            '--label', 'integration', 
            '--label', 'pm-team',
            '--label', 'agent-system',
            '--label', 'high-priority',
            '--assignee', 'pm-agent'
        ], capture_output=True, text=True, check=True)
        
        # Extract issue URL from output
        output_lines = result.stdout.strip().split('\n')
        issue_url = output_lines[-1] if output_lines else "Issue created successfully"
        
        print("🎉 PM and Agent Integration Epic Created Successfully!")
        print("=" * 60)
        print(f"📋 Title: {title}")
        print(f"🔗 URL: {issue_url}")
        print(f"👤 Assigned to: pm-agent")
        print(f"🏷️ Labels: epic, integration, pm-team, agent-system, high-priority")
        print(f"📅 Target Completion: {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')}")
        print()
        print("✅ NEXT STEPS:")
        print("1. PM Agent should review and approve the epic")
        print("2. DevOps team can begin organization setup")
        print("3. Development team can start implementation")
        print("4. QA team can prepare test scenarios")
        print()
        print("🚀 All technical components are ready for implementation!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create GitHub issue: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🏗️ Creating PM and Agent Integration Epic...")
    print("=" * 50)
    
    success = create_pm_agent_integration_epic()
    
    if success:
        print("\n🎯 EPIC CREATION COMPLETE!")
        print("PM and Agent team integration is ready for implementation.")
    else:
        print("\n❌ EPIC CREATION FAILED!")
        print("Please check GitHub CLI authentication and repository access.")
    
    exit(0 if success else 1)
