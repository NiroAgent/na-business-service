#!/usr/bin/env python3
"""
Integrate VisualForgeMediaV2 with NiroSubs
Updates secrets to enable cross-service communication
"""

import json
import boto3

REGION = 'us-east-1'

# Initialize clients
cf_client = boto3.client('cloudformation', region_name=REGION)
secrets_client = boto3.client('secretsmanager', region_name=REGION)

def get_stack_outputs(stack_name):
    """Get outputs from a CloudFormation stack"""
    try:
        response = cf_client.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        outputs = {}
        for output in stack.get('Outputs', []):
            outputs[output['OutputKey']] = output['OutputValue']
        return outputs
    except Exception as e:
        print(f"Error getting stack outputs for {stack_name}: {e}")
        return {}

def update_integration_secrets():
    """Update secrets with integration endpoints"""
    
    # Get NiroSubs endpoints
    nirosubs_staging = {
        'api': 'https://gkjhn4m606.execute-api.us-east-1.amazonaws.com/staging',
        'cloudfront': 'https://d1mt74nsjx1seq.cloudfront.net',
        'cognitoPoolId': 'us-east-1_rdE2qCAIe'
    }
    
    # Get VisualForgeMedia endpoints
    vf_dev = get_stack_outputs('dev-vf-serverless-stack')
    vf_staging = get_stack_outputs('staging-vf-serverless-stack')
    
    # Create consolidated integration secret
    integration_config = {
        'nirosubs': {
            'staging': nirosubs_staging,
            'services': ['auth', 'dashboard', 'payments', 'user', 'core']
        },
        'visualforgemedia': {
            'dev': {
                'api': vf_dev.get('ApiEndpoint', ''),
                'cloudfront': f"https://{vf_dev.get('CloudFrontURL', '')}",
                'services': ['audio', 'video', 'image', 'text', 'bulk']
            },
            'staging': {
                'api': vf_staging.get('ApiEndpoint', ''),
                'cloudfront': f"https://{vf_staging.get('CloudFrontURL', '')}",
                'services': ['audio', 'video', 'image', 'text', 'bulk']
            }
        },
        'integration': {
            'enabled': True,
            'corsOrigins': [
                'https://d1mt74nsjx1seq.cloudfront.net',
                f"https://{vf_dev.get('CloudFrontURL', '')}",
                f"https://{vf_staging.get('CloudFrontURL', '')}",
                'http://localhost:3000',
                'http://localhost:3001'
            ]
        }
    }
    
    # Update or create the integration secret
    secret_name = 'visualforge-integration-config'
    
    try:
        # Try to update existing secret
        secrets_client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(integration_config, indent=2)
        )
        print(f"[OK] Updated integration secret: {secret_name}")
    except secrets_client.exceptions.ResourceNotFoundException:
        # Create new secret
        secrets_client.create_secret(
            Name=secret_name,
            Description='Integration configuration between NiroSubs and VisualForgeMedia',
            SecretString=json.dumps(integration_config, indent=2)
        )
        print(f"[OK] Created integration secret: {secret_name}")
    
    return integration_config

def test_endpoints(config):
    """Test that all endpoints are accessible"""
    import requests
    
    print("\nTesting endpoint connectivity...")
    
    # Test NiroSubs staging
    try:
        response = requests.get(f"{config['nirosubs']['staging']['api']}/core/api/health", timeout=5)
        print(f"[OK] NiroSubs staging: {response.status_code}")
    except Exception as e:
        print(f"[WARN] NiroSubs staging unreachable: {e}")
    
    # Test VisualForgeMedia dev
    try:
        vf_dev_api = config['visualforgemedia']['dev']['api']
        if vf_dev_api:
            response = requests.get(f"{vf_dev_api}/audio/health", timeout=5)
            print(f"[OK] VisualForgeMedia dev: {response.status_code}")
    except Exception as e:
        print(f"[WARN] VisualForgeMedia dev unreachable: {e}")
    
    # Test VisualForgeMedia staging
    try:
        vf_staging_api = config['visualforgemedia']['staging']['api']
        if vf_staging_api:
            response = requests.get(f"{vf_staging_api}/audio/health", timeout=5)
            print(f"[OK] VisualForgeMedia staging: {response.status_code}")
    except Exception as e:
        print(f"[WARN] VisualForgeMedia staging unreachable: {e}")

def main():
    print("=" * 60)
    print("Integrating VisualForgeMediaV2 with NiroSubs")
    print("=" * 60)
    
    # Update integration secrets
    config = update_integration_secrets()
    
    # Display integration details
    print("\nIntegration Configuration:")
    print("-" * 40)
    print(f"NiroSubs Staging API: {config['nirosubs']['staging']['api']}")
    print(f"VisualForgeMedia Dev API: {config['visualforgemedia']['dev']['api']}")
    print(f"VisualForgeMedia Staging API: {config['visualforgemedia']['staging']['api']}")
    
    # Test endpoints
    test_endpoints(config)
    
    print("\n" + "=" * 60)
    print("Integration Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Deploy Lambda functions with actual code")
    print("2. Deploy frontend applications")
    print("3. Run integration tests")
    print("4. Configure API Gateway routes")

if __name__ == "__main__":
    main()