#!/bin/bash
# Test Agent Assignment System
# =============================

echo "=================================="
echo "TESTING AGENT ASSIGNMENT SYSTEM"
echo "=================================="

# Test configuration
TEST_REPO="vf-dashboard-service"
TEST_ISSUE="8"  # The dashboard issue that needs cost monitoring
TEST_AGENT="vf-developer-agent"

echo ""
echo "Test Target:"
echo "  Repository: $TEST_REPO"
echo "  Issue: #$TEST_ISSUE (Dashboard cost monitoring)"
echo "  Agent: $TEST_AGENT"
echo ""

# Step 1: Check if issue exists
echo "[1] Checking if issue exists..."
gh issue view $TEST_ISSUE --repo VisualForgeMediaV2/$TEST_REPO > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Issue found"
else
    echo "  ✗ Issue not found. Creating test issue..."
    gh issue create \
        --repo VisualForgeMediaV2/$TEST_REPO \
        --title "[STORY] Dashboard Cost Monitoring Implementation" \
        --body "Test issue for agent assignment

## Requirements
- Implement cost monitoring view
- Fix tab system
- Add activity feed

assigned_agent: $TEST_AGENT
priority: P0"
    TEST_ISSUE=$(gh issue list --repo VisualForgeMediaV2/$TEST_REPO --limit 1 --json number -q '.[0].number')
    echo "  Created issue #$TEST_ISSUE"
fi

# Step 2: Assign agent to issue
echo ""
echo "[2] Assigning agent to issue..."

# Update issue body with agent assignment
CURRENT_BODY=$(gh issue view $TEST_ISSUE --repo VisualForgeMediaV2/$TEST_REPO --json body -q .body)

if echo "$CURRENT_BODY" | grep -q "assigned_agent:"; then
    echo "  Agent already assigned, updating..."
    NEW_BODY=$(echo "$CURRENT_BODY" | sed "s/assigned_agent:.*/assigned_agent: $TEST_AGENT/")
else
    echo "  Adding agent assignment..."
    NEW_BODY="$CURRENT_BODY

---
**Agent Assignment**
assigned_agent: $TEST_AGENT
agent_status: pending
priority: P0"
fi

gh issue edit $TEST_ISSUE --repo VisualForgeMediaV2/$TEST_REPO --body "$NEW_BODY"
echo "  ✓ Agent assigned"

# Step 3: Add labels
echo ""
echo "[3] Adding labels..."
gh issue edit $TEST_ISSUE \
    --repo VisualForgeMediaV2/$TEST_REPO \
    --add-label "ai-processing,priority-p0,assigned:$TEST_AGENT" 2>/dev/null
echo "  ✓ Labels added"

# Step 4: Trigger workflow
echo ""
echo "[4] Triggering GitHub Actions workflow..."

# Check if workflow exists
gh workflow list --repo VisualForgeMediaV2/$TEST_REPO | grep -q "Custom Field Agent" 
if [ $? -eq 0 ]; then
    echo "  Workflow exists, triggering..."
    gh workflow run "Custom Field Agent Processor" \
        --repo VisualForgeMediaV2/$TEST_REPO \
        -f issue_number=$TEST_ISSUE
    echo "  ✓ Workflow triggered"
else
    echo "  ⚠ Workflow not found. Manual trigger required."
fi

# Step 5: Check dispatcher status
echo ""
echo "[5] Checking dispatcher status..."
curl -s https://vf-dev.visualforgemedia.com/status 2>/dev/null | python3 -m json.tool 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Dispatcher is running"
else
    echo "  ⚠ Dispatcher may not be running on vf-dev"
fi

# Step 6: Monitor progress
echo ""
echo "=================================="
echo "TEST INITIATED"
echo "=================================="
echo ""
echo "WHAT SHOULD HAPPEN NEXT:"
echo "1. GitHub Action reads the agent assignment"
echo "2. Webhook sent to vf-dev dispatcher"
echo "3. Dispatcher finds available $TEST_AGENT instance"
echo "4. Agent processes issue #$TEST_ISSUE"
echo "5. Agent updates issue with progress"
echo ""
echo "MONITOR PROGRESS:"
echo "  - GitHub: https://github.com/VisualForgeMediaV2/$TEST_REPO/issues/$TEST_ISSUE"
echo "  - Actions: https://github.com/VisualForgeMediaV2/$TEST_REPO/actions"
echo "  - Dispatcher: curl https://vf-dev.visualforgemedia.com/status"
echo ""
echo "VERIFY SUCCESS:"
echo "  - Issue should have agent comment"
echo "  - Code changes should appear as PR"
echo "  - Cost monitoring should be implemented"