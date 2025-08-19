#!/usr/bin/env python3
"""
Automated resource renaming script for AWS resources
Removes environment prefixes and standardizes on org prefixes (vf-, ns-, na-)
"""

import boto3
import json
import sys
from datetime import datetime

# Initialize AWS clients
cf_client = boto3.client('cloudformation')
lambda_client = boto3.client('lambda')
dynamodb_client = boto3.client('dynamodb')
apigateway_client = boto3.client('apigateway')

# Mapping of old names to new names
LAMBDA_RENAMES = {
    # VisualForge functions
    'dev-visualforge-core': 'vf-core',
    'dev-vf-dashboard-lambda': 'vf-dashboard',
    'dev-vf-auth-lambda': 'vf-auth',
    'dev-vf-image-lambda': 'vf-image',
    'dev-vf-video-lambda': 'vf-video',
    'dev-vf-audio-lambda': 'vf-audio',
    'dev-vf-text-lambda': 'vf-text',
    'dev-vf-bulk-lambda': 'vf-bulk',
    'dev-visualforge-budgets-api': 'vf-budgets-api',
    'dev-visualforge-costs-api': 'vf-costs-api',
    'dev-visualforge-payments-api': 'vf-payments-api',
    'dev-visualforge-user-api': 'vf-user-api',
    'dev-visualforge-dashboard-api': 'vf-dashboard-api',
    'dev-visualforge-test-jwks': 'vf-test-jwks',
    'dev-visualforge-init-db': 'vf-init-db',
    'dev-visualforge-create-tables': 'vf-create-tables',
    'dev-visualforge-debug-db': 'vf-debug-db',
    'dev-visualforge-update-user': 'vf-update-user',
    
    # NiroSubs functions
    'dev-ns-core-lambda': 'ns-core',
    'dev-ns-user-lambda': 'ns-user',
    'dev-ns-dashboard-lambda': 'ns-dashboard',
    'dev-ns-dashboard-api': 'ns-dashboard-api',
    'dev-ns-payments-lambda': 'ns-payments',
    'dev-ns-payments-api': 'ns-payments-api',
    'dev-ns-user-api': 'ns-user-api',
    'dev-ns-auth-lambda': 'ns-auth',
    'dev-ns-core': 'ns-core-v2',
    
    # General functions
    'dev-create-test-users': 'na-create-test-users',
    'create_checkout_session': 'na-checkout-session',
}

DYNAMODB_RENAMES = {
    'dev-vf-media': 'vf-media',
    'dev-vf-users': 'vf-users',
    'dev-visualforge-budget-config': 'vf-budget-config',
    'dev-visualforge-tenant-costs': 'vf-tenant-costs',
    'vf-ai-generations-dev': 'vf-ai-generations',
    'vf-media-items-dev': 'vf-media-items',
    'vf-projects-dev': 'vf-projects',
    'vf-subscriptions-dev': 'vf-subscriptions',
    'DocumentManagementSystem': 'na-document-management',
    'UsersTable': 'na-users',
}

STACK_RENAMES = {
    'dev-vf-serverless-stack': 'vf-serverless-stack',
    'dev-visualforge-database': 'vf-database',
    'dev-monitoring-simple': 'na-monitoring',
    'dev-secrets-manager': 'na-secrets',
    'dev-route53-dns': 'na-route53',
    'dev-ns-lambda-functions': 'ns-lambda-stack',
    'dev-ns-auth': 'ns-auth-stack',
}

