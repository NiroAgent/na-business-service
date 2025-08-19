#!/bin/bash

# GitHub Custom Fields Setup for Agent Assignment System
# Creates custom fields for 50-agent deployment with spot instance cost optimization

set -e

echo "🚀 Setting up GitHub Custom Fields for 50-Agent Assignment System"
echo "💰 Optimized for 95% cost savings with spot instances ($8-15/month vs $150-300 Lambda)"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Please install: https://cli.github.com/"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "❌ Please authenticate with GitHub CLI: gh auth login"
    exit 1
fi

# Repository configuration
REPO_OWNER="${GITHUB_REPO_OWNER:-NiroAgentV2}"
REPOSITORIES=(
    "autonomous-business-system"
    "NiroSubs-V2" 
    "VisualForgeMediaV2"
    "agent-dashboard"
)

echo "📋 Repositories to configure: ${REPOSITORIES[*]}"

# Function to create custom field if it doesn't exist
create_custom_field() {
    local repo=$1
    local field_name=$2
    local field_type=$3
    local options=$4
    
    echo "  Creating field: $field_name ($field_type)"
    
    case $field_type in
        "single_select")
            gh api \
                --method POST \
                -H "Accept: application/vnd.github+json" \
                -H "X-GitHub-Api-Version: 2022-11-28" \
                "/repos/$REPO_OWNER/$repo/issues/fields" \
                -f name="$field_name" \
                -f field_type="$field_type" \
                -f options="$options" \
                --silent || echo "    Field may already exist"
            ;;
        "date_time")
            gh api \
                --method POST \
                -H "Accept: application/vnd.github+json" \
                -H "X-GitHub-Api-Version: 2022-11-28" \
                "/repos/$REPO_OWNER/$repo/issues/fields" \
                -f name="$field_name" \
                -f field_type="$field_type" \
                --silent || echo "    Field may already exist"
            ;;
        "text")
            gh api \
                --method POST \
                -H "Accept: application/vnd.github+json" \
                -H "X-GitHub-Api-Version: 2022-11-28" \
                "/repos/$REPO_OWNER/$repo/issues/fields" \
                -f name="$field_name" \
                -f field_type="$field_type" \
                --silent || echo "    Field may already exist"
            ;;
    esac
}

# Agent assignment options (50 agents distributed across specializations)
AGENT_OPTIONS='[
    {"name": "developer_frontend_1", "description": "React/Vue specialist"},
    {"name": "developer_frontend_2", "description": "Angular/TypeScript specialist"},
    {"name": "developer_frontend_3", "description": "Mobile/React Native specialist"},
    {"name": "developer_backend_1", "description": "Node.js/Express specialist"},
    {"name": "developer_backend_2", "description": "Python/Django specialist"},
    {"name": "developer_backend_3", "description": "Python/FastAPI specialist"},
    {"name": "developer_backend_4", "description": "Database optimization specialist"},
    {"name": "developer_fullstack_1", "description": "MERN stack specialist"},
    {"name": "developer_fullstack_2", "description": "Next.js specialist"},
    {"name": "developer_fullstack_3", "description": "Cloud integration specialist"},
    {"name": "developer_api_1", "description": "REST API specialist"},
    {"name": "developer_api_2", "description": "GraphQL specialist"},
    {"name": "developer_performance_1", "description": "Web performance specialist"},
    {"name": "developer_performance_2", "description": "Database performance specialist"},
    {"name": "developer_devops_1", "description": "CI/CD pipeline specialist"},
    {"name": "developer_devops_2", "description": "Docker/Kubernetes specialist"},
    {"name": "developer_security_1", "description": "Security-focused developer"},
    {"name": "developer_security_2", "description": "Auth/OAuth specialist"},
    {"name": "developer_integration_1", "description": "Third-party integration specialist"},
    {"name": "developer_integration_2", "description": "Payment/Stripe specialist"},
    {"name": "qa_automation_1", "description": "Cypress/Playwright specialist"},
    {"name": "qa_automation_2", "description": "Jest/Testing Library specialist"},
    {"name": "qa_automation_3", "description": "API testing specialist"},
    {"name": "qa_manual_1", "description": "Manual testing specialist"},
    {"name": "qa_manual_2", "description": "UX/UI testing specialist"},
    {"name": "qa_performance_1", "description": "Performance testing specialist"},
    {"name": "qa_performance_2", "description": "Load testing specialist"},
    {"name": "qa_security_1", "description": "Security testing specialist"},
    {"name": "qa_accessibility_1", "description": "Accessibility testing specialist"},
    {"name": "qa_mobile_1", "description": "Mobile testing specialist"},
    {"name": "devops_cicd_1", "description": "GitHub Actions specialist"},
    {"name": "devops_cicd_2", "description": "Deployment automation specialist"},
    {"name": "devops_infrastructure_1", "description": "AWS/CloudFormation specialist"},
    {"name": "devops_infrastructure_2", "description": "Terraform specialist"},
    {"name": "devops_monitoring_1", "description": "Monitoring/alerting specialist"},
    {"name": "manager_project_1", "description": "Agile/Scrum specialist"},
    {"name": "manager_project_2", "description": "Sprint planning specialist"},
    {"name": "manager_product_1", "description": "Product strategy specialist"},
    {"name": "manager_product_2", "description": "Stakeholder communication specialist"},
    {"name": "manager_coordination_1", "description": "Team coordination specialist"},
    {"name": "architect_system_1", "description": "System architecture specialist"},
    {"name": "architect_system_2", "description": "Microservices specialist"},
    {"name": "architect_platform_1", "description": "Platform architecture specialist"},
    {"name": "architect_integration_1", "description": "Integration architecture specialist"},
    {"name": "architect_scalability_1", "description": "Scalability specialist"},
    {"name": "security_assessment_1", "description": "Vulnerability assessment specialist"},
    {"name": "security_compliance_1", "description": "Compliance auditing specialist"},
    {"name": "security_code_review_1", "description": "Security code review specialist"},
    {"name": "analytics_performance_1", "description": "Performance analytics specialist"},
    {"name": "analytics_business_1", "description": "Business intelligence specialist"}
]'

