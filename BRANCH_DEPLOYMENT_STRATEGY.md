# Branch-Based Deployment Strategy

## Overview
The VF Live Dashboard uses a GitOps approach with automatic branch-based deployments to different AWS environments.

## Deployment Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  development    │    │   release/*     │    │      main       │
│     branch      │    │   branches      │    │     branch      │
│                 │    │                 │    │                 │
│     ↓           │    │      ↓          │    │       ↓         │
│  VF-dev env     │    │  Staging env    │    │ Production env  │
│ (319040880702)  │    │ (275057778147)  │    │ (229742714212)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Branch Mapping

### Development Environment (`VF-dev`)
- **Branches:** `development`, `dev`
- **AWS Account:** `319040880702`
- **Domain:** `dev.visualforge.com`
- **Purpose:** Development and testing environment
- **Auto-deploy:** ✅ Automatic on push

### Staging Environment
- **Branches:** `release/*`, `release/**`
- **AWS Account:** `275057778147`
- **Domain:** `staging.visualforge.com`
- **Purpose:** Pre-production testing and QA
- **Auto-deploy:** ✅ Automatic on push to release branches

### Production Environment
- **Branches:** `main`
- **AWS Account:** `229742714212`
- **Domain:** `visualforge.com`
- **Purpose:** Production workloads
- **Auto-deploy:** ✅ Automatic on push to main

## Workflow Examples

### Feature Development
```bash
# Create feature branch from development
git checkout development
git checkout -b feature/dashboard-enhancement

# Make changes and commit
git add .
git commit -m "Add new dashboard features"

# Merge back to development (triggers dev deployment)
git checkout development
git merge feature/dashboard-enhancement
git push origin development
# → Deploys to VF-dev environment
```

### Release Process
```bash
# Create release branch from development
git checkout development
git checkout -b release/2024.08.19

# Final testing and bug fixes
git add .
git commit -m "Prepare release 2024.08.19"
git push origin release/2024.08.19
# → Deploys to Staging environment

# After QA approval, merge to main
git checkout main
git merge release/2024.08.19
git push origin main
# → Deploys to Production environment
```

### Hotfix Process
```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-fix

# Apply critical fix
git add .
git commit -m "Fix critical production issue"

# Merge to main (triggers production deployment)
git checkout main
git merge hotfix/critical-fix
git push origin main
# → Deploys to Production environment

# Also merge back to development
git checkout development
git merge hotfix/critical-fix
git push origin development
# → Updates development environment
```

## Manual Deployment

You can also trigger manual deployments using the GitHub Actions workflow dispatch:

1. Go to **Actions** tab in GitHub repository
2. Select **Deploy VF Live Dashboard** workflow
3. Click **Run workflow**
4. Choose target environment (dev, staging, production)
5. Click **Run workflow**

## Environment Protection

Each environment has specific protections:

### Development (`dev`)
- ✅ Open deployment from development/dev branches
- ✅ No approval required
- ✅ Immediate deployment

### Staging
- ✅ Automatic deployment from release/* branches
- ⚠️ Optional: Require approval for sensitive changes
- ✅ Automated testing before deployment

### Production
- ✅ Automatic deployment from main branch only
- 🔒 **Recommended:** Require manual approval
- 🔒 **Recommended:** Restrict to specific reviewers
- ✅ Full automated testing and health checks

## Security Features

### OIDC Authentication
- ✅ No long-lived AWS credentials in GitHub
- ✅ Temporary credentials for each deployment
- ✅ Role-based access per environment

### Environment Isolation
- 🏗️ Separate AWS accounts per environment
- 🔒 Environment-specific IAM roles
- 🌐 Isolated DNS domains and resources

## Monitoring and Alerts

### Deployment Status
- ✅ Real-time deployment progress in GitHub Actions
- ✅ Slack/Teams notifications on success/failure
- ✅ Automated rollback on health check failures

### Health Checks
- ✅ Post-deployment health verification
- ✅ Application startup confirmation
- ✅ DNS resolution validation

## Troubleshooting

### Deployment Failures
1. Check GitHub Actions logs for specific error
2. Verify AWS credentials and permissions
3. Ensure CloudFormation templates are valid
4. Check EKS cluster health and capacity

### Branch Protection Issues
1. Ensure you have write access to target branch
2. Check if branch protection rules are blocking merge
3. Verify required status checks are passing

### Environment Access
1. Confirm AWS account access for target environment
2. Verify OIDC role configuration
3. Check IAM permissions for deployment actions

## Configuration Files

- **GitHub Actions:** `.github/workflows/deploy-dashboard.yml`
- **CloudFormation:** `infrastructure/cloudformation/*.yml`
- **Kubernetes:** `dashboard/k8s-deployment.yaml`
- **Docker:** `dashboard/Dockerfile`
- **Management:** `scripts/gitops-deploy.sh`

## Next Steps

1. **Set up OIDC:** Run `./scripts/gitops-deploy.sh setup-oidc --env dev`
2. **Deploy Infrastructure:** Run `./scripts/gitops-deploy.sh deploy-infra --env dev`
3. **Test Deployment:** Push changes to `development` branch
4. **Monitor:** Check dashboard at `https://dev.visualforge.com/dashboard`

---

**Note:** This strategy ensures safe, automated deployments with proper testing stages while maintaining environment isolation and security best practices.
