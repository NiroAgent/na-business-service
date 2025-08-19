#!/bin/bash

# DynamoDB Table Migration Script
echo "Starting DynamoDB table migration..."

# Function to copy DynamoDB table
copy_dynamodb_table() {
    OLD_TABLE=$1
    NEW_TABLE=$2
    
    echo "Copying $OLD_TABLE to $NEW_TABLE..."
    
    # Create new table with same schema
    aws dynamodb create-table \
        --table-name $NEW_TABLE \
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
