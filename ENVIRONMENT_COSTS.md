# AWS Environment Costs Breakdown

## Current Running Resources

### EC2 Instances (3 running)
| Instance | Name | Type | Hourly Cost | Daily Cost | Monthly Cost |
|----------|------|------|-------------|------------|--------------|
| i-0b3d9893712d5a6f9 | BastionHTTPSProxy | t3.nano | $0.0052 | $0.12 | $3.74 |
| i-0af59b7036f7b0b77 | vf-dev-agent-instance | t3.large | $0.0832 | $2.00 | $60.00 |
| i-0c8fef744add7803c | (Unnamed) | m5.large | $0.096 | $2.30 | $69.12 |

### RDS Database
| Database | Type | Estimated Monthly |
|----------|------|------------------|
| dev-visualforge-database | Aurora Serverless | ~$50-80 |

### Other Services
- ElastiCache: ~$7/month
- WAF: ~$2/month
- CloudWatch: ~$1/month
- VPC/Networking: ~$1/month

## Total Costs by Environment

### Development Environment (vf-dev)
- **EC2 Agent Instance (t3.large)**: $60/month
- **Aurora Serverless DB**: ~$50/month
- **Supporting Services**: ~$10/month
- **TOTAL**: ~$120/month

### Bastion/Proxy
- **EC2 Bastion (t3.nano)**: $3.74/month
- **TOTAL**: ~$4/month

### Unknown/Other Environment
- **EC2 m5.large instance**: $69/month
- **TOTAL**: ~$69/month

## Summary

### Current Month-to-Date (Aug 1-19)
**TOTAL: $197.61**

### Daily Average
**$10.40/day**

### Projected Monthly Total (31 days)
**$322/month**

## Cost by Environment

| Environment | Monthly Cost | % of Total |
|-------------|-------------|------------|
| Development (vf-dev) | $120 | 37% |
| Unknown m5.large | $69 | 21% |
| Database (Aurora) | $50 | 16% |
| Other Services | $79 | 25% |
| Bastion | $4 | 1% |
| **TOTAL** | **$322** | **100%** |

## Recommendations

1. **URGENT**: Identify the unnamed m5.large instance - it's costing $69/month
2. **vf-dev**: Already optimized, can reduce further to $18/month with scheduling
3. **Database**: Consider pausing Aurora Serverless when not in use
4. **Unknown instance**: Should be investigated and possibly terminated if not needed

## What You Owe Right Now

Based on August 1-19 usage:
- **Already incurred**: $197.61
- **Daily run rate**: $10.40
- **End of month projection**: ~$322

To reduce costs immediately:
1. Stop the unknown m5.large instance (save $2.30/day)
2. Stop vf-dev agents overnight (save $1.33/day)
3. Pause Aurora DB when not testing (save $1.60/day)