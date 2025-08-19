# AI Agent Instructions for NiroSubs-V2 & VisualForgeMediaV2 Projects

## 🎯 Quick Context
You are working with two active V2 microservices platforms:
- **NiroSubs-V2**: Subscription management platform
- **VisualForgeMediaV2**: Media processing services platform

## 📁 Project Structure
```
E:\Projects\
├── NiroSubs-V2/                    # Main subscription platform
│   ├── ns-auth/                    # Authentication service
│   ├── ns-dashboard/               # Dashboard frontend
│   ├── ns-shell/                   # Main frontend shell
│   ├── ns-user/                    # User management
│   ├── ns-payments/                # Payment processing
│   ├── ns-orchestration/           # Infrastructure & deployment
│   │   ├── cloudformation/         # AWS CloudFormation templates
│   │   └── lambda/                 # Lambda functions
│   ├── scripts/                    # Deployment & utility scripts
│   ├── tests/                      # Test suites
│   │   └── e2e/                    # Playwright E2E tests
│   └── docs/                       # Project documentation
├── VisualForgeMediaV2/             # Media processing platform
│   ├── vf-auth-service/            # Authentication microservice
│   ├── vf-dashboard-service/       # Dashboard microservice
│   ├── vf-video-service/           # Video processing service
│   ├── vf-audio-service/           # Audio processing service
│   ├── vf-image-service/           # Image processing service
│   ├── vf-text-service/            # Text processing service
│   ├── vf-agent-service/           # AI agent service
│   ├── vf-bulk-service/            # Bulk processing service
│   ├── vf-bulk-generator-service/  # Bulk generation service
│   ├── vf-media-types/             # Shared TypeScript types
│   ├── vf-shared-components/       # Shared React components
│   ├── vf-utils/                   # Shared utilities
│   ├── aws/                        # AWS CloudFormation templates
│   ├── scripts/                    # Deployment scripts
│   ├── starter-kit/                # Template for new services
│   ├── niro-platform-hub/          # Platform management hub
│   └── integration-tests/          # Cross-service tests

# Note: V1 Projects archived at E:\ProjectsArchive\ - DO NOT MODIFY
```

## 🚀 Essential Commands

### Quick Project Status
```bash
# Check current git status for both projects
cd /e/Projects/NiroSubs-V2 && git status --porcelain
cd /e/Projects/VisualForgeMediaV2 && git status --porcelain

# Check deployment status
gh run list --repo stevesurles/NiroSubs-V2 --limit 3
gh run list --repo stevesurles/VisualForgeMediaV2 --limit 3

# Check AWS infrastructure status
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --region us-east-1
```

### Development Workflow
```bash
# NiroSubs-V2 Development
cd /e/Projects/NiroSubs-V2/ns-shell
npm run dev                         # Start frontend dev server
# Access: http://localhost:5173

# VisualForgeMediaV2 Development
cd /e/Projects/VisualForgeMediaV2
./start-all-services.sh            # Start all microservices
# Individual services start on ports 4000-4009
```

### Deployment Commands
```bash
# Deploy NiroSubs-V2 to Staging
cd /e/Projects/NiroSubs-V2
git push origin staging             # Auto-deploys via GitHub Actions

# Deploy to Production (requires confirmation)
bash scripts/deploy-production.sh  # Will prompt for confirmation

# Manual S3 frontend deployment
cd /e/Projects/NiroSubs-V2/ns-shell
npm run build
aws s3 sync dist/ s3://staging-nirosubs-frontend/ --delete
aws cloudfront create-invalidation --distribution-id EHSKT1O05B9XA --paths "/*"
```

## 🛠️ Development Guidelines

### Working with NiroSubs-V2
1. **Frontend Changes**: Work in `ns-shell/` directory
2. **API Changes**: Work in respective service directories (`ns-auth/`, `ns-user/`, etc.)
3. **Infrastructure**: CloudFormation templates in `ns-orchestration/cloudformation/`
4. **Authentication**: AWS Cognito (configured)
5. **Environment**: Use `.env.development` for local, `.env.production` for deployed

