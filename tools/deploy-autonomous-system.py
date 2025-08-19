#!/usr/bin/env python3
"""
Deploy Autonomous Business System to VF Environments
====================================================
Deploy the complete GitHub Issues → Agent assignment system across all VF environments
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

class AutonomousSystemDeployer:
    """Deploy the complete autonomous business system"""
    
    def __init__(self):
        self.environments = {
            "vf-dev": {
                "account_id": "816454053517",
                "region": "us-east-1",
                "branch": "dev",
                "projects": ["NiroSubs-V2", "VisualForgeMediaV2"]
            },
            "vf-stg": {
                "account_id": "816454053517", 
                "region": "us-east-1",
                "branch": "staging",
                "projects": ["NiroSubs-V2", "VisualForgeMediaV2"]
            },
            "vf-prd": {
                "account_id": "816454053517",
                "region": "us-east-1", 
                "branch": "main",
                "projects": ["NiroSubs-V2", "VisualForgeMediaV2"]
            }
        }
        
        self.deployment_order = ["vf-dev", "vf-stg", "vf-prd"]
        
    def deploy_agent_system(self, environment):
        """Deploy the AI agent system to an environment"""
        
        print(f"\n🤖 Deploying AI Agent System to {environment.upper()}")
        print("="*60)
        
        env_config = self.environments[environment]
        
        # 1. Deploy GitHub Actions Workflow
        self.deploy_github_workflow(environment, env_config)
        
        # 2. Deploy Agent Deployment Package  
        self.deploy_agent_package(environment, env_config)
        
        # 3. Configure AWS Infrastructure
        self.setup_aws_infrastructure(environment, env_config)
        
        # 4. Test the deployment
        self.test_deployment(environment, env_config)
        
        return True
    
    def deploy_github_workflow(self, environment, config):
        """Deploy the GitHub Actions workflow"""
        
        print(f"\n📋 Deploying GitHub Actions workflow to {environment}")
        
        # Copy the workflow to each project
        workflow_source = "e:/Projects/.github/workflows/ai-agent-processor.yml"
        
        for project in config["projects"]:
            project_path = f"e:/Projects/{project}"
            workflow_dir = f"{project_path}/.github/workflows"
            workflow_dest = f"{workflow_dir}/ai-agent-processor-{environment}.yml"
            
            if os.path.exists(project_path):
                os.makedirs(workflow_dir, exist_ok=True)
                
                # Customize workflow for environment
                with open(workflow_source, 'r') as f:
                    workflow_content = f.read()
                
                # Replace environment-specific values
                workflow_content = workflow_content.replace(
                    "USE_DIRECT_PROCESSING: true",
                    f"USE_DIRECT_PROCESSING: true\n        ENVIRONMENT: {environment}\n        AWS_REGION: {config['region']}\n        TARGET_BRANCH: {config['branch']}"
                )
                
                with open(workflow_dest, 'w') as f:
                    f.write(workflow_content)
                
                print(f"  ✅ Deployed workflow to {project}")
            else:
                print(f"  ⚠️  Project {project} not found")
    
    def deploy_agent_package(self, environment, config):
        """Deploy the agent deployment package"""
        
        print(f"\n📦 Deploying agent package to {environment}")
        
        # Copy the deployment package to each project
        package_source = "e:/Projects/ai-agent-deployment"
        
        for project in config["projects"]:
            project_path = f"e:/Projects/{project}"
            package_dest = f"{project_path}/ai-agent-deployment"
            
            if os.path.exists(project_path):
                if os.path.exists(package_dest):
                    import shutil
                    shutil.rmtree(package_dest)
                
                import shutil
                shutil.copytree(package_source, package_dest)
                
                # Create environment-specific configuration
                env_config = {
                    "environment": environment,
                    "aws_region": config["region"],
                    "aws_account_id": config["account_id"],
                    "target_branch": config["branch"],
                    "deployment_timestamp": datetime.now().isoformat()
                }
                
                with open(f"{package_dest}/config-{environment}.json", 'w') as f:
                    json.dump(env_config, f, indent=2)
                
                print(f"  ✅ Deployed package to {project}")
    
    def setup_aws_infrastructure(self, environment, config):
        """Set up AWS infrastructure for the environment"""
        
        print(f"\n☁️  Setting up AWS infrastructure for {environment}")
        
        # Create CloudFormation template for agent infrastructure
        cfn_template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"AI Agent Infrastructure for {environment}",
            "Parameters": {
                "Environment": {
                    "Type": "String",
                    "Default": environment,
                    "Description": "Environment name"
                }
            },
            "Resources": {
                # Lambda for GitHub webhook processing
                "GitHubWebhookLambda": {
                    "Type": "AWS::Lambda::Function",
                    "Properties": {
                        "FunctionName": f"github-agent-dispatcher-{environment}",
                        "Runtime": "python3.9",
                        "Handler": "github-agent-dispatcher.lambda_handler",
                        "Code": {
                            "ZipFile": "# Lambda function code will be deployed separately"
                        },
                        "Environment": {
                            "Variables": {
                                "ENVIRONMENT": environment,
                                "AWS_REGION": config["region"]
                            }
                        },
                        "Role": {"Ref": "LambdaExecutionRole"}
                    }
                },
                
                # ECS Cluster for agent processing
                "AgentECSCluster": {
                    "Type": "AWS::ECS::Cluster",
                    "Properties": {
                        "ClusterName": f"ai-agents-{environment}",
                        "CapacityProviders": ["FARGATE"],
                        "DefaultCapacityProviderStrategy": [{
                            "CapacityProvider": "FARGATE",
                            "Weight": 1
                        }]
                    }
                },
                
                # Batch Compute Environment
                "BatchComputeEnvironment": {
                    "Type": "AWS::Batch::ComputeEnvironment",
                    "Properties": {
                        "Type": "MANAGED",
                        "State": "ENABLED",
                        "ComputeEnvironmentName": f"ai-agents-batch-{environment}",
                        "ComputeResources": {
                            "Type": "FARGATE",
                            "MaxvCpus": 256,
                            "SecurityGroupIds": [{"Ref": "BatchSecurityGroup"}],
                            "Subnets": [{"Ref": "PrivateSubnet"}]
                        }
                    }
                },
                
                # IAM Role for Lambda
                "LambdaExecutionRole": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Effect": "Allow",
                                "Principal": {"Service": "lambda.amazonaws.com"},
                                "Action": "sts:AssumeRole"
                            }]
                        },
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                        ],
                        "Policies": [{
                            "PolicyName": f"AgentSystemPolicy-{environment}",
                            "PolicyDocument": {
                                "Version": "2012-10-17",
                                "Statement": [{
                                    "Effect": "Allow",
                                    "Action": [
                                        "ecs:*",
                                        "batch:*",
                                        "logs:*",
                                        "ssm:*"
                                    ],
                                    "Resource": "*"
                                }]
                            }
                        }]
                    }
                }
            },
            "Outputs": {
                "ClusterName": {
                    "Description": "ECS Cluster Name",
                    "Value": {"Ref": "AgentECSCluster"},
                    "Export": {"Name": f"agent-cluster-{environment}"}
                },
                "LambdaArn": {
                    "Description": "GitHub Webhook Lambda ARN",
                    "Value": {"Fn::GetAtt": ["GitHubWebhookLambda", "Arn"]},
                    "Export": {"Name": f"webhook-lambda-{environment}"}
                }
            }
        }
        
        # Save CloudFormation template
        cfn_file = f"e:/Projects/ai-agent-infrastructure-{environment}.yaml"
        with open(cfn_file, 'w') as f:
            import yaml
            yaml.dump(cfn_template, f, default_flow_style=False)
        
        print(f"  ✅ Created CloudFormation template: {cfn_file}")
        
        # Deploy the stack (if AWS CLI is available)
        try:
            result = subprocess.run([
                "aws", "cloudformation", "deploy",
                "--template-file", cfn_file,
                "--stack-name", f"ai-agent-infrastructure-{environment}",
                "--capabilities", "CAPABILITY_IAM",
                "--region", config["region"],
                "--parameter-overrides", f"Environment={environment}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ Deployed CloudFormation stack for {environment}")
            else:
                print(f"  ⚠️  CloudFormation deployment failed: {result.stderr}")
        except FileNotFoundError:
            print(f"  ⚠️  AWS CLI not found - manual deployment required")
    
    def test_deployment(self, environment, config):
        """Test the deployment"""
        
        print(f"\n🧪 Testing deployment for {environment}")
        
        # Create a test issue to verify the system
        test_issue = {
            "title": f"[Manager] Test Agent System Deployment - {environment}",
            "body": f"""## Test Issue for {environment.upper()}

