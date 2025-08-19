# Parameter Store Migration - Implementation Tasks

## 🎯 Overview
Migrate VisualForgeMediaV2 configuration management from scattered environment variables to AWS Parameter Store + Secrets Manager, following the proven NiroSubs-V2 pattern.

## 📋 GitHub Issues Strategy

**YES - Create GitHub Issues at the Repository Level**

### Why GitHub Issues Work Better:
1. **Centralized Tracking**: All tasks visible in one place
2. **Cross-Service Coordination**: Many tasks span multiple services
3. **Progress Visibility**: Team can see overall migration progress
4. **Integration**: Links with PRs, commits, and deployments
5. **Documentation**: Preserves decision history and discussions

### Recommended Issue Structure:
```
Repository: stevesurles/VisualForgeMediaV2
Labels: enhancement, config-migration, priority-high
Milestone: "Parameter Store Migration v1.0"
```

## 🔐 Secrets Management Approach (Current Best Practice)

**CONFIRMED: Single Secret with Multiple Key-Value Pairs**

### Current NiroSubs-V2 Pattern (FOLLOW THIS):
```json
// Secret Name: visualforge/dev/database/main
{
  "engine": "postgres",
  "host": "dev-aurora-cluster.cluster-xyz.us-east-1.rds.amazonaws.com",
  "username": "dbuser",
  "password": "securepassword123",
  "dbname": "visualforge_dev",
  "port": 5432
}

// Secret Name: visualforge/dev/stripe/keys  
{
  "publishableKey": "pk_test_xyz...",
  "secretKey": "sk_test_abc...",
  "webhookSecret": "whsec_def..."
}

// Secret Name: visualforge/dev/cognito/config
{
  "userPoolId": "us-east-1_H9ZWvtTNg",
  "userPoolClientId": "1nufa1so5bp1rjki3td1rr2f49",
  "identityPoolId": "us-east-1:identity-pool-id"
}
```

### Cost Analysis:
- **Single Secret Approach**: $0.40/month per secret
- **Multiple Secrets**: $0.40/month × number of keys = EXPENSIVE
- **Savings**: ~$15-20/month per environment (75% cost reduction)

## 📝 Implementation Tasks (GitHub Issues)

### Phase 1: Foundation Setup (Week 1-2)

#### Issue #1: Create Parameter Store Hierarchy Structure
**Priority**: High | **Effort**: 1 day | **Assignee**: DevOps/Config Specialist

**Description:**
Create standardized parameter hierarchy for VisualForgeMediaV2 following NiroSubs-V2 patterns.

**Acceptance Criteria:**
- [ ] Design parameter hierarchy structure
- [ ] Create shared parameters (`/visualforge/shared/*`)
- [ ] Create environment parameters (`/visualforge/environments/{dev,staging,production}/*`)
- [ ] Create service parameters (`/visualforge/services/{auth,video,image,audio,text,bulk}/*`)
- [ ] Create integration parameters (`/visualforge/integrations/*`)
- [ ] Document parameter naming conventions

**Implementation Details:**
```bash
# Shared Configuration
/visualforge/shared/region
/visualforge/shared/project-name

# Environment-Specific
/visualforge/environments/dev/account-id
/visualforge/environments/dev/domain
/visualforge/environments/dev/log-level
/visualforge/environments/dev/cors-origins

# Service Configuration  
/visualforge/services/auth/port
/visualforge/services/auth/rate-limit-max
/visualforge/services/video/port
/visualforge/services/video/max-file-size
```

---

#### Issue #2: Consolidate Secrets Manager Structure
**Priority**: High | **Effort**: 2 days | **Assignee**: Security/DevOps

**Description:**
Audit and restructure Secrets Manager to use single secrets with multiple key-value pairs for cost optimization.

**Acceptance Criteria:**
- [ ] Audit current secret usage across all services
- [ ] Design consolidated secret structure per service/function
- [ ] Create migration script for existing secrets
- [ ] Update IAM permissions for new secret structure
- [ ] Validate cost reduction (target: 75% reduction)