### Working with VisualForgeMediaV2
1. **Service Architecture**: Each service has `/api` and optionally `/mfe` directories
2. **Core Services**: 
   - `vf-auth-service` - Authentication & authorization
   - `vf-dashboard-service` - Main dashboard interface  
   - `vf-video-service` - Video processing & generation
   - `vf-audio-service` - Audio processing & generation
   - `vf-image-service` - Image processing & generation
   - `vf-text-service` - Text processing & generation
   - `vf-agent-service` - AI agent functionality
   - `vf-bulk-service` - Bulk processing operations
3. **Shared Libraries**: `vf-media-types/`, `vf-utils/`, `vf-shared-components/`
4. **Infrastructure**: AWS ECS with CloudFormation templates in `aws/`
5. **Local Testing**: Use Docker Compose or individual service startup
6. **Service Ports**: Typically start at 4000 and increment (4000, 4001, 4002, etc.)

### Environment Variables
```bash
# NiroSubs-V2 Staging Environment
VITE_API_URL=https://gkjhn4m606.execute-api.us-east-1.amazonaws.com/staging
VITE_COGNITO_USER_POOL_ID=us-east-1_rdE2qCAIe
VITE_COGNITO_CLIENT_ID=[Will be set after Cognito client creation]

# NiroSubs-V2 Production Environment  
VITE_API_URL=https://[PRODUCTION_API_ID].execute-api.us-east-1.amazonaws.com/production
VITE_COGNITO_USER_POOL_ID=[Production pool ID]
VITE_COGNITO_CLIENT_ID=[Production client ID]

# VisualForgeMediaV2 Key Variables
AWS_REGION=us-east-1
NODE_ENV=development
SERVICE_PORT=4000  # Varies by service
```

## 🔍 Troubleshooting Quick Reference

### Common Issues & Solutions
```bash
# Port conflicts
lsof -ti:5173 | xargs kill -9      # Kill Vite dev server
lsof -ti:4000 | xargs kill -9      # Kill API service

# Node modules issues
rm -rf node_modules package-lock.json && npm install

# AWS CLI issues
aws configure list                  # Check AWS configuration
aws sts get-caller-identity        # Verify AWS access

# Git issues
git remote -v                      # Verify remote URLs
git branch -a                      # List all branches

# Windows-specific issues
python scripts/fix-cloudfront-windows.py  # Fix CloudFront on Windows
```

### Log Locations
```bash
# CloudWatch logs (AWS)
aws logs tail /aws/lambda/staging-ns-core-lambda --follow
aws logs tail /aws/lambda/staging-ns-auth-lambda --follow

# Local development logs
tail -f /e/Projects/NiroSubs-V2/ns-shell/logs/dev.log
tail -f /e/Projects/VisualForgeMediaV2/logs/service.log
```

## 📊 Current Deployment Status

### NiroSubs-V2 Infrastructure Status
| Component | Development | Staging | Production |
|-----------|------------|---------|------------|
| Cognito User Pool | ✅ Deployed | ✅ us-east-1_rdE2qCAIe | 🔧 Ready to deploy |
| API Gateway | ✅ Minimal | ✅ gkjhn4m606 | 🔧 Ready to deploy |
| Lambda Functions | ✅ 5 functions | ✅ All deployed | 🔧 Script ready |
| CloudFront CDN | ✅ ES9YJR8EBUOCL | ✅ EHSKT1O05B9XA | 🔧 Template ready |
| S3 Buckets | ✅ 6 buckets | ✅ All created | 🔧 Template ready |
| DynamoDB Tables | ❌ Not used | ✅ users, payments | 🔧 Template ready |
| Route53 DNS | ✅ Configured | ✅ staging.visualforge.ai | 🔧 visualforge.ai |
| Secrets Manager | ✅ Basic | ✅ Structured | 🔧 Template ready |
| CloudWatch | ✅ Basic | ✅ Alarms configured | 🔧 Template ready |
| GitHub Actions | ✅ CI/CD | ✅ Auto-deploy | 🔧 Manual trigger |

