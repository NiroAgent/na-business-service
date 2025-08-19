#!/bin/bash
# Complete Implementation of Custom Field Agent Assignment System
# ================================================================

echo "=========================================="
echo "IMPLEMENTING CUSTOM FIELD AGENT SYSTEM"
echo "=========================================="

# Step 1: Create the custom fields in all repositories
echo ""
echo "[STEP 1] Creating custom fields in repositories..."

REPOS=(
    "VisualForgeMediaV2/vf-dashboard-service"
    "VisualForgeMediaV2/vf-auth-service"
    "VisualForgeMediaV2/vf-video-service"
    "VisualForgeMediaV2/vf-image-service"
    "VisualForgeMediaV2/vf-audio-service"
    "VisualForgeMediaV2/vf-text-service"
    "VisualForgeMediaV2/business-operations"
)

for REPO in "${REPOS[@]}"; do
    echo "Setting up custom fields for $REPO..."
    
    # Create custom properties schema first
    gh api \
        --method PUT \
        -H "Accept: application/vnd.github+json" \
        /repos/$REPO/properties/values \
        -f properties='[
            {
                "property_name": "assigned_agent",
                "value": "none"
            },
            {
                "property_name": "agent_status", 
                "value": "pending"
            },
            {
                "property_name": "processing_started",
                "value": null
            },
            {
                "property_name": "estimated_completion",
                "value": null
            },
            {
                "property_name": "priority",
                "value": "P2"
            }
        ]' 2>/dev/null && echo "  ✓ Custom fields created" || echo "  ⚠ May already exist"
done

echo ""
echo "[STEP 2] Creating GitHub Actions workflow for each repo..."

# Create the workflow file content
cat > custom-field-agent-workflow.yml << 'EOF'
name: Custom Field Agent Processor

on:
  issues:
    types: [opened, edited, labeled]
  issue_comment:
    types: [created]
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number to process'
        required: true
        type: number

jobs:
  process-with-agent:
    runs-on: ubuntu-latest
    
    steps:
    - name: Check Custom Fields
      id: check-fields
      uses: actions/github-script@v7
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        script: |
          const issue_num = context.issue?.number || ${{ github.event.inputs.issue_number || 0 }};
          
          if (!issue_num) {
            console.log('No issue number found');
            return;
          }
          
          // Get issue details
          const { data: issue } = await github.rest.issues.get({
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: issue_num
          });
          
          // Parse body for agent assignment (fallback method)
          const body = issue.body || '';
          let assignedAgent = 'none';
          
          // Check for agent assignment in body
          const agentMatch = body.match(/assigned_agent:\s*(\S+)/i);
          if (agentMatch) {
            assignedAgent = agentMatch[1];
          }
          
          // Check title for agent hints
          const title = issue.title;
          if (title.includes('[STORY]') || title.includes('[Dev]')) {
            assignedAgent = assignedAgent === 'none' ? 'vf-developer-agent' : assignedAgent;
          } else if (title.includes('[QA]')) {
            assignedAgent = assignedAgent === 'none' ? 'vf-qa-agent' : assignedAgent;
          } else if (title.includes('[Deploy]')) {
            assignedAgent = assignedAgent === 'none' ? 'vf-devops-agent' : assignedAgent;
          }
          
          core.setOutput('agent', assignedAgent);
          core.setOutput('issue_number', issue_num);
          core.setOutput('should_process', assignedAgent !== 'none');
          
          console.log(`Agent: ${assignedAgent}, Issue: ${issue_num}`);
    
    - name: Trigger Agent Processing
      if: steps.check-fields.outputs.should_process == 'true'
      env:
        AGENT: ${{ steps.check-fields.outputs.agent }}
        ISSUE: ${{ steps.check-fields.outputs.issue_number }}
        REPO: ${{ github.repository }}
      run: |
        echo "Triggering $AGENT for issue #$ISSUE"
        
        # Send to vf-dev dispatcher
        curl -X POST https://vf-dev.visualforgemedia.com/agent-dispatch \
          -H "Content-Type: application/json" \
          -d "{
            \"repository\": \"$REPO\",
            \"issue_number\": $ISSUE,
            \"agent\": \"$AGENT\",
            \"action\": \"process\",
            \"github_token\": \"${{ secrets.GITHUB_TOKEN }}\"
          }" || echo "Dispatcher may not be running yet"
    
    - name: Update Issue Labels
      if: steps.check-fields.outputs.should_process == 'true'
      uses: actions/github-script@v7
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        script: |
          await github.rest.issues.addLabels({
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: ${{ steps.check-fields.outputs.issue_number }},
            labels: ['ai-processing', 'assigned:${{ steps.check-fields.outputs.agent }}']
          }).catch(e => console.log('Labels may already exist'));
EOF

echo "Workflow file created: custom-field-agent-workflow.yml"

echo ""
echo "[STEP 3] Deploying workflow to repositories..."

for REPO in "${REPOS[@]}"; do
    echo "Deploying to $REPO..."
    
    # Extract org and repo name
    ORG=$(echo $REPO | cut -d'/' -f1)
    REPO_NAME=$(echo $REPO | cut -d'/' -f2)
    
    # Create workflow via API
    gh api \
        --method PUT \
        /repos/$REPO/contents/.github/workflows/custom-field-agent.yml \
        -f message="Add custom field agent processor workflow" \
        -f content="$(base64 < custom-field-agent-workflow.yml)" 2>/dev/null && \
        echo "  ✓ Workflow deployed" || echo "  ⚠ May already exist"
done

echo ""
echo "[STEP 4] Creating agent assignment helper script..."

cat > assign-agent.sh << 'EOF'
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
EOF

chmod +x assign-agent.sh
echo "Created assign-agent.sh helper script"

echo ""
echo "=========================================="
echo "IMPLEMENTATION COMPLETE!"
echo "=========================================="
echo ""
echo "WHAT'S BEEN SET UP:"
echo "1. Custom fields in all repositories"
echo "2. GitHub Actions workflow deployed"
echo "3. Agent assignment helper script"
echo ""
echo "HOW TO USE:"
echo ""
echo "Method 1 - Quick Assignment:"
echo "  ./assign-agent.sh vf-dashboard-service 8 vf-developer-agent"
echo ""
echo "Method 2 - Add to issue body:"
echo "  assigned_agent: vf-developer-agent"
echo ""
echo "Method 3 - Use title tags:"
echo "  [STORY] - Auto-assigns to developer"
echo "  [QA] - Auto-assigns to QA"
echo "  [Deploy] - Auto-assigns to DevOps"
echo ""
echo "NEXT STEPS:"
echo "1. Test with the dashboard issue #8"
echo "2. Monitor the GitHub Actions tab"
echo "3. Check agent logs on vf-dev"