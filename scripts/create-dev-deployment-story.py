#!/usr/bin/env python3
"""
Create deployment story for agent assignment system to dev environment
"""

import subprocess
import json
from datetime import datetime

def create_deployment_story():
    """Create GitHub issue for deploying agent assignment system to dev"""
    
    # Story details
    title = "Deploy Agent Assignment System to Dev Environment"
    
    body = f"""# 🚀 Deploy Agent Assignment System to Dev Environment

**Epic**: Agent Assignment & PM Integration  
**Priority**: P1 - High  
**Environment**: Development  
**Estimated Effort**: 4-6 hours

## 📋 Story Description

Deploy the complete agent assignment system with PM integration to the development environment for testing and validation before production rollout.

## 🎯 Acceptance Criteria

### ✅ **Infrastructure Deployment**
- [ ] Deploy GitHub Actions workflow (`agent-assignment-pm.yml`)
- [ ] Validate all agent assignment labels are configured
- [ ] Verify custom fields setup across all repositories
- [ ] Deploy cost monitoring integration
- [ ] Set up PM notification system

### ✅ **System Integration**
- [ ] Test automatic agent assignment algorithm
- [ ] Validate PM approval workflow
- [ ] Verify priority-based assignment logic
- [ ] Test cost optimization tracking
- [ ] Validate status progression workflow

### ✅ **Testing & Validation**
- [ ] Create test issues for each agent type (15 agents)
- [ ] Test PM override capabilities
- [ ] Validate escalation workflows
- [ ] Test cost monitoring alerts
- [ ] Verify dashboard integration

### ✅ **Documentation & Training**
- [ ] Deploy user documentation
- [ ] Create PM training materials
- [ ] Set up monitoring dashboards
- [ ] Document troubleshooting procedures

## 🔧 **Technical Implementation**

### **Phase 1: Core Deployment** (2 hours)
```bash
# 1. Deploy GitHub Actions workflow
cp .github/workflows/agent-assignment-pm.yml .github/workflows/
git add .github/workflows/agent-assignment-pm.yml
git commit -m "Deploy agent assignment workflow to dev"
git push origin develop

# 2. Verify label configuration
./setup-agent-labels.sh

# 3. Deploy cost monitoring
python deploy-cost-monitoring.py --env=dev
```

### **Phase 2: Integration Testing** (2 hours)
```bash
# 1. Run comprehensive test suite
./test-agent-assignment.sh --full-suite

# 2. Test PM workflows
python test-pm-integration.py

# 3. Validate cost optimization
python validate-cost-monitoring.py
```

### **Phase 3: Monitoring & Documentation** (1-2 hours)
```bash
# 1. Deploy monitoring dashboards
python deploy-monitoring-dashboard.py --env=dev

# 2. Generate deployment report
python generate-deployment-report.py
```

## 💰 **Cost Analysis**

### **Development Environment Costs**
- **Agent System**: $8-12/month (95% optimized)
- **Monitoring**: $2-3/month
- **Storage**: $1-2/month
- **Total Dev Cost**: ~$15/month

### **Cost Optimization Features**
- Spot instance deployment (95% savings)
- Intelligent workload distribution
- Auto-scaling based on demand
- PM-controlled budget alerts

## 🎯 **Success Metrics**

### **Performance Targets**
- ⚡ **Assignment Speed**: < 30 seconds average
- 💰 **Cost Efficiency**: 95%+ savings vs traditional methods
- 🎯 **Assignment Accuracy**: 90%+ correct agent selection
- 📊 **PM Satisfaction**: Successful override capabilities

### **Quality Gates**
- [ ] All 15 agent types can be assigned
- [ ] PM approval workflow functions correctly
- [ ] Cost monitoring alerts trigger properly
- [ ] Dashboard shows real-time status
- [ ] No critical bugs in assignment logic

## 📁 **Files to Deploy**

### **Core System Files**
- `.github/workflows/agent-assignment-pm.yml`
- `pm-agent-config.json`
- `cost-monitoring-pm-integration.json`
- `setup-agent-labels.sh`

### **Testing & Validation**
- `test-agent-assignment.sh`
- `test-pm-integration.py`
- `validate-cost-monitoring.py`

### **Documentation**
- `AGENT_FIELDS_SETUP_COMPLETE.md`
- `AGENT_SYSTEM_INTEGRATION_SUMMARY.md`
- `PM_TRAINING_GUIDE.md`

## 🚨 **Risk Assessment**

### **Low Risk**
- Label configuration (easily reversible)
- Cost monitoring setup (read-only initially)
- Documentation deployment

### **Medium Risk**
- GitHub Actions workflow (test thoroughly)
- PM notification system (validate endpoints)
- Dashboard integration (monitor performance)

### **Mitigation Strategies**
- Deploy to feature branch first
- Comprehensive testing before merge
- Rollback plan documented
- PM approval before production

## 🔄 **Rollback Plan**

If issues occur:
1. **Disable GitHub Actions**: Comment out workflow triggers
2. **Revert Labels**: Run label cleanup script
3. **Stop Monitoring**: Disable cost monitoring alerts
4. **Restore Previous**: Git revert to last stable commit

## 📊 **Monitoring & Alerts**

### **Key Metrics to Monitor**
- Assignment success rate
- Average assignment time
- Cost optimization percentage
- PM approval response time
- System error rates

### **Alert Thresholds**
- Assignment failures > 5%
- Cost increases > 10%
- PM approval delays > 4 hours
- System errors > 1%

## 🎉 **Definition of Done**

- [ ] All acceptance criteria completed
- [ ] Test suite passes 100%
- [ ] PM can successfully assign/override agents
- [ ] Cost monitoring shows 95%+ optimization
- [ ] Dashboard displays real-time metrics
- [ ] Documentation is complete and accessible
- [ ] Rollback procedures tested
- [ ] Team training completed

## 📞 **Stakeholders**

- **PM**: @pm-agent (approval required)
- **DevOps**: @devops-team (deployment support)
- **QA**: @qa-team (testing validation)
- **Development Team**: @dev-team (integration support)

---

**🎯 Ready for Development Environment Deployment**  
**💰 Cost Optimized • 🚀 PM Integrated • 📊 Fully Monitored**

Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
Environment: Development  
Deployment Type: Agent Assignment System with PM Integration"""

    return title, body

