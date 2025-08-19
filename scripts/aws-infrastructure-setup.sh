#!/bin/bash

# AWS Infrastructure Setup for AI Agent Processing
# This script sets up the necessary AWS resources for processing GitHub issues

echo "Setting up AWS infrastructure for AI Agent Processing"
echo "======================================================"

# Variables
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BATCH_COMPUTE_ENV="ai-agents-compute-env"
BATCH_JOB_QUEUE="ai-agents-queue"
LAMBDA_FUNCTION="ai-agent-processor"
S3_BUCKET="ai-agents-code-${ACCOUNT_ID}"

# Create S3 bucket for agent code
echo "Creating S3 bucket for agent code..."
aws s3 mb s3://${S3_BUCKET} --region ${REGION} 2>/dev/null || echo "Bucket may already exist"

# Upload agent scripts to S3
echo "Uploading agent scripts to S3..."
for agent in ai-*.py; do
    if [ -f "$agent" ]; then
        aws s3 cp "$agent" s3://${S3_BUCKET}/agents/ --region ${REGION}
        echo "Uploaded $agent"
    fi
done

# Create IAM roles
echo "Creating IAM roles..."

# Batch execution role
cat > batch-execution-role-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "batch.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
    --role-name ai-agent-batch-execution-role \
    --assume-role-policy-document file://batch-execution-role-policy.json \
    2>/dev/null || echo "Execution role may already exist"

aws iam attach-role-policy \
    --role-name ai-agent-batch-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Batch job role
cat > batch-job-role-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
    --role-name ai-agent-batch-role \
    --assume-role-policy-document file://batch-job-role-policy.json \
    2>/dev/null || echo "Job role may already exist"

# Create policy for job role
cat > batch-job-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::${S3_BUCKET}/*",
        "arn:aws:s3:::${S3_BUCKET}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:github-token-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name ai-agent-batch-role \
    --policy-name ai-agent-batch-policy \
    --policy-document file://batch-job-policy.json

# Create Batch compute environment
echo "Creating Batch compute environment..."
cat > compute-environment.json << EOF
{
  "computeEnvironmentName": "${BATCH_COMPUTE_ENV}",
  "type": "MANAGED",
  "state": "ENABLED",
  "computeResources": {
    "type": "FARGATE_SPOT",
    "maxvCpus": 4,
    "subnets": ["subnet-xxxxx", "subnet-yyyyy"],
    "securityGroupIds": ["sg-xxxxx"]
  },
  "serviceRole": "arn:aws:iam::${ACCOUNT_ID}:role/aws-batch-service-role"
}
EOF

# Note: You need to update subnets and security groups
echo "NOTE: Update subnets and security groups in compute-environment.json"

# Create Batch job queue
echo "Creating Batch job queue..."
aws batch create-job-queue \
    --job-queue-name ${BATCH_JOB_QUEUE} \
    --priority 1 \
    --compute-environment-order order=1,computeEnvironment=${BATCH_COMPUTE_ENV} \
    --region ${REGION} \
    2>/dev/null || echo "Job queue may already exist"

# Register job definition
echo "Registering Batch job definition..."
# Update the account ID in the job definition
sed -i "s/ACCOUNT_ID/${ACCOUNT_ID}/g" aws-batch-job-definition.json
aws batch register-job-definition --cli-input-json file://aws-batch-job-definition.json --region ${REGION}

# Create Lambda function
echo "Creating Lambda function for P0 issues..."
zip lambda-function.zip aws-batch-agent-processor.py

aws lambda create-function \
    --function-name ${LAMBDA_FUNCTION} \
    --runtime python3.11 \
    --role arn:aws:iam::${ACCOUNT_ID}:role/lambda-execution-role \
    --handler aws-batch-agent-processor.lambda_handler \
    --zip-file fileb://lambda-function.zip \
    --timeout 60 \
    --memory-size 256 \
    --environment "Variables={GITHUB_TOKEN=ENCRYPTED,GITHUB_REPO=VisualForgeMediaV2/business-operations}" \
    --region ${REGION} \
    2>/dev/null || echo "Lambda function may already exist"

# Store GitHub token in Secrets Manager
echo "Storing GitHub token in Secrets Manager..."
echo "Run: aws secretsmanager create-secret --name github-token --secret-string 'YOUR_GITHUB_TOKEN'"

echo "======================================================"
echo "AWS Infrastructure Setup Complete!"
echo "======================================================"
echo ""
echo "Next steps:"
echo "1. Update subnets and security groups in compute-environment.json"
echo "2. Create the compute environment: aws batch create-compute-environment --cli-input-json file://compute-environment.json"
echo "3. Store your GitHub token: aws secretsmanager create-secret --name github-token --secret-string 'YOUR_TOKEN'"
echo "4. Update GitHub Actions secrets in your repository settings"
echo "5. Push the workflow file to trigger automatic processing"

# Clean up temp files
rm -f batch-*.json compute-environment.json lambda-function.zip