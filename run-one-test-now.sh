#!/bin/bash

echo "Running Playwright test for vf-dashboard-service..."

cd E:/Projects/VisualForgeMediaV2/vf-dashboard-service/mfe

# Install if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    npx playwright install
fi

# Run tests and capture output
echo "Executing tests..."
npx playwright test --reporter=list 2>&1 | tee test-output.log

# Check result
if [ $? -ne 0 ]; then
    echo "Tests failed! Creating bug issue..."
    
    # Create bug issue for failures
    gh issue create \
        --repo "VisualForgeMediaV2/vf-dashboard-service" \
        --title "[BUG] Playwright test failures detected" \
        --body "## Test Failures Found

Playwright tests are failing in vf-dashboard-service.

### Test Output
\`\`\`
$(tail -50 test-output.log)
\`\`\`

### Required Actions
1. Review failing tests
2. Fix application bugs causing failures
3. Re-run tests to verify fixes

**Priority**: P1 - High
**Assigned to**: Development team" \
        --label "bug,testing,priority/P1"
    
    echo "Bug issue created for test failures"
else
    echo "All tests passed!"
fi