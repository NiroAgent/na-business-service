#!/bin/bash
# Master launcher for all VS Code agent workspaces

echo "🚀 Launching ALL Agent Workspaces"
echo "=================================="

# Function to launch a service's workspaces
launch_service() {
    local repo=$1
    local service=$2
    
    echo "Launching $service agents..."
    cd "E:/Projects/$repo/$service"
    
    # Launch dev workspace
    code "$service-dev-agent.code-workspace" --new-window &
    sleep 1
    
    # Launch staging workspace
    code "$service-staging-agent.code-workspace" --new-window &
    sleep 1
}

# Launch NiroSubs services
echo "Starting NiroSubs agents..."
launch_service "NiroSubs-V2" "ns-auth"
launch_service "NiroSubs-V2" "ns-dashboard"
launch_service "NiroSubs-V2" "ns-payments"
launch_service "NiroSubs-V2" "ns-user"
launch_service "NiroSubs-V2" "ns-shell"

# Launch VisualForgeMedia services
echo "Starting VisualForgeMedia agents..."
launch_service "VisualForgeMediaV2" "vf-audio-service"
launch_service "VisualForgeMediaV2" "vf-video-service"
launch_service "VisualForgeMediaV2" "vf-image-service"
launch_service "VisualForgeMediaV2" "vf-text-service"
launch_service "VisualForgeMediaV2" "vf-bulk-service"
launch_service "VisualForgeMediaV2" "vf-dashboard-service"

echo "✅ All agent workspaces launched!"
echo ""
echo "You now have 22 VS Code windows open (11 services × 2 environments)"
echo "Each window has GitHub Copilot ready to act as an autonomous agent"
echo ""
echo "In each window:"
echo "1. Open GitHub Copilot Chat (Ctrl+Shift+I)"
echo "2. Ask: 'Please read COPILOT_AGENT_PROMPT_[ENV].md and start testing'"
echo "3. Copilot will execute the tests and fix issues autonomously"
