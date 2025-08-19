# Product Architecture Clarification

## The Real Structure

### What You Actually Have:

1. **NiroForge** (NF) - The core product platform
   - This is your main product
   - The actual codebase and infrastructure
   - What you're developing

2. **NiroSubs** (NS) - Subscription/payment component
   - Part of the NiroForge ecosystem
   - Handles subscriptions and payments

3. **VisualForge** (VF) - A branded instance
   - Just a deployment of NiroForge
   - Like a "customer" instance (but it's just you)
   - Could theoretically have other branded instances later

## The Problem This Creates

You're mixing **product code** with **instance configuration**:

```
Current confusion:
- dev-visualforge-core      <- Is this the product or the instance?
- dev-vf-dashboard-lambda   <- Product feature or customer branding?
- vf-media-items-dev        <- Core table or instance-specific?
```

## Recommended Architecture

### Option 1: Product-First Naming (Recommended)
Everything is NiroForge (nf-) since that's the actual product:

```
Product Resources (what you're building):
- nf-core                   (not vf-core)
- nf-dashboard             
- nf-auth
- nf-media-service
- nf-user-service
- ns-payments              (subsystem of NiroForge)
- ns-subscriptions

Instance Configuration:
- Config file or environment variables specify "VisualForge" branding
- BRAND_NAME=VisualForge
- INSTANCE_ID=visualforge
```

### Option 2: Separate Product from Instance
Keep infrastructure generic, configure instances separately:

```
Infrastructure:
- core-service
- dashboard-service
- auth-service
- media-service

Instance Config (environment variables):
- INSTANCE=visualforge
- BRAND=VisualForge
- THEME=vf-theme
```

### Option 3: Multi-Tenant Architecture
Build for multiple instances from the start:

```
Shared Infrastructure:
- nf-core-engine
- nf-tenant-manager
- nf-dashboard-renderer

Per-Instance Resources:
- vf-config (VisualForge instance)
- af-config (AnotherForge instance)
- cf-config (ClientForge instance)
```

## The Core Question

**Are you building:**
- A) NiroForge product that happens to have one instance (VisualForge)?
- B) VisualForge as a standalone product?
- C) A multi-tenant platform that could have many branded instances?

## My Recommendation

Since VisualForge is just a branded instance of NiroForge:

1. **Rename everything to NF (NiroForge)**:
   ```
   nf-core
   nf-dashboard
   nf-auth
   nf-media
   ```

2. **Keep NS for subscription components**:
   ```
   ns-payments
   ns-billing
   ns-subscriptions
   ```

3. **Use configuration for branding**:
   ```yaml
   # instance-config.yml
   instance:
     id: visualforge
     brand_name: "VisualForge"
     domain: "visualforge.com"
     theme: "vf-blue"
   ```

This way:
- Your AWS resources reflect what you're actually building (NiroForge)
- VisualForge becomes just configuration/branding
- You could easily add more instances later
- No confusion about what's product vs. instance

## Current State Problems

Right now you have:
- **Product logic** mixed with **instance branding**
- **VF prefixes** that don't represent the actual product
- Confusion about what's core platform vs. deployment

## Clean Architecture

```
NiroForge Platform (Product):
├── nf-core/
├── nf-services/
│   ├── nf-auth/
│   ├── nf-media/
│   ├── nf-dashboard/
├── ns-subsystem/
│   ├── ns-payments/
│   ├── ns-subscriptions/
└── instances/
    └── visualforge/
        └── config.yml  (branding/customization)
```

This makes it clear:
- **NiroForge** = What you're building
- **VisualForge** = How it's branded/deployed
- **Resources** = Named after the product (NF), not the instance (VF)