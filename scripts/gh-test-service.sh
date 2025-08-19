#!/bin/bash
# Quick GitHub Copilot Testing Script

REPO=${1:-"NiroSubs-V2"}
SERVICE=${2:-"ns-auth"}
ENVIRONMENT=${3:-"dev"}

echo "🧪 Testing $SERVICE in $REPO ($ENVIRONMENT)"

# Navigate to Projects folder
cd /e/Projects || cd E:/Projects

# Build instruction path
INSTRUCTION_PATH="$REPO/$SERVICE/AGENT_INSTRUCTIONS_${ENVIRONMENT^^}.md"

# Test command
TEST_PROMPT="Test and remediate $SERVICE in $REPO using instructions at $INSTRUCTION_PATH. Focus on health checks, functional tests, security, and performance."

# Run gh copilot
echo "🤖 Running GitHub Copilot..."
gh copilot suggest "$TEST_PROMPT"

# Offer follow-up
echo ""
echo "💬 Need a follow-up command? (Enter command or press Enter to skip)"
read -p "> " FOLLOW_UP
if [ ! -z "$FOLLOW_UP" ]; then
    gh copilot suggest "For $SERVICE in $REPO: $FOLLOW_UP"
fi
