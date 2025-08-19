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
