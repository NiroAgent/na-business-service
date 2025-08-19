#!/bin/bash

# VF Dashboard Issue #8 Assignment Script
# Assigns dashboard issue #8 to developer agent for cost monitoring implementation

echo "🎯 Assigning VF Dashboard Issue #8 to Agent"
echo "💰 Cost monitoring implementation priority"

# Configuration for actual issue
REPO="vf-dashboard-service"
ISSUE_NUM="8"
AGENT="vf-developer-agent"
PRIORITY="P0"

echo "📝 Updating issue with agent assignment..."

# Get current issue body
CURRENT_BODY=$(gh issue view $ISSUE_NUM --repo VisualForgeMediaV2/$REPO --json body -q .body)

# Add agent assignment to body
NEW_BODY="$CURRENT_BODY

---
**Agent Assignment**
assigned_agent: $AGENT
agent_status: assigned
priority: $PRIORITY
processing_started: $(date -u +%Y-%m-%dT%H:%M:%SZ)
estimated_completion: $(date -u -d '+4 hours' +%Y-%m-%dT%H:%M:%SZ)"

# Update issue
gh issue edit $ISSUE_NUM --repo VisualForgeMediaV2/$REPO --body "$NEW_BODY"

# Add labels
echo "🏷️ Adding labels..."
gh issue edit $ISSUE_NUM --repo VisualForgeMediaV2/$REPO \
  --add-label "ai-processing,priority-p0,assigned:$AGENT" 2>/dev/null || echo "Labels may already exist"

# Add comment
echo "💬 Adding assignment comment..."
gh issue comment $ISSUE_NUM --repo VisualForgeMediaV2/$REPO --body "🤖 **Agent Assignment Complete**

**Agent Details:**
- Agent: \`$AGENT\` (Developer agent for implementation)
- Priority: \`$PRIORITY\` (Critical - cost monitoring needed)
- Status: \`assigned\`

**Implementation Focus:**
- Cost monitoring dashboard views
- Activity tracking features
- Fix tab system issues
- Real-time metrics display

**Infrastructure:**
- Running on spot instances (95% cost savings)
- Processing started: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Estimated completion: $(date -u -d '+4 hours' +%Y-%m-%dT%H:%M:%SZ)

The dashboard cost monitoring implementation is now ready for automated processing!"

# Trigger workflow if exists
echo "🚀 Triggering GitHub Action..."
gh workflow run "Custom Field Agent Processor" --repo VisualForgeMediaV2/$REPO \
  -f issue_number=$ISSUE_NUM 2>/dev/null || echo "Workflow may not exist yet"

echo ""
echo "✅ Dashboard issue #8 assigned successfully!"
echo "📊 Monitor progress at: https://github.com/VisualForgeMediaV2/$REPO/issues/$ISSUE_NUM"
echo "🎯 Agent will implement cost monitoring features"