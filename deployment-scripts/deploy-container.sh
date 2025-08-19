#!/bin/bash
# Deploy Container-based Agent System

echo "Building and deploying container-based agent system..."

# Build and push Docker image
docker build -f Dockerfile.agents -t vf-dev-agents .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 816454053517.dkr.ecr.us-east-1.amazonaws.com
docker tag vf-dev-agents:latest 816454053517.dkr.ecr.us-east-1.amazonaws.com/vf-dev-agents:latest
docker push 816454053517.dkr.ecr.us-east-1.amazonaws.com/vf-dev-agents:latest

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create or update service
aws ecs create-service \
  --cluster vf-dev-agents \
  --service-name multi-agent-service \
  --task-definition vf-dev-multi-agents \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"

echo "Container deployment complete!"
echo "Cost: ~$85-95/month for Fargate"