**Target Secret Structure:**
```json
// visualforge/dev/database/main (ALL DB configs)
{
  "host": "...", "username": "...", "password": "...", "dbname": "...", "port": 5432,
  "readOnlyHost": "...", "migrationPassword": "..."
}

// visualforge/dev/external-apis/main (ALL API keys)
{
  "openaiApiKey": "...", "stabilityApiKey": "...", "elevenLabsApiKey": "...",
  "stripeSecretKey": "...", "stripeWebhookSecret": "..."
}

// visualforge/dev/jwt/main (ALL auth secrets)
{
  "jwtSecret": "...", "apiKeySecret": "...", "refreshTokenSecret": "..."
}
```

---

#### Issue #3: Create Configuration Loading Utility Library
**Priority**: High | **Effort**: 3 days | **Assignee**: Backend Developer

**Description:**
Create shared utility library for loading configuration from Parameter Store and Secrets Manager with caching.

**Acceptance Criteria:**
- [ ] Create `@vf-media/config` package in `vf-utils`
- [ ] Implement `ConfigLoader` class with caching (5-minute TTL)
- [ ] Implement `SecretsLoader` class with caching (15-minute TTL)
- [ ] Add environment-specific config loading methods
- [ ] Add service-specific config loading methods
- [ ] Include fallback to environment variables for local development
- [ ] Add comprehensive error handling and logging
- [ ] Write unit tests with >90% coverage

**API Design:**
```typescript
const configLoader = new ConfigLoader();
const envConfig = await configLoader.getEnvironmentConfig('dev');
const serviceConfig = await configLoader.getServiceConfig('auth');
const secrets = await configLoader.getSecrets('visualforge/dev/database/main');
```

---

### Phase 2: Service Migration (Week 3-6)

#### Issue #4: Migrate vf-auth-service (Pilot Project)
**Priority**: High | **Effort**: 3 days | **Assignee**: Backend Developer

**Description:**
Migrate vf-auth-service as pilot to validate approach and create patterns for other services.

**Acceptance Criteria:**
- [ ] Update service to use `@vf-media/config` library
- [ ] Remove hardcoded environment variables from code
- [ ] Update CloudFormation template to use Parameter Store references
- [ ] Update deployment scripts to use parameter-driven configuration
- [ ] Migrate secrets to consolidated structure
- [ ] Test locally with fallback to environment variables
- [ ] Test in dev environment with Parameter Store
- [ ] Create service migration documentation template
- [ ] Validate performance impact (target: <100ms additional latency)

**Technical Changes:**
```typescript
// OLD: process.env.JWT_SECRET
// NEW: await configLoader.getSecrets('visualforge/dev/jwt/main').jwtSecret

// OLD: process.env.CORS_ORIGINS
// NEW: await configLoader.getEnvironmentConfig('dev').corsOrigins
```

---

#### Issue #5: Migrate vf-video-service
**Priority**: Medium | **Effort**: 2 days | **Assignee**: Backend Developer

**Description:**
Apply patterns from vf-auth-service migration to vf-video-service.

**Acceptance Criteria:**
- [ ] Follow vf-auth-service migration patterns
- [ ] Update video-specific configuration parameters
- [ ] Migrate video processing API keys to consolidated secrets
- [ ] Update CloudFormation template
- [ ] Test video generation workflows end-to-end
- [ ] Validate no performance regression in video processing

---

#### Issue #6: Migrate vf-image-service
**Priority**: Medium | **Effort**: 2 days | **Assignee**: Backend Developer

**Acceptance Criteria:**
- [ ] Follow established migration patterns
- [ ] Migrate image processing API keys
- [ ] Test image generation workflows
- [ ] Validate configuration loading performance

---

#### Issue #7: Migrate vf-audio-service
**Priority**: Medium | **Effort**: 2 days | **Assignee**: Backend Developer