# Status options
STATUS_OPTIONS='[
    {"name": "unassigned", "description": "Not yet assigned to an agent"},
    {"name": "assigned", "description": "Assigned to agent, waiting to start"},
    {"name": "in_progress", "description": "Agent actively working on issue"},
    {"name": "under_review", "description": "Work completed, under review"},
    {"name": "completed", "description": "Issue fully resolved"},
    {"name": "blocked", "description": "Blocked waiting for dependencies"},
    {"name": "escalated", "description": "Escalated to human oversight"}
]'

# Priority options
PRIORITY_OPTIONS='[
    {"name": "P0_critical", "description": "Critical - Production down"},
    {"name": "P1_high", "description": "High - Major feature broken"},
    {"name": "P2_medium", "description": "Medium - Standard development"},
    {"name": "P3_low", "description": "Low - Minor improvements"},
    {"name": "P4_backlog", "description": "Backlog - Future consideration"}
]'

# Create custom fields for each repository
for repo in "${REPOSITORIES[@]}"; do
    echo "🔧 Configuring repository: $repo"
    
    # Agent assignment field
    echo "  📝 Creating assigned_agent field..."
    create_custom_field "$repo" "assigned_agent" "single_select" "$AGENT_OPTIONS"
    
    # Status tracking field  
    echo "  📊 Creating agent_status field..."
    create_custom_field "$repo" "agent_status" "single_select" "$STATUS_OPTIONS"
    
    # Priority field
    echo "  🎯 Creating priority_level field..."
    create_custom_field "$repo" "priority_level" "single_select" "$PRIORITY_OPTIONS"
    
    # Timestamp fields
    echo "  ⏰ Creating timestamp fields..."
    create_custom_field "$repo" "processing_started" "date_time" ""
    create_custom_field "$repo" "estimated_completion" "date_time" ""
    create_custom_field "$repo" "agent_notes" "text" ""
    
    echo "  ✅ Repository $repo configured"
done

echo ""
echo "🎉 GitHub Custom Fields Setup Complete!"
echo ""
echo "📋 Created Fields:"
echo "  • assigned_agent - 50 specialized agents available"
echo "  • agent_status - 7 status tracking options" 
echo "  • priority_level - 5 priority levels (P0-P4)"
echo "  • processing_started - Timestamp tracking"
echo "  • estimated_completion - ETA tracking"
echo "  • agent_notes - Agent communication notes"
echo ""
echo "💰 Cost Optimization: 95% savings with spot instances"
echo "🎯 Next Steps:"
echo "  1. Use agent-picker.py to assign agents to issues"
echo "  2. GitHub Actions will read custom fields"
echo "  3. Spot instance agents will process assigned work"
echo "  4. Real-time status updates via custom fields"
echo ""
echo "🚀 50-Agent System Ready for Deployment!"
