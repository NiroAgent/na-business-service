# Steve Surles AWS Account - What's Actually Running

## Your VF Development Environment Services

### 1. Lambda Functions (17 functions)
**VisualForge Functions:**
- dev-visualforge-core
- dev-vf-dashboard-lambda
- dev-visualforge-budgets-api
- dev-vf-auth-lambda
- dev-vf-image-lambda

**NiroSubs Functions:**
- dev-ns-core-lambda
- dev-ns-user-lambda
- dev-ns-dashboard-api
- dev-ns-dashboard-lambda
- dev-ns-payments-lambda
- dev-ns-user-api

**Other:**
- create_checkout_session (Python)
- dev-create-test-users

### 2. API Gateways (2 APIs)
- **dev-visualforge-api** (created Aug 11)
- **dev-NiroSubs-V2-api** (created Aug 18)

### 3. Databases
**RDS Aurora PostgreSQL:**
- dev-visualforge-database (Serverless) - $50/month

**DynamoDB Tables (10+ tables):**
- DocumentManagementSystem
- UsersTable
- dev-vf-media
- dev-vf-users
- dev-visualforge-budget-config
- dev-visualforge-tenant-costs
- vf-ai-generations-dev
- vf-media-items-dev
- vf-projects-dev
- vf-subscriptions-dev

### 4. ECS Clusters (4 clusters - but no running tasks!)
- vf-media-development-cluster
- fargate-cluster
- dev-vf-bulk-cluster
- vf-media-cluster

**⚠️ NOTE: All ECS clusters have 0 running tasks/services**

## Cost Breakdown by Service Type

| Service | Count | Est. Monthly Cost |
|---------|-------|------------------|
| Lambda Functions | 17 | ~$5 (pay per use) |
| API Gateway | 2 | ~$3.50 |
| Aurora Database | 1 | $50 |
| DynamoDB Tables | 10+ | ~$25 |
| ECS Clusters | 4 | $0 (no tasks) |
| EC2 (AI Agents) | 1 | $60 |
| CloudWatch/Logs | - | ~$5 |
| **TOTAL** | | **~$148.50** |

## What Your AI Agents Should Be Testing

The agents are configured to test these services but they need to be pointed at the right endpoints:

1. **VisualForge API**: dev-visualforge-api
   - Lambda: dev-visualforge-core
   - Dashboard: dev-vf-dashboard-lambda
   - Auth: dev-vf-auth-lambda
   - Image: dev-vf-image-lambda

2. **NiroSubs V2 API**: dev-NiroSubs-V2-api
   - Core: dev-ns-core-lambda
   - Users: dev-ns-user-lambda
   - Dashboard: dev-ns-dashboard-api
   - Payments: dev-ns-payments-lambda

## Issues Found

1. **ECS Clusters are empty** - No containers running
2. **AI Agents might not have correct endpoints** - Need to configure them to test the Lambda/API Gateway endpoints
3. **Two separate projects** (VF and NS) both in dev

## Recommendations

1. **Configure AI Agents** to test the actual Lambda functions via API Gateway
2. **Consider consolidating** VF and NS if they're related
3. **Remove empty ECS clusters** if not needed
4. **Set up proper test suites** for the Lambda functions

Your environment has the services deployed (Lambda + API Gateway + Databases) but the AI agents need to be configured to actually test these endpoints instead of looking for containers that don't exist!