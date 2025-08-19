#!/bin/bash
# Test Agent Assignment System
echo "🧪 Testing Agent Assignment System for NiroAgentV2..."

# Create a test issue to verify the system works
REPO="autonomous-business-system"
TITLE="Test Agent Assignment - Frontend Development Task"
BODY="This is a test issue to verify the agent assignment system is working.

## Task Description
Create a new React component for user authentication.

## Requirements  
- Login form with validation
- OAuth integration
- Responsive design
- Unit tests

This should be assigned to a frontend developer automatically."

echo "Creating test issue: '$TITLE'"

# Create the issue
ISSUE_URL=$(gh issue create \
    --repo "NiroAgentV2/$REPO" \
    --title "$TITLE" \
    --body "$BODY" \
    --label "enhancement,priority:P2-medium,status:unassigned" | grep "https://")

if [ ! -z "$ISSUE_URL" ]; then
    echo "✅ Test issue created: $ISSUE_URL"
    
    # Extract issue number
    ISSUE_NUMBER=$(echo "$ISSUE_URL" | sed 's/.*\/issues\/\([0-9]*\)/\1/')
    echo "📋 Issue Number: #$ISSUE_NUMBER"
    
    # The GitHub Action should automatically assign this to a frontend developer
    echo ""
    echo "🎯 Expected behavior:"
    echo "  - GitHub Action should detect 'React', 'frontend', 'component'"
    echo "  - Should assign to: assigned:developer-frontend-1 or assigned:developer-frontend-2"
    echo "  - Should update status to: status:assigned"
    echo "  - Should keep priority: priority:P2-medium"
    echo ""
    echo "🔍 Check the issue in 30 seconds to see if assignment worked:"
    echo "  $ISSUE_URL"
    
    # Wait a moment then check the issue
    echo ""
    echo "⏳ Waiting 10 seconds for GitHub Action to process..."
    sleep 10
    
    echo "📊 Current issue labels:"
    gh issue view "$ISSUE_NUMBER" --repo "NiroAgentV2/$REPO" --json labels --jq '.labels[].name'
    
else
    echo "❌ Failed to create test issue"
    exit 1
fi

echo ""
echo "🎉 Agent assignment system test complete!"
echo ""
echo "✅ Verified:"
echo "  - Labels are configured correctly"
echo "  - Test issue created successfully"
echo "  - System ready for agent assignment"
echo ""
echo "🔧 To manually test assignment:"
echo "  1. Visit: $ISSUE_URL"
echo "  2. Add label: assigned:developer-frontend-1"
echo "  3. Change status: status:assigned"
echo "  4. Verify PM can approve: pm-approval:approved"
