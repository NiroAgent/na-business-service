#!/usr/bin/env python3
"""
PM and Agent Integration Setup Instructions
Complete guide for setting up PM and Agent team with NiroAgentV2 organization
"""

print("🏗️ PM AND AGENT TEAM INTEGRATION SETUP")
print("=" * 60)

setup_instructions = """
# 🎯 COMPREHENSIVE PM AND AGENT INTEGRATION PLAN

## 🚀 IMMEDIATE ACTIONS NEEDED:

### 1. 🔧 GitHub Organization Setup
```bash
# Add team members to NiroAgentV2 organization
gh api orgs/NiroAgentV2/members --method POST --field "invitee=pm-agent"
gh api orgs/NiroAgentV2/members --method POST --field "invitee=dev-team-lead"

# Create teams
gh api orgs/NiroAgentV2/teams --method POST --field "name=pm-team"
gh api orgs/NiroAgentV2/teams --method POST --field "name=agent-development-team"
gh api orgs/NiroAgentV2/teams --method POST --field "name=qa-team"
gh api orgs/NiroAgentV2/teams --method POST --field "name=devops-team"
```

### 2. 🏷️ Custom Fields Setup
```bash
# Create custom fields for issue tracking
gh api repos/NiroAgentV2/autonomous-business-system/custom_fields --method POST \\
  --field "name=assigned_agent" \\
  --field "type=single_select" \\
  --field "options[]=['pm-agent','frontend-agent','backend-agent','devops-agent','qa-agent','security-agent']"

gh api repos/NiroAgentV2/autonomous-business-system/custom_fields --method POST \\
  --field "name=agent_status" \\
  --field "type=single_select" \\
  --field "options[]=['available','assigned','processing','review','completed']"

gh api repos/NiroAgentV2/autonomous-business-system/custom_fields --method POST \\
  --field "name=priority_level" \\
  --field "type=single_select" \\
  --field "options[]=['P0-Critical','P1-High','P2-Medium','P3-Low','P4-Backlog']"
```

### 3. 🔗 Webhook Configuration
```bash
# Set up organization-level webhook
gh api orgs/NiroAgentV2/hooks --method POST \\
  --field "name=web" \\
  --field "config[url]=https://your-webhook-endpoint.com/webhook/github" \\
  --field "config[content_type]=json" \\
  --field "config[secret]=$WEBHOOK_SECRET" \\
  --field "events[]=['issues','issue_comment','pull_request']"
```

## 📋 GITHUB ISSUES TO CREATE:

### Epic: PM and Agent Team Integration
**Title**: 🏗️ EPIC: PM and Agent Team Integration with NiroAgentV2 Organization
**Assignee**: pm-agent
**Labels**: epic, integration, pm-team, agent-system, high-priority

### Supporting Stories:
1. 🔧 Setup NiroAgentV2 Organization Custom Fields
2. 🔗 Implement GitHub Webhook for Agent Assignment  
3. 👥 Configure PM Agent Integration
4. 🤖 Setup Agent Team Management System
5. 🧪 Integration Testing and Validation

## 🛠️ TECHNICAL COMPONENTS CREATED:

✅ **GitHub Action Workflow**: .github/workflows/agent-assignment.yml
   - Automatic agent assignment based on issue content
   - Priority calculation and estimation
   - Label management and tracking
   - Integration with existing agent system

✅ **Webhook Handler**: github-webhook-handler.py
   - Real-time GitHub event processing
   - Intelligent agent assignment algorithm
   - Workload balancing and skill matching
   - PM notification system
   - Agent system integration

## 🤖 AGENT ASSIGNMENT ALGORITHM:

### Skill-Based Assignment:
- **PM Agent**: epic, planning, coordination, management
- **Frontend Agent**: ui, ux, react, dashboard, frontend
- **Backend Agent**: api, database, server, backend, python
- **DevOps Agent**: deployment, infrastructure, aws, docker
- **QA Agent**: testing, qa, quality, validation, bug
- **Security Agent**: security, auth, encryption, vulnerability
- **Integration Agent**: webhook, api, integration, automation

### Priority Calculation:
- **P0-Critical**: urgent, critical, emergency keywords
- **P1-High**: high, important keywords or high-priority label
- **P2-Medium**: Default priority
- **P3-Low**: low, minor keywords or low-priority label  
- **P4-Backlog**: backlog label

### Workload Balancing:
- Tracks current assignments per agent
- Prefers less busy agents for new assignments
- PM oversight for all assignments

## 🔄 INTEGRATION POINTS:

### With Existing Systems:
✅ Enhanced EC2 Dashboard (enhanced-ec2-dashboard.py)
✅ Cost Monitoring System with Kill Switch
✅ Agent Orchestration System  
✅ GitHub Issue Management
🔄 PM Workflow System (to be integrated)
🔄 Agent Communication Hub (to be integrated)

### New Endpoints:
- `/webhook/github` - Main webhook handler
- `/api/agents/workload` - Current agent workload
- `/api/agents/skills` - Agent skills mapping
- `/health` - System health check

## 📊 MONITORING AND METRICS:

### Dashboard Integration:
- Real-time assignment updates
- Agent workload visualization
- PM oversight dashboard
- Performance metrics

### Key Metrics:
- Assignment speed (target: < 5 seconds)
- Agent utilization balance
- Issue resolution times
- PM approval rates
- System uptime

## 🚀 DEPLOYMENT CHECKLIST:

### Prerequisites:
- [ ] GitHub token with organization permissions
- [ ] Webhook endpoint deployment
- [ ] Custom fields creation
- [ ] Team member invitations

### Deployment Steps:
1. [ ] Deploy webhook handler to production
2. [ ] Configure organization webhook
3. [ ] Set up custom fields
4. [ ] Test assignment workflow
5. [ ] Integrate with existing dashboard
6. [ ] PM training and validation

### Validation:
- [ ] Create test issue and verify assignment
- [ ] Check webhook event processing
- [ ] Validate PM oversight capabilities
- [ ] Test agent notification system
- [ ] Verify dashboard integration

## 🔒 SECURITY CONSIDERATIONS:

### Authentication:
- GitHub webhook signature validation
- Secure token management
- API endpoint authentication
- PM privilege controls

### Data Protection:
- Encrypted webhook payloads
- Secure agent data storage
- Audit logging for assignments
- GDPR compliance measures

## 📞 NEXT STEPS:

1. **PM Agent**: Review and approve integration plan
2. **DevOps Team**: Deploy webhook handler and configure organization
3. **Development Team**: Integrate with existing dashboard system
4. **QA Team**: Create comprehensive test scenarios
5. **All Teams**: Participate in training and validation

## 🎯 SUCCESS CRITERIA:

✅ **Automatic Assignment**: Every new issue automatically assigned
✅ **PM Oversight**: PM can view, modify, and approve all assignments  
✅ **Real-time Updates**: Dashboard shows live assignment status
✅ **Workload Balance**: Even distribution across agent team
✅ **Performance**: < 5 second assignment time
✅ **Reliability**: 99.9% uptime for assignment system

---

**Status**: 🔄 Ready for Implementation
**Owner**: PM Agent  
**Priority**: P1 - High
**Estimated Timeline**: 2 weeks
**Dependencies**: GitHub organization access, webhook deployment
"""

print(setup_instructions)

print("\n🎯 FILES CREATED:")
print("✅ create-pm-agent-integration-story.py - Comprehensive story creator")
print("✅ .github/workflows/agent-assignment.yml - GitHub Action for assignment")
print("✅ github-webhook-handler.py - Real-time webhook processor")

print("\n🚀 TO IMPLEMENT:")
print("1. Set GITHUB_TOKEN environment variable")
print("2. Run: python create-pm-agent-integration-story.py")
print("3. Deploy webhook handler to production")
print("4. Configure organization webhook")
print("5. Test complete integration")

print("\n🎉 INTEGRATION READY!")
print("All components prepared for PM and Agent team management with NiroAgentV2 organization!")
