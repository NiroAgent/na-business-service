# AWS Environment Costs Breakdown

## Current Running Resources

### EC2 Instances (3 running)
| Instance | Purpose | Type | Hourly Cost | Daily Cost | Monthly Cost |
|----------|---------|------|-------------|------------|--------------|
| i-0b3d9893712d5a6f9 | Bastion/HTTPS Proxy | t3.nano | $0.0052 | $0.12 | $3.74 |
| i-0af59b7036f7b0b77 | VF-Dev AI Agents | t3.large | $0.0832 | $2.00 | $60.00 |
| i-0af59b7036f7b0b77 | **Container Host** | m5.large | $0.096 | $2.30 | $69.12 |

### RDS Database
| Database | Type | Estimated Monthly |
|----------|------|------------------|
| dev-visualforge-database | Aurora Serverless PostgreSQL | ~$50-80 |

### Other Services
- ElastiCache: ~$7/month
- WAF: ~$2/month
- CloudWatch: ~$1/month
- VPC/Networking: ~$1/month
- ECR (Container Registry): ~$0.15/month

## Total Costs by Environment

### 1. Development Environment (vf-dev)
- **AI Agent Instance (t3.large)**: $60/month
- **Aurora Serverless DB**: ~$50/month
- **Supporting Services**: ~$10/month
- **Subtotal**: ~$120/month

### 2. Container Infrastructure
- **Container Host (m5.large)**: $69/month
- **ECR Storage**: ~$0.15/month
- **Subtotal**: ~$69/month

### 3. Network/Security
- **Bastion/Proxy (t3.nano)**: $3.74/month
- **WAF**: ~$2/month
- **Subtotal**: ~$6/month

## Summary

### Current Month-to-Date (Aug 1-19)
**TOTAL INCURRED: $197.61**

### Daily Breakdown
- **Current daily rate**: $10.40/day
- Container host: $2.30/day
- AI agents: $2.00/day
- Database: ~$1.60/day
- Other services: ~$4.50/day

### Projected Monthly Total (31 days)
**$322/month**

## Cost by Purpose

| Purpose | Monthly Cost | % of Total | Status |
|---------|-------------|------------|--------|
| Development/Testing (vf-dev) | $120 | 37% | ✅ Optimized |
| Container Infrastructure | $69 | 21% | ✅ Required |
| Database (Aurora) | $50 | 16% | 🔍 Can optimize |
| Other AWS Services | $79 | 25% | 🔍 Review needed |
| Network/Security | $4 | 1% | ✅ Minimal |
| **TOTAL** | **$322** | **100%** | |

## Optimization Opportunities

### Already Completed Today:
✅ Reduced AI agent test frequency (saving ~$10/month)
✅ Stopped excessive monitoring
✅ Set up billing alerts

### Additional Savings Available:

1. **Schedule AI Agents** (Save $42/month)
   - Stop nights/weekends
   - Use: `./instance-scheduler.sh stop`

2. **Pause Aurora DB When Idle** (Save $25/month)
   - Stop during non-testing hours
   ```bash
   aws rds stop-db-cluster --db-cluster-identifier dev-visualforge-database
   ```

3. **Container Host Optimization**
   - Consider if m5.large is right-sized
   - Could use spot instances for non-production (70% savings)

## What You Owe

### August 2025 (as of Aug 19)
- **Already charged**: $197.61
- **Remaining days (12)**: ~$125
- **Total August estimate**: ~$322

### Going Forward (with current setup)
- **Monthly**: ~$322
- **Annual**: ~$3,864

### With Optimizations
- **Monthly**: ~$230 (save $92/month)
- **Annual**: ~$2,760 (save $1,104/year)

## Action Items

1. ✅ Container host (m5.large) - Confirmed needed for containers
2. 📅 Schedule AI agents for business hours only
3. 📅 Set up Aurora auto-pause for idle periods
4. 📊 Review "Other AWS Services" consuming 25% of budget