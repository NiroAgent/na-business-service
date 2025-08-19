# Simplified DNS Strategy - No Personal Account

## Current State
- **Domain Registrar**: Porkbun
- **Current NS**: Pointing to vf-dev AWS account ✅
- **Remove**: Hosted zone in stevesurles personal account

## Simple Environment-Specific Approach

### For Development (Current)
```
Porkbun → vf-dev Route53
```
- ✅ Already working
- Manage all dev.visualforge.ai records

### For Staging (When Ready)
```
Porkbun → vf-stg Route53
```
1. Create hosted zone in vf-stg account
2. Update Porkbun NS records to vf-stg nameservers
3. Configure all staging DNS records

### For Production (When Ready)
```
Porkbun → vf-prod Route53
```
1. Create hosted zone in vf-prod account
2. Update Porkbun NS records to vf-prod nameservers
3. Configure all production DNS records

## Benefits of This Approach
- ✅ **Simple**: One account owns everything for each environment
- ✅ **Clean**: No cross-account complexity
- ✅ **Secure**: Each environment completely isolated
- ✅ **No Personal Account**: Everything in organization accounts

## DNS Record Structure per Environment

### Development (vf-dev account)
- dev.visualforge.ai → CloudFront
- api-dev.visualforge.ai → API Gateway
- auth-dev.visualforge.ai → Cognito
- app-dev.visualforge.ai → CloudFront

### Staging (vf-stg account)
- stg.visualforge.ai → CloudFront
- api-stg.visualforge.ai → API Gateway
- auth-stg.visualforge.ai → Cognito
- app-stg.visualforge.ai → CloudFront

### Production (vf-prod account)
- visualforge.ai → CloudFront
- www.visualforge.ai → CloudFront
- api.visualforge.ai → API Gateway
- auth.visualforge.ai → Cognito
- app.visualforge.ai → CloudFront

## Switching Between Environments

When ready to deploy to a new environment:

1. **Export current DNS records** (backup):
```bash
aws route53 list-resource-record-sets --hosted-zone-id Z015790023056BKZ15UTB > dns-backup.json
```

2. **Create hosted zone in new account**:
```bash
aws route53 create-hosted-zone --name visualforge.ai --caller-reference $(date +%s)
```

3. **Note the new nameservers** from output

4. **Update Porkbun**:
- Login to Porkbun
- Update NS records to new environment's nameservers

5. **Wait for propagation** (up to 48 hours, usually much faster)

## Current Action Items

1. ✅ Keep vf-dev as-is (working)
2. Remove visualforge.ai hosted zone from stevesurles account (cleanup)
3. Document the nameservers for each environment as you create them

## Nameserver Reference

### vf-dev (Current - Active)
```
ns-1277.awsdns-31.org
ns-174.awsdns-21.com
ns-1830.awsdns-36.co.uk
ns-932.awsdns-52.net
```

### vf-stg (To be created)
```
[Will be generated when hosted zone created]
```

### vf-prod (To be created)
```
[Will be generated when hosted zone created]
```