### VisualForgeMediaV2 Status
| Component | Status |
|-----------|--------|
| Database | ⏳ Setup in progress |
| Authentication | ⏳ Pending |
| API Gateway | ⏳ Pending |
| Lambda Functions | ⏳ Deployment needed |
| Frontend | ⏳ Setup needed |
| CI/CD | ✅ GitHub Actions |

## 🚨 Critical Rules for AI Agents

### ⚠️ DO NOT TOUCH
- **Archive directories**: Never modify anything in `E:\ProjectsArchive\` (V1 projects)
- **Production secrets**: Never hardcode credentials
- **Main branch**: Always work on `dev` or `staging` branch unless specified
- **Production deployment**: Always require explicit confirmation

### ✅ ALWAYS DO
- Check current branch before making changes: `git branch`
- Use absolute paths when referencing files: `/e/Projects/...`
- Verify AWS credentials are configured: `aws sts get-caller-identity`
- Test locally before pushing to dev/staging branch
- Include descriptive commit messages
- Update CloudFormation templates for infrastructure changes
- Run E2E tests before production deployment

### 🔄 Workflow Pattern
1. **Understand the request** - Read existing documentation first
2. **Check current state** - Use git status, check logs, verify deployments
3. **Make changes** - Follow established patterns in the codebase
4. **Test locally** - Ensure changes work in development environment
5. **Deploy to staging** - Push to staging branch for testing
6. **Run E2E tests** - Validate with Playwright tests
7. **Deploy to production** - Only after staging validation and approval

## 📚 Documentation References

### Key Documentation Files
- `README.md` - Project overview and quick start
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `STAGING_DEPLOYMENT_SUMMARY.md` - Current staging environment details
- `DEPLOYMENT_REPORT.md` - Complete deployment status report
- `STRIPE_WEBHOOK_SETUP.md` - Stripe integration guide
- `docs/DEVELOPER-GUIDE.md` - Development setup and patterns
- `docs/AWS-DEPLOYMENT-COMPLETE.md` - AWS infrastructure details

### External Resources
- [AWS Console](https://console.aws.amazon.com/) - Account: vf-dev (816454053517)
- [GitHub Actions - NiroSubs](https://github.com/stevesurles/NiroSubs-V2/actions)
- [CloudWatch Logs](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)
- [Staging Environment](https://d1mt74nsjx1seq.cloudfront.net)
- [Staging DNS](https://staging.visualforge.ai)

## 🔗 VisualForgeMedia Integration with NiroSubs

### Integration Architecture
NiroSubs-V2 integrates with VisualForgeMediaV2 using **Module Federation** and **iframe-based micro frontends**:

#### Module Federation Setup
```bash
# NiroSubs Shell (Host Application)
# File: /e/Projects/NiroSubs-V2/ns-shell/vite.config.ts
- Uses @originjs/vite-plugin-federation
- Acts as the main shell application
- Hosts media services as federated modules

# Dashboard MFE (Exposed Module)  
# File: /e/Projects/NiroSubs-V2/ns-dashboard/frontend/vite.config.ts
- Exposes Dashboard and CostDashboard components
- Runs on port 5174
- Shares React and @visualforge/types
```

#### Media Services Integration Component
```bash
# Main Integration: /e/Projects/NiroSubs-V2/ns-shell/src/components/MediaServicesIntegration.tsx
# Features:
- Grid of media service cards (Video, Image, Audio, Text)
- Dynamic service URL resolution (dev/staging/production)
- Iframe-based service loading with authentication
- PostMessage communication for auth token transfer
- Real-time usage tracking and navigation handling
```

#### Authentication Flow
```bash
# Cross-service authentication via postMessage:
1. User logs into NiroSubs (Cognito)
2. MediaServicesIntegration loads VisualForge service in iframe
3. Authentication token passed via postMessage
4. User context (ID, email, tier) shared with media services
5. Real-time auth refresh handling
```

#### Service Communication
```bash
# PostMessage API between NiroSubs and VisualForge:
- AUTH_TOKEN: Initial authentication
- REQUEST_AUTH_REFRESH: Token refresh requests  
- NAVIGATION: Service navigation requests
- USAGE_UPDATE: Real-time usage statistics
- MEDIA_PROCESSED: Completed media operations
```

#### Environment Configuration
```bash
# Media Services URL Resolution:
- Development: http://localhost:5173 (local)
- Staging: https://d1mt74nsjx1seq.cloudfront.net
- Production: https://visualforge.ai

