#!/bin/bash
# Agent Assignment Labels Setup for NiroAgentV2
echo "🏷️ Setting up agent assignment labels..."

# Define repositories
REPOS=("autonomous-business-system" "agent-dashboard" "business-operations")

# Agent assignment labels
AGENT_LABELS=(
    "assigned:pm-agent|4CAF50|Project Manager assigned"
    "assigned:developer-frontend-1|2196F3|Frontend Developer 1 assigned"
    "assigned:developer-frontend-2|2196F3|Frontend Developer 2 assigned" 
    "assigned:developer-backend-1|FF9800|Backend Developer 1 assigned"
    "assigned:developer-backend-2|FF9800|Backend Developer 2 assigned"
    "assigned:developer-fullstack-1|9C27B0|Fullstack Developer 1 assigned"
    "assigned:developer-fullstack-2|9C27B0|Fullstack Developer 2 assigned"
    "assigned:qa-automation-1|E91E63|QA Automation 1 assigned"
    "assigned:qa-manual-1|E91E63|QA Manual 1 assigned"
    "assigned:devops-infrastructure-1|607D8B|DevOps Infrastructure 1 assigned"
    "assigned:devops-deployment-1|607D8B|DevOps Deployment 1 assigned"
    "assigned:security-compliance-1|F44336|Security Compliance 1 assigned"
    "assigned:analytics-reporting-1|795548|Analytics Reporting 1 assigned"
    "assigned:architect-review-1|3F51B5|Architect Review 1 assigned"
    "assigned:manager-coordination-1|009688|Manager Coordination 1 assigned"
)

# Status labels
STATUS_LABELS=(
    "status:unassigned|BDBDBD|No agent assigned yet"
    "status:assigned|FFB74D|Agent has been assigned"
    "status:in-progress|2196F3|Agent is working on this"
    "status:review-needed|FF9800|Ready for review"
    "status:pm-review|9C27B0|Waiting for PM review"
    "status:completed|4CAF50|Task completed"
    "status:blocked|F44336|Blocked - needs attention"
)

# Priority labels
PRIORITY_LABELS=(
    "priority:P0-critical|F44336|Critical priority - immediate attention"
    "priority:P1-high|FF5722|High priority"
    "priority:P2-medium|FF9800|Medium priority"
    "priority:P3-low|4CAF50|Low priority"
    "priority:P4-backlog|9E9E9E|Backlog item"
)

# PM approval labels
APPROVAL_LABELS=(
    "pm-approval:pending|FFB74D|Waiting for PM approval"
    "pm-approval:approved|4CAF50|Approved by PM"
    "pm-approval:needs-revision|FF9800|PM requested revisions"
    "pm-approval:escalated|F44336|Escalated to higher management"
)

# Function to create label
create_label() {
    local repo=$1
    local label_info=$2
    
    IFS='|' read -r name color description <<< "$label_info"
    
    echo "Creating label: $name"
    gh api "repos/NiroAgentV2/$repo/labels" -X POST \
        -f name="$name" \
        -f color="$color" \
        -f description="$description" 2>/dev/null || echo "  ⚠️ Label $name might already exist"
}

# Create labels for each repository
for repo in "${REPOS[@]}"; do
    echo ""
    echo "🔧 Configuring labels for $repo..."
    
    # Create agent assignment labels
    for label in "${AGENT_LABELS[@]}"; do
        create_label "$repo" "$label"
    done
    
    # Create status labels
    for label in "${STATUS_LABELS[@]}"; do
        create_label "$repo" "$label"
    done
    
    # Create priority labels
    for label in "${PRIORITY_LABELS[@]}"; do
        create_label "$repo" "$label"
    done
    
    # Create approval labels
    for label in "${APPROVAL_LABELS[@]}"; do
        create_label "$repo" "$label"
    done
    
    echo "✅ Labels configured for $repo"
done

echo ""
echo "🎉 Agent assignment labels setup complete!"
echo ""
echo "✅ Created label categories:"
echo "  📋 Agent Assignment (15 agents)"
echo "  📊 Status Tracking (7 statuses)"
echo "  ⚡ Priority Levels (5 priorities)"
echo "  ✅ PM Approval (4 approval states)"
echo ""
echo "🎯 Agent assignment system ready!"
echo ""
echo "💡 Usage:"
echo "  - Issues will automatically get assigned: labels"
echo "  - PM can override assignments using labels"
echo "  - Status tracking via status: labels"
echo "  - Priority management via priority: labels"
