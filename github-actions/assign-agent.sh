#!/bin/bash
# Helper script to assign agents to issues

if [ $# -lt 3 ]; then
    echo "Usage: $0 <repo> <issue_number> <agent>"
    echo "Example: $0 vf-dashboard-service 8 vf-developer-agent"
    echo ""
    echo "Available agents:"
    echo "  vf-developer-agent - For development tasks"
    echo "  vf-qa-agent - For testing tasks"
    echo "  vf-devops-agent - For deployment tasks"
    echo "  vf-architect-agent - For design reviews"
    echo "  vf-manager-agent - For project management"
    exit 1
fi

REPO=$1
ISSUE=$2
AGENT=$3

echo "Assigning $AGENT to issue #$ISSUE in $REPO..."

# Update issue body with agent assignment
CURRENT_BODY=$(gh issue view $ISSUE --repo VisualForgeMediaV2/$REPO --json body -q .body)

# Add or update agent assignment
if echo "$CURRENT_BODY" | grep -q "assigned_agent:"; then
    # Update existing
    NEW_BODY=$(echo "$CURRENT_BODY" | sed "s/assigned_agent:.*/assigned_agent: $AGENT/")
else
    # Add new
    NEW_BODY="$CURRENT_BODY

---
assigned_agent: $AGENT
agent_status: pending"
fi

# Update the issue
gh issue edit $ISSUE --repo VisualForgeMediaV2/$REPO --body "$NEW_BODY"

echo "✓ Agent assigned. Triggering workflow..."

# Trigger the workflow
gh workflow run custom-field-agent.yml \
    --repo VisualForgeMediaV2/$REPO \
    -f issue_number=$ISSUE

echo "✓ Workflow triggered. Agent should start processing soon."
