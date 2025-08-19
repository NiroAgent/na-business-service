#!/bin/bash

# Delegate test monitoring to operations agent

gh issue create \
  --repo "VisualForgeMediaV2/business-operations" \
  --title "[P0] Monitor and Enforce Playwright Testing Across All Services" \
  --body "## Priority: P0 - CRITICAL MONITORING TASK

## Assignment: @ai-operations-agent

## Monitoring Requirements

The operations/monitoring agent must continuously monitor and enforce:

### 1. Test Execution Status
- Track which services have run their Playwright tests
- Monitor test pass/fail rates
- Identify services not running tests
- Alert on test failures

### 2. Bug Tracking
- Monitor bugs discovered by tests
- Track bug fix progress
- Ensure critical bugs are prioritized
- Report on time-to-fix metrics

### 3. Agent Activity Monitoring
- Verify ai-qa-agent is running tests
- Verify ai-developer-agent is fixing bugs
- Identify idle agents and reassign to testing
- Track agent productivity on test/fix tasks

### 4. Service Coverage
Monitor test execution for ALL services:

**VisualForgeMediaV2 Services:**
- vf-dashboard-service/mfe/tests/
- vf-image-service/mfe/tests/
- vf-audio-service/mfe/tests/
- vf-video-service/mfe/tests/
- vf-text-service/mfe/tests/
- vf-agent-service/tests/e2e/
- vf-bulk-service/mfe/tests/

**NiroSubs-V2 Services:**
- ns-shell/tests/
- ns-auth/frontend/tests/
- ns-dashboard/frontend/tests/
- ns-payments/tests/
- ns-user/frontend/tests/

### 5. Reporting Requirements

Generate hourly reports including:
- Services tested vs not tested
- Total tests run
- Pass/fail rates
- Bugs found
- Bugs fixed
- Agent activity
- Blockers and issues

### 6. Enforcement Actions

When monitoring detects issues:
- Alert coordinator immediately for P0 failures
- Reassign idle agents to testing work
- Escalate blockers to management
- Track SLA compliance for bug fixes

### Success Metrics
- 100% of services have tests executed daily
- 0 critical bugs remain unfixed > 4 hours
- All agents actively working on test/fix cycle
- Daily improvement in pass rates

### Monitoring Tools
Use these scripts:
- coordinator-agent-monitor.py
- testing-progress-monitor.py
- run-all-tests-now.py

### Reference Documents
- RUN_AND_FIX_TESTS_DIRECTIVE.md
- CRITICAL_TESTING_DIRECTIVE.md

Begin continuous monitoring immediately." \
  --label "priority/P0,operations/monitoring,testing/enforcement,agent-task"

echo "Test monitoring task delegated to ai-operations-agent"