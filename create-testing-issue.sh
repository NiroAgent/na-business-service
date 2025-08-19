#!/bin/bash

# Create critical testing issue for business-operations repo

gh issue create \
  --repo "VisualForgeMediaV2/business-operations" \
  --title "[P0 CRITICAL] Implement Comprehensive Playwright Testing for ALL Services" \
  --body "## Priority: P0 - CRITICAL

## Directive from Coordinator

Every service has bugs. ALL development and QA agents must immediately begin comprehensive Playwright testing and bug remediation.

## Requirements

### Phase 1: Pilot (vf-agent-service)
- Full E2E Playwright test coverage
- Test against live vf-dev services  
- Complete logging and monitoring
- Fix ALL bugs found
- Document lessons learned

### Phase 2: Roll Out to All Services
After pilot success, immediately roll out to:
- ns-auth, ns-payments, ns-dashboard, ns-user, ns-shell
- vf-audio, vf-video, vf-image, vf-text-service, vf-bulk
- All other services

### Test Coverage Required
1. Authentication flows
2. All API endpoints
3. UI components
4. Service integrations
5. Performance tests
6. Security tests
7. Error handling
8. Data integrity

### Success Criteria
- 100% test coverage per service
- Zero critical/high bugs
- All tests passing in vf-dev
- Full integration testing
- Performance benchmarks met

## Agent Assignments

**Pilot Team (vf-agent-service)**:
- Lead: @ai-qa-agent
- Development: @ai-developer-agent  
- Infrastructure: @ai-devops-agent

**After Pilot**:
- ALL dev and QA agents assigned to services
- No idle agents allowed
- Daily progress reports required

## Timeline
- Week 1: Pilot (vf-agent-service)
- Week 2: Critical services (auth, payments)
- Week 3: User-facing services
- Week 4: Processing services
- Week 5: Support services

## Reporting
Daily updates required on:
- Tests written
- Bugs found
- Bugs fixed
- Coverage percentage
- Blockers

## Reference
See CRITICAL_TESTING_DIRECTIVE.md for full details

This is not optional. Begin immediately." \
  --label "priority/P0,testing/playwright,development/critical,qa/required,management/directive" \
  --assignee "@ai-manager-agent"

echo "Testing directive issue created for business-operations"