# Dynamic URL fetching via SSM Parameter Store in production
# Fallback to environment variables for local development
```

#### Available Media Services
```bash
# Integrated Services:
1. Video Editor (/video) - Professional video editing and generation
2. Image Studio (/image) - AI-powered image generation and editing  
3. Audio Mixer (/audio) - Advanced audio editing and synthesis
4. Text Generator (/text) - AI text generation and processing

# Access via: NiroSubs Shell → Media Services tab
```

#### Integration Testing
```bash
# Test the integration:
cd /e/Projects/NiroSubs-V2/ns-shell
npm run dev                    # Start NiroSubs shell (port 5173)

# In browser: http://localhost:5173
# Login → Click "Media Services" tab
# Should load VisualForge services in iframe with auth context

# Cross-service integration tests:
cd /e/Projects/NiroSubs-V2
npx playwright test tests/e2e/staging.spec.ts
```

#### Troubleshooting Integration
```bash
# Common issues:
1. CORS errors: Check media services URL configuration
2. Auth failures: Verify token passing via postMessage
3. Iframe loading: Check sandbox permissions and CSP headers
4. Service discovery: Verify SSM parameter or environment variables

# Debug postMessage communication:
# Browser DevTools → Console → Filter for "postMessage" logs
```

## 🧪 Testing Standards & Guidelines

### Test Environments & Strategy

#### 5 Configurable Testing Modes

**Mode 1: Local Mock (`localmock`)**
```bash
# Fastest testing - fully mocked dependencies
npm run test:mock
npm run test:unit

# Use case: CI/CD pipelines, rapid development feedback
# Database: Fully mocked with MockPool class
# Services: Mocked responses, no external calls
# Speed: Fastest (~30 seconds)
# Environment variables: .env.test.mock
```

**Mode 2: Local Services (`localservice`)**
```bash
# Docker orchestration - real services locally
cd /e/Projects/VisualForgeMediaV2
docker-compose up -d
npm run test:live
npm run test:integration

# Use case: Full local integration testing
# Database: Local PostgreSQL (Docker)
# Services: All VF services running in Docker
# Speed: Medium (~2-5 minutes)
# Environment variables: .env.test.local
```

**Mode 3: AWS Development (`vf-dev`)**
```bash
# Real AWS development environment
npm run test:aws:dev
npx playwright test --config=playwright.config.integration.ts

# Use case: Pre-deployment validation, feature testing
# Account ID: 816454053517
# Database: AWS RDS Development instance
# Services: https://gkjhn4m606.execute-api.us-east-1.amazonaws.com/dev
# Speed: Medium-Slow (~5-10 minutes)
# Environment variables: .env.test.aws.dev
```

**Mode 4: AWS Staging (`vf-stg`)**
```bash
# Production-like AWS staging environment  
npm run test:aws:staging
npx playwright test --project=chromium,firefox,webkit

# Use case: Pre-production validation, release testing
# Account ID: 816454053517
# Database: AWS RDS Staging instance
# Services: https://gkjhn4m606.execute-api.us-east-1.amazonaws.com/staging
# Speed: Slow (~10-15 minutes)
# Environment variables: .env.test.aws.staging
```

**Mode 5: AWS Production (`vf-prd`)**
```bash
# Production environment - READ ONLY tests
npm run test:aws:prod --read-only
npm run test:health-checks

