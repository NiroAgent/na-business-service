# Agent Task Issue Template

## Quick Template for Creating Agent Tasks

Copy this template when creating new agent task issues:

```markdown
Service: [service-name]
Environment: dev
Phase: develop

## Context
All agents must read: E:/Projects/MASTER_SDLC_AGENT_INSTRUCTIONS.md

## Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## References
- System Architecture: E:/Projects/AI_AGENT_INSTRUCTIONS.md
- Deployment Guide: E:/Projects/DEPLOYMENT-GUIDE.md
- Service Structure: E:/Projects/NIROSUBS_STRUCTURE_SUMMARY.md

## Success Criteria
- Tests pass
- Coverage > 80%
- No critical issues

## Labels
agent-task, sdlc, [phase]
```

## Example Issues

### Example 1: Test Service
```markdown
Title: [SDLC] Test ns-auth service
Labels: agent-task, sdlc, test

Service: ns-auth
Environment: dev
Phase: test

## Context
All agents must read: E:/Projects/MASTER_SDLC_AGENT_INSTRUCTIONS.md

## Tasks
- [ ] Run unit tests
- [ ] Check coverage
- [ ] Run integration tests
- [ ] Security scan

## References
- System Architecture: E:/Projects/AI_AGENT_INSTRUCTIONS.md
- Testing Strategy: E:/Projects/CICD_INFRASTRUCTURE_DELTA_ANALYSIS.md
```

### Example 2: Full SDLC Iteration
```markdown
Title: [SDLC] Complete iteration for vf-audio-service
Labels: agent-task, sdlc

Service: vf-audio-service
Environment: dev
Phase: develop

## Context
All agents must read: E:/Projects/MASTER_SDLC_AGENT_INSTRUCTIONS.md
Iterate through all phases until production-ready.

## Tasks
- [ ] Complete develop phase
- [ ] Complete test phase
- [ ] Complete deploy phase
- [ ] Complete document phase
- [ ] Iterate if needed

## References
- Full System Docs: E:/Projects/AI_AGENT_INSTRUCTIONS.md
- SDLC Process: E:/Projects/MASTER_SDLC_AGENT_INSTRUCTIONS.md
```

### Example 3: Production Deployment
```markdown
Title: [DEPLOY] Production deployment checklist for ns-payments
Labels: agent-task, sdlc, deploy, production

Service: ns-payments
Environment: production
Phase: deploy

## Context
CRITICAL: Production deployment - requires manual approval
All agents must read: E:/Projects/MASTER_SDLC_AGENT_INSTRUCTIONS.md

## Tasks
- [ ] Validate staging tests
- [ ] Review deployment guide: E:/Projects/DEPLOYMENT-GUIDE.md
- [ ] Check DNS configuration: E:/Projects/DNS_ARCHITECTURE.md
- [ ] Verify secrets: E:/Projects/AWS_PARAMETER_STORE_MIGRATION_STRATEGY.md
- [ ] Create rollback plan
- [ ] Get approval
- [ ] Deploy
- [ ] Monitor

## References
- Complete deployment process: E:/Projects/DEPLOYMENT-GUIDE.md
- Infrastructure: E:/Projects/AI_AGENT_INSTRUCTIONS.md
```