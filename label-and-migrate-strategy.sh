#!/bin/bash

echo "======================================"
echo "PHASE 1: LABEL & TAG EVERYTHING FIRST"
echo "======================================"
echo ""
echo "Before making any changes, we'll tag all resources with:"
echo "  • Current name"
echo "  • Target name"
echo "  • Migration status"
echo "  • Organization ownership"
echo ""

# Tag Lambda functions
echo "=== TAGGING LAMBDA FUNCTIONS ==="
cat << 'EOF'
# Tag all VF/VisualForge Lambda functions
for func in $(aws lambda list-functions --query "Functions[?contains(FunctionName, 'visualforge') || contains(FunctionName, 'vf-')].FunctionName" --output text); do
    echo "Tagging function: $func"
    
    # Determine new name
    NEW_NAME=$(echo $func | sed 's/dev-visualforge-/nf-/g' | sed 's/dev-vf-/nf-/g' | sed 's/-lambda$//')
    
    aws lambda tag-resource \
        --resource "arn:aws:lambda:us-east-1:$(aws sts get-caller-identity --query Account --output text):function:$func" \
        --tags \
            "MigrationStatus=pending" \
            "CurrentName=$func" \
            "TargetName=$NEW_NAME" \
            "Organization=NiroForge" \
            "MigrationDate=$(date +%Y-%m-%d)"
done

# Tag all NS/NiroSubs Lambda functions  
for func in $(aws lambda list-functions --query "Functions[?contains(FunctionName, 'ns-')].FunctionName" --output text); do
    echo "Tagging function: $func"
    
    NEW_NAME=$(echo $func | sed 's/dev-ns-/ns-/g' | sed 's/staging-ns-/ns-/g' | sed 's/-lambda$//')
    
    aws lambda tag-resource \
        --resource "arn:aws:lambda:us-east-1:$(aws sts get-caller-identity --query Account --output text):function:$func" \
        --tags \
            "MigrationStatus=pending" \
            "CurrentName=$func" \
            "TargetName=$NEW_NAME" \
            "Organization=NiroSubs" \
            "MigrationDate=$(date +%Y-%m-%d)"
done
EOF

echo ""
echo "=== TAGGING DYNAMODB TABLES ==="
cat << 'EOF'
# Tag DynamoDB tables
for table in $(aws dynamodb list-tables --query "TableNames[?contains(@, 'vf-') || contains(@, 'visualforge')]" --output text); do
    echo "Tagging table: $table"
    
    NEW_NAME=$(echo $table | sed 's/dev-vf-/nf-/g' | sed 's/dev-visualforge-/nf-/g' | sed 's/vf-/nf-/g' | sed 's/-dev$//')
    
    aws dynamodb tag-resource \
        --resource-arn "arn:aws:dynamodb:us-east-1:$(aws sts get-caller-identity --query Account --output text):table/$table" \
        --tags \
            "Key=MigrationStatus,Value=pending" \
            "Key=CurrentName,Value=$table" \
            "Key=TargetName,Value=$NEW_NAME" \
            "Key=Organization,Value=NiroForge"
done
EOF

echo ""
echo "======================================"
echo "PHASE 2: ORGANIZATION RENAME"
echo "======================================"
echo ""
echo "GitHub Organization Rename:"
echo "  Current: VisualForgeMediaV2"
echo "  New: NiroForge (or NiroForgeV2)"
echo ""
echo "This will affect:"
echo "  • All repository URLs"
echo "  • CI/CD pipelines"
echo "  • Git remotes"
echo "  • Documentation links"
echo ""

echo "======================================"
echo "PHASE 3: MIGRATION INVENTORY"
echo "======================================"
echo ""

# Create inventory script
cat << 'INVENTORY' > create-migration-inventory.py
#!/usr/bin/env python3
import boto3
import json
from datetime import datetime

