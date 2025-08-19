#!/bin/bash

echo "======================================"
echo "SAFE TAGGING SCRIPT - NO CHANGES"
echo "======================================"
echo "This script only TAGS resources, doesn't change anything"
echo ""

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
DATE=$(date +%Y-%m-%d)

echo "Account ID: $ACCOUNT_ID"
echo "Migration Date: $DATE"
echo ""

# Tag Lambda functions
echo "=== Tagging Lambda Functions ==="
aws lambda list-functions --query "Functions[*].FunctionName" --output text | tr '\t' '\n' | while read func; do
    if [[ $func == *"visualforge"* ]] || [[ $func == *"vf-"* ]]; then
        # It's a VisualForge function -> becomes NiroForge
        NEW_NAME=$(echo $func | sed 's/dev-visualforge-/nf-/g' | sed 's/dev-vf-/nf-/g' | sed 's/-lambda$//')
        ORG="NiroForge"
    elif [[ $func == *"ns-"* ]]; then
        # It's a NiroSubs function
        NEW_NAME=$(echo $func | sed 's/dev-ns-/ns-/g' | sed 's/staging-ns-/ns-/g' | sed 's/-lambda$//')
        ORG="NiroSubs"
    else
        # General/utility function
        NEW_NAME=$(echo $func | sed 's/dev-/na-/g')
        ORG="General"
    fi
    
    echo "  $func -> $NEW_NAME ($ORG)"
    
    aws lambda tag-resource \
        --resource "arn:aws:lambda:us-east-1:$ACCOUNT_ID:function:$func" \
        --tags \
            "MigrationStatus=pending" \
            "CurrentName=$func" \
            "TargetName=$NEW_NAME" \
            "Organization=$ORG" \
            "MigrationDate=$DATE" 2>/dev/null || echo "    [Already tagged or error]"
done

echo ""
echo "=== Tagging DynamoDB Tables ==="
aws dynamodb list-tables --query "TableNames[*]" --output text | tr '\t' '\n' | while read table; do
    if [[ $table == *"vf"* ]] || [[ $table == *"visualforge"* ]]; then
        # VisualForge table -> becomes NiroForge
        NEW_NAME=$(echo $table | sed 's/dev-vf-/nf-/g' | sed 's/dev-visualforge-/nf-/g' | sed 's/vf-/nf-/g' | sed 's/-dev$//')
        ORG="NiroForge"
    elif [[ $table == *"ns-"* ]]; then
        # NiroSubs table
        NEW_NAME=$(echo $table | sed 's/dev-ns-/ns-/g')
        ORG="NiroSubs"
    else
        # General table
        NEW_NAME="na-$table"
        ORG="General"
    fi
    
    echo "  $table -> $NEW_NAME ($ORG)"
    
    aws dynamodb tag-resource \
        --resource-arn "arn:aws:dynamodb:us-east-1:$ACCOUNT_ID:table/$table" \
        --tags \
            "Key=MigrationStatus,Value=pending" \
            "Key=CurrentName,Value=$table" \
            "Key=TargetName,Value=$NEW_NAME" \
            "Key=Organization,Value=$ORG" \
            "Key=MigrationDate,Value=$DATE" 2>/dev/null || echo "    [Already tagged or error]"
done

echo ""
echo "======================================"
echo "TAGGING COMPLETE - Resources labeled for migration"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Review the tags in AWS Console"
echo "2. Run: python3 create-migration-inventory.py"
echo "3. Plan the actual migration"