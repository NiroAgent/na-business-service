#!/bin/bash
# Create Organization-Level GitHub Project with All Issues

echo "========================================"
echo "CREATING ORGANIZATION-LEVEL PROJECT"
echo "========================================"

# Create project for VisualForgeMediaV2 (main org)
ORG="VisualForgeMediaV2"
PROJECT_NAME="Master Operations Dashboard"

echo ""
echo "[1] Creating project: $PROJECT_NAME"

# Create the project using GitHub CLI
gh project create \
  --owner $ORG \
  --title "$PROJECT_NAME" \
  --body "Centralized view of all issues across all repositories in both VisualForgeMediaV2 and NiroSubs-V2 organizations. Auto-updated with all issues." \
  --visibility public

# Get project number
PROJECT_NUM=$(gh project list --owner $ORG --limit 100 --format json | jq -r ".projects[] | select(.title==\"$PROJECT_NAME\") | .number")

if [ -z "$PROJECT_NUM" ]; then
    echo "Failed to get project number. Trying alternative method..."
    # Try to get the most recently created project
    PROJECT_NUM=$(gh api graphql -f query='
    {
      organization(login: "'$ORG'") {
        projectsV2(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes {
            number
            title
          }
        }
      }
    }' --jq '.data.organization.projectsV2.nodes[0].number')
fi

echo "Project number: $PROJECT_NUM"

# Configure project fields
echo ""
echo "[2] Adding custom fields to project..."

# Add Status field
gh project field-create $PROJECT_NUM \
  --owner $ORG \
  --name "Status" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "Not Started,In Progress,In Review,Blocked,Done"

# Add Priority field  
gh project field-create $PROJECT_NUM \
  --owner $ORG \
  --name "Priority" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "P0-Critical,P1-High,P2-Medium,P3-Low"

# Add Service field
gh project field-create $PROJECT_NUM \
  --owner $ORG \
  --name "Service" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "ns-auth,ns-dashboard,ns-payments,ns-user,ns-shell,vf-auth,vf-dashboard,vf-video,vf-image,vf-audio,vf-text,vf-bulk,operations"

# Add Agent field
gh project field-create $PROJECT_NUM \
  --owner $ORG \
  --name "Assigned Agent" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "pm-agent,developer-agent,qa-agent,devops-agent,architect-agent,none"

echo ""
echo "[3] Adding all issues from all repositories..."

# Function to add issues from a repo to project
add_repo_issues() {
    local repo=$1
    echo "  Adding issues from $repo..."
    
    # Get all issue numbers
    issue_nums=$(gh issue list --repo $repo --limit 1000 --state all --json number -q '.[].number')
    
    for issue_num in $issue_nums; do
        # Add issue to project
        gh project item-add $PROJECT_NUM \
          --owner $ORG \
          --url "https://github.com/$repo/issues/$issue_num" 2>/dev/null || true
    done
    
    # Also add PRs
    pr_nums=$(gh pr list --repo $repo --limit 100 --state all --json number -q '.[].number')
    
    for pr_num in $pr_nums; do
        gh project item-add $PROJECT_NUM \
          --owner $ORG \
          --url "https://github.com/$repo/pull/$pr_num" 2>/dev/null || true
    done
}

# Add issues from all VisualForgeMediaV2 repos
REPOS_VF=(
    "VisualForgeMediaV2/vf-auth-service"
    "VisualForgeMediaV2/vf-dashboard-service"
    "VisualForgeMediaV2/vf-video-service"
    "VisualForgeMediaV2/vf-image-service"
    "VisualForgeMediaV2/vf-audio-service"
    "VisualForgeMediaV2/vf-text-service"
    "VisualForgeMediaV2/vf-bulk-service"
    "VisualForgeMediaV2/business-operations"
)

echo ""
echo "Adding VisualForgeMediaV2 repositories..."
for repo in "${REPOS_VF[@]}"; do
    add_repo_issues $repo
done

# Add issues from all NiroSubs-V2 repos
REPOS_NS=(
    "NiroSubs-V2/ns-auth"
    "NiroSubs-V2/ns-dashboard"
    "NiroSubs-V2/ns-payments"
    "NiroSubs-V2/ns-user"
    "NiroSubs-V2/ns-shell"
)

echo ""
echo "Adding NiroSubs-V2 repositories..."
for repo in "${REPOS_NS[@]}"; do
    add_repo_issues $repo
done

echo ""
echo "========================================"
echo "PROJECT CREATION COMPLETE!"
echo "========================================"
echo ""
echo "Project URL: https://github.com/orgs/$ORG/projects/$PROJECT_NUM"
echo ""
echo "Features:"
echo "  ✓ All issues from all repos in one view"
echo "  ✓ Custom fields for Status, Priority, Service, Agent"
echo "  ✓ Kanban and table views available"
echo "  ✓ Filtering and sorting capabilities"
echo ""
echo "Next Steps:"
echo "1. Open the project URL above"
echo "2. Switch to Board or Table view"
echo "3. Group by Status or Service"
echo "4. Filter by Priority or Agent"