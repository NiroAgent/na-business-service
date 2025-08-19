#!/bin/bash

# VF Live Dashboard - GitOps Deployment Guide
# This script helps configure the infrastructure for automated deployments

set -e

echo "🚀 VF Live Dashboard - GitOps Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━function trigger_deployment() {
    local ENV=$1
    
    echo "🚀 Triggering GitHub Actions deployment for environment: $ENV"
    
    # Determine target branch based on environment
    case $ENV in
        dev)
            BRANCH="development"
            echo "📱 Target branch: $BRANCH (development branch → VF-dev)"
            ;;
        staging)
            BRANCH="release/$(date +%Y.%m.%d)"
            echo "📦 Target branch: $BRANCH (release branch → Staging)"
            ;;
        production)
            BRANCH="main"
            echo "🏭 Target branch: $BRANCH (main branch → Production)"
            ;;
        *)
            echo "❌ Invalid environment: $ENV"
            echo "   Valid environments: dev, staging, production"
            return 1
            ;;
    esac
    
    echo ""
    echo "🔄 Deployment Strategy:"
    echo "   • development/dev branch → VF-dev environment"
    echo "   • release/* branches → Staging environment"
    echo "   • main branch → Production environment"
    echo ""# Configuration
GITHUB_REPO="NiroAgentV2/autonomous-business-system"
ENVIRONMENTS=("dev" "staging" "production")
ACCOUNT_MAPPING=(
    "dev:319040880702"
    "staging:275057778147" 
    "production:229742714212"
)

echo "📋 Repository: https://github.com/${GITHUB_REPO}"
echo "🏗️ Environments: ${ENVIRONMENTS[*]}"
echo ""

function print_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup-oidc     Configure GitHub OIDC for AWS authentication"
    echo "  deploy-infra   Deploy CloudFormation infrastructure"
    echo "  check-status   Check deployment status"
    echo "  trigger-deploy Trigger GitHub Actions deployment"
    echo "  help           Show this help message"
    echo ""
    echo "Options:"
    echo "  --env          Environment (dev, staging, production)"
    echo "  --account      AWS Account ID"
    echo ""
    echo "Examples:"
    echo "  $0 setup-oidc --env dev --account 319040880702"
    echo "  $0 deploy-infra --env dev"
    echo "  $0 trigger-deploy --env dev"
}

function setup_oidc() {
    local ENV=$1
    local ACCOUNT_ID=$2
    
    echo "🔐 Setting up GitHub OIDC for environment: $ENV"
    echo "   Account: $ACCOUNT_ID"
    
    # Create OIDC Identity Provider
    cat > oidc-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${GITHUB_REPO}:*"
        }
      }
    }
  ]
}
EOF

    # Check if OIDC provider exists
    if ! aws iam get-open-id-connect-provider \
        --open-id-connect-provider-arn "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com" \
        --region us-east-1 2>/dev/null; then
        
        echo "📝 Creating OIDC provider..."
        aws iam create-open-id-connect-provider \
            --url https://token.actions.githubusercontent.com \
            --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
            --client-id-list sts.amazonaws.com \
            --region us-east-1
    else
        echo "✅ OIDC provider already exists"
    fi
    
    # Create or update role
    ROLE_NAME="GitHubActionsRole-Dashboard-${ENV}"
    
    if aws iam get-role --role-name "$ROLE_NAME" --region us-east-1 2>/dev/null; then
        echo "📝 Updating existing role: $ROLE_NAME"
        aws iam update-assume-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-document file://oidc-trust-policy.json \
            --region us-east-1
    else
        echo "📝 Creating new role: $ROLE_NAME"
        aws iam create-role \
            --role-name "$ROLE_NAME" \
            --assume-role-policy-document file://oidc-trust-policy.json \
            --region us-east-1
    fi
    
    # Attach necessary policies
    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser \
        --region us-east-1
        
    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy \
        --region us-east-1
        
    # Clean up temp files
    rm -f oidc-trust-policy.json
    
    echo "✅ OIDC setup complete for $ENV environment"
    echo "   Role ARN: arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
}

