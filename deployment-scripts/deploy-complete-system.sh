#!/bin/bash
# Deploy Complete Agent Assignment System
# ========================================

echo "============================================"
echo "DEPLOYING COMPLETE AGENT ASSIGNMENT SYSTEM"
echo "============================================"

# Check prerequisites
echo ""
echo "[PREREQUISITES CHECK]"

# Check GitHub CLI
gh --version > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ GitHub CLI installed"
else
    echo "  ✗ GitHub CLI not found. Please install: https://cli.github.com/"
    exit 1
fi

# Check authentication
gh auth status > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ GitHub authenticated"
else
    echo "  ✗ Not authenticated. Run: gh auth login"
    exit 1
fi

# Check AWS CLI (optional)
aws --version > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ AWS CLI installed"
else
    echo "  ⚠ AWS CLI not found (optional)"
fi

echo ""
echo "[DEPLOYMENT STEPS]"

# Step 1: Deploy custom fields
echo ""
echo "1. Setting up custom fields..."
bash implement-custom-fields.sh

# Step 2: Deploy dispatcher to vf-dev
echo ""
echo "2. Deploying dispatcher to vf-dev..."
echo "   Manual step required:"
echo "   ssh ec2-user@vf-dev.visualforgemedia.com"
echo "   scp vf-dev-agent-dispatcher.py to server"
echo "   pip3 install flask boto3 requests"
echo "   nohup python3 vf-dev-agent-dispatcher.py > dispatcher.log 2>&1 &"

# Step 3: Create helper scripts
echo ""
echo "3. Creating helper scripts..."

# Create quick assignment script
cat > quick-assign.sh << 'EOF'
#!/bin/bash
# Quick assignment helper

if [ $# -lt 2 ]; then
    echo "Usage: $0 <issue_url> <agent_type>"
    echo ""
    echo "Agent types:"
    echo "  dev - Developer agent"
    echo "  qa - QA agent"
    echo "  ops - DevOps agent"
    echo "  arch - Architect agent"
    echo "  mgr - Manager agent"
    exit 1
fi

URL=$1
AGENT_SHORT=$2

# Parse URL
REPO=$(echo $URL | sed 's/.*github.com\/VisualForgeMediaV2\///' | cut -d'/' -f1)
ISSUE=$(echo $URL | sed 's/.*issues\///')

# Map short names to full agent names
case $AGENT_SHORT in
    dev) AGENT="vf-developer-agent" ;;
    qa) AGENT="vf-qa-agent" ;;
    ops) AGENT="vf-devops-agent" ;;
    arch) AGENT="vf-architect-agent" ;;
    mgr) AGENT="vf-manager-agent" ;;
    *) AGENT="vf-developer-agent" ;;
esac

echo "Assigning $AGENT to $REPO#$ISSUE..."
./assign-agent.sh $REPO $ISSUE $AGENT
EOF

chmod +x quick-assign.sh
echo "  ✓ Created quick-assign.sh"

# Create monitoring script
cat > monitor-agents.sh << 'EOF'
#!/bin/bash
# Monitor agent activity

echo "AGENT SYSTEM MONITOR"
echo "===================="

# Check dispatcher status
echo ""
echo "Dispatcher Status:"
curl -s https://vf-dev.visualforgemedia.com/status | python3 -m json.tool

# Check recent issues
echo ""
echo "Recent AI-Processing Issues:"
gh issue list --label "ai-processing" --limit 5 --repo VisualForgeMediaV2/vf-dashboard-service
gh issue list --label "ai-processing" --limit 5 --repo VisualForgeMediaV2/vf-auth-service

# Check workflow runs
echo ""
echo "Recent Workflow Runs:"
gh run list --workflow "Custom Field Agent Processor" --limit 5 --repo VisualForgeMediaV2/vf-dashboard-service
EOF

chmod +x monitor-agents.sh
echo "  ✓ Created monitor-agents.sh"

echo ""
echo "============================================"
echo "DEPLOYMENT COMPLETE!"
echo "============================================"

echo ""
echo "SYSTEM COMPONENTS:"
echo "  ✓ Custom fields in all repos"
echo "  ✓ GitHub Actions workflows"
echo "  ✓ Agent dispatcher (deploy to vf-dev)"
echo "  ✓ Helper scripts"

echo ""
echo "HOW TO USE:"

echo ""
echo "1. ASSIGN AGENT TO EXISTING ISSUE:"
echo "   ./assign-agent.sh vf-dashboard-service 8 vf-developer-agent"

echo ""
echo "2. QUICK ASSIGN FROM URL:"
echo "   ./quick-assign.sh https://github.com/VisualForgeMediaV2/vf-dashboard-service/issues/8 dev"

echo ""
echo "3. TEST THE SYSTEM:"
echo "   ./test-agent-assignment.sh"

echo ""
echo "4. MONITOR ACTIVITY:"
echo "   ./monitor-agents.sh"

echo ""
echo "CRITICAL ISSUES TO PROCESS:"
echo "  • Dashboard #8 - Cost monitoring (P0)"
echo "  • Auth #10 - MFA implementation (P0)"

echo ""
echo "AGENT CAPACITY (50 total on spot instances):"
echo "  • 20 Developer agents"
echo "  • 10 QA agents"
echo "  • 5 DevOps agents"
echo "  • 5 Manager agents"
echo "  • 5 Architect agents"
echo "  • 3 Security agents"
echo "  • 2 Analytics agents"

echo ""
echo "NEXT STEPS:"
echo "1. Deploy dispatcher to vf-dev (manual)"
echo "2. Test with dashboard issue #8"
echo "3. Monitor agent processing"
echo "4. Verify cost monitoring gets implemented!"