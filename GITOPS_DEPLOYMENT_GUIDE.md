# VF Live Dashboard - GitOps Deployment

Complete Infrastructure-as-Code solution for deploying the VF Live Dashboard across multiple AWS environments using GitHub Actions and CloudFormation.

## 🎯 Overview

This solution provides:
- **Infrastructure as Code**: CloudFormation templates for all AWS resources
- **GitOps Workflow**: Automated deployments via GitHub Actions
- **Multi-Environment**: Dev, Staging, and Production environments
- **Security**: OIDC authentication, no long-lived credentials
- **Monitoring**: Built-in CloudWatch monitoring and alerts

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │    │  GitHub Actions │    │   AWS Account   │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Dashboard   │ │───▶│ │ Build &     │ │───▶│ │ ECR         │ │
│ │ Code        │ │    │ │ Push Image  │ │    │ │ Repository  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ CloudForm.  │ │───▶│ │ Deploy      │ │───▶│ │ EKS Cluster │ │
│ │ Templates   │ │    │ │ Infra       │ │    │ │ + Dashboard │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Directory Structure

```
E:\Projects\
├── .github/workflows/
│   └── deploy-dashboard.yml          # GitHub Actions workflow
├── dashboard/
│   ├── vf-live-dashboard.py         # Main dashboard application
│   ├── Dockerfile                   # Container configuration
│   ├── k8s-deployment.yaml         # Kubernetes manifests
│   └── requirements.txt            # Python dependencies
├── infrastructure/cloudformation/
│   ├── ecr-repository.yml          # ECR + IAM roles
│   ├── eks-cluster.yml             # EKS cluster + networking
│   ├── alb-ingress.yml            # ALB + SSL certificates
│   └── route53-record.yml         # DNS configuration
└── scripts/
    └── gitops-deploy.sh           # Deployment management script
```

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Navigate to the project
cd E:\Projects

# Set up GitHub OIDC authentication for dev environment
./scripts/gitops-deploy.sh setup-oidc --env dev --account 319040880702

# Deploy infrastructure
./scripts/gitops-deploy.sh deploy-infra --env dev
```

### 2. Deploy Dashboard

```bash
# Trigger automated deployment
./scripts/gitops-deploy.sh trigger-deploy --env dev

# Check deployment status
./scripts/gitops-deploy.sh check-status --env dev
```

### 3. Access Dashboard

Once deployed, the dashboard will be available at:
- **Dev**: https://dev.visualforge.com/
- **Staging**: https://staging.visualforge.com/
- **Production**: https://visualforge.com/

## 🏃‍♂️ Environment Configuration

### AWS Accounts
- **Dev**: 319040880702 (vf-dev)
- **Staging**: 275057778147 (vf-staging) 
- **Production**: 229742714212 (vf-production)

### GitHub Environments
Configure these in your GitHub repository settings:

1. Go to `Settings` → `Environments`
2. Create environments: `dev`, `staging`, `production`
3. Add environment-specific secrets if needed

## 🔐 Security Setup

### OIDC Authentication
No long-lived AWS credentials required. Uses GitHub OIDC provider:

```bash
# For each environment
./scripts/gitops-deploy.sh setup-oidc --env dev --account 319040880702
./scripts/gitops-deploy.sh setup-oidc --env staging --account 275057778147
./scripts/gitops-deploy.sh setup-oidc --env production --account 229742714212
```

### IAM Permissions
The GitHub Actions role has minimal permissions:
- ECR: Push/pull container images
- EKS: Deploy to clusters
- CloudFormation: Manage infrastructure
- Route53: Update DNS records
- CloudWatch: Monitoring access

## 📊 Dashboard Features

### Real-time Monitoring
- **EC2 Instances**: Live status across all VF environments
- **CloudWatch Metrics**: CPU, memory, network utilization
- **Cost Breakdown**: Environment-specific cost analysis
- **WebSocket Updates**: 30-second real-time refresh

### Multi-Environment Support
- **Dev Environment**: Development and testing
- **Staging Environment**: Pre-production validation
- **Production Environment**: Live production monitoring

## 🔄 GitOps Workflow

### Automatic Deployments
Triggered on:
- Push to `master` branch with dashboard changes
- Manual workflow dispatch
- Environment-specific deployments

### Deployment Process
1. **Build**: Docker image creation
2. **Push**: Upload to ECR
3. **Deploy**: Update Kubernetes deployment
4. **Verify**: Health checks and validation
5. **DNS**: Update Route53 records

### Branch Strategy
- `master` → Production deployment
- `staging` → Staging deployment  
- `dev` → Development deployment

## 🛠️ Local Development

### Prerequisites
```bash
# Install dependencies
pip install -r dashboard/requirements.txt

# Configure AWS credentials
aws configure --profile vf-dev
```

### Run Locally
```bash
cd dashboard
python vf-live-dashboard.py
```

Access at: http://localhost:5003

## 📋 Operations

### Monitoring
- CloudWatch Dashboard: `VF-Dashboard-{environment}`
- Logs: `/aws/eks/vf-dashboard`
- Alerts: Email notifications for issues

### Scaling
```bash
# Scale deployment
kubectl scale deployment vf-live-dashboard --replicas=3 -n vf-dev
```

### Troubleshooting
```bash
# Check pods
kubectl get pods -n vf-dev -l app=vf-live-dashboard

# View logs
kubectl logs -f deployment/vf-live-dashboard -n vf-dev

# Check service
kubectl get svc vf-live-dashboard-service -n vf-dev
```

## 🔧 Configuration

### Environment Variables
Set in `dashboard/k8s-deployment.yaml`:
- `VF_DEV_ACCOUNT`: Dev account ID
- `VF_STAGING_ACCOUNT`: Staging account ID
- `VF_PROD_ACCOUNT`: Production account ID
- `AWS_DEFAULT_REGION`: AWS region

### Resource Limits
- **CPU**: 250m request, 500m limit
- **Memory**: 256Mi request, 512Mi limit
- **Replicas**: 2 (default), auto-scaling available

## 📈 Cost Optimization

### Infrastructure Costs
- **EKS Cluster**: ~$73/month (cluster) + nodes
- **ALB**: ~$16/month + data transfer
- **ECR**: ~$0.10/GB/month
- **Route53**: ~$0.50/hosted zone

### Optimization Features
- Spot instances for non-production
- Image lifecycle policies
- Resource limits and requests
- Auto-scaling based on demand

## 🎯 Next Steps

1. **SSL Certificates**: Ensure valid certificates for production
2. **Monitoring**: Set up comprehensive alerting
3. **Backup**: Configure automated backups
4. **Performance**: Implement caching for better performance
5. **Security**: Regular security scanning and updates

## 🆘 Support

### Common Issues
1. **OIDC Setup**: Ensure GitHub repository has correct permissions
2. **EKS Access**: Update kubeconfig with correct cluster
3. **DNS Issues**: Verify Route53 hosted zone configuration
4. **Image Pulls**: Check ECR repository permissions

### Getting Help
- Check GitHub Actions logs for deployment issues
- Use `./scripts/gitops-deploy.sh check-status` for diagnostics
- Review CloudFormation events for infrastructure issues

---

**Repository**: https://github.com/NiroAgentV2/autonomous-business-system  
**Dashboard URL**: https://dev.visualforge.com/  
**Documentation**: This README and inline comments
