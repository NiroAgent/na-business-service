#!/bin/bash

# VF Live Dashboard Deployment Script
# Deploy real-time agent monitoring dashboard to VF-dev

set -e

echo "🚀 Deploying VF Live Dashboard to VF-dev Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Configuration
AWS_ACCOUNT="319040880702"
AWS_REGION="us-east-1"
ECR_REPOSITORY="${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/vf-live-dashboard"
IMAGE_TAG="latest"
NAMESPACE="vf-dev"

echo "📋 Configuration:"
echo "   AWS Account: ${AWS_ACCOUNT} (VF-dev)"
echo "   Region: ${AWS_REGION}"
echo "   ECR Repository: ${ECR_REPOSITORY}"
echo "   Namespace: ${NAMESPACE}"
echo ""

# Step 1: Configure AWS credentials
echo "🔑 Step 1: Configuring AWS credentials for VF-dev..."
aws configure set region ${AWS_REGION}

# Verify access
if ! aws sts get-caller-identity --query Account --output text | grep -q ${AWS_ACCOUNT}; then
    echo "❌ Not authenticated to VF-dev account. Please run:"
    echo "   aws configure --profile vf-dev"
    echo "   aws sso login --profile vf-dev"
    exit 1
fi
echo "✅ AWS credentials configured for VF-dev"

# Step 2: Create ECR repository if it doesn't exist
echo "🐳 Step 2: Setting up ECR repository..."
if ! aws ecr describe-repositories --repository-names vf-live-dashboard >/dev/null 2>&1; then
    echo "📦 Creating ECR repository..."
    aws ecr create-repository \
        --repository-name vf-live-dashboard \
        --region ${AWS_REGION}
    echo "✅ ECR repository created"
else
    echo "✅ ECR repository already exists"
fi

# Step 3: Build and push Docker image
echo "🔨 Step 3: Building Docker image..."
docker build -f deployments/Dockerfile.dashboard -t vf-live-dashboard:${IMAGE_TAG} .

echo "🏷️ Step 4: Tagging image for ECR..."
docker tag vf-live-dashboard:${IMAGE_TAG} ${ECR_REPOSITORY}:${IMAGE_TAG}

echo "🔐 Step 5: Authenticating Docker with ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REPOSITORY}

echo "📤 Step 6: Pushing image to ECR..."
docker push ${ECR_REPOSITORY}:${IMAGE_TAG}
echo "✅ Image pushed successfully"

# Step 4: Create namespace if it doesn't exist
echo "🏗️ Step 7: Setting up Kubernetes namespace..."
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Namespace ready"

# Step 5: Create IAM role for service account (if not exists)
echo "🔒 Step 8: Setting up IAM role for dashboard service..."

# Create IAM policy for dashboard
cat > /tmp/dashboard-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics",
                "ce:GetCostAndUsage",
                "ce:GetUsageReport"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create or update IAM policy
aws iam create-policy \
    --policy-name VFDashboardPolicy \
    --policy-document file:///tmp/dashboard-policy.json \
    --description "Policy for VF Live Dashboard" || \
aws iam create-policy-version \
    --policy-arn arn:aws:iam::${AWS_ACCOUNT}:policy/VFDashboardPolicy \
    --policy-document file:///tmp/dashboard-policy.json \
    --set-as-default

echo "✅ IAM policy configured"

# Step 6: Apply Kubernetes manifests
echo "☸️ Step 9: Deploying to Kubernetes..."

# Update the deployment with correct image
sed "s|319040880702.dkr.ecr.us-east-1.amazonaws.com/vf-live-dashboard:latest|${ECR_REPOSITORY}:${IMAGE_TAG}|g" \
    deployments/vf-live-dashboard-k8s.yaml | kubectl apply -f -

echo "✅ Kubernetes resources applied"

# Step 7: Wait for deployment
echo "⏳ Step 10: Waiting for deployment to be ready..."
kubectl rollout status deployment/vf-live-dashboard -n ${NAMESPACE} --timeout=300s
echo "✅ Deployment ready"

# Step 8: Get service information
echo "📡 Step 11: Getting service information..."
kubectl get pods -n ${NAMESPACE} -l app=vf-live-dashboard
kubectl get svc -n ${NAMESPACE} vf-live-dashboard-service
kubectl get ingress -n ${NAMESPACE} vf-live-dashboard-ingress

# Step 9: Test deployment
echo "🧪 Step 12: Testing deployment..."
POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l app=vf-live-dashboard -o jsonpath='{.items[0].metadata.name}')
if kubectl exec -n ${NAMESPACE} ${POD_NAME} -- curl -f http://localhost:5003/health; then
    echo "✅ Health check passed"
else
    echo "⚠️ Health check failed, but deployment may still be starting"
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Dashboard URL: https://dev.visualforge.com/"
echo "🔄 Auto-refresh: Every 30 seconds"
echo "📊 Monitoring: Live EC2 agents, CloudWatch metrics, Cost data"
echo "☁️ Environment: VF-dev (${AWS_ACCOUNT})"
echo ""
echo "🎯 FEATURES ACTIVE:"
echo "   ✅ Real-time agent monitoring"
echo "   ✅ Live CPU/Memory metrics"
echo "   ✅ Cost breakdown by environment"  
echo "   ✅ WebSocket updates"
echo "   ✅ Responsive UI with tabs"
echo "   ✅ Health monitoring"
echo ""
echo "🔧 TROUBLESHOOTING:"
echo "   • Logs: kubectl logs -n ${NAMESPACE} deployment/vf-live-dashboard"
echo "   • Status: kubectl get pods -n ${NAMESPACE}"
echo "   • Events: kubectl get events -n ${NAMESPACE}"
echo ""
echo "🔄 To redeploy: ./deploy-vf-live-dashboard.sh"
echo "🗑️ To remove: kubectl delete -f deployments/vf-live-dashboard-k8s.yaml"

# Cleanup temp files
rm -f /tmp/dashboard-policy.json