def generate_cloudformation_updates():
    """Generate CloudFormation template updates"""
    print("\n=== CLOUDFORMATION TEMPLATE UPDATES ===\n")
    
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Standardized resource naming - no environment prefixes",
        "Resources": {}
    }
    
    # Generate Lambda function resources
    for old_name, new_name in LAMBDA_RENAMES.items():
        if old_name.startswith('dev-vf') or 'visualforge' in old_name:
            org = 'vf'
        elif old_name.startswith('dev-ns'):
            org = 'ns'
        else:
            org = 'na'
            
        resource_name = ''.join([word.capitalize() for word in new_name.replace('-', ' ').split()])
        
        template["Resources"][resource_name] = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "FunctionName": new_name,
                "Runtime": "nodejs18.x",
                "Handler": "index.handler",
                "Role": {"Fn::Sub": "arn:aws:iam::${AWS::AccountId}:role/lambda-execution-role"},
                "Tags": [
                    {"Key": "Organization", "Value": org.upper()},
                    {"Key": "Environment", "Value": "development"},
                    {"Key": "ManagedBy", "Value": "CloudFormation"}
                ]
            }
        }
    
    # Save template
    with open('standardized-naming-template.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("Template saved to: standardized-naming-template.json")
    print("\nKey changes:")
    print("  • Removed all 'dev-' and 'staging-' prefixes")
    print("  • Standardized on org prefixes: vf-, ns-, na-")
    print("  • Added consistent tagging for organization tracking")

def generate_serverless_config():
    """Generate Serverless Framework configuration"""
    print("\n=== SERVERLESS.YML CONFIGURATION ===\n")
    
    vf_config = """
service: vf-services

provider:
  name: aws
  runtime: nodejs18.x
  region: us-east-1
  # No stage prefix - this is your dev account!
  
functions:
  core:
    name: vf-core
    handler: src/core/handler.main
    
  dashboard:
    name: vf-dashboard
    handler: src/dashboard/handler.main
    
  auth:
    name: vf-auth
    handler: src/auth/handler.main
    
  image:
    name: vf-image
    handler: src/image/handler.main

resources:
  Resources:
    MediaTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: vf-media
        
    UsersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: vf-users
"""

    ns_config = """
service: ns-services

provider:
  name: aws
  runtime: nodejs18.x
  region: us-east-1
  
functions:
  core:
    name: ns-core
    handler: src/core/handler.main
    
  user:
    name: ns-user
    handler: src/user/handler.main
    
  dashboard:
    name: ns-dashboard
    handler: src/dashboard/handler.main
    
  payments:
    name: ns-payments
    handler: src/payments/handler.main
"""

    with open('serverless-vf.yml', 'w') as f:
        f.write(vf_config)
    
    with open('serverless-ns.yml', 'w') as f:
        f.write(ns_config)
    
    print("Generated serverless configurations:")
    print("  • serverless-vf.yml - VisualForge services")
    print("  • serverless-ns.yml - NiroSubs services")

def generate_migration_script():
    """Generate migration bash script"""
    print("\n=== MIGRATION SCRIPT ===\n")
    
    script = """#!/bin/bash

# DynamoDB Table Migration Script
echo "Starting DynamoDB table migration..."

# Function to copy DynamoDB table
copy_dynamodb_table() {
    OLD_TABLE=$1
    NEW_TABLE=$2
    
    echo "Copying $OLD_TABLE to $NEW_TABLE..."
    
    # Create new table with same schema
    aws dynamodb create-table \\
        --table-name $NEW_TABLE \\
        --cli-input-json "$(aws dynamodb describe-table --table-name $OLD_TABLE --query 'Table.{AttributeDefinitions:AttributeDefinitions,KeySchema:KeySchema,BillingMode:BillingMode,GlobalSecondaryIndexes:GlobalSecondaryIndexes,LocalSecondaryIndexes:LocalSecondaryIndexes}' --output json)"
    
    # Wait for table to be active
    aws dynamodb wait table-exists --table-name $NEW_TABLE
    
    # Copy data (you might want to use AWS Data Pipeline for large tables)
    echo "Table created. Use AWS Data Pipeline or DynamoDB Streams for data migration."
}

# Migrate VF tables
copy_dynamodb_table "dev-vf-media" "vf-media"
copy_dynamodb_table "dev-vf-users" "vf-users"
copy_dynamodb_table "dev-visualforge-budget-config" "vf-budget-config"
copy_dynamodb_table "dev-visualforge-tenant-costs" "vf-tenant-costs"

echo "Migration script complete!"
"""

    with open('migrate-tables.sh', 'w') as f:
        f.write(script)
    
    print("Generated migration script: migrate-tables.sh")

def main():
    print("====================================")
    print("RESOURCE NAMING STANDARDIZATION")
    print("====================================")
    print()
    print("This script will help standardize AWS resource naming:")
    print("  • Remove environment prefixes (dev-, staging-)")
    print("  • Organize by organization (vf-, ns-, na-)")
    print("  • Generate updated configurations")
    print()
    
    # Generate all configurations
    generate_cloudformation_updates()
    generate_serverless_config()
    generate_migration_script()
    
    print("\n====================================")
    print("NEXT STEPS:")
    print("====================================")
    print()
    print("1. Review generated configuration files")
    print("2. Update your application code to use new resource names")
    print("3. Deploy new resources with standardized names")
    print("4. Migrate data from old resources")
    print("5. Delete old resources once migration is complete")
    print()
    print("IMPORTANT: This is a significant change that requires:")
    print("  • Application code updates")
    print("  • Configuration updates")
    print("  • Data migration")
    print("  • Careful testing")
    
if __name__ == "__main__":
    main()