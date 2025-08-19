# Master SDLC Agent Instructions - Complete System Understanding

## 🎯 Purpose
This document provides all agents with complete system understanding by referencing existing documentation. No duplicates - just organized references.

## 📚 Required Reading for All Agents

### 1. System Architecture & Overview
- **Primary Reference**: [`AI_AGENT_INSTRUCTIONS.md`](./AI_AGENT_INSTRUCTIONS.md)
  - Complete system architecture
  - Service relationships
  - Technology stack
  - Infrastructure details

- **Structure Details**: [`NIROSUBS_STRUCTURE_SUMMARY.md`](./NIROSUBS_STRUCTURE_SUMMARY.md)
  - Repository organization
  - Service breakdown
  - Module dependencies

### 2. Infrastructure & Deployment
- **Deployment Guide**: [`DEPLOYMENT-GUIDE.md`](./DEPLOYMENT-GUIDE.md)
  - Step-by-step deployment process
  - Environment configurations
  - CloudFormation templates

- **DNS Architecture**: [`DNS_ARCHITECTURE.md`](./DNS_ARCHITECTURE.md)
  - Domain configuration
  - Route 53 setup
  - CloudFront distributions

- **AWS Secrets**: [`AWS_PARAMETER_STORE_MIGRATION_STRATEGY.md`](./AWS_PARAMETER_STORE_MIGRATION_STRATEGY.md)
  - Secrets management
  - Cost optimization
  - Caching strategy

### 3. CI/CD & Testing
- **Infrastructure Analysis**: [`CICD_INFRASTRUCTURE_DELTA_ANALYSIS.md`](./CICD_INFRASTRUCTURE_DELTA_ANALYSIS.md)
  - GitHub Actions workflows
  - Pipeline configurations
  - Testing strategies

- **Agent Testing Guide**: [`AGENT_TESTING_SUMMARY.md`](./AGENT_TESTING_SUMMARY.md)
  - Testing methodology
  - Agent orchestration
  - Monitoring approach

### 4. Cost Optimization
- **Cost Strategy**: [`cost-optimized-orchestrator.md`](./cost-optimized-orchestrator.md)
  - Resource optimization
  - Local vs cloud execution
  - Budget management

## 🔄 SDLC Process for Agents

### Phase 1: DEVELOP
1. Read [`AI_AGENT_INSTRUCTIONS.md`](./AI_AGENT_INSTRUCTIONS.md) section on service architecture
2. Check service-specific instructions in `{service}/AGENT_INSTRUCTIONS_{ENV}.md`
3. Review code quality standards
4. Tasks:
   - Lint code
   - Fix TODOs/FIXMEs
   - Update dependencies
   - Refactor problematic areas

### Phase 2: TEST
1. Refer to [`CICD_INFRASTRUCTURE_DELTA_ANALYSIS.md`](./CICD_INFRASTRUCTURE_DELTA_ANALYSIS.md) for test configuration
2. Execute tests as defined in service `package.json`
3. Success criteria:
   - All tests pass
   - Coverage > 80%
   - No security vulnerabilities
   - Performance benchmarks met

### Phase 3: DEPLOY
1. Follow [`DEPLOYMENT-GUIDE.md`](./DEPLOYMENT-GUIDE.md)
2. Check [`DNS_ARCHITECTURE.md`](./DNS_ARCHITECTURE.md) for domain configuration
3. Validate:
   - CloudFormation templates
   - Environment variables
   - IAM permissions
   - Deployment packages

