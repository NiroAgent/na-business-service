# Agent Instructions - Autonomous Business Operations

## Quick Start Guide

### For New Developers
1. Clone the repository
2. Install Python 3.x and pip
3. Install GitHub CLI: `gh auth login`
4. Run demo: `python ai-[agent]-agent.py --demo`
5. Test coordinator: `python agent-policy-coordinator.py --once`

### For Operations Team
1. Create GitHub issue with proper labels
2. Agents automatically process based on priority
3. Monitor progress in issue comments
4. Check status report: AUTONOMOUS_BUSINESS_STATUS.md

## Agent Execution Instructions

### Individual Agent Testing
```bash
# Basic demo mode
python ai-security-agent.py --demo

# Process specific issue
python ai-security-agent.py --process-issue 123 --issue-data issue_123.json

# Get help
python ai-security-agent.py --help
```

### Coordinator Operations
```bash
# One-time processing of all issues
python agent-policy-coordinator.py --once

# Continuous monitoring (runs every 60 seconds)
python agent-policy-coordinator.py --monitor

# Check specific issue
gh issue view 123 --repo VisualForgeMediaV2/business-operations
```

## Creating Business Operations

### Issue Template
```markdown
## Operation Request
**Type**: [security/finance/analytics/operations/support/marketing/sales]
**Priority**: [P0/P1/P2/P3]
**Requester**: [Name/Team]

### Description
Detailed description of the business operation needed.

### Success Criteria
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Criteria 3

### Additional Context
Any relevant information, links, or dependencies.
```

### Label Structure
Always include:
1. Operation type label (e.g., `security/compliance`)
2. Priority label (e.g., `priority/P1`)
3. Optional: `agent/[agent-name]` for direct assignment

## Agent Capabilities Reference

### Security Agent (`ai-security-agent`)
- Threat detection and response
- Compliance audits
- Access control management
- Security incident handling

### Finance Agent (`ai-finance-agent`)
- Budget analysis
- Expense tracking
- Financial reporting
- Compliance verification

### Analytics Agent (`ai-analytics-agent`)
- Data analysis
- Report generation
- KPI tracking
- Business intelligence

### Operations Agent (`ai-operations-agent`)
- System monitoring
- Performance optimization
- Infrastructure management
- Health checks

### Support Agent (`ai-support-agent`)
- Customer issue resolution
- Quality assurance
- Documentation updates
- Support ticket processing

### Customer Success Agent (`ai-customer-success-agent`)
- User experience research
- Customer feedback analysis
- Retention strategies
- Success metrics

### Marketing Agent (`ai-marketing-agent`)
- Campaign management
- Content creation
- Market analysis
- Brand management

### Sales Agent (`ai-sales-agent`)
- Lead management
- Pipeline tracking
- Sales reporting
- Customer acquisition

### Project Manager Agent (`ai-project-manager-agent`)
- Executive oversight
- Resource allocation
- Escalation handling
- KPI monitoring

## Troubleshooting Guide

### Common Issues

#### Agent Not Processing Issue
```bash
# Check if agent has proper argument handling
python ai-agent-name.py --help

# Verify issue has correct labels
gh issue view [number] --repo VisualForgeMediaV2/business-operations

# Test with mock data
echo '{"title":"Test","labels":[{"name":"security/compliance"}]}' > test.json
python ai-security-agent.py --process-issue 1 --issue-data test.json
```

#### GitHub API Errors
```bash
# Check authentication
gh auth status

# Refresh token
gh auth refresh

# Test API access
gh issue list --repo VisualForgeMediaV2/business-operations
```

#### Coordinator Not Finding Issues
```bash
# Check repository access
gh repo view VisualForgeMediaV2/business-operations

# List all open issues
gh issue list --state open --repo VisualForgeMediaV2/business-operations

# Check label configuration
gh label list --repo VisualForgeMediaV2/business-operations
```

## AWS Deployment Instructions

### Prerequisites
1. AWS CLI installed and configured
2. Docker installed
3. ECR repository created
4. IAM roles configured

