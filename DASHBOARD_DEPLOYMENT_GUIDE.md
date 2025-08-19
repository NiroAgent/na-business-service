# VF Live Dashboard - Deployment Guide

## 🎯 Quick Start (Local Development)

Your live AWS-integrated dashboard is ready! Since we detected authentication issues with the VF-dev profile, here's how to proceed:

### Option 1: Run Locally (Ready Now)
```bash
cd /e/Projects
chmod +x scripts/start-local-dashboard.sh
./scripts/start-local-dashboard.sh
```

**Dashboard URL:** http://localhost:5003

### Option 2: Deploy to VF-dev (After AWS Setup)

1. **Configure VF-dev AWS credentials:**
   ```bash
   aws configure --profile vf-dev
   # Enter VF-dev account credentials (319040880702)
   ```

2. **Deploy to production:**
   ```bash
   ./scripts/deploy-vf-live-dashboard.sh
   ```

3. **Access production dashboard:**
   https://dev.visualforge.com/

## 🔧 Current Setup Status

### ✅ Completed
- **Live Dashboard Implementation**: Real AWS integration with EC2, CloudWatch, Cost Explorer
- **Local Testing**: Dashboard running successfully on localhost:5003
- **Deployment Infrastructure**: Kubernetes manifests, Docker container, deployment scripts
- **Real-time Features**: WebSocket updates, 30-second refresh, live metrics

### 🔄 AWS Authentication Status
- **Default Account**: 816454053517 (authenticated)
- **VF-staging**: AKIAUACVYTXRUP7Z2GMG (authenticated)
- **VF-dev**: ❌ Needs credentials configuration
- **VF-production**: ❌ Needs credentials configuration

## 📊 Dashboard Features

### Current Implementation
1. **Environment Cost Breakdown**: Real-time cost data from Cost Explorer API
2. **EC2 Instance Grid**: Live monitoring of all instances across environments
3. **CloudWatch Metrics**: CPU, memory, network utilization in real-time
4. **Agent Console Grid**: Real-time output streaming from agent processes
5. **Interactive Debugging**: Click console for full-screen debugging interface

### Enhanced PM Stories (Completed)
- **Epic Summary**: 42 story points across 3 enhancement stories
- **Cost Breakdown Enhancement**: 8 points - Environment-specific cost analysis
- **Console Grid Enhancement**: 13 points - Real-time console monitoring grid
- **Interactive Debugging**: 21 points - Full-screen debugging with feedback system

## 🚀 Production Deployment Process

When ready for VF-dev deployment:

1. **Pre-deployment Checks**:
   ```bash
   ./scripts/check-aws-auth.sh
   ```

2. **Full Deployment**:
   ```bash
   ./scripts/deploy-vf-live-dashboard.sh
   ```

3. **Deployment Includes**:
   - ECR image build and push
   - Kubernetes deployment (2 replicas)
   - ALB ingress configuration
   - Service account with IAM roles
   - Health checks and monitoring

## 💡 Next Actions

1. **Immediate**: Dashboard is running locally with live AWS data
2. **Short-term**: Configure VF-dev AWS credentials for production deployment
3. **Production**: Deploy to dev.visualforge.com for permanent access

The dashboard is fully functional now - just needs the AWS credentials for the target deployment environment!