def create_inventory():
    """Create complete inventory of resources to migrate"""
    
    inventory = {
        "timestamp": datetime.now().isoformat(),
        "account_id": boto3.client('sts').get_caller_identity()['Account'],
        "resources": {
            "lambda_functions": [],
            "dynamodb_tables": [],
            "api_gateways": [],
            "s3_buckets": [],
            "cloudformation_stacks": []
        },
        "github_repos": [],
        "total_resources": 0
    }
    
    # Lambda functions
    lambda_client = boto3.client('lambda')
    functions = lambda_client.list_functions()
    
    for func in functions['Functions']:
        name = func['FunctionName']
        if 'vf' in name.lower() or 'visualforge' in name.lower():
            new_name = name.replace('dev-visualforge-', 'nf-').replace('dev-vf-', 'nf-').replace('-lambda', '')
            inventory['resources']['lambda_functions'].append({
                'current': name,
                'target': new_name,
                'type': 'NiroForge'
            })
        elif 'ns-' in name:
            new_name = name.replace('dev-ns-', 'ns-').replace('staging-ns-', 'ns-').replace('-lambda', '')
            inventory['resources']['lambda_functions'].append({
                'current': name,
                'target': new_name,
                'type': 'NiroSubs'
            })
    
    # DynamoDB tables
    dynamodb_client = boto3.client('dynamodb')
    tables = dynamodb_client.list_tables()
    
    for table_name in tables['TableNames']:
        if 'vf' in table_name.lower() or 'visualforge' in table_name.lower():
            new_name = table_name.replace('dev-vf-', 'nf-').replace('vf-', 'nf-').replace('-dev', '')
            inventory['resources']['dynamodb_tables'].append({
                'current': table_name,
                'target': new_name,
                'type': 'NiroForge'
            })
    
    # Count total
    for category in inventory['resources'].values():
        inventory['total_resources'] += len(category)
    
    # Save inventory
    with open('migration-inventory.json', 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"Inventory created: {inventory['total_resources']} resources to migrate")
    return inventory

if __name__ == "__main__":
    create_inventory()
INVENTORY

echo ""
echo "======================================"
echo "PHASE 4: GITHUB ORG MIGRATION"
echo "======================================"
echo ""
echo "Steps to rename GitHub organization:"
echo "1. Go to: https://github.com/organizations/VisualForgeMediaV2/settings"
echo "2. Rename to: NiroForge or NiroForgeV2"
echo "3. GitHub will create redirects automatically"
echo ""
echo "After GitHub rename, update:"
echo "  • Local git remotes"
echo "  • CI/CD webhook URLs"
echo "  • Documentation"
echo "  • AWS Secrets storing GitHub URLs"
echo ""

echo "======================================"
echo "PHASE 5: MIGRATION ORDER"
echo "======================================"
echo ""
echo "Recommended migration sequence:"
echo ""
echo "1. TAG EVERYTHING (safe, no changes)"
echo "   ./label-and-migrate-strategy.sh tag"
echo ""
echo "2. CREATE INVENTORY (document current state)"
echo "   python3 create-migration-inventory.py"
echo ""
echo "3. RENAME GITHUB ORG"
echo "   - Via GitHub settings"
echo "   - Update git remotes"
echo ""
echo "4. MIGRATE AWS RESOURCES (in order):"
echo "   a. Create new CloudFormation stacks with NF names"
echo "   b. Create new Lambda functions with NF names"
echo "   c. Copy DynamoDB data to new NF tables"
echo "   d. Update API Gateway with NF endpoints"
echo "   e. Update Route53 DNS if needed"
echo ""
echo "5. UPDATE APPLICATIONS"
echo "   - Environment variables"
echo "   - Config files"
echo "   - API endpoints"
echo ""
echo "6. TEST EVERYTHING"
echo ""
echo "7. DELETE OLD RESOURCES (after verification)"
echo ""

echo "======================================"
echo "SAFETY FIRST APPROACH"
echo "======================================"
echo ""
echo "✅ Safe to do now:"
echo "  • Tag all resources"
echo "  • Create inventory"
echo "  • Document current state"
echo ""
echo "⚠️  Requires planning:"
echo "  • GitHub org rename (affects all repos)"
echo "  • AWS resource migration (requires downtime)"
echo ""
echo "💡 Tip: Do this over a weekend when you can test thoroughly"