def deploy_story():
    """Deploy the story to GitHub Issues"""
    
    print("🚀 Creating deployment story for agent assignment system...")
    
    title, body = create_deployment_story()
    
    # Create labels for the story (using existing labels)
    labels = [
        "enhancement",
        "priority:P1-high", 
        "assigned:pm-agent",
        "status:assigned",
        "pm-approval:pending"
    ]
    
    try:
        # Create the GitHub issue
        cmd = [
            'gh', 'issue', 'create',
            '--repo', 'NiroAgentV2/autonomous-business-system',
            '--title', title,
            '--body', body,
            '--label', ','.join(labels)
        ]
        
        print("📝 Creating GitHub issue...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        issue_url = result.stdout.strip()
        print(f"✅ Deployment story created: {issue_url}")
        
        # Extract issue number
        issue_number = issue_url.split('/')[-1]
        
        print("\n🎯 Story Details:")
        print(f"  📋 Issue: #{issue_number}")
        print(f"  🔗 URL: {issue_url}")
        print(f"  🏷️ Labels: {', '.join(labels)}")
        print(f"  ⚡ Priority: P1 - High")
        print(f"  👤 Assigned: PM Agent")
        print(f"  📊 Status: Assigned (pending PM approval)")
        
        print("\n📋 Next Steps:")
        print("  1. PM reviews and approves deployment plan")
        print("  2. DevOps team prepares dev environment") 
        print("  3. Execute deployment phases 1-3")
        print("  4. Run comprehensive testing")
        print("  5. Generate deployment report")
        
        # Create deployment checklist file
        create_deployment_checklist(issue_number)
        
        return issue_url
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create GitHub issue: {e}")
        print(f"Error output: {e.stderr}")
        return None

def create_deployment_checklist(issue_number):
    """Create deployment checklist file"""
    
    checklist_content = f"""# 🚀 Agent Assignment System - Dev Deployment Checklist

**Issue**: #{issue_number}  
**Environment**: Development  
**Date**: {datetime.now().strftime('%Y-%m-%d')}

## 📋 Pre-Deployment Checklist

### **Infrastructure Preparation**
- [ ] Dev environment provisioned
- [ ] GitHub Actions permissions configured
- [ ] PM notifications set up
- [ ] Cost monitoring enabled
- [ ] Rollback procedures documented

### **Code Deployment**
- [ ] GitHub Actions workflow deployed
- [ ] Agent labels configured
- [ ] PM configuration deployed
- [ ] Cost monitoring integrated
- [ ] Documentation updated

## 🔧 Deployment Commands

### **Phase 1: Core System**
```bash
# Deploy workflow
git checkout develop
cp .github/workflows/agent-assignment-pm.yml .github/workflows/
git add .github/workflows/agent-assignment-pm.yml
git commit -m "Deploy agent assignment workflow to dev"
git push origin develop

# Setup labels
./setup-agent-labels.sh

# Deploy PM config
cp pm-agent-config.json config/dev/
cp cost-monitoring-pm-integration.json config/dev/
```

### **Phase 2: Testing**
```bash
# Run test suite
./test-agent-assignment.sh --env=dev --full-suite

# Test PM integration
python test-pm-integration.py --env=dev

# Validate cost monitoring
python validate-cost-monitoring.py --env=dev
```

### **Phase 3: Validation**
```bash
# Deploy monitoring
python deploy-monitoring-dashboard.py --env=dev

# Generate report
python generate-deployment-report.py --env=dev
```

## ✅ Post-Deployment Validation

### **Functional Testing**
- [ ] Create test issue (frontend task)
- [ ] Verify automatic assignment works
- [ ] Test PM override capability
- [ ] Validate status progression
- [ ] Check cost monitoring alerts

### **Performance Testing**
- [ ] Assignment speed < 30 seconds
- [ ] Dashboard loads < 3 seconds
- [ ] Cost optimization > 95%
- [ ] PM notifications deliver < 1 minute

### **Integration Testing**
- [ ] GitHub Actions trigger correctly
- [ ] Labels apply automatically
- [ ] PM approval workflow functions
- [ ] Cost alerts trigger at thresholds
- [ ] Dashboard shows real-time data

## 📊 Success Criteria

- ✅ All 15 agent types assignable
- ✅ PM can override any assignment
- ✅ Cost optimization maintains 95%+
- ✅ Dashboard shows live metrics
- ✅ No critical deployment errors

## 🚨 Rollback Triggers

If any of these occur, execute rollback:
- Assignment failure rate > 5%
- Cost increases > 10%
- Critical system errors
- PM approval workflow broken
- Dashboard unavailable > 15 minutes

---

**Deployment Owner**: PM Agent  
**Technical Lead**: DevOps Team  
**Environment**: Development  
**Status**: Ready for Deployment"""

    with open(f"dev-deployment-checklist-{issue_number}.md", "w", encoding='utf-8') as f:
        f.write(checklist_content)
    
    print(f"📄 Deployment checklist created: dev-deployment-checklist-{issue_number}.md")

if __name__ == "__main__":
    print("🎯 Agent Assignment System - Dev Deployment Story Creator")
    print("=" * 60)
    
    issue_url = deploy_story()
    
    if issue_url:
        print("\n🎉 SUCCESS: Deployment story created and ready for PM approval!")
        print("💼 The PM agent can now review and approve this deployment plan.")
        print("🚀 Once approved, DevOps can proceed with development deployment.")
    else:
        print("\n❌ FAILED: Could not create deployment story.")
        print("Please check GitHub CLI authentication and repository access.")
