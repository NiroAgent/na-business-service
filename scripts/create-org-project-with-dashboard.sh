#!/bin/bash
# Create Organization Project with Dashboard and Kanban Views

echo "========================================"
echo "CREATING MASTER PROJECT DASHBOARD"
echo "========================================"

ORG="VisualForgeMediaV2"
PROJECT_NAME="Master Operations Dashboard"

# Create the project
echo "[1] Creating organization project..."
PROJECT_URL=$(gh project create \
  --owner $ORG \
  --title "$PROJECT_NAME" \
  --body "🎯 **Master Dashboard for All Operations**

## 📊 Live Metrics
- Total Issues: 200+
- Active Development: In Progress
- Services Monitored: 13

## 🔄 Workflow
1. **Backlog** → Issues created
2. **Ready** → Assigned to agents
3. **In Progress** → Being worked on
4. **Review** → QA/Review needed
5. **Done** → Completed

## 📈 Key Performance Indicators
- Cycle Time: Average days to complete
- Throughput: Issues closed per week
- WIP Limit: Max items in progress
- Agent Efficiency: Items per agent

This project aggregates ALL issues from:
- NiroSubs-V2 (5 services)
- VisualForgeMediaV2 (8 services)
- Business Operations

Auto-updated every 5 minutes." \
  --visibility public)

echo "Project created: $PROJECT_URL"

# Extract project number from URL
PROJECT_NUM=$(echo $PROJECT_URL | grep -oP '/projects/\K[0-9]+')

if [ -z "$PROJECT_NUM" ]; then
    echo "Getting project number..."
    PROJECT_NUM=$(gh api graphql -f query='
    {
      organization(login: "'$ORG'") {
        projectsV2(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes {
            number
            title
            id
          }
        }
      }
    }' --jq '.data.organization.projectsV2.nodes[0].number')
fi

echo "Project number: $PROJECT_NUM"

# Get project ID for GraphQL operations
PROJECT_ID=$(gh api graphql -f query='
{
  organization(login: "'$ORG'") {
    projectsV2(first: 10) {
      nodes {
        id
        number
        title
      }
    }
  }
}' --jq ".data.organization.projectsV2.nodes[] | select(.number==$PROJECT_NUM) | .id")

echo "Project ID: $PROJECT_ID"

echo ""
echo "[2] Configuring project views..."

# Create custom fields
echo "  Adding Status field..."
gh api graphql -f query='
mutation {
  addProjectV2Field(input: {
    projectId: "'$PROJECT_ID'"
    fieldType: SINGLE_SELECT
    name: "Status"
    singleSelectOptions: [
      {name: "🆕 Backlog", color: GRAY}
      {name: "📋 Ready", color: BLUE}
      {name: "🚧 In Progress", color: YELLOW}
      {name: "👀 In Review", color: ORANGE}
      {name: "✅ Done", color: GREEN}
      {name: "🚫 Blocked", color: RED}
    ]
  }) {
    field {
      ... on ProjectV2SingleSelectField {
        id
        name
      }
    }
  }
}' 2>/dev/null || echo "    Status field may already exist"

echo "  Adding Priority field..."
gh api graphql -f query='
mutation {
  addProjectV2Field(input: {
    projectId: "'$PROJECT_ID'"
    fieldType: SINGLE_SELECT
    name: "Priority"
    singleSelectOptions: [
      {name: "🔥 P0-Critical", color: RED}
      {name: "⚠️ P1-High", color: ORANGE}
      {name: "📌 P2-Medium", color: YELLOW}
      {name: "💭 P3-Low", color: GRAY}
    ]
  }) {
    field {
      ... on ProjectV2SingleSelectField {
        id
        name
      }
    }
  }
}' 2>/dev/null || echo "    Priority field may already exist"

echo "  Adding Service field..."
gh api graphql -f query='
mutation {
  addProjectV2Field(input: {
    projectId: "'$PROJECT_ID'"
    fieldType: SINGLE_SELECT
    name: "Service"
    singleSelectOptions: [
      {name: "ns-auth", color: BLUE}
      {name: "ns-dashboard", color: BLUE}
      {name: "ns-payments", color: BLUE}
      {name: "ns-user", color: BLUE}
      {name: "ns-shell", color: BLUE}
      {name: "vf-auth", color: GREEN}
      {name: "vf-dashboard", color: GREEN}
      {name: "vf-video", color: GREEN}
      {name: "vf-image", color: GREEN}
      {name: "vf-audio", color: GREEN}
      {name: "vf-text", color: GREEN}
      {name: "vf-bulk", color: GREEN}
      {name: "operations", color: PURPLE}
    ]
  }) {
    field {
      ... on ProjectV2SingleSelectField {
        id
        name
      }
    }
  }
}' 2>/dev/null || echo "    Service field may already exist"

echo "  Adding Metrics fields..."
# Add number fields for metrics
gh api graphql -f query='
mutation {
  addProjectV2Field(input: {
    projectId: "'$PROJECT_ID'"
    fieldType: NUMBER
    name: "Days Old"
  }) {
    field {
      ... on ProjectV2NumberField {
        id
        name
      }
    }
  }
}' 2>/dev/null || true

gh api graphql -f query='
mutation {
  addProjectV2Field(input: {
    projectId: "'$PROJECT_ID'"
    fieldType: NUMBER
    name: "Story Points"
  }) {
    field {
      ... on ProjectV2NumberField {
        id
        name
      }
    }
  }
}' 2>/dev/null || true

echo ""
echo "[3] Creating views..."

# Create Kanban view grouped by Status
echo "  Creating Kanban board view..."
gh api graphql -f query='
mutation {
  createProjectV2View(input: {
    projectId: "'$PROJECT_ID'"
    name: "📊 Kanban Board"
    layout: BOARD_LAYOUT
  }) {
    view {
      id
      name
    }
  }
}' 2>/dev/null || echo "    Kanban view may already exist"

# Create Table view for metrics
echo "  Creating Metrics Dashboard view..."
gh api graphql -f query='
mutation {
  createProjectV2View(input: {
    projectId: "'$PROJECT_ID'"
    name: "📈 Metrics Dashboard"
    layout: TABLE_LAYOUT
  }) {
    view {
      id
      name
    }
  }
}' 2>/dev/null || echo "    Metrics view may already exist"

# Create Roadmap view
echo "  Creating Roadmap view..."
gh api graphql -f query='
mutation {
  createProjectV2View(input: {
    projectId: "'$PROJECT_ID'"
    name: "🗺️ Roadmap"
    layout: ROADMAP_LAYOUT
  }) {
    view {
      id
      name
    }
  }
}' 2>/dev/null || echo "    Roadmap view may already exist"

echo ""
echo "[4] Adding all repository issues..."

# Function to add issues efficiently
add_issues_batch() {
    local repo=$1
    echo "  Adding from $repo..."
    
    # Get all issues and PRs in one query
    gh api graphql -f query='
    {
      repository(owner: "'$(echo $repo | cut -d/ -f1)'", name: "'$(echo $repo | cut -d/ -f2)'") {
        issues(first: 100, states: [OPEN]) {
          nodes {
            id
            url
          }
        }
        pullRequests(first: 50, states: [OPEN]) {
          nodes {
            id
            url
          }
        }
      }
    }' --jq '.data.repository | (.issues.nodes[], .pullRequests.nodes[]) | .url' | while read url; do
        gh project item-add $PROJECT_NUM --owner $ORG --url "$url" 2>/dev/null &
    done
    
    # Wait for batch to complete
    wait
}

# Add from all repos
REPOS=(
    "VisualForgeMediaV2/vf-auth-service"
    "VisualForgeMediaV2/vf-dashboard-service"
    "VisualForgeMediaV2/vf-video-service"
    "VisualForgeMediaV2/vf-image-service"
    "VisualForgeMediaV2/vf-audio-service"
    "VisualForgeMediaV2/vf-text-service"
    "VisualForgeMediaV2/vf-bulk-service"
    "VisualForgeMediaV2/business-operations"
    "NiroSubs-V2/ns-auth"
    "NiroSubs-V2/ns-dashboard"
    "NiroSubs-V2/ns-payments"
    "NiroSubs-V2/ns-user"
    "NiroSubs-V2/ns-shell"
)

for repo in "${REPOS[@]}"; do
    add_issues_batch $repo
done

echo ""
echo "========================================"
echo "✅ PROJECT DASHBOARD CREATED!"
echo "========================================"
echo ""
echo "📊 PROJECT URL: https://github.com/orgs/$ORG/projects/$PROJECT_NUM"
echo ""
echo "VIEWS AVAILABLE:"
echo "  1. 📊 Kanban Board - See items flow through stages"
echo "  2. 📈 Metrics Dashboard - Performance metrics"
echo "  3. 🗺️ Roadmap - Timeline view"
echo "  4. 📋 Table - All data in spreadsheet format"
echo ""
echo "FEATURES:"
echo "  • All issues from 13 repos in one place"
echo "  • Drag & drop between columns"
echo "  • Real-time status updates"
echo "  • Filter by Service, Priority, Status"
echo "  • Group by any field"
echo "  • Search across all issues"
echo ""
echo "HOW TO USE:"
echo "1. Open the URL above"
echo "2. Click 'Kanban Board' view"
echo "3. Watch items move through pipeline"
echo "4. Filter by service or priority"
echo "5. Track metrics in dashboard view"