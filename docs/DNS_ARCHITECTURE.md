# DNS Architecture for Multi-Environment Setup

## Current Situation
- **Domain Registrar**: Porkbun (visualforge.ai)
- **Potential Conflict**: Hosted zones in multiple AWS accounts

## Recommended Architecture

### Option 1: Centralized DNS (RECOMMENDED)
Keep the main hosted zone in ONE account (stevesurles personal) and delegate subdomains:

```
Porkbun (visualforge.ai)
    ↓ NS records point to
stevesurles AWS Account (Main Hosted Zone)
    ├── prod records (visualforge.ai, www.visualforge.ai)
    ├── dev.visualforge.ai → NS delegation to vf-dev account
    ├── stg.visualforge.ai → NS delegation to vf-stg account
    └── api.visualforge.ai, etc.
```

**At Porkbun:**
- Set NS records to point to stevesurles AWS Route53 hosted zone

**In stevesurles account Route53:**
```
# Production records
visualforge.ai        A     → CloudFront (prod account)
www.visualforge.ai    A     → CloudFront (prod account)
api.visualforge.ai    CNAME → API Gateway (prod account)

# Delegate dev subdomain to vf-dev account
dev.visualforge.ai    NS    → vf-dev Route53 nameservers

# Delegate stg subdomain to vf-stg account  
stg.visualforge.ai    NS    → vf-stg Route53 nameservers
```

**In vf-dev account Route53:**
- Create hosted zone for `dev.visualforge.ai`
- Manage all dev.* subdomains

**In vf-stg account Route53:**
- Create hosted zone for `stg.visualforge.ai`
- Manage all stg.* subdomains

### Option 2: Direct Environment Zones
Have Porkbun point directly to the environment-specific account:

```
Porkbun
    ↓ NS records point to
vf-dev AWS (for dev)
vf-stg AWS (for staging)  
vf-prod AWS (for production)
```

**Problem**: Can only point to ONE account at a time, not suitable for multi-env.

## Implementation Steps

### For Option 1 (Recommended):

1. **At Porkbun:**
   - Ensure NS records point to stevesurles AWS account Route53

2. **In stevesurles AWS account:**
   ```bash
   # Get the hosted zone ID for visualforge.ai
   aws route53 list-hosted-zones --query "HostedZones[?Name=='visualforge.ai.']"
   
   # Create NS delegation for dev subdomain
   aws route53 change-resource-record-sets --hosted-zone-id MAIN_ZONE_ID \
     --change-batch '{
       "Changes": [{
         "Action": "CREATE",
         "ResourceRecordSet": {
           "Name": "dev.visualforge.ai",
           "Type": "NS",
           "TTL": 300,
           "ResourceRecords": [
             {"Value": "ns-xxx.awsdns-xx.org"},
             {"Value": "ns-xxx.awsdns-xx.com"},
             {"Value": "ns-xxx.awsdns-xx.net"},
             {"Value": "ns-xxx.awsdns-xx.co.uk"}
           ]
         }
       }]
     }'
   ```

3. **In vf-dev AWS account:**
   ```bash
   # Create hosted zone for dev.visualforge.ai
   aws route53 create-hosted-zone --name dev.visualforge.ai \
     --caller-reference $(date +%s)
   
   # Note the NS records from the output
   # These are what you put in the stevesurles account delegation
   ```

4. **Update CloudFormation templates:**
   - Remove routes for base domain from dev/stg environments
   - Only manage subdomain records in each environment

## Benefits of This Approach

1. **Clear Separation**: Each environment manages its own subdomain
2. **No Conflicts**: No overlapping DNS records between accounts
3. **Independent Deployments**: Each environment can update DNS without affecting others
4. **Security**: Production DNS isolated from dev/staging
5. **Scalability**: Easy to add new environments

## SSL Certificates

- **Dev Account**: Wildcard cert for `*.dev.visualforge.ai`
- **Stg Account**: Wildcard cert for `*.stg.visualforge.ai`  
- **Prod Account**: Wildcard cert for `*.visualforge.ai` and `visualforge.ai`

## Current Action Items

1. ✅ Check Porkbun NS records
2. ✅ Identify which AWS account should be authoritative
3. ✅ Set up subdomain delegation
4. ✅ Update CloudFormation templates for proper subdomain management
5. ✅ Test DNS resolution