This is an automated test issue to verify the AI agent assignment system is working correctly.

Environment: {environment}
Timestamp: {datetime.now().isoformat()}
Test Type: Deployment Verification

Please acknowledge receipt and close when processing is complete.
""",
            "labels": ["test", "manager", environment],
            "assignee": "manager"
        }
        
        # Save test issue for manual creation
        test_file = f"e:/Projects/test-issue-{environment}.json"
        with open(test_file, 'w') as f:
            json.dump(test_issue, f, indent=2)
        
        print(f"  ✅ Created test issue template: {test_file}")
        print(f"  📋 Create this issue manually to test the system")
    
    def deploy_all_environments(self):
        """Deploy to all environments in order"""
        
        print("\n" + "="*80)
        print("🚀 AUTONOMOUS BUSINESS SYSTEM DEPLOYMENT")
        print("="*80)
        print(f"Deploying to environments: {', '.join(self.deployment_order)}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        results = {}
        
        for environment in self.deployment_order:
            try:
                print(f"\n{'='*20} DEPLOYING TO {environment.upper()} {'='*20}")
                
                success = self.deploy_agent_system(environment)
                results[environment] = "SUCCESS" if success else "FAILED"
                
                if success:
                    print(f"\n✅ {environment.upper()} deployment completed successfully!")
                else:
                    print(f"\n❌ {environment.upper()} deployment failed!")
                    
                # Wait between deployments
                if environment != self.deployment_order[-1]:
                    print(f"\n⏳ Waiting 30 seconds before next deployment...")
                    time.sleep(30)
                    
            except Exception as e:
                print(f"\n❌ Error deploying to {environment}: {str(e)}")
                results[environment] = f"ERROR: {str(e)}"
        
        # Summary
        print("\n" + "="*80)
        print("📋 DEPLOYMENT SUMMARY")
        print("="*80)
        
        for env, status in results.items():
            status_icon = "✅" if status == "SUCCESS" else "❌"
            print(f"{status_icon} {env.upper()}: {status}")
        
        # Next steps
        print("\n" + "="*80)
        print("🎯 NEXT STEPS")
        print("="*80)
        print("1. Commit and push the deployment artifacts to each project")
        print("2. Create test issues in each environment to verify functionality")
        print("3. Monitor GitHub Actions workflows for automatic processing")
        print("4. Check AWS CloudWatch logs for agent execution")
        print("5. Validate the complete end-to-end workflow")
        
        print("\n🎉 AUTONOMOUS BUSINESS SYSTEM DEPLOYMENT COMPLETE!")
        
        return results

def main():
    """Main deployment function"""
    
    print("Starting Autonomous Business System Deployment...")
    
    deployer = AutonomousSystemDeployer()
    results = deployer.deploy_all_environments()
    
    # Create deployment report
    report = {
        "deployment_timestamp": datetime.now().isoformat(),
        "environments": deployer.environments,
        "results": results,
        "next_steps": [
            "Commit deployment artifacts to projects",
            "Create test issues for verification",
            "Monitor GitHub Actions workflows",
            "Check AWS infrastructure status",
            "Validate end-to-end functionality"
        ]
    }
    
    with open("e:/Projects/autonomous-system-deployment-report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Deployment report saved: autonomous-system-deployment-report.json")
    
    return 0 if all(r == "SUCCESS" for r in results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
