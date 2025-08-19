#!/bin/bash
# Deploy Single Instance Agent System to VF-Dev

echo "Deploying cost-optimized single instance agent system..."

aws cloudformation deploy \
  --template-file single-instance-agents.yaml \
  --stack-name vf-dev-single-instance-agents \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    InstanceType=t3.large \
    Environment=vf-dev \
  --region us-east-1

echo "Getting deployment outputs..."
aws cloudformation describe-stacks \
  --stack-name vf-dev-single-instance-agents \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'

echo "Deployment complete! All 50 agents will be running on a single instance."
echo "Cost: ~$60-70/month"