# Use case: Production monitoring, health validation
# Account ID: 816454053517
# Database: AWS RDS Production (READ ONLY)
# Services: https://[PROD_API].execute-api.us-east-1.amazonaws.com/production
# Speed: Fast (~1-2 minutes, limited tests)
# Environment variables: .env.test.aws.prod
```

### Testing Framework Structure

#### Modern Testing Strategy (Microservices-Focused)
```bash
# Integration Tests with Live Services (40%) - Most important
npm run test:live             # Real services in Docker
npm run test:aws:dev          # Against AWS environments
npm run test:integration      # API endpoints, DB operations

# UI/E2E Tests (40%) - Critical user journeys
npm run test:e2e              # Full workflows
npm run test:ui               # Component interactions
npx playwright test --ui      # Interactive UI testing

# Unit Tests (20%) - Fast feedback for business logic
npm run test:unit             # Individual functions/components
npm run test:mock             # Mocked dependencies (CI/CD only)
```

### Playwright UI Testing

#### Playwright Test Configurations
Both projects use Playwright for comprehensive UI testing:

**NiroSubs-V2 Playwright Setup**
```bash
# Main E2E testing against deployed environments
cd /e/Projects/NiroSubs-V2
npx playwright test                    # Run all E2E tests
npx playwright test --ui              # Interactive UI mode
npx playwright test --headed          # Show browser during tests
npx playwright test --debug           # Debug mode with DevTools

# Specific test files
npx playwright test tests/e2e/staging.spec.ts
```

**VisualForgeMediaV2 Playwright Setup**
```bash
# Integration testing across all services
cd /e/Projects/VisualForgeMediaV2
npx playwright test --config=playwright.config.integration.ts

# Individual service UI testing
cd /e/Projects/VisualForgeMediaV2/vf-video-service/mfe
npx playwright test --config=playwright.config.ui.ts --ui
```

#### Cross-Browser Testing
```bash
# Test across all browsers
npx playwright test --project=chromium,firefox,webkit

# Mobile testing
npx playwright test --project="Mobile Chrome","Mobile Safari"

# Specific browser only
npx playwright test --project=chromium
```

### Testing Before Deployment

#### Required Test Sequence (Priority Order)
```bash
# 1. Integration tests with real services - CRITICAL
npm run test:live             # Docker services
npm run test:aws:dev          # AWS development environment

# 2. UI/E2E testing - CRITICAL for user-facing changes
npm run test:e2e              # Complete workflows
npx playwright test           # Cross-browser validation

# 3. Unit tests - Supporting validation
npm run test:unit             # Business logic verification

# 4. Integration tests with mocks - CI/CD validation only
npm run test:mock             # Fast feedback for pipelines
```

#### Pre-Push Testing Checklist (Revised Priority)
- ✅ **Integration tests with live services passing** (CRITICAL)
- ✅ **UI/E2E tests passing** (CRITICAL for UI changes)
- ✅ **No console errors in live environment**
- ✅ **Cross-browser compatibility verified** (if UI changes)
- ✅ **Performance thresholds met** (integration + UI)
- ✅ Unit tests passing (supporting validation)
- ✅ No linting errors (`npm run lint`)
- ✅ TypeScript compilation successful (`npm run build`)
- ✅ Accessibility checks passed (if UI changes)

### Debugging Failed Tests

#### Test Debugging Commands
```bash
# Enable debug mode
DEBUG_TESTS=true npm test

# Run single failing test
npm test -- --testNamePattern="specific test name"

# Show browser interactions (E2E)
HEADLESS=false SLOW_MO=500 npm run test:e2e

# Check test reports
open test-reports/html/report.html    # HTML report
ls test-reports/screenshots/          # Failure screenshots
```

#### Common Test Issues & Solutions
```bash
# Port conflicts
lsof -ti:5173 | xargs kill -9      # Kill frontend dev server
lsof -ti:4000 | xargs kill -9      # Kill API service