function deploy_infrastructure() {
    local ENV=$1
    
    echo "🏗️ Deploying infrastructure for environment: $ENV"
    
    # Get account ID for environment
    local ACCOUNT_ID=""
    for mapping in "${ACCOUNT_MAPPING[@]}"; do
        if [[ $mapping == ${ENV}:* ]]; then
            ACCOUNT_ID=${mapping#*:}
            break
        fi
    done
    
    if [[ -z "$ACCOUNT_ID" ]]; then
        echo "❌ Unknown environment: $ENV"
        exit 1
    fi
    
    echo "   Account: $ACCOUNT_ID"
    
    # Deploy ECR repository
    echo "📦 Deploying ECR repository..."
    aws cloudformation deploy \
        --template-file infrastructure/cloudformation/ecr-repository.yml \
        --stack-name "vf-dashboard-ecr-${ENV}" \
        --parameter-overrides \
            Environment="$ENV" \
            RepositoryName="vf-live-dashboard" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region us-east-1
    
    # Deploy EKS cluster (optional - might already exist)
    echo "☸️ Checking EKS cluster..."
    if ! aws eks describe-cluster --name "vf-dashboard-${ENV}" --region us-east-1 2>/dev/null; then
        echo "📝 Deploying EKS cluster..."
        aws cloudformation deploy \
            --template-file infrastructure/cloudformation/eks-cluster.yml \
            --stack-name "vf-dashboard-eks-${ENV}" \
            --parameter-overrides \
                Environment="$ENV" \
                ClusterName="vf-dashboard-${ENV}" \
            --capabilities CAPABILITY_NAMED_IAM \
            --region us-east-1 \
            --timeout-in-minutes 30
    else
        echo "✅ EKS cluster already exists"
    fi
    
    # Deploy ALB and ingress (optional)
    echo "🌐 Deploying ALB ingress..."
    aws cloudformation deploy \
        --template-file infrastructure/cloudformation/alb-ingress.yml \
        --stack-name "vf-dashboard-alb-${ENV}" \
        --parameter-overrides \
            Environment="$ENV" \
            DomainName="${ENV}.visualforge.com" \
            ClusterName="vf-dashboard-${ENV}" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region us-east-1 || echo "⚠️ ALB deployment may require manual DNS configuration"
    
    echo "✅ Infrastructure deployment complete for $ENV"
}

function check_deployment_status() {
    local ENV=$1
    
    echo "📊 Checking deployment status for: $ENV"
    
    # Check CloudFormation stacks
    echo ""
    echo "📋 CloudFormation Stacks:"
    aws cloudformation list-stacks \
        --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
        --query "StackSummaries[?contains(StackName, 'vf-dashboard') && contains(StackName, '${ENV}')].{Name:StackName,Status:StackStatus,Created:CreationTime}" \
        --output table \
        --region us-east-1
    
    # Check ECR repository
    echo ""
    echo "📦 ECR Repository:"
    if aws ecr describe-repositories --repository-names vf-live-dashboard --region us-east-1 2>/dev/null; then
        echo "✅ ECR repository exists"
        aws ecr describe-images \
            --repository-name vf-live-dashboard \
            --query 'imageDetails[*].{Tags:imageTags,Pushed:imagePushedAt,Size:imageSizeInBytes}' \
            --output table \
            --region us-east-1 | head -10
    else
        echo "❌ ECR repository not found"
    fi
    
    # Check EKS cluster
    echo ""
    echo "☸️ EKS Cluster:"
    if aws eks describe-cluster --name "vf-dashboard-${ENV}" --region us-east-1 2>/dev/null; then
        echo "✅ EKS cluster exists"
        
        # Check if we can connect to cluster
        if kubectl cluster-info 2>/dev/null; then
            echo "✅ kubectl connected to cluster"
            
            # Check dashboard deployment
            if kubectl get deployment vf-live-dashboard -n vf-dev 2>/dev/null; then
                echo "✅ Dashboard deployment found"
                kubectl get pods -n vf-dev -l app=vf-live-dashboard
            else
                echo "❌ Dashboard deployment not found"
            fi
        else
            echo "⚠️ kubectl not connected to cluster"
            echo "   Run: aws eks update-kubeconfig --region us-east-1 --name vf-dashboard-${ENV}"
        fi
    else
        echo "❌ EKS cluster not found"
    fi
}

function trigger_deployment() {
    local ENV=$1
    
    echo "🚀 Triggering GitHub Actions deployment for: $ENV"
    
    # Check if gh CLI is available
    if ! command -v gh &> /dev/null; then
        echo "❌ GitHub CLI (gh) is required for triggering deployments"
        echo "   Install: https://cli.github.com/"
        echo ""
        echo "🔧 Manual trigger:"
        echo "   1. Go to: https://github.com/${GITHUB_REPO}/actions/workflows/deploy-dashboard.yml"
        echo "   2. Click 'Run workflow'"
        echo "   3. Select environment: $ENV"
        echo "   4. Click 'Run workflow'"
        return 1
    fi
    
    # Trigger workflow
    echo "📝 Triggering workflow for environment: $ENV"
    gh workflow run deploy-dashboard.yml \
        --repo "$GITHUB_REPO" \
        --field environment="$ENV"
    
    echo "✅ Deployment triggered!"
    echo "🔗 View progress: https://github.com/${GITHUB_REPO}/actions"
    
    # Wait a moment and show recent runs
    sleep 3
    echo ""
    echo "📊 Recent workflow runs:"
    gh run list \
        --repo "$GITHUB_REPO" \
        --workflow deploy-dashboard.yml \
        --limit 5
}

# Parse command line arguments
COMMAND=$1
ENV=""
ACCOUNT_ID=""

shift 2>/dev/null || true

while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENV="$2"
            shift 2
            ;;
        --account)
            ACCOUNT_ID="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            print_help
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    setup-oidc)
        if [[ -z "$ENV" || -z "$ACCOUNT_ID" ]]; then
            echo "❌ Environment and account ID required for OIDC setup"
            print_help
            exit 1
        fi
        setup_oidc "$ENV" "$ACCOUNT_ID"
        ;;
    deploy-infra)
        if [[ -z "$ENV" ]]; then
            echo "❌ Environment required for infrastructure deployment"
            print_help
            exit 1
        fi
        deploy_infrastructure "$ENV"
        ;;
    check-status)
        if [[ -z "$ENV" ]]; then
            ENV="dev"
        fi
        check_deployment_status "$ENV"
        ;;
    trigger-deploy)
        if [[ -z "$ENV" ]]; then
            ENV="dev"
        fi
        trigger_deployment "$ENV"
        ;;
    help|--help|-h)
        print_help
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        print_help
        exit 1
        ;;
esac

echo ""
echo "🎉 GitOps deployment management complete!"
echo "📚 For more information, see: README.md"
