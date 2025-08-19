#!/bin/bash

# AWS Authentication Check for VF Environments
echo "🔐 Checking AWS Authentication Status..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check current identity
echo "📍 Current AWS Identity:"
aws sts get-caller-identity 2>/dev/null || echo "❌ No default AWS credentials"

echo ""
echo "📋 Available AWS Profiles:"
aws configure list-profiles 2>/dev/null || echo "❌ No AWS profiles configured"

echo ""
echo "🏢 VF Environment Authentication Status:"

# Check VF-dev
echo "  VF-dev (319040880702):"
aws sts get-caller-identity --profile vf-dev 2>/dev/null && echo "  ✅ Authenticated" || echo "  ❌ Not authenticated"

# Check VF-staging  
echo "  VF-staging (275057778147):"
aws sts get-caller-identity --profile vf-staging 2>/dev/null && echo "  ✅ Authenticated" || echo "  ❌ Not authenticated"

# Check VF-production
echo "  VF-production (229742714212):"
aws sts get-caller-identity --profile vf-production 2>/dev/null && echo "  ✅ Authenticated" || echo "  ❌ Not authenticated"

echo ""
echo "🔧 Quick Setup Commands:"
echo "  aws configure --profile vf-dev"
echo "  aws configure --profile vf-staging" 
echo "  aws configure --profile vf-production"
echo ""
echo "🔑 For SSO-based authentication:"
echo "  aws sso login --profile vf-dev"
echo "  aws sso login --profile vf-staging"
echo "  aws sso login --profile vf-production"
