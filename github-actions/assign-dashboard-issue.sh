#!/bin/bash

# Dashboard Issue Assignment Script
# Assigns dashboard issue to frontend developer agent with cost monitoring priority

echo "🎯 Assigning Dashboard Issue to Agent"
echo "💰 Using 95% cost-optimized spot instance deployment"

# Configuration
REPO="autonomous-business-system"
ISSUE_NUM="1"  # Update with actual dashboard issue number
AGENT="developer_frontend_1"
PRIORITY="P1_high"

# Assign custom fields
echo "📝 Setting custom fields..."

gh issue edit $ISSUE_NUM --repo NiroAgentV2/$REPO \
  --add-field "assigned_agent=$AGENT" \
  --add-field "agent_status=assigned" \
  --add-field "priority_level=$PRIORITY" \
  --add-field "processing_started=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --add-field "estimated_completion=$(date -u -d '+4 hours' +%Y-%m-%dT%H:%M:%SZ)"

# Add assignment comment
gh issue comment $ISSUE_NUM --repo NiroAgentV2/$REPO --body "🤖 **Agent Assignment Complete**

**Agent Details:**
- Agent: \`$AGENT\` (React/Vue specialist)
- Priority: \`$PRIORITY\` (High priority - major feature)
- Status: \`assigned\`

**Cost Optimization:**
- Platform: Spot Instances (95% savings)
- Monthly Cost: $8-15 vs $150-300 Lambda
- Processing Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)

**Dashboard Focus:**
This agent will prioritize cost monitoring features in the dashboard, ensuring we maintain our 95% cost optimization goals while delivering the requested functionality.

The dashboard issue is now ready for automated processing on our cost-optimized infrastructure!"

# Trigger GitHub Action
echo "🚀 Triggering GitHub Action..."
gh workflow run agent-assignment.yml --repo NiroAgentV2/$REPO \
  -f issue_number=$ISSUE_NUM \
  -f agents=$AGENT

echo "✅ Dashboard issue assigned successfully!"
echo "🎯 Agent will process with cost monitoring as priority"
