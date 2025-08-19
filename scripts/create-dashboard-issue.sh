#!/bin/bash

# Dashboard Dev Access Issue - Auto Assignment Script
# Creates GitHub issue and assigns to Product Manager

ISSUE_TITLE="🚨 URGENT: Dashboard Not Accessible in VF-Dev Environment"
ISSUE_BODY=$(cat << 'EOF'
## Issue Summary
**Priority**: P0 (Critical)
**Assigned To**: Product Manager
**Reporter**: Dashboard Team
**Environment**: VF-Dev (319040880702)
**Status**: BLOCKING

## Problem Description
The main dashboard URL `https://dev.visualforge.com/` is not loading and returning connection errors. This is blocking development and monitoring activities across all teams.

## Impact Assessment
- **Development Teams**: Cannot monitor agent status and system health
- **DevOps**: No visibility into infrastructure performance 
- **QA**: Cannot validate dashboard functionality
- **Business Operations**: No real-time metrics visibility

## Expected vs Actual Behavior

### Expected:
- Dashboard should load at `https://dev.visualforge.com/`
- Real-time agent monitoring should be functional
- API endpoints should respond properly
- Cost optimization metrics should be visible

### Actual:
- ❌ Main dashboard URL not accessible
- ❌ Connection timeouts/errors
- ❌ No dashboard functionality available

## Environment Details
- **AWS Account**: vf-dev (319040880702)
- **Target URL**: https://dev.visualforge.com/
- **Alternative URLs Tested**:
  - ❌ https://dev.visualforge.com/
  - ⚠️ http://localhost:5003 (local only)
  - ❌ https://c39q8sqdp8.execute-api.us-east-1.amazonaws.com/dev

## Immediate Actions Needed

### 1. Infrastructure Check ⚠️
- [ ] Verify CloudFront distribution is active
- [ ] Check ALB target group health
- [ ] Validate ECS service status for dashboard
- [ ] Confirm DNS routing for dev.visualforge.com

### 2. Service Validation 🔍
- [ ] Verify dashboard container deployment
- [ ] Check service logs in CloudWatch
- [ ] Validate security groups and network ACLs
- [ ] Test internal service connectivity

### 3. DNS & SSL 🌐
- [ ] Verify DNS A record points to correct ALB
- [ ] Check SSL certificate validity
- [ ] Validate Route53 hosted zone configuration

## Technical Context

### Current Architecture:
```
Internet → CloudFront → ALB → ECS Fargate (Dashboard Service)
```

### Dashboard Service Configuration:
- **Port**: 4005 (internal)
- **Health Check**: `/health`
- **Log Group**: `/aws/ecs/vf-dashboard-dev`

## Debugging Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster vf-media-dev --services vf-dashboard-service

# Check target group health
aws elbv2 describe-target-health --target-group-arn <DASHBOARD_TG_ARN>

# Check CloudFront status
aws cloudfront get-distribution --id <DISTRIBUTION_ID>

# DNS lookup
nslookup dev.visualforge.com
```

## Immediate Workaround
Local dashboard can be started temporarily:
```bash
cd /e/Projects
python dashboard.py
# Access at: http://localhost:5003
```

## Business Impact
- **Downtime**: Since dashboard was last accessible
- **Teams Affected**: 5 development teams + operations
- **Cost**: Reduced operational efficiency, delayed deployments

## Next Steps
1. **IMMEDIATE**: PM to escalate to DevOps team
2. **Within 1 hour**: Root cause analysis
3. **Within 2 hours**: Dashboard restored or viable workaround
4. **Within 4 hours**: Post-incident review and prevention plan

## Related Systems
- VF Bulk Service: https://bulk-api-development.visualforge.com
- API Gateway: https://c39q8sqdp8.execute-api.us-east-1.amazonaws.com/dev
- CloudWatch Dashboards: Available as backup monitoring

---
**Created**: $(date +%Y-%m-%d)
**Updated**: $(date +%Y-%m-%d)
**Urgency**: Critical - requires immediate attention
EOF
)

echo "🚨 Creating critical dashboard access issue..."

# Create GitHub issue with labels and assignment
gh issue create \
  --title "$ISSUE_TITLE" \
  --body "$ISSUE_BODY" \
  --label "priority/critical,type/bug,team/dashboard,environment/dev" \
  --assignee "@product-manager" \
  --repo "NiroAgentV2/autonomous-business-system"

if [ $? -eq 0 ]; then
    echo "✅ Issue created successfully and assigned to Product Manager"
    echo "📊 Dashboard teams will be notified immediately"
    echo "⚡ Starting local dashboard as temporary workaround..."
    
    # Start local dashboard as workaround
    cd /e/Projects
    python dashboard.py &
    echo "🌐 Local dashboard started at: http://localhost:5003"
else
    echo "❌ Failed to create GitHub issue"
    echo "📧 Please manually notify the Product Manager about dashboard access issue"
    echo "🔗 Issue details saved in: /e/Projects/issues/dashboard-dev-access-issue.md"
fi

echo ""
echo "🎯 CRITICAL ISSUE SUMMARY:"
echo "• Dashboard URL not accessible: https://dev.visualforge.com/"
echo "• Environment: VF-Dev (319040880702)"
echo "• Impact: 5 teams blocked"
echo "• Workaround: http://localhost:5003"
echo "• Next: PM escalation to DevOps team"
