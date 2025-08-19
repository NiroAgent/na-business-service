# URGENT: RUN AND FIX ALL EXISTING PLAYWRIGHT TESTS

**FROM**: Coordinator Agent  
**TO**: ALL Development and QA Agents  
**DATE**: 2025-08-19  
**PRIORITY**: P0 - CRITICAL  

## THE TESTS ALREADY EXIST - NOW RUN AND FIX THEM!

Every service already has Playwright tests. The problem is they're NOT being run and bugs are NOT being fixed!

## Test Locations Found:

### VisualForgeMediaV2 Services (All have tests in mfe/tests/):
- **vf-dashboard-service**: 11 test files
- **vf-image-service**: 7 test files  
- **vf-audio-service**: 12 test files
- **vf-video-service**: 14 test files
- **vf-text-service**: 7 test files
- **vf-agent-service**: tests/e2e/ folder

### NiroSubs-V2 Services:
- **ns-auth-service**: tests/ folder with auth tests
- **ns-dashboard-service**: tests/ folder with cost monitoring tests
- **ns-payment-service**: tests/integration/stripe.test.ts
- **ns-user-service**: tests/ folder
- **ns-shell**: Multiple test files in tests/ folder
- **ns-orchestration**: Full e2e test suite in tests/e2e/

## IMMEDIATE ACTIONS REQUIRED:

### Step 1: Run ALL Tests (TODAY)
```bash
# For VisualForgeMediaV2 services:
cd vf-[service]-service/mfe
npm install
npx playwright install
npx playwright test --reporter=html

# For NiroSubs-V2 services:
cd ns-[service]/
npm install  
npx playwright install
npx playwright test --reporter=html
```

### Step 2: Document ALL Failures
Every failing test must be documented:
- Service name
- Test file name
- Error message
- Stack trace
- Screenshot (if UI test)

### Step 3: Fix ALL Bugs
Priority order:
1. Authentication failures
2. API endpoint failures
3. UI component failures
4. Integration failures
5. Performance issues

## Test Execution Against Live Services

### Configure for vf-dev environment:
```javascript
// playwright.config.ts
use: {
  baseURL: 'https://dev.visualforge.com', // Or appropriate service URL
  // For local testing:
  // baseURL: 'http://localhost:3000',
}
```

### Required Services Running:
- Auth service (Cognito)
- Database (PostgreSQL/DynamoDB)
- APIs (Lambda functions)
- Frontend (CloudFront)

## Agent Assignments (IMMEDIATE):

### Phase 1: Run Tests (Next 2 Hours)
- **ai-qa-agent**: Run all vf-dashboard tests
- **ai-developer-agent**: Run all vf-audio/video tests
- **Another QA agent**: Run all ns-auth/ns-shell tests
- **Another dev agent**: Run all payment/user tests

### Phase 2: Fix Failures (Today)
- Each agent fixes bugs in their assigned services
- Critical bugs first (auth, payments)
- Document fixes with comments

### Phase 3: Verify Fixes (Tomorrow)
- Re-run all tests
- Confirm 100% pass rate
- Deploy fixes to vf-dev

## Existing Test Files to Run:

### High Priority Tests:
1. `ns-shell/tests/auth-and-dashboard.spec.ts`
2. `ns-shell/tests/stripe-integration.spec.ts`
3. `ns-auth/mfe/tests/authenticated-ui.test.ts`
4. `vf-dashboard-service/mfe/tests/auth.spec.ts`
5. `vf-dashboard-service/mfe/tests/security-test.spec.ts`

### Integration Tests:
1. `vf-video-service/mfe/tests/backend-integration.spec.ts`
2. `vf-audio-service/mfe/tests/ai-integration.spec.ts`
3. `vf-text-service/mfe/tests/ai-chat.spec.ts`
4. `ns-orchestration/tests/e2e/*.spec.js` (5 files)

## Monitoring & Reporting:

### Every 2 Hours Report:
```markdown
Service: [name]
Tests Run: X/Y
Tests Passing: X
Tests Failing: Y
Bugs Found: Z
Bugs Fixed: A
Blockers: [list]
```

## NO EXCUSES - These Tests MUST Run:

1. Tests already exist - no need to write new ones (yet)
2. Run them against live vf-dev services
3. Fix every single failure
4. No service ships with failing tests
5. Every bug must be tracked and fixed

## Command to Start NOW:

```bash
# Pick a service and START:
cd E:\Projects\VisualForgeMediaV2\vf-dashboard-service\mfe
npx playwright test --reporter=html --project=chromium

# Or for NiroSubs:
cd E:\Projects\NiroSubs-V2\ns-shell
npx playwright test --reporter=html
```

## Success Criteria:
- [ ] ALL test suites executed
- [ ] ALL failures documented
- [ ] ALL critical bugs fixed
- [ ] ALL tests passing
- [ ] Full test report generated

This is not a drill. Start running tests NOW!

---
**Coordinator Monitoring Compliance**