### Build and Deploy
```bash
# Build Docker image
docker build -t ai-agents .

# Tag for ECR
docker tag ai-agents:latest [account].dkr.ecr.[region].amazonaws.com/ai-agents:latest

# Push to ECR
aws ecr get-login-password --region [region] | docker login --username AWS --password-stdin [account].dkr.ecr.[region].amazonaws.com
docker push [account].dkr.ecr.[region].amazonaws.com/ai-agents:latest

# Deploy infrastructure
bash aws-infrastructure-setup.sh

# Test deployment
aws batch submit-job \
  --job-name test-agent \
  --job-queue ai-agents-queue \
  --job-definition ai-agent-fargate
```

### GitHub Actions Setup
1. Add repository secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `GITHUB_TOKEN`

2. Enable Actions:
   ```bash
   gh workflow enable agent-processor.yml --repo VisualForgeMediaV2/business-operations
   ```

3. Test workflow:
   ```bash
   gh workflow run agent-processor.yml --repo VisualForgeMediaV2/business-operations
   ```

## Monitoring and Metrics

### Local Monitoring
```bash
# Watch coordinator output
python agent-policy-coordinator.py --monitor | tee agent.log

# Check processing metrics
grep "WORK SUMMARY" agent.log

# View completed issues
gh issue list --state closed --label "status/done" --repo VisualForgeMediaV2/business-operations
```

### AWS CloudWatch (When Deployed)
```bash
# View Batch job logs
aws logs tail /aws/batch/job --follow

# Check Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=agent-processor \
  --start-time 2025-08-19T00:00:00Z \
  --end-time 2025-08-19T23:59:59Z \
  --period 3600 \
  --statistics Average
```

## Best Practices

### Issue Creation
1. Use clear, descriptive titles
2. Include all necessary context
3. Set appropriate priority
4. Add relevant labels
5. Link related issues

### Agent Development
1. Follow the template structure
2. Implement proper error handling
3. Add logging for debugging
4. Test with mock data first
5. Document new capabilities

### System Maintenance
1. Regular status report reviews
2. Monitor SLA compliance
3. Update documentation
4. Archive completed issues
5. Performance optimization

## Emergency Procedures

### Critical Issue (P0)
1. Create issue with `priority/P0` label
2. Coordinator triggers immediate processing
3. Project Manager notified automatically
4. Lambda function executes within minutes
5. Status updates posted to issue

### System Recovery
```bash
# Stop all processing
pkill -f agent-policy-coordinator

# Clear stuck issues
for issue in $(gh issue list --label "processing" --json number -q ".[].number"); do
  gh issue edit $issue --remove-label "processing" --add-label "retry"
done

# Restart coordinator
python agent-policy-coordinator.py --monitor
```

### Rollback Procedure
```bash
# Revert to previous version
git checkout [previous-commit]

# Test agents
for agent in ai-*-agent.py; do
  python $agent --demo
done

# If successful, create hotfix
git checkout -b hotfix/agent-recovery
git push origin hotfix/agent-recovery
```

## Performance Tuning

### Optimization Settings
```python
# In agent-policy-coordinator.py
RATE_LIMIT_DELAY = 2  # Seconds between API calls
MONITORING_INTERVAL = 60  # Seconds between cycles
MAX_PARALLEL_AGENTS = 5  # Concurrent agent executions
TIMEOUT_SECONDS = 60  # Agent execution timeout
```

### Resource Limits
- Lambda: 3GB memory, 15-minute timeout
- Fargate: 0.25 vCPU, 512MB memory
- Batch: 2 retry attempts, 300-second timeout

## Support and Contact

### Internal Support
- Create issue with `help/agent` label
- Check AUTONOMOUS_BUSINESS_STATUS.md
- Review agent logs

### Documentation
- Design: AUTONOMOUS_BUSINESS_DESIGN.md
- Status: AUTONOMOUS_BUSINESS_STATUS.md
- Context: CLAUDE.md
- This file: AGENT_INSTRUCTIONS.md

### Repositories
- Main: https://github.com/VisualForgeMediaV2/business-operations
- Issues: https://github.com/VisualForgeMediaV2/business-operations/issues

---

**Version**: 1.0
**Last Updated**: August 2025
**Maintained By**: AI Project Manager Agent