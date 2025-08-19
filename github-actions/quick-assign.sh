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