**Acceptance Criteria:**
- [ ] Follow established migration patterns
- [ ] Migrate audio processing API keys
- [ ] Test audio generation workflows
- [ ] Validate configuration loading performance

---

#### Issue #8: Migrate vf-text-service
**Priority**: Medium | **Effort**: 2 days | **Assignee**: Backend Developer

**Acceptance Criteria:**
- [ ] Follow established migration patterns
- [ ] Migrate text processing API keys (OpenAI, etc.)
- [ ] Test text generation workflows
- [ ] Validate configuration loading performance

---

#### Issue #9: Migrate vf-bulk-service
**Priority**: Medium | **Effort**: 3 days | **Assignee**: Backend Developer

**Description:**
Migrate bulk service with additional complexity for batch processing configuration.

**Acceptance Criteria:**
- [ ] Migrate bulk processing parameters (batch sizes, limits, timeouts)
- [ ] Update job queue configuration
- [ ] Migrate database connection parameters
- [ ] Test bulk processing workflows
- [ ] Validate performance with high-volume operations

---

### Phase 3: Infrastructure Updates (Week 7)

#### Issue #10: Update CloudFormation Templates
**Priority**: High | **Effort**: 2 days | **Assignee**: DevOps Engineer

**Description:**
Update all CloudFormation templates to use Parameter Store references instead of hardcoded values.

**Acceptance Criteria:**
- [ ] Remove hardcoded mappings from all templates
- [ ] Add Parameter Store references using `{{resolve:ssm:}}` syntax
- [ ] Update parameter types and defaults
- [ ] Test template validation
- [ ] Create deployment validation scripts
- [ ] Update infrastructure documentation

**Template Updates:**
```yaml
# OLD: Hardcoded mapping
Mappings:
  EnvironmentConfig:
    dev:
      AccountId: 319040880702

# NEW: Parameter Store reference
Environment:
  - Name: ACCOUNT_ID
    Value: !Sub "{{resolve:ssm:/visualforge/environments/${Environment}/account-id:1}}"
```

---

#### Issue #11: Update Deployment Scripts and CI/CD
**Priority**: High | **Effort**: 2 days | **Assignee**: DevOps Engineer

**Description:**
Update all deployment scripts and GitHub Actions to use parameter-driven configuration.

**Acceptance Criteria:**
- [ ] Update `deploy-to-vf-dev.yml` to use Parameter Store
- [ ] Create parameter-driven deployment scripts
- [ ] Update service discovery mechanism
- [ ] Remove hardcoded environment variables from CI/CD
- [ ] Test deployments in dev environment
- [ ] Create rollback procedures
- [ ] Update deployment documentation

---

### Phase 4: Integration and Testing (Week 8)

#### Issue #12: Update NiroSubs Integration
**Priority**: Medium | **Effort**: 2 days | **Assignee**: Full-Stack Developer

**Description:**
Update NiroSubs-V2 integration to use Parameter Store for VisualForge service discovery.

**Acceptance Criteria:**
- [ ] Update MediaServicesIntegration.tsx to use Parameter Store for URLs
- [ ] Remove hardcoded service URLs from environment variables
- [ ] Test iframe integration with dynamic URL resolution
- [ ] Validate postMessage communication still works
- [ ] Test across all environments (dev, staging, production)
- [ ] Update integration documentation

**URL Resolution Change:**
```typescript
// OLD: process.env.VITE_MEDIA_URL
// NEW: await getParameter('/visualforge/integrations/nirosubs/media-url')
```

---

#### Issue #13: Comprehensive Testing
**Priority**: High | **Effort**: 3 days | **Assignee**: QA Engineer

**Description:**
Execute comprehensive testing across all services and environments.

**Acceptance Criteria:**
- [ ] Test all services in dev environment with Parameter Store
- [ ] Validate configuration loading performance (<100ms overhead)
- [ ] Test service-to-service communication
- [ ] Validate secrets loading and caching
- [ ] Test fallback to environment variables in local development
- [ ] Execute integration tests with NiroSubs
- [ ] Validate cost reduction in AWS billing
- [ ] Create performance baseline documentation

