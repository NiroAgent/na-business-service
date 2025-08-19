#!/bin/bash

echo "======================================"
echo "CLEANUP UNUSED AWS RESOURCES"
echo "======================================"
echo ""
echo "This script will remove resources outside your main solution"
echo ""

# Failed/Rolled back stacks that can be deleted
FAILED_STACKS=(
    "vf-media-secrets-dev-v2"
    "dev-cognito-google-oauth-real"
    "dev-cognito-google-oauth"
    "ns-route53-dns"
    "ns-api-integrated"
    "ns-route53"
    "ns-auth"
)

# Stacks that might be old/unused
QUESTIONABLE_STACKS=(
    "bmg-monitoring"
    "bmg-apigw-batch-proxy"
    "bmg-batch"
    "bmg-sqs"
    "bmg-ecr"
    "staging-vf-serverless-stack"
    "staging-visualforge-core"
)

echo "1. DELETING FAILED/ROLLED BACK STACKS (Safe to remove):"
echo "---------------------------------------------------------"
for stack in "${FAILED_STACKS[@]}"; do
    echo "Deleting: $stack"
    aws cloudformation delete-stack --stack-name "$stack" 2>/dev/null && echo "  ✓ Deletion initiated" || echo "  ✗ Already deleted or error"
done

echo ""
echo "2. REVIEWING POTENTIALLY UNUSED STACKS:"
echo "---------------------------------------------------------"
echo "These appear to be old or for different projects (bmg, staging):"
echo ""
for stack in "${QUESTIONABLE_STACKS[@]}"; do
    echo "- $stack"
done

echo ""
echo "3. CHECKING FOR UNUSED NAT GATEWAYS (expensive):"
aws ec2 describe-nat-gateways --filter "Name=state,Values=available" --query 'NatGateways[*].[NatGatewayId, State, Tags[?Key==`Name`].Value|[0]]' --output table

echo ""
echo "4. CHECKING FOR UNUSED ELASTIC IPs:"
aws ec2 describe-addresses --query 'Addresses[?AssociationId==`null`].[PublicIp, AllocationId]' --output table

echo ""
echo "5. CHECKING FOR OLD SNAPSHOTS:"
aws ec2 describe-snapshots --owner-ids self --query 'Snapshots[?StartTime<=`2025-07-01`].[SnapshotId, StartTime, VolumeSize]' --output table | head -10

echo ""
echo "6. CHECKING ELASTICACHE (costing $7/month):"
aws elasticache describe-cache-clusters --query 'CacheClusters[*].[CacheClusterId, CacheNodeType, CacheClusterStatus]' --output table

echo ""
echo "======================================"
echo "RECOMMENDATIONS:"
echo "======================================"
echo ""
echo "To delete the questionable stacks (bmg/staging), run:"
echo "  aws cloudformation delete-stack --stack-name [STACK_NAME]"
echo ""
echo "To delete unused Elastic IPs:"
echo "  aws ec2 release-address --allocation-id [ALLOCATION_ID]"
echo ""
echo "To delete ElastiCache cluster:"
echo "  aws elasticache delete-cache-cluster --cache-cluster-id [CLUSTER_ID]"