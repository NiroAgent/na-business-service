# Master Agent Testing & Remediation Instructions

## Overview
This document contains the testing and remediation strategy for all services across all environments.

## Service Matrix

| Repository | Service | Dev | Staging | Production |
|------------|---------|-----|---------|------------|
| NiroSubs-V2 | ns-auth | ✅ | ✅ | ⚠️ |
| NiroSubs-V2 | ns-dashboard | ✅ | ✅ | ⚠️ |
| NiroSubs-V2 | ns-payments | ✅ | ✅ | ⚠️ |
| NiroSubs-V2 | ns-user | ✅ | ✅ | ⚠️ |
| NiroSubs-V2 | ns-shell | ✅ | ✅ | ⚠️ |
| VisualForgeMediaV2 | vf-audio-service | ✅ | ✅ | ⚠️ |
| VisualForgeMediaV2 | vf-video-service | ✅ | ✅ | ⚠️ |
| VisualForgeMediaV2 | vf-image-service | ✅ | ✅ | ⚠️ |
| VisualForgeMediaV2 | vf-text-service | ✅ | ✅ | ⚠️ |
| VisualForgeMediaV2 | vf-bulk-service | ✅ | ✅ | ⚠️ |
| VisualForgeMediaV2 | vf-dashboard-service | ✅ | ✅ | ⚠️ |


## Testing Priorities

### Critical Path (Test First)
1. Authentication services (ns-auth, vf-auth-service)
2. Payment processing (ns-payments)
3. User management (ns-user)
4. Core dashboards (ns-dashboard, vf-dashboard-service)

### Secondary Services
1. Media processing (vf-audio, vf-video, vf-image, vf-text)
2. Bulk operations (vf-bulk-service)
3. Shell/UI (ns-shell)

## Parallel Execution Strategy

### Phase 1: Health Checks (All Services Parallel)
- Quick health check on all endpoints
- Identify completely broken services
- Priority fix for any 500/503 errors

### Phase 2: Service Testing (Grouped by Dependency)
- Group 1: Auth & User services
- Group 2: Core services (dashboard, payments)
- Group 3: Media services
- Group 4: UI/Shell services

### Phase 3: Integration Testing
- Cross-service communication
- Data flow validation
- End-to-end user journeys

### Phase 4: Performance & Security
- Load testing
- Security scanning
- Performance optimization

## Remediation Priority

1. **P0 - Critical**: Service completely down
2. **P1 - High**: Core functionality broken
3. **P2 - Medium**: Performance issues or minor bugs
4. **P3 - Low**: Cosmetic or nice-to-have improvements

## Agent Coordination

Agents should:
1. Check in every 5 minutes with status
2. Not modify production without approval
3. Create PRs for staging/production fixes
4. Log all actions to CloudWatch
5. Coordinate through shared state in S3

## Success Metrics

- All services: 99% uptime
- API response: < 500ms p95
- Error rate: < 1%
- Test coverage: > 80%
- Security score: A rating

## Rollback Procedures

Each agent must maintain:
1. Backup of current working version
2. Rollback script ready
3. Database migration rollback if applicable
4. CloudFormation stack rollback plan
