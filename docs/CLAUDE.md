

## CRITICAL: DELEGATION POLICY

### MY #1 RULE: DELEGATE EVERYTHING THROUGH THE SYSTEM

I must ONLY:
1. Create ONE issue to a manager
2. Monitor progress
3. Nothing else

### Delegation Pattern:
```bash
# CORRECT - One delegation to manager
gh issue create --repo business-operations --title "[Manager] Fix X"

# WRONG - Never do these:
- Don't create developer tasks
- Don't create QA tasks  
- Don't write implementation details
- Don't make technical decisions
```

### The System:
- GitHub Issues = Delegation mechanism
- Always delegate to managers
- Managers create all sub-tasks
- I only monitor

### Anti-Patterns to Avoid:
- Creating multiple issues = Micromanaging
- Writing code examples = Doing developer's job
- Creating test cases = Doing QA's job
- Technical decisions = Architect's job

### My Mantras:
- "One delegation, then monitor"
- "Through the system, not around it"
- "If I'm writing code, I'm doing it wrong"
- "Managers manage, I delegate"

### Issue Repository Rules:
- I create issues ONLY in: `business-operations`
- Managers create issues in service repos
- RULE #1: Issues belong in their own repos


# CLAUDE.md - Project Context for AI Assistants

## Current Project: Autonomous Business Operations System

This is an **Autonomous Business Operations System** that uses AI agents to automatically process business operations through GitHub Issues. The system consists of 14 specialized AI agents that handle everything from development to customer success.

## Legacy Overview (Previous System)
Previously served as master orchestration for microservices ecosystem. That documentation is preserved below for reference.

## Current System Architecture

### Core Technology Stack
- **Language**: Python 3.x
- **Database**: GitHub Issues (operational database)
- **Cloud**: AWS (Lambda, Fargate, Batch)
- **Orchestration**: GitHub Actions
- **Coordination**: Policy-based agent coordinator

### Active AI Agents (14 Total)
**Development Pipeline (5 agents)**
- `ai-architect-agent.py`: System design and architecture
- `ai-developer-agent.py`: Code implementation
- `ai-qa-agent.py`: Testing and quality assurance
- `ai-devops-agent.py`: Deployment and infrastructure
- `ai-manager-agent.py`: General management

**Business Operations (9 agents)**
- `ai-project-manager-agent.py`: Executive oversight
- `ai-marketing-agent.py`: Marketing operations
- `ai-sales-agent.py`: Sales operations
- `ai-support-agent.py`: Customer support
- `ai-customer-success-agent.py`: User experience
- `ai-analytics-agent.py`: Data analysis and reporting
- `ai-finance-agent.py`: Financial operations
- `ai-operations-agent.py`: Infrastructure operations
- `ai-security-agent.py`: Security and compliance

## Key Commands for Autonomous Business System

### Testing Agents
```bash
# Test individual agent
python ai-security-agent.py --process-issue 123 --issue-data issue.json

# Run coordinator once
python agent-policy-coordinator.py --once

# Monitor continuously
python agent-policy-coordinator.py --monitor
```

### GitHub Issue Processing
```bash
# View business operations issues
gh issue list --repo VisualForgeMediaV2/business-operations --state open

# Create new operation
gh issue create --repo VisualForgeMediaV2/business-operations \
  --title "Operation Title" \
  --label "operations/monitoring,priority/P2"
```

## Current Documentation
- **MASTER_SDLC_AGENT_INSTRUCTIONS.md** - Your primary guide
- **AI_AGENT_INSTRUCTIONS.md** - Complete system architecture
- **NIROSUBS_STRUCTURE_SUMMARY.md** - Repository structures
- **DEPLOYMENT-GUIDE.md** - Deployment procedures
- **DNS_ARCHITECTURE.md** - DNS and CloudFront setup
- **AWS_PARAMETER_STORE_MIGRATION_STRATEGY.md** - Secrets management
- **CICD_INFRASTRUCTURE_DELTA_ANALYSIS.md** - CI/CD configuration
- **cost-optimized-orchestrator.md** - Cost optimization

## Label System for Issue Routing

### Priority Labels
- `priority/P0`: Critical (1 hour SLA)
- `priority/P1`: High (4 hour SLA)  
- `priority/P2`: Medium (24 hour SLA)
- `priority/P3`: Low (72 hour SLA)