# AWS connection issues
aws sts get-caller-identity        # Verify AWS credentials
aws logs describe-log-groups       # Check CloudWatch access

# Service health checks
curl https://gkjhn4m606.execute-api.us-east-1.amazonaws.com/staging/core/api/health
curl https://d1mt74nsjx1seq.cloudfront.net
```

## 🎯 Quick Task Templates

### Add New Feature
```bash
cd /e/Projects/NiroSubs-V2
git checkout staging
git pull origin staging
# Make changes
npm test                           # Run tests
git add .
git commit -m "feat: description of new feature"
git push origin staging
# Monitor GitHub Actions for deployment
```

### Fix Bug
```bash
cd /e/Projects/[PROJECT]
git checkout staging
# Identify issue via logs/debugging
# Make fix
# Test fix locally
npm run test:e2e                  # Validate fix
git add .
git commit -m "fix: description of bug fix"
git push origin staging
```

### Deploy to Production
```bash
# REQUIRES EXPLICIT APPROVAL
cd /e/Projects/NiroSubs-V2

# 1. Ensure staging is stable
npx playwright test tests/e2e/staging.spec.ts

# 2. Run production deployment script
bash scripts/deploy-production.sh
# Type 'deploy-production' when prompted

# 3. Verify production deployment
curl https://visualforge.ai
curl https://[PROD_API].execute-api.us-east-1.amazonaws.com/production/core/api/health
```

### Update Infrastructure
```bash
# Always update CloudFormation templates
cd /e/Projects/NiroSubs-V2/ns-orchestration/cloudformation/templates

# Edit template
vim staging-complete.yaml

# Deploy changes
aws cloudformation update-stack \
  --stack-name staging-visualforge-core \
  --template-body file://staging-complete.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Wait for update to complete
aws cloudformation wait stack-update-complete \
  --stack-name staging-visualforge-core \
  --region us-east-1
```

## 🔐 Security & Compliance

### Security Best Practices
- All secrets in AWS Secrets Manager
- IAM roles follow least privilege principle
- S3 buckets have public access blocked
- CloudFront uses Origin Access Identity
- DynamoDB tables have encryption enabled
- Cognito with MFA capability
- API Gateway with throttling enabled

### Compliance Requirements
- GDPR compliance for user data
- SOC2 security controls
- PII handling validation
- Audit trail verification
- Data encryption at rest and in transit

## 📈 Monitoring & Observability

### CloudWatch Dashboards
- Lambda function metrics
- API Gateway request/error rates
- DynamoDB read/write capacity
- CloudFront cache hit ratio
- Application custom metrics

### Alerts Configuration
- High error rates (>10 errors in 5 minutes)
- API response time (>5 seconds)
- Lambda throttling
- DynamoDB throttling
- Budget alerts for cost management

### Health Checks
```bash
# Staging health checks
curl https://gkjhn4m606.execute-api.us-east-1.amazonaws.com/staging/core/api/health
curl https://gkjhn4m606.execute-api.us-east-1.amazonaws.com/staging/auth/api/health
curl https://gkjhn4m606.execute-api.us-east-1.amazonaws.com/staging/payments/api/health

# CloudFront health
curl -I https://d1mt74nsjx1seq.cloudfront.net
curl -I https://staging.visualforge.ai
```

---

**Last Updated**: 2025-08-18  
**Maintained by**: Development Team  
**Version**: 2.1 (Post-Staging Deployment Update)

## Recent Updates
- ✅ Staging environment fully deployed and operational
- ✅ All infrastructure now in CloudFormation templates
- ✅ E2E testing suite implemented with Playwright
- ✅ Production deployment scripts ready
- ✅ DNS configured for staging.visualforge.ai
- ✅ Monitoring and alerting configured
- ✅ Google OAuth and Stripe integration documented