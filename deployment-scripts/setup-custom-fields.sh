#!/bin/bash
# Setup GitHub Custom Fields for Agent Assignment

echo "Setting up custom fields for agent assignment..."

# For each repository, create custom field
REPOS=(
    "VisualForgeMediaV2/vf-dashboard-service"
    "VisualForgeMediaV2/vf-auth-service"
    "VisualForgeMediaV2/vf-video-service"
    "VisualForgeMediaV2/vf-image-service"
    "VisualForgeMediaV2/vf-audio-service"
    "VisualForgeMediaV2/business-operations"
)

for REPO in "${REPOS[@]}"; do
    echo "Creating custom field for $REPO..."
    
    # Create custom field via GitHub API
    gh api "/repos/$REPO/properties/values" \
        -X PATCH \
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
                "value": ""
            },
            {
                "property_name": "estimated_completion",
                "value": ""
            }
        ]' 2>/dev/null || echo "  Custom fields may already exist"
done

echo "Custom fields setup complete!"
