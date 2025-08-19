#!/usr/bin/env python3
"""
DevOps Deployment Story Creator
Creates GitHub issue for deploying dashboard to vf-dev and vf-staging environments
"""

import subprocess
import sys
from datetime import datetime

def create_deployment_issue():
    """Create deployment story for DevOps agent"""
    
    repo = "NiroAgentV2/autonomous-business-system"
    pm_username = "stevesurles"
    
    deployment_story = {
        "title": "🚀 DevOps: Deploy Enhanced Dashboard to vf-dev & vf-staging Environments",
        "body": """# 🚀 DevOps Deployment: Enhanced Dashboard to VF Environments

**STATUS: READY FOR DEVOPS DEPLOYMENT AFTER QA TESTING ✅**

## 📋 Deployment Story
**As a** DevOps engineer  
**I want** to deploy the enhanced dashboard to vf-dev and vf-staging environments  
**So that** the team can access the production-ready dashboard in cloud environments

## 🎯 Deployment Scope

### **Target Environments:**
- **vf-dev**: Development environment for team testing
- **vf-staging**: Staging environment for pre-production validation

### **Application Details:**
- **Source**: `enhanced-ec2-dashboard.py`
- **Type**: Flask + Socket.IO application
- **Port**: 5003
- **Dependencies**: flask, flask-socketio, psutil, boto3

## ✅ Prerequisites (Must Complete Before Deployment)

### **QA Validation Required:**
- [ ] All 7 tabs tested and functional
- [ ] Kill switch safety testing completed ⚠️ CRITICAL
- [ ] Cost monitoring accuracy validated
- [ ] Performance testing passed
- [ ] Cross-browser compatibility verified
- [ ] API endpoints integration tested

### **Infrastructure Requirements:**
- [ ] EC2 instances configured for vf-dev and vf-staging
- [ ] Security groups configured for port 5003
- [ ] Load balancer setup (if required)
- [ ] SSL certificates configured
- [ ] Environment variables configured

## 🔧 Technical Deployment Requirements

### **Environment Configuration:**
```bash
# Environment Variables Required
PORT=5003
FLASK_ENV=production  # or development for vf-dev
AWS_REGION=us-east-1
COST_MONITORING_ENABLED=true
ALERT_THRESHOLD=3.0
KILL_THRESHOLD=5.0
```

### **Dependencies Installation:**
```bash
pip install -r requirements.txt
# Required packages:
# flask>=2.0.0
# flask-socketio>=5.0.0
# psutil>=5.8.0
# boto3>=1.26.0
```

### **Application Startup:**
```bash
# Production startup command
python enhanced-ec2-dashboard.py

# Alternative with gunicorn for production
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5003 enhanced-ec2-dashboard:app
```

## 🚀 Deployment Steps

### **Phase 1: vf-dev Deployment**
1. [ ] **Pre-deployment Checklist**
   - Verify QA testing complete
   - Backup current vf-dev dashboard (if exists)
   - Prepare rollback plan

2. [ ] **Infrastructure Setup**
   - Configure EC2 instance with required specs
   - Set up security groups (port 5003 access)
   - Configure environment variables
   - Install Python dependencies

3. [ ] **Application Deployment**
   - Transfer `enhanced-ec2-dashboard.py` to vf-dev
   - Configure startup scripts
   - Start application service
   - Verify health check endpoints

4. [ ] **Post-deployment Validation**
   - Test all 7 dashboard tabs
   - Verify real-time updates working
   - Test kill switch functionality ⚠️
   - Validate cost monitoring accuracy
   - Confirm WebSocket connections stable

### **Phase 2: vf-staging Deployment**
5. [ ] **Staging Prerequisites**
   - vf-dev deployment successful and validated
   - All critical issues resolved
   - Performance benchmarks met

6. [ ] **Staging Deployment**
   - Mirror vf-dev configuration to staging
   - Deploy application with production settings
   - Configure monitoring and alerting
   - Set up log aggregation

7. [ ] **Staging Validation**
   - Full end-to-end testing
   - Load testing with multiple users
   - Security testing and validation
   - Performance monitoring setup

## 🔒 Security Considerations

### **Network Security:**
- [ ] Configure security groups for least privilege access
- [ ] Enable HTTPS/SSL for production traffic
- [ ] Set up VPC and subnet configurations
- [ ] Configure firewall rules

### **Application Security:**
- [ ] Environment variable security (no hardcoded secrets)
- [ ] Input validation for all API endpoints
- [ ] Rate limiting for API calls
- [ ] CORS configuration for allowed origins

## 📊 Monitoring & Alerting

### **Health Monitoring:**
- [ ] Application health check endpoint: `/health`
- [ ] System metrics monitoring (CPU, memory, disk)
- [ ] WebSocket connection monitoring
- [ ] Cost monitoring system alerts

### **Logging:**
- [ ] Application logs aggregation
- [ ] Error tracking and alerting
- [ ] Cost monitoring event logs
- [ ] Kill switch activation logs

## 🚨 Emergency Procedures

### **Rollback Plan:**
- [ ] Document current application version
- [ ] Prepare rollback scripts
- [ ] Test rollback procedures in dev environment
- [ ] Define rollback triggers and decision process

### **Kill Switch Testing:**
- [ ] Test emergency shutdown in dev environment ⚠️
- [ ] Validate cost spike simulation
- [ ] Verify manual override functionality
- [ ] Test recovery procedures

## 📈 Success Criteria

### **vf-dev Environment:**
- [ ] Dashboard accessible at https://vf-dev.example.com:5003
- [ ] All 7 tabs load within 3 seconds
- [ ] Real-time updates working every 3 seconds
- [ ] Kill switch responds within 30 seconds
- [ ] Cost monitoring accuracy within ±2%

### **vf-staging Environment:**
- [ ] Dashboard accessible at https://vf-staging.example.com:5003
- [ ] Production-level performance achieved
- [ ] Security scanning passed
- [ ] Load testing passed (10+ concurrent users)
- [ ] Monitoring and alerting functional

## 🔧 Technical Specifications

### **Server Requirements:**
- **CPU**: 2+ cores
- **Memory**: 4GB+ RAM
- **Storage**: 20GB+ SSD
- **Network**: 1Gbps+ bandwidth
- **OS**: Ubuntu 20.04+ or Amazon Linux 2

### **Performance Targets:**
- **Response Time**: <100ms for API endpoints
- **Page Load**: <3 seconds for dashboard
- **WebSocket Latency**: <50ms
- **Uptime**: 99.9% availability
- **Concurrent Users**: Support 25+ users

## 📋 DevOps Checklist

### **Pre-deployment:**
- [ ] QA testing completed and signed off
- [ ] Infrastructure provisioned and configured
- [ ] Security review completed
- [ ] Backup and rollback procedures tested

### **During Deployment:**
- [ ] Monitor application startup
- [ ] Verify all health checks pass
- [ ] Test critical functionality
- [ ] Monitor system resources

### **Post-deployment:**
- [ ] Comprehensive smoke testing
- [ ] Performance validation
- [ ] Security testing
- [ ] Documentation updated
- [ ] Team notification of successful deployment

## 🎯 Timeline & Dependencies

### **Dependencies:**
- **Blocker**: QA testing must be 100% complete
- **Blocker**: Kill switch safety validation required
- **Prerequisite**: Infrastructure provisioning
- **Prerequisite**: Security review approval

### **Estimated Timeline:**
- **vf-dev Deployment**: 4-6 hours
- **vf-dev Validation**: 2-4 hours  
- **vf-staging Deployment**: 2-4 hours
- **vf-staging Validation**: 4-6 hours
- **Total**: 12-20 hours over 2-3 days

## 📞 Escalation & Support

### **Primary Contacts:**
- **DevOps Lead**: [To be assigned]
- **QA Lead**: [To be assigned]  
- **Security Team**: [To be assigned]
- **PM**: stevesurles

### **Emergency Contacts:**
- **On-call DevOps**: [Emergency contact]
- **Infrastructure Team**: [Emergency contact]
- **Security Incident Response**: [Emergency contact]

---

**🚨 CRITICAL SAFETY NOTE:**
The kill switch functionality MUST be thoroughly tested in vf-dev before staging deployment. This system has the ability to automatically shutdown all agents and requires careful validation.

**⚠️ DEPLOYMENT BLOCKER:**
This deployment cannot proceed until GitHub Issue #9 (QA Testing) is marked complete and the kill switch safety has been validated.

**🎯 Success Definition:**
Deployment is considered successful when both vf-dev and vf-staging environments are running the enhanced dashboard with all 7 tabs functional, cost monitoring active, and kill switch tested and operational.

---
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Dependencies**: Issues #1-#9 (Complete QA Testing Required)
**Environments**: vf-dev, vf-staging
**Priority**: HIGH - Ready for DevOps after QA completion ✅"""
    }
    
    print("🚀 Creating DevOps Deployment Story...")
    
    # Create the GitHub issue
    cmd = [
        "gh", "issue", "create",
        "--repo", repo,
        "--title", deployment_story["title"],
        "--body", deployment_story["body"],
        "--assignee", pm_username
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issue_url = result.stdout.strip()
        print(f"✅ Created Deployment Story: {issue_url}")
        return issue_url
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating deployment issue: {e}")
        print(f"   Error: {e.stderr}")
        return None

def main():
    """Main execution"""
    print("🚀 DevOps Deployment Story Creator")
    print("=" * 50)
    
    # Check GitHub CLI
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        print("✅ GitHub CLI available")
        
        # Create the deployment issue
        issue_url = create_deployment_issue()
        
        if issue_url:
            print(f"\n✅ Successfully created DevOps deployment story!")
            print(f"🔗 Issue URL: {issue_url}")
            print("\n📋 Deployment Story Summary:")
            print("  • Target Environments: vf-dev, vf-staging")
            print("  • Prerequisites: Complete QA testing required")
            print("  • Critical: Kill switch safety validation")
            print("  • Timeline: 12-20 hours over 2-3 days")
            print("  • Assigned to: stevesurles (PM)")
            
            print("\n🚨 Important Notes:")
            print("  • Deployment BLOCKED until QA testing complete")
            print("  • Kill switch testing is CRITICAL for safety")
            print("  • Both environments require full validation")
            print("  • Rollback procedures must be tested")
            
            print("\n🎯 Next Steps:")
            print("  1. Complete QA testing (Issue #9)")
            print("  2. Validate kill switch safety")
            print("  3. Provision infrastructure")
            print("  4. Execute deployment plan")
        else:
            print("\n❌ Failed to create deployment story.")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GitHub CLI not found or not authenticated")
        print("   Please install and authenticate: gh auth login")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