---

### Phase 5: Documentation and Cleanup (Week 9)

#### Issue #14: Update Documentation
**Priority**: Medium | **Effort**: 2 days | **Assignee**: Technical Writer/Developer

**Description:**
Update all documentation to reflect new configuration management approach.

**Acceptance Criteria:**
- [ ] Update AI_AGENT_INSTRUCTIONS.md with Parameter Store approach
- [ ] Update individual service README files
- [ ] Create Parameter Store management runbook
- [ ] Update developer setup guides
- [ ] Document troubleshooting procedures
- [ ] Create configuration rollback procedures
- [ ] Update security documentation

---

#### Issue #15: Environment Cleanup
**Priority**: Low | **Effort**: 1 day | **Assignee**: DevOps Engineer

**Description:**
Clean up old configuration files and validate new approach.

**Acceptance Criteria:**
- [ ] Remove old .env files from repositories (keep .env.example)
- [ ] Remove hardcoded configurations from CloudFormation templates
- [ ] Validate all old environment variables are migrated
- [ ] Create parameter audit script
- [ ] Document any remaining environment variables
- [ ] Create cost analysis report

---

## 🎯 Success Metrics and Validation

### Performance Metrics
- [ ] Configuration loading overhead: <100ms per service startup
- [ ] Cache hit ratio: >90% for parameter requests
- [ ] Service startup time: No increase >500ms

### Cost Metrics
- [ ] Secrets Manager cost reduction: >75%
- [ ] Parameter Store monthly cost: <$10/month
- [ ] Engineering time savings: >6 hours/month

### Security Metrics
- [ ] Zero hardcoded secrets in code
- [ ] All sensitive data in Secrets Manager
- [ ] Proper IAM permissions for parameter access

### Operational Metrics
- [ ] Configuration updates without deployment: ✅
- [ ] Environment consistency: 100%
- [ ] Deployment error reduction: >50%

## 🚨 Risk Mitigation

### High Priority Risks
1. **Service Startup Failures**: Implement robust fallback to environment variables
2. **Parameter Store Availability**: Add aggressive caching and circuit breakers
3. **IAM Permission Issues**: Create comprehensive permission documentation
4. **Cost Overrun**: Monitor usage and implement alerts

### Rollback Strategy
Each issue should include:
- [ ] Rollback procedure documented
- [ ] Fallback mechanism tested
- [ ] Previous configuration backed up

## 📊 Project Timeline

```
Week 1-2: Foundation (Issues #1-3)
Week 3-6: Service Migration (Issues #4-9) 
Week 7:   Infrastructure (Issues #10-11)
Week 8:   Integration/Testing (Issues #12-13)
Week 9:   Documentation/Cleanup (Issues #14-15)
```

## 🔗 Dependencies

### External Dependencies
- AWS Parameter Store availability
- AWS Secrets Manager availability
- IAM permissions setup

### Internal Dependencies  
- `@vf-media/config` library (Issue #3) blocks all service migrations
- vf-auth-service migration (Issue #4) provides pattern for others
- CloudFormation updates (Issue #10) required for deployment

## 📋 Issue Template

```markdown
## Parameter Store Migration: [Service/Component Name]

### Priority: [High/Medium/Low]
### Effort: [X days]  
### Assignee: [Role/Name]

### Description
[Brief description of what needs to be migrated]

### Acceptance Criteria
- [ ] [Specific, testable criteria]
- [ ] [Performance validation]
- [ ] [Testing requirements]

### Technical Details
[Code examples, configuration changes]

### Dependencies
- [ ] Issue #X: [Dependency description]

### Definition of Done
- [ ] Code changes completed and tested
- [ ] Documentation updated
- [ ] Performance validated
- [ ] Rollback procedure documented
```

---

This task breakdown provides clear, actionable GitHub issues that can be assigned to different team members and tracked independently while maintaining overall project coordination.