### Phase 4: DOCUMENT
1. Update service README
2. Reference master docs (don't duplicate)
3. Document:
   - API endpoints
   - Environment variables
   - Troubleshooting steps
   - Version changes

## 🏗️ System Architecture Summary

### NiroSubs-V2 Services
Per [`AI_AGENT_INSTRUCTIONS.md`](./AI_AGENT_INSTRUCTIONS.md):
- **ns-auth**: Authentication service (Cognito + Lambda)
- **ns-dashboard**: Main UI (React + S3 + CloudFront)
- **ns-payments**: Stripe integration (Lambda + DynamoDB)
- **ns-user**: User management (Lambda + DynamoDB)
- **ns-shell**: Shell UI components

### VisualForgeMediaV2 Services
Per [`NIROSUBS_STRUCTURE_SUMMARY.md`](./NIROSUBS_STRUCTURE_SUMMARY.md):
- **vf-audio-service**: Audio processing (Lambda + FFmpeg layer)
- **vf-video-service**: Video processing (Lambda + MediaConvert)
- **vf-image-service**: Image processing (Lambda + Sharp)
- **vf-text-service**: Text analysis (Lambda + Comprehend)
- **vf-bulk-service**: Batch processing (SQS + Lambda)
- **vf-dashboard-service**: Media dashboard UI

## 🔗 Service Integration Points

### Authentication Flow
Reference: [`AI_AGENT_INSTRUCTIONS.md`](./AI_AGENT_INSTRUCTIONS.md) - Authentication section
- All services validate JWT tokens from ns-auth
- Cognito User Pool: `us-east-1_xxxxx`
- Token validation in API Gateway

### Data Flow
1. User request → API Gateway
2. API Gateway → Lambda function
3. Lambda → DynamoDB/S3
4. Response → CloudFront → User

### Media Processing Pipeline
1. Upload to S3 input bucket
2. S3 event triggers Lambda
3. Lambda processes media
4. Output saved to S3 output bucket
5. CloudFront serves processed media

## 📋 Agent Task Processing

### Reading GitHub Issues
Agents should look for issues with these labels:
- `agent-task`: General agent task
- `sdlc`: SDLC iteration task
- `develop`, `test`, `deploy`, `document`: Phase-specific

### Issue Format
```markdown
Service: [service-name]
Environment: [dev|staging|production]
Phase: [develop|test|deploy|document]

Tasks:
- Specific task 1
- Specific task 2

References:
- See AI_AGENT_INSTRUCTIONS.md for architecture
- See DEPLOYMENT-GUIDE.md for deployment steps
```

## 🚨 Important Constraints

### Never Duplicate These Files
These master documents should only exist in E:/Projects/:
- AI_AGENT_INSTRUCTIONS.md
- DEPLOYMENT-GUIDE.md
- DNS_ARCHITECTURE.md
- NIROSUBS_STRUCTURE_SUMMARY.md

### Always Reference, Don't Copy
When creating service-specific docs, reference master docs:
```markdown
For system architecture, see [E:/Projects/AI_AGENT_INSTRUCTIONS.md]
For deployment process, see [E:/Projects/DEPLOYMENT-GUIDE.md]
```

## 🤖 Agent Execution Flow

1. **Check Issues**: Read GitHub issues for tasks
2. **Load Context**: Read referenced documentation
3. **Execute Phase**: Follow SDLC phase instructions
4. **Report Results**: Comment on GitHub issue
5. **Handle Timeouts**: Schedule retry if Claude unavailable
6. **Iterate**: Move to next phase or service

## 📊 Success Metrics

### Production Ready Criteria
Service is production-ready when:
- ✅ All SDLC phases pass
- ✅ Test coverage > 80%
- ✅ No critical security issues
- ✅ Documentation complete
- ✅ Deployment validated
- ✅ Performance benchmarks met

## 🔄 Continuous Improvement

Agents should:
1. Read new issues every 30 minutes
2. Process SDLC phases sequentially
3. Iterate until production-ready
4. Handle timeouts gracefully
5. Update issues with progress

## 📝 Notes for Agents

- **Cost Awareness**: Run locally to avoid cloud costs
- **Resource Management**: Check CPU/memory before running
- **Rate Limiting**: Wait between GitHub API calls
- **Error Handling**: Always report errors to issues
- **Documentation**: Reference, don't duplicate

---

*This is the master instruction document for all SDLC agents. It references existing documentation to avoid duplication while ensuring complete system understanding.*