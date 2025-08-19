# PowerShell
# Master launcher for all VS Code agent workspaces

Write-Host "🚀 Launching ALL Agent Workspaces"
Write-Host "=================================="

# Function to launch a service's workspaces
launch_service() {
    local repo=$1
    local service=$2
    
    Write-Host "Launching $service agents..."
    cd "E:/Projects/$repo/$service"
    
    # Launch dev workspace
    code.cmd "$service-dev-agent.code.cmd-workspace" --new-window 
    Start-Sleep 1
    
    # Launch staging workspace
    code.cmd "$service-staging-agent.code.cmd-workspace" --new-window 
    Start-Sleep 1
}

# Launch NiroSubs services
Write-Host "Starting NiroSubs agents..."
launch_service "NiroSubs-V2" "ns-auth"
launch_service "NiroSubs-V2" "ns-dashboard"
launch_service "NiroSubs-V2" "ns-payments"
launch_service "NiroSubs-V2" "ns-user"
launch_service "NiroSubs-V2" "ns-shell"

# Launch VisualForgeMedia services
Write-Host "Starting VisualForgeMedia agents..."
launch_service "VisualForgeMediaV2" "vf-audio-service"
launch_service "VisualForgeMediaV2" "vf-video-service"
launch_service "VisualForgeMediaV2" "vf-image-service"
launch_service "VisualForgeMediaV2" "vf-text-service"
launch_service "VisualForgeMediaV2" "vf-bulk-service"
launch_service "VisualForgeMediaV2" "vf-dashboard-service"

Write-Host "✅ All agent workspaces launched!"
Write-Host ""
Write-Host "You now have 22 VS Code windows open (11 services × 2 environments)"
Write-Host "Each window has GitHub Copilot ready to act as an autonomous agent"
Write-Host ""
Write-Host "In each window:"
Write-Host "1. Open GitHub Copilot Chat (Ctrl+Shift+I)"
Write-Host "2. Ask: 'Please read COPILOT_AGENT_PROMPT_[ENV].md and start testing'"
Write-Host "3. Copilot will execute the tests and fix issues autonomously"
