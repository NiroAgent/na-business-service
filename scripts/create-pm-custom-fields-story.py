#!/usr/bin/env python3
"""
Configure Existing Agent Custom Fields System for PM Integration
Uses the existing custom field infrastructure but adds PM oversight and agent management
"""

import subprocess
import json
from datetime import datetime, timedelta

def create_pm_agent_custom_fields_story():
    """Create story to properly configure the existing custom fields system"""
    
    title = "🔧 Configure PM and Agent Custom Fields Integration"
    
    body = f"""# 🔧 Configure PM and Agent Custom Fields Integration

**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority**: P1 - High
**Epic**: PM and Agent Team Integration
**Assignee**: PM Agent

## 🎯 OBJECTIVE
Configure the existing GitHub custom fields agent assignment system to include PM oversight, proper agent field setup, and integration with the NiroAgentV2 organization.

## ✅ EXISTING INFRASTRUCTURE DISCOVERED:
- **Custom Fields System**: `deployment-scripts/agent-custom-field-assignment.py` ✅
- **GitHub Action**: `github-actions/agent-assignment.yml` ✅  
- **Test Framework**: `github-actions/test-dashboard-assignment.py` ✅
- **50-Agent Configuration**: Spot instance deployment ready ✅
- **Cost Optimization**: 95% savings vs Lambda ✅

## 🔧 CUSTOM FIELDS TO CONFIGURE:

### Required Fields for All NiroAgentV2 Repositories:
```yaml
assigned_agent:
  type: single_select
  options:
    - pm-agent
    - developer_frontend_1
    - developer_frontend_2  
    - developer_backend_1
    - developer_backend_2
    - developer_fullstack_1
    - developer_fullstack_2
    - qa_automation_1
    - qa_manual_1
    - devops_infrastructure_1
    - devops_deployment_1
    - security_compliance_1
    - analytics_reporting_1
    - architect_review_1
    - manager_coordination_1

agent_status:
  type: single_select
  options:
    - unassigned
    - assigned
    - in_progress
    - review_needed
    - pm_review
    - completed
    - blocked

priority_level:
  type: single_select
  options:
    - P0_critical
    - P1_high
    - P2_medium
    - P3_low
    - P4_backlog

processing_started:
  type: date
  
estimated_completion:
  type: date

pm_approved:
  type: single_select
  options:
    - pending
    - approved
    - needs_revision
    - escalated
```

## 🏗️ IMPLEMENTATION TASKS:

### Task 1: Update Agent Configuration
- [ ] Update `deployment-scripts/agent-custom-field-assignment.py` with PM integration
- [ ] Add PM agent as primary coordinator
- [ ] Configure 15 specialized agents (vs current 7)
- [ ] Add PM approval workflow

### Task 2: Configure Custom Fields
```bash
# Run for each repository in NiroAgentV2:
# - autonomous-business-system
# - agent-dashboard  
# - business-operations

gh api "repos/NiroAgentV2/{{repo}}/properties/values" \\
  -X PATCH \\
  -f properties='[
    {{"property_name": "assigned_agent", "value": "unassigned"}},
    {{"property_name": "agent_status", "value": "unassigned"}},
    {{"property_name": "priority_level", "value": "P2_medium"}},
    {{"property_name": "processing_started", "value": ""}},
    {{"property_name": "estimated_completion", "value": ""}},
    {{"property_name": "pm_approved", "value": "pending"}}
  ]'
```

### Task 3: Update GitHub Action
- [ ] Modify `.github/workflows/agent-assignment.yml` to include PM notifications
- [ ] Add PM approval checkpoint before agent deployment
- [ ] Include cost monitoring alerts for PM
- [ ] Add escalation workflow for blocked items

### Task 4: PM Agent Integration
- [ ] Register PM agent in the system
- [ ] Configure PM oversight dashboard
- [ ] Set up automatic PM notifications for:
  - P0/P1 issues
  - Cost threshold alerts
  - Agent assignment conflicts
  - Overdue items

### Task 5: Enhanced Agent Picker
- [ ] Update `scripts/agent-picker.ts` with PM integration
- [ ] Add PM approval step
- [ ] Include workload balancing
- [ ] Add cost estimation per assignment

## 🤖 AGENT ASSIGNMENT ALGORITHM UPDATE:

### Current System Enhancement:
```javascript
// Enhanced agent selection with PM oversight
function selectAgent(issue) {{
  // 1. Analyze issue content and labels
  const skillMatch = analyzeSkillRequirements(issue);
  
  // 2. Check agent availability and workload
  const availableAgents = getAvailableAgents(skillMatch);
  
  // 3. PM approval for P0/P1 issues
  if (issue.priority === 'P0_critical' || issue.priority === 'P1_high') {{
    return {{
      agent: selectBestAgent(availableAgents),
      requiresPMApproval: true,
      escalationPath: ['pm-agent', 'architect_review_1']
    }};
  }}
  
  // 4. Standard assignment for P2-P4
  return {{
    agent: selectBestAgent(availableAgents),
    requiresPMApproval: false,
    autoAssign: true
  }};
}}
```

### PM Oversight Workflow:
1. **Issue Created** → Auto-assign or queue for PM review
2. **PM Review** → Approve, modify assignment, or escalate
3. **Agent Assignment** → Notify agent and update custom fields
4. **Progress Tracking** → PM receives status updates
5. **Completion** → PM final review and approval

## 💰 COST OPTIMIZATION INTEGRATION:

### Current System (Maintained):
- **Spot Instances**: $8-15/month vs $150-300 Lambda
- **95% Cost Savings**: Maintained with PM oversight
- **Auto-scaling**: Based on issue queue and priority

### PM Cost Controls:
- **Budget Alerts**: PM notified at 3% cost increase
- **Emergency Stop**: PM can halt all agents if needed
- **Cost Reports**: Weekly cost analysis to PM
- **Optimization Tracking**: Monthly savings reports

## 🔄 INTEGRATION POINTS:

### With Existing Systems:
- ✅ **Enhanced EC2 Dashboard**: Already displays 50 agents
- ✅ **Cost Monitoring**: Kill switch at 3%/5% thresholds
- ✅ **GitHub Actions**: Custom field processing ready
- 🔄 **PM Dashboard**: Add PM oversight tab
- 🔄 **Agent Communication**: PM coordination hub

### New PM Features:
- **Assignment Override**: PM can reassign any issue
- **Priority Modification**: PM can change priority levels
- **Agent Performance**: View individual agent metrics
- **Cost Dashboard**: Real-time cost monitoring with controls
- **Escalation Management**: Handle blocked or overdue items

## 📊 SUCCESS CRITERIA:

### Functional Requirements:
- [ ] All custom fields configured across NiroAgentV2 repositories
- [ ] PM agent integrated with oversight capabilities
- [ ] 15 specialized agents properly configured
- [ ] Automatic assignment working with PM approval workflow
- [ ] Cost monitoring integrated with PM controls

### Performance Requirements:
- Assignment speed: < 5 seconds
- PM notification: < 10 seconds for P0/P1 issues
- Cost alerts: Real-time when thresholds exceeded
- Dashboard updates: < 3 seconds
- System uptime: 99.9%

## 🚀 IMPLEMENTATION SCRIPT:

### Automated Setup:
```bash
#!/bin/bash
# PM Agent Custom Fields Configuration

echo "🔧 Configuring PM Agent Custom Fields System..."

# 1. Setup custom fields for all repos
./deployment-scripts/setup-custom-fields.sh

# 2. Update agent configuration
python deployment-scripts/agent-custom-field-assignment.py --add-pm-integration

# 3. Test assignment flow
python github-actions/test-dashboard-assignment.py --include-pm-workflow

# 4. Deploy GitHub Action updates
cp github-actions/agent-assignment.yml .github/workflows/

echo "✅ PM Agent Custom Fields System Configured!"
```

## 🔒 SECURITY & PERMISSIONS:

### PM Agent Permissions:
- **Repository Access**: Admin on all NiroAgentV2 repos
- **Custom Field Management**: Full read/write access
- **Agent Coordination**: Can view/modify all assignments
- **Cost Controls**: Emergency stop and budget management
- **Escalation Rights**: Can escalate to architecture team

### Agent Permissions:
- **Repository Access**: Read/write to assigned repositories
- **Custom Field Updates**: Can update status and progress
- **Issue Management**: Comment and label permissions
- **Cost Visibility**: View but not modify cost settings

## 📅 TIMELINE:

### Day 1-2: Configuration
- Setup custom fields in all repositories
- Update agent configuration files
- Test field assignment functionality

### Day 3-4: PM Integration  
- Add PM agent to system
- Configure oversight workflows
- Test PM approval processes

### Day 5-6: Testing & Validation
- End-to-end testing with actual issues
- PM workflow validation
- Cost monitoring integration testing

### Day 7: Deployment
- Deploy to production
- Monitor initial assignments
- Gather PM feedback and adjust

## 🎯 IMMEDIATE NEXT STEPS:

1. **PM Agent**: Review and approve this configuration plan
2. **DevOps**: Run custom fields setup script
3. **Development**: Test assignment workflow
4. **QA**: Validate PM oversight functionality
5. **PM**: Begin using system for issue assignment

---

## ✅ ACCEPTANCE CRITERIA:

- [ ] Custom fields configured in all NiroAgentV2 repositories
- [ ] PM agent properly integrated with oversight capabilities
- [ ] 15+ specialized agents available for assignment
- [ ] Automatic assignment working with skill matching
- [ ] PM approval workflow for high-priority issues
- [ ] Cost monitoring integrated with PM controls
- [ ] Dashboard showing real-time assignment status
- [ ] Emergency override controls working
- [ ] Performance metrics meeting targets

**Ready for PM review and implementation!**

---

**Assignee**: @pm-agent  
**Epic**: PM and Agent Team Integration  
**Labels**: configuration, custom-fields, pm-integration, high-priority  
**Estimated Effort**: 1 week
**Dependencies**: GitHub organization permissions"""

    try:
        # Create the issue using GitHub CLI without assignee (since pm-agent doesn't exist yet)
        result = subprocess.run([
            'gh', 'issue', 'create',
            '--repo', 'NiroAgentV2/autonomous-business-system',
            '--title', title,
            '--body', body,
            '--label', 'feature',
            '--label', 'custom-fields', 
            '--label', 'pm-integration',
            '--label', 'configuration',
            '--label', 'high-priority'
        ], capture_output=True, text=True, check=True)
        
        # Extract issue URL from output
        output_lines = result.stdout.strip().split('\n')
        issue_url = output_lines[-1] if output_lines else "Issue created successfully"
        
        print("🎉 PM Agent Custom Fields Configuration Story Created!")
        print("=" * 60)
        print(f"📋 Title: {title}")
        print(f"🔗 URL: {issue_url}")
        print(f"🏷️ Labels: feature, custom-fields, pm-integration, configuration, high-priority")
        print()
        print("✅ KEY FINDINGS:")
        print("• Existing custom fields system is already built!")
        print("• 50-agent spot instance deployment ready")
        print("• 95% cost optimization already achieved")
        print("• Just needs PM integration and proper configuration")
        print()
        print("🎯 NEXT STEPS:")
        print("1. Configure custom fields in all NiroAgentV2 repos")
        print("2. Add PM agent to the existing system")
        print("3. Update GitHub Actions for PM workflow")
        print("4. Test and deploy PM oversight features")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create GitHub issue: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Creating PM Agent Custom Fields Configuration Story...")
    print("=" * 60)
    
    success = create_pm_agent_custom_fields_story()
    
    if success:
        print("\n🎯 STORY CREATION COMPLETE!")
        print("PM Agent custom fields integration is ready for configuration.")
        print("\n💡 KEY INSIGHT: The agent assignment system already exists!")
        print("We just need to add PM integration and proper field configuration.")
    else:
        print("\n❌ STORY CREATION FAILED!")
        print("Please check GitHub CLI authentication and repository access.")
    
    exit(0 if success else 1)
