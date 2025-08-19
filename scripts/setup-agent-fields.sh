#!/bin/bash
# Agent Fields Setup for NiroAgentV2 Organization
echo "🔧 Setting up agent fields for NiroAgentV2 organization..."

# Create organization-level custom properties first
echo "Creating organization custom properties..."

# Create assigned_agent field
gh api "orgs/NiroAgentV2/properties" -X POST \
  -f property_name="assigned_agent" \
  -f value_type="single_select" \
  -f required=false \
  -f default_value="unassigned" \
  -f allowed_values='["unassigned","pm-agent","developer_frontend_1","developer_frontend_2","developer_backend_1","developer_backend_2","developer_fullstack_1","developer_fullstack_2","qa_automation_1","qa_manual_1","devops_infrastructure_1","devops_deployment_1","security_compliance_1","analytics_reporting_1","architect_review_1","manager_coordination_1"]'

# Create agent_status field  
gh api "orgs/NiroAgentV2/properties" -X POST \
  -f property_name="agent_status" \
  -f value_type="single_select" \
  -f required=false \
  -f default_value="unassigned" \
  -f allowed_values='["unassigned","assigned","in_progress","review_needed","pm_review","completed","blocked"]'

# Create priority_level field
gh api "orgs/NiroAgentV2/properties" -X POST \
  -f property_name="priority_level" \
  -f value_type="single_select" \
  -f required=false \
  -f default_value="P2_medium" \
  -f allowed_values='["P0_critical","P1_high","P2_medium","P3_low","P4_backlog"]'

# Create pm_approved field
gh api "orgs/NiroAgentV2/properties" -X POST \
  -f property_name="pm_approved" \
  -f value_type="single_select" \
  -f required=false \
  -f default_value="pending" \
  -f allowed_values='["pending","approved","needs_revision","escalated"]'

echo "✅ Organization custom properties created!"

# Now set initial values for repositories
echo "Setting initial values for repositories..."

REPOS=("autonomous-business-system" "agent-dashboard" "business-operations")

for repo in "${REPOS[@]}"; do
    echo "Configuring $repo..."
    
    # Set initial property values
    gh api "repos/NiroAgentV2/$repo/properties/values" -X PATCH \
      -f properties='[
        {"property_name": "assigned_agent", "value": "unassigned"},
        {"property_name": "agent_status", "value": "unassigned"}, 
        {"property_name": "priority_level", "value": "P2_medium"},
        {"property_name": "pm_approved", "value": "pending"}
      ]' || echo "⚠️ Could not set values for $repo (repo may not exist)"
done

echo "🎉 Agent fields setup complete!"
echo ""
echo "✅ Created custom properties:"
echo "  - assigned_agent (16 agent options)"
echo "  - agent_status (7 status options)"
echo "  - priority_level (5 priority levels)"
echo "  - pm_approved (4 approval states)"
echo ""
echo "🎯 Ready for agent assignment system!"
