#!/bin/bash

echo "======================================"
echo "ENVIRONMENT PREFIX ANALYSIS"
echo "======================================"
echo ""
echo "Your personal account has unnecessary environment prefixes."
echo "Everything should just be named cleanly without dev-/staging-"
echo ""

echo "CURRENT NAMING ISSUES:"
echo "----------------------"
echo ""
echo "Lambda Functions with prefixes:"
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `dev-`) || starts_with(FunctionName, `staging-`)].FunctionName' --output text | tr '\t' '\n'

echo ""
echo "DynamoDB Tables with prefixes:"
aws dynamodb list-tables --query 'TableNames[?starts_with(@, `dev-`) || starts_with(@, `staging-`)]' --output text | tr '\t' '\n'

echo ""
echo "CloudFormation Stacks with prefixes:"
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query 'StackSummaries[?starts_with(StackName, `dev-`) || starts_with(StackName, `staging-`)].StackName' --output text | tr '\t' '\n'

echo ""
echo "======================================"
echo "RECOMMENDATIONS:"
echo "======================================"
echo ""
echo "In your personal account, resources should be named:"
echo "  ❌ dev-visualforge-core     →  ✅ visualforge-core"
echo "  ❌ dev-vf-dashboard-lambda  →  ✅ vf-dashboard-lambda"
echo "  ❌ dev-ns-user-api          →  ✅ ns-user-api"
echo "  ❌ dev-vf-users (table)     →  ✅ vf-users"
echo ""
echo "This would:"
echo "1. Make names cleaner and shorter"
echo "2. Avoid confusion (everything is dev in your personal account)"
echo "3. Make URLs and endpoints simpler"
echo "4. Save characters in ARNs and names"
echo ""
echo "To implement this, you would need to:"
echo "1. Update CloudFormation templates to remove prefixes"
echo "2. Redeploy stacks with new names"
echo "3. Update any hardcoded references"
echo "4. Delete old prefixed resources"