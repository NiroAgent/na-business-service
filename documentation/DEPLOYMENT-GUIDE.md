# VF-Dev Deployment Guide

This guide documents the CI/CD pipeline setup for deploying NiroSubs-V2 and VisualForgeMediaV2 to the vf-dev AWS account.

## Overview

Both projects are configured with GitHub Actions pipelines that automatically deploy to the vf-dev AWS account when code is merged to the `dev` branch.

### AWS Account Details
- **Account ID**: 816454053517
- **Region**: us-east-1
- **Environment**: vf-dev

## Projects

### 1. NiroSubs-V2
- **Location**: `E:\Projects\NiroSubs-V2`
- **Pipeline**: `.github/workflows/deploy-to-vf-dev.yml`
- **Services**:
  - Authentication (Cognito)
  - API Gateway
  - Lambda Functions (Core, Auth, Dashboard, Payments, User)
  - Frontend Applications (Shell, Auth, Dashboard, Payments, User)
  - Database (Aurora Serverless)

### 2. VisualForgeMediaV2
- **Location**: `E:\Projects\VisualForgeMediaV2`
- **Pipeline**: `.github/workflows/deploy-to-vf-dev.yml`
- **Services**:
  - ECS Cluster with Fargate
  - Media Services (Video, Image, Audio, Text, Dashboard)
  - ECR Repositories for Docker images
  - CloudFront Distribution
  - Application Load Balancer

## Deployment Process

### Automatic Deployment (Recommended)

The deployment is triggered automatically when code is pushed to the `dev` branch:

```bash
# Switch to dev branch
git checkout dev

# Make your changes
git add .
git commit -m "Your changes"

# Push to trigger deployment
git push origin dev
```

### Manual Deployment

Use the provided PowerShell script to trigger deployments:

```powershell
# Deploy both projects
.\deploy-to-vf-dev.ps1

# Deploy only NiroSubs-V2
.\deploy-to-vf-dev.ps1 -NiroSubsOnly

# Deploy only VisualForgeMediaV2
.\deploy-to-vf-dev.ps1 -MediaOnly

# Deploy from a different branch
.\deploy-to-vf-dev.ps1 -Branch feature-branch
```

## Pipeline Features

### NiroSubs-V2 Pipeline

1. **Infrastructure Deployment**
   - Database stack (Aurora Serverless)
   - Cognito authentication
   - API Gateway configuration

2. **Lambda Functions**
   - Builds and deploys all Lambda functions
   - Uses Node.js 18 runtime
   - Automatic dependency installation

3. **Frontend Applications**
   - Builds React applications
   - Deploys to S3 buckets
   - CloudFront invalidation

4. **Integration Tests**
   - Health checks for all API endpoints
   - Optional integration test suite

### VisualForgeMediaV2 Pipeline

1. **Infrastructure Setup**
   - VPC configuration
   - ECS cluster creation
   - Secrets Manager setup
   - Monitoring dashboard

2. **Container Services**
   - Builds Docker images for each service
   - Pushes to ECR repositories
   - Deploys to ECS with Fargate

3. **Integration with NiroSubs**
   - Stores service URLs in SSM Parameter Store
   - Enables cross-project communication

## Integration Between Projects

The VisualForgeMedia services are integrated into NiroSubs through:

1. **Media Services Tab**: Added to NiroSubs dashboard
2. **Secure iFrame Integration**: Media services displayed within NiroSubs
3. **Shared Authentication**: Token passing via postMessage API
4. **Configuration**: Stored in SSM Parameter Store

### Integration Components

- **NiroSubs Component**: `ns-shell/src/components/MediaServicesIntegration.tsx`
- **Configuration**: `ns-shell/src/config/media-services.ts`
- **Dashboard Integration**: Media Services tab in main navigation

## Prerequisites

### Required Tools
- Git
- Node.js 18+
- Docker (for VisualForgeMediaV2)
- AWS CLI configured with credentials
- GitHub CLI (optional, for monitoring)

### AWS Setup

1. **OIDC Provider**: GitHub Actions OIDC provider must be configured
2. **IAM Role**: `GitHubActionsRole` with necessary permissions
3. **SSL Certificate**: Required for HTTPS endpoints
4. **Route53**: Domain configuration (optional)

## Monitoring Deployment

### GitHub Actions
- View workflow runs: https://github.com/[your-org]/[repo]/actions
- Check deployment status in real-time
- View logs for troubleshooting

### AWS Console
- CloudFormation: Check stack status
- ECS: Monitor container services
- CloudWatch: View application logs
- API Gateway: Test endpoints

## URLs After Deployment

### NiroSubs-V2
- **Application**: https://dev.visualforge.ai
- **API Gateway**: https://api-dev.visualforge.ai
- **Endpoints**:
  - Core API: https://api-dev.visualforge.ai/core/api/health
  - User API: https://api-dev.visualforge.ai/user/api/health
  - Dashboard API: https://api-dev.visualforge.ai/dashboard/api/health
  - Payments API: https://api-dev.visualforge.ai/payments/api/health

### VisualForgeMediaV2
- **CloudFront**: https://media-dev.visualforge.ai
- **ALB**: http://vf-media-alb-dev.us-east-1.elb.amazonaws.com
- **Services**:
  - Video: /video
  - Image: /image
  - Audio: /audio
  - Text: /text
  - Dashboard: /dashboard

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure AWS credentials are configured
   - Check IAM role permissions
   - Verify OIDC provider setup

2. **Build Failures**
   - Check Node.js version compatibility
   - Verify package dependencies
   - Review build logs in GitHub Actions

3. **Deployment Failures**
   - Check CloudFormation stack events
   - Verify resource limits in AWS account
   - Review ECS task logs for container issues

4. **Integration Issues**
   - Verify SSM parameters are set correctly
   - Check CORS configuration
   - Ensure authentication tokens are passed correctly

### Debug Commands

```bash
# Check AWS credentials
aws sts get-caller-identity

# List CloudFormation stacks
aws cloudformation list-stacks --region us-east-1

# Check ECS services
aws ecs list-services --cluster vf-media-cluster-dev

# View SSM parameters
aws ssm get-parameter --name /dev/vf-media/alb-url
aws ssm get-parameter --name /dev/vf-media/cloudfront-url
```

## Security Considerations

1. **Secrets Management**
   - Database passwords stored in Secrets Manager
   - API keys in environment variables
   - No hardcoded credentials in code

2. **Network Security**
   - VPC isolation for backend services
   - Security groups restrict access
   - HTTPS enforced for all public endpoints

3. **Authentication**
   - AWS Cognito for user management
   - JWT tokens for API access
   - Cross-origin security via CORS

## Maintenance

### Updating Pipelines
1. Modify `.github/workflows/deploy-to-vf-dev.yml`
2. Test changes in a feature branch
3. Create PR and merge to dev

### Adding New Services
1. Update pipeline to include new service
2. Add ECR repository (for containers)
3. Update task definitions or Lambda configurations
4. Add health check endpoints

### Scaling
- Adjust ECS task counts
- Modify Lambda memory/timeout settings
- Update CloudFront cache behaviors
- Scale Aurora Serverless capacity

## Support

For issues or questions:
1. Check GitHub Actions logs
2. Review AWS CloudWatch logs
3. Consult AWS CloudFormation events
4. Check integration test results

## Next Steps

After successful deployment:
1. Run integration tests
2. Verify all services are healthy
3. Test media service integration in NiroSubs
4. Configure monitoring alerts
5. Set up backup strategies