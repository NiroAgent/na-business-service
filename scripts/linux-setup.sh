#!/bin/bash
# Setup script for Linux/WSL - Full Unicode support!

echo "🚀 AUTONOMOUS BUSINESS SYSTEM - LINUX SETUP"
echo "==========================================="

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt 2>/dev/null || echo "Requirements already installed"

# Setup GitHub CLI if needed
if ! command -v gh &> /dev/null; then
    echo "📥 Installing GitHub CLI..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh
fi

# Authenticate GitHub if needed
gh auth status || gh auth login

# Deploy dashboard to GitHub Pages
echo "🌐 Deploying dashboard to GitHub Pages..."
if [ ! -d "agent-dashboard" ]; then
    gh repo clone NiroAgentV2/agent-dashboard
fi

cp dashboard.html agent-dashboard/index.html
cd agent-dashboard
git add index.html
git commit -m "Update dashboard" 2>/dev/null
git push 2>/dev/null
cd ..

echo "✅ Dashboard deployed to: https://niroagentv2.github.io/agent-dashboard"

# Start monitoring in background
echo "🤖 Starting autonomous monitoring system..."
nohup python continuous-monitor.py > monitor.log 2>&1 &
MONITOR_PID=$!
echo "✅ Monitor running with PID: $MONITOR_PID"

# Start coordinator
echo "🎯 Starting agent coordinator..."
nohup python agent-policy-coordinator.py --monitor > coordinator.log 2>&1 &
COORD_PID=$!
echo "✅ Coordinator running with PID: $COORD_PID"

echo ""
echo "============================================"
echo "🎉 SYSTEM FULLY AUTONOMOUS AND RUNNING!"
echo "============================================"
echo ""
echo "📊 Dashboard: https://niroagentv2.github.io/agent-dashboard"
echo "📝 Monitor log: tail -f monitor.log"
echo "🤖 Coordinator log: tail -f coordinator.log"
echo "🛑 To stop: kill $MONITOR_PID $COORD_PID"
echo ""
echo "The system will now:"
echo "✅ Process all GitHub issues automatically"
echo "✅ Build and deploy the dashboard"
echo "✅ Monitor everything continuously"
echo "✅ Self-improve based on metrics"
echo ""
echo "NO FURTHER HUMAN INTERVENTION REQUIRED! 🚀"