### Operation Labels
- `operations/monitoring`: System monitoring
- `security/compliance`: Security tasks
- `analytics/reporting`: Data analysis
- `finance/analysis`: Financial operations
- `support/quality-assurance`: QA tasks
- `marketing/*`: Marketing operations
- `sales/*`: Sales operations

---

# LEGACY DOCUMENTATION

## Previous Repositories Managed

### NiroSubs-V2
- Subscription management platform
- Services: ns-auth, ns-dashboard, ns-payments, ns-user, ns-shell
- Tech: Lambda, DynamoDB, Cognito, React, CloudFront

### VisualForgeMediaV2
- Media processing platform
- Services: vf-audio, vf-video, vf-image, vf-text, vf-bulk, vf-dashboard
- Tech: Lambda, S3, MediaConvert, FFmpeg, Sharp

## Agent Scripts (All run locally)

### SDLC Iterator
```python
python sdlc-iterator-agent.py --continuous
```
Iterates through develop→test→deploy→document until production-ready

### Issue-Driven Agent
```python
python issue-driven-local-agent.py --monitor
```
Monitors GitHub issues and processes agent-task labels

### Local Orchestrator
```python
python local-agent-system.py --scheduled
```
Runs scheduled health checks locally

## GitHub Issue Processing

### Finding Tasks
```bash
# Check all repos for agent tasks
gh issue list --repo stevesurles/NiroSubs-V2 --label agent-task
gh issue list --repo stevesurles/VisualForgeMediaV2 --label agent-task
gh issue list --repo stevesurles/Projects --label agent-task
```

### Issue Labels
- `agent-task` - General agent task
- `sdlc` - SDLC iteration
- `develop`, `test`, `deploy`, `document` - Phase-specific
- `production-ready` - Service certified

## SDLC Process

### Iteration Cycle
1. **DEVELOP** - Code quality, linting, refactoring
2. **TEST** - Unit tests, coverage >80%, integration
3. **DEPLOY** - Validate configs, package, prepare
4. **DOCUMENT** - Update README, API docs, examples

### Production Ready Criteria
- ✅ All phases pass
- ✅ Test coverage >80%
- ✅ No critical issues
- ✅ Documentation complete
- ✅ Deployment validated
- ✅ Performance benchmarks met

## Timeout Recovery
When you timeout:
1. System automatically schedules retry in 30 minutes
2. State is saved in `.agent_state.pkl`
3. Retry queue in `.agent_retry_queue.json`
4. Continues from where you left off

## Local Execution
Everything runs locally to avoid costs:
- No GitHub Actions minutes used
- No AWS API calls unless necessary
- Results posted to GitHub issues
- HTML reports generated locally

## Key Commands

### Check System Health
```bash
# Check all services
python orchestrator-agent.py

# View saved state
python sdlc-iterator-agent.py --check-retries
```

### Create Issues
```bash
# Use template
gh issue create --repo stevesurles/Projects \
  --title "[SDLC] Service Name" \
  --body-file agent-issue-template.md \
  --label agent-task
```

### Monitor Progress
```bash
# View agent reports
ls agent-reports/*.html

# Check retry queue
cat .agent_retry_queue.json
```

## Important Rules
1. **Never duplicate** master documentation
2. **Always reference** existing docs with paths
3. **Run locally** to avoid cloud costs
4. **Report progress** in GitHub issues
5. **Handle timeouts** gracefully
6. **Create PRs** for code changes

## Success Metrics
- All services production-ready
- Zero cloud costs
- Complete documentation
- Automated testing
- Issue tracking

## When You Start (Current System)
1. Check AUTONOMOUS_BUSINESS_STATUS.md for system state
2. Review AUTONOMOUS_BUSINESS_DESIGN.md for architecture
3. Run `python agent-policy-coordinator.py --once` to test
4. Check GitHub issues at VisualForgeMediaV2/business-operations
5. Monitor agent processing with coordinator

## Important Notes
- System is fully operational with 14 AI agents
- All agents process GitHub issues automatically
- Policy coordinator enforces SLAs and routes work
- Project Manager agent provides executive oversight
- AWS deployment ready but running locally for now

---
**Last Updated**: August 2025
**Current System**: Autonomous Business Operations v2.0
**Status**: Fully Operational - Ready for Production