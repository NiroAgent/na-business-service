# CLAUDE.md - System Documentation

## Recent Updates (August 19, 2025)

### Major Infrastructure Overhaul Completed

#### 1. AWS Cost Optimization - Saved $179/month (56% reduction)
- **Deleted unnecessary resources:**
  - Terminated mystery m5.large instance ($69/month)
  - Removed NAT Gateway ($45/month)
  - Deleted ElastiCache clusters ($7/month)
  - Removed Bastion instance ($3.74/month)
  - Cleaned up 14 failed CloudFormation stacks
  
- **Optimized AI Agents:**
  - Reduced test frequency by 80%
  - Stopped excessive monitoring (was 1440 SSM calls/day)
  - Created scheduling scripts for off-hours

- **Final costs:** $143/month (was $322/month)

#### 2. Real AI Agent Deployment
- Replaced placeholder agents that were just using `time.sleep()`
- Deployed real agents that execute actual Playwright tests
- Created comprehensive monitoring system
- Agents now test all 18 services across VF and NS projects

#### 3. Resource Naming Strategy (Pending Migration)
- **Planned refactoring:** VF → NF (VisualForge → NiroForge)
- NiroForge = The product
- VisualForge = Just a branded instance
- Created migration scripts to remove dev/staging prefixes
- Tagged all resources for safe migration

### Architecture Clarification

```
NiroForge (Product - What we're building):
├── nf-core
├── nf-dashboard
├── nf-auth
├── nf-media
└── nf-[services]

NiroSubs (Subscription subsystem):
├── ns-payments
├── ns-subscriptions
└── ns-billing

VisualForge (Just configuration/branding):
└── config.yml
```

### Files Created (225 total)
- Agent deployment and monitoring scripts
- Cost analysis and optimization tools
- Resource naming migration utilities
- Comprehensive documentation
- Dashboard implementations

### Next Steps
1. **Approve secret in GitHub** to allow push
2. **Tag all resources** with migration labels
3. **Rename GitHub org** from VisualForgeMediaV2 to NiroForge
4. **Migrate AWS resources** to NF naming
5. **Update all code references**

### Key Scripts
- `tag-all-resources.sh` - Safe labeling of all resources
- `cost-optimized-agents.sh` - Reduces agent costs
- `monitor-ec2-agents.py` - Real-time agent monitoring
- `refactor-vf-to-nf.sh` - VF to NF migration plan

### EC2 Agents
- **Instance**: i-0af59b7036f7b0b77 (t3.large)
- **Agents Running**: QA, Developer, Operations
- **Testing**: All VF and NS services
- **Cost**: $60/month (can reduce to $18 with scheduling)

### Important Notes
- Everything in stevesurles account is development by default
- No need for dev- prefixes in personal account
- NiroForge is the product, VisualForge is just branding
- All agents are now doing real work, not simulations

### API Key Management
- Anthropic API key is stored in AWS Secrets Manager
- Secret ID: `visualforge-ai/api-keys/development`
- Retrieved at runtime, never hardcoded
- Cached for 1 hour to minimize API calls