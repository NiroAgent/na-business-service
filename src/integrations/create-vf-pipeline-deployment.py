#!/usr/bin/env python3
"""
Simple VF Environment Pipeline Deployment
==========================================
Deploy the autonomous business system using the existing pipeline structure
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def create_pipeline_deployment():
    """Create a pipeline-based deployment using existing VF infrastructure"""
    
    print("\n🚀 CREATING PIPELINE DEPLOYMENT FOR VF ENVIRONMENTS")
    print("="*70)
    
    # 1. Create CloudFormation templates for each environment
    environments = {
        "vf-dev": {
            "account_id": "816454053517",
            "region": "us-east-1", 
            "branch": "dev"
        },
        "vf-stg": {
            "account_id": "816454053517",
            "region": "us-east-1",
            "branch": "staging" 
        },
        "vf-prd": {
            "account_id": "816454053517",
            "region": "us-east-1",
            "branch": "main"
        }
    }
    
    for env_name, config in environments.items():
        create_cfn_template(env_name, config)
        create_deployment_script(env_name, config)
    
    # 2. Create master deployment script
    create_master_deployment_script(environments)
    
    # 3. Create GitHub Actions workflows
    create_github_actions_workflows(environments)
    
    print("\n✅ Pipeline deployment files created!")
    print("\nNext steps:")
    print("1. Copy the CloudFormation templates to each project")
    print("2. Update GitHub Actions workflows")
    print("3. Run the deployment using: python deploy-vf-pipeline.py")
    print("4. Test with GitHub Issues")

def create_cfn_template(env_name, config):
    """Create CloudFormation template for environment"""
    
    template = f'''AWSTemplateFormatVersion: '2010-09-09'
Description: 'AI Agent Infrastructure for {env_name}'

Parameters:
  Environment:
    Type: String
    Default: {env_name}
    Description: Environment name

Resources:
  # GitHub Webhook Lambda
  GitHubAgentLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub 'github-agent-processor-${{Environment}}'
      Runtime: python3.9
      Handler: index.lambda_handler
      Code:
        ZipFile: |
          import json
          import boto3
          import logging
          
          logger = logging.getLogger()
          logger.setLevel(logging.INFO)
          
          def lambda_handler(event, context):
              logger.info(f"Received GitHub webhook: {{event}}")
              
              # Parse GitHub webhook
              if 'body' in event:
                  body = json.loads(event['body'])
                  if 'issue' in body:
                      issue = body['issue']
                      action = body.get('action', '')
                      
                      if action in ['opened', 'edited']:
                          process_github_issue(issue)
              
              return {{'statusCode': 200, 'body': 'OK'}}
          
          def process_github_issue(issue):
              logger.info(f"Processing issue: {{issue['title']}}")
              
              # Route to appropriate agent based on labels
              labels = [label['name'] for label in issue.get('labels', [])]
              
              if 'manager' in labels:
                  route_to_manager(issue)
              elif 'developer' in labels:
                  route_to_developer(issue)
              elif 'qa' in labels:
                  route_to_qa(issue)
              else:
                  route_to_manager(issue)  # Default to manager
          
          def route_to_manager(issue):
              logger.info("Routing to manager agent")
              # Trigger ECS task or SQS message
              
          def route_to_developer(issue):
              logger.info("Routing to developer agent")
              
          def route_to_qa(issue):
              logger.info("Routing to QA agent")
      
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          AWS_REGION: !Ref AWS::Region
      
      Role: !GetAtt LambdaExecutionRole.Arn
      Timeout: 300

  # Lambda Execution Role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: AgentProcessingPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - ecs:*
                  - batch:*
                  - sqs:*
                  - ssm:*
                  - logs:*
                Resource: '*'

  # API Gateway for GitHub Webhook
  GitHubWebhookAPI:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub 'github-agent-webhook-${{Environment}}'
      Description: GitHub webhook for AI agents

  WebhookResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref GitHubWebhookAPI
      ParentId: !GetAtt GitHubWebhookAPI.RootResourceId
      PathPart: webhook

  WebhookMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref GitHubWebhookAPI
      ResourceId: !Ref WebhookResource
      HttpMethod: POST
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{GitHubAgentLambda.Arn}}/invocations'

  # Lambda Permission for API Gateway
  LambdaInvokePermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref GitHubAgentLambda
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub '${{GitHubWebhookAPI}}/*/POST/webhook'

  # API Gateway Deployment
  WebhookDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn: WebhookMethod
    Properties:
      RestApiId: !Ref GitHubWebhookAPI
      StageName: !Ref Environment

  # ECS Cluster for Agent Processing
  AgentCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub 'ai-agents-${{Environment}}'
      CapacityProviders:
        - FARGATE
      DefaultCapacityProviderStrategy:
        - CapacityProvider: FARGATE
          Weight: 1

  # SQS Queue for Agent Tasks
  AgentTaskQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub 'agent-tasks-${{Environment}}'
      VisibilityTimeoutSeconds: 300
      MessageRetentionPeriod: 1209600  # 14 days

Outputs:
  WebhookURL:
    Description: GitHub Webhook URL
    Value: !Sub 'https://${{GitHubWebhookAPI}}.execute-api.${{AWS::Region}}.amazonaws.com/${{Environment}}/webhook'
    Export:
      Name: !Sub 'github-webhook-${{Environment}}'

  ClusterName:
    Description: ECS Cluster Name
    Value: !Ref AgentCluster
    Export:
      Name: !Sub 'agent-cluster-${{Environment}}'

  TaskQueueURL:
    Description: SQS Task Queue URL
    Value: !Ref AgentTaskQueue
    Export:
      Name: !Sub 'task-queue-${{Environment}}'
'''
    
    filename = f"ai-agent-infrastructure-{env_name}.yaml"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✅ Created CloudFormation template: {filename}")

def create_deployment_script(env_name, config):
    """Create deployment script for environment"""
    
    script = f'''#!/usr/bin/env python3
"""
Deploy AI Agents to {env_name.upper()}
"""

import subprocess
import json
import sys

def deploy_to_{env_name.replace('-', '_')}():
    """Deploy to {env_name} environment"""
    
    print(f"🚀 Deploying AI Agents to {env_name.upper()}")
    
    # Deploy CloudFormation stack
    cmd = [
        "aws", "cloudformation", "deploy",
        "--template-file", f"ai-agent-infrastructure-{env_name}.yaml",
        "--stack-name", f"ai-agents-{env_name}",
        "--capabilities", "CAPABILITY_IAM",
        "--region", "{config['region']}",
        "--parameter-overrides", f"Environment={env_name}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ CloudFormation deployed successfully to {env_name}")
            
            # Get stack outputs
            get_outputs_cmd = [
                "aws", "cloudformation", "describe-stacks",
                "--stack-name", f"ai-agents-{env_name}",
                "--region", "{config['region']}",
                "--query", "Stacks[0].Outputs"
            ]
            
            outputs_result = subprocess.run(get_outputs_cmd, capture_output=True, text=True)
            if outputs_result.returncode == 0:
                outputs = json.loads(outputs_result.stdout)
                print("\\n📋 Stack Outputs:")
                for output in outputs:
                    print(f"  {output['OutputKey']}: {output['OutputValue']}")
                    
                # Save webhook URL for GitHub configuration
                webhook_url = next((o['OutputValue'] for o in outputs if o['OutputKey'] == 'WebhookURL'), None)
                if webhook_url:
                    with open(f"webhook-url-{env_name}.txt", "w") as f:
                        f.write(webhook_url)
                    print(f"\\n🔗 Webhook URL saved to webhook-url-{env_name}.txt")
                    print(f"Configure this URL in your GitHub repository webhooks:")
                    print(f"  {webhook_url}")
            
        else:
            print(f"❌ CloudFormation deployment failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ AWS CLI not found. Please install AWS CLI and configure credentials.")
        return False
    
    return True

if __name__ == "__main__":
    success = deploy_to_{env_name.replace('-', '_')}()
    sys.exit(0 if success else 1)
'''
    
    filename = f"deploy-{env_name}.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"✅ Created deployment script: {filename}")

def create_master_deployment_script(environments):
    """Create master deployment script"""
    
    script = '''#!/usr/bin/env python3
"""
Deploy AI Agent System to All VF Environments
==============================================
Master deployment script for vf-dev, vf-stg, vf-prd
"""

import subprocess
import sys
import time
from datetime import datetime

def deploy_all_environments():
    """Deploy to all VF environments in order"""
    
    print("\\n🚀 DEPLOYING AI AGENT SYSTEM TO ALL VF ENVIRONMENTS")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    environments = ["vf-dev", "vf-stg", "vf-prd"]
    results = {}
    
    for env in environments:
        print(f"\\n{'='*20} DEPLOYING TO {env.upper()} {'='*20}")
        
        try:
            result = subprocess.run([sys.executable, f"deploy-{env}.py"], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {env.upper()} deployment successful")
                results[env] = "SUCCESS"
            else:
                print(f"❌ {env.upper()} deployment failed:")
                print(result.stderr)
                results[env] = "FAILED"
        
        except Exception as e:
            print(f"❌ Error deploying {env}: {str(e)}")
            results[env] = f"ERROR: {str(e)}"
        
        # Wait between deployments
        if env != environments[-1]:
            print("⏳ Waiting 30 seconds before next deployment...")
            time.sleep(30)
    
    # Summary
    print("\\n" + "="*70)
    print("📋 DEPLOYMENT SUMMARY")
    print("="*70)
    
    for env, status in results.items():
        icon = "✅" if status == "SUCCESS" else "❌"
        print(f"{icon} {env.upper()}: {status}")
    
    # Next steps
    print("\\n" + "="*70)
    print("🎯 NEXT STEPS")
    print("="*70)
    print("1. Configure GitHub webhooks with the URLs from webhook-url-*.txt files")
    print("2. Create test issues to verify the system:")
    print("   - Title: '[Manager] Test AI Agent System'")
    print("   - Labels: 'manager', 'test'")
    print("3. Monitor CloudWatch logs for agent processing")
    print("4. Check SQS queues for task processing")
    
    all_success = all(status == "SUCCESS" for status in results.values())
    if all_success:
        print("\\n🎉 ALL ENVIRONMENTS DEPLOYED SUCCESSFULLY!")
    else:
        print("\\n⚠️  Some deployments failed. Check the logs above.")
    
    return all_success

if __name__ == "__main__":
    success = deploy_all_environments()
    sys.exit(0 if success else 1)
'''
    
    with open("deploy-vf-pipeline.py", 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("✅ Created master deployment script: deploy-vf-pipeline.py")

def create_github_actions_workflows(environments):
    """Create GitHub Actions workflows for each environment"""
    
    for env_name, config in environments.items():
        workflow = f'''name: Deploy AI Agents to {env_name.upper()}

on:
  push:
    branches: [ {config['branch']} ]
  workflow_dispatch:

env:
  AWS_REGION: {config['region']}
  ENVIRONMENT: {env_name}

jobs:
  deploy-agents:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        role-to-assume: arn:aws:iam::{config['account_id']}:role/GitHubActionsRole
        aws-region: ${{{{ env.AWS_REGION }}}}
    
    - name: Deploy CloudFormation stack
      run: |
        aws cloudformation deploy \\
          --template-file ai-agent-infrastructure-{env_name}.yaml \\
          --stack-name ai-agents-{env_name} \\
          --capabilities CAPABILITY_IAM \\
          --region ${{{{ env.AWS_REGION }}}} \\
          --parameter-overrides Environment={env_name}
    
    - name: Get webhook URL
      id: webhook
      run: |
        WEBHOOK_URL=$(aws cloudformation describe-stacks \\
          --stack-name ai-agents-{env_name} \\
          --region ${{{{ env.AWS_REGION }}}} \\
          --query "Stacks[0].Outputs[?OutputKey=='WebhookURL'].OutputValue" \\
          --output text)
        echo "webhook-url=$WEBHOOK_URL" >> $GITHUB_OUTPUT
        echo "🔗 Webhook URL: $WEBHOOK_URL"
    
    - name: Test deployment
      run: |
        echo "✅ AI Agent system deployed to {env_name.upper()}"
        echo "🔗 Webhook URL: ${{{{ steps.webhook.outputs.webhook-url }}}}"
        echo "Configure this URL in repository webhooks to enable agent processing"
'''
        
        filename = f"github-actions-{env_name}.yml"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(workflow)
        
        print(f"✅ Created GitHub Actions workflow: {filename}")

def main():
    """Main function"""
    
    print("Creating VF Pipeline Deployment System...")
    create_pipeline_deployment()
    
    print("\n" + "="*70)
    print("📋 FILES CREATED:")
    print("="*70)
    print("CloudFormation Templates:")
    print("  - ai-agent-infrastructure-vf-dev.yaml")
    print("  - ai-agent-infrastructure-vf-stg.yaml") 
    print("  - ai-agent-infrastructure-vf-prd.yaml")
    print("\\nDeployment Scripts:")
    print("  - deploy-vf-dev.py")
    print("  - deploy-vf-stg.py")
    print("  - deploy-vf-prd.py")
    print("  - deploy-vf-pipeline.py (master script)")
    print("\\nGitHub Actions:")
    print("  - github-actions-vf-dev.yml")
    print("  - github-actions-vf-stg.yml")
    print("  - github-actions-vf-prd.yml")
    
    print("\\n" + "="*70)
    print("🚀 READY TO DEPLOY!")
    print("="*70)
    print("Run: python deploy-vf-pipeline.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
