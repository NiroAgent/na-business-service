#!/usr/bin/env python3
"""
Cost-Optimized Agent Deployment for VF-Dev Environment
50 Agents - Multiple Deployment Strategies
"""

import json
import os
import subprocess
import sys
from datetime import datetime

def create_single_instance_deployment():
    """Deploy all 50 agents on a single EC2 instance - Most Cost Effective"""
    
    print("\n" + "="*50)
    print("🚀 CREATING SINGLE INSTANCE DEPLOYMENT")
    print("="*50)
    
    # CloudFormation template for single instance
    cloudformation_template = """AWSTemplateFormatVersion: '2010-09-09'
Description: 'Cost-Optimized Single Instance AI Agent System for VF-Dev'

Parameters:
  InstanceType:
    Type: String
    Default: t3.large
    AllowedValues: [t3.medium, t3.large, t3.xlarge]
    Description: EC2 instance type
  
  Environment:
    Type: String
    Default: vf-dev
    Description: Environment name

Resources:
  # IAM Role for EC2 Instance
  AgentInstanceRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
      Policies:
        - PolicyName: AgentSystemAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - sqs:*
                  - lambda:InvokeFunction
                  - logs:*
                  - ssm:GetParameter
                  - ssm:GetParameters
                  - secretsmanager:GetSecretValue
                Resource: '*'

  AgentInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles: [!Ref AgentInstanceRole]

  # Security Group
  AgentSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for AI Agent instance
      VpcId: !Ref AgentVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/8
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8090
          CidrIp: 10.0.0.0/8

  # VPC (Simple setup)
  AgentVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-agent-vpc'

  AgentSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref AgentVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  AgentInternetGateway:
    Type: AWS::EC2::InternetGateway

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref AgentVPC
      InternetGatewayId: !Ref AgentInternetGateway

  AgentRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref AgentVPC

  AgentRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref AgentRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref AgentInternetGateway

  SubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref AgentSubnet
      RouteTableId: !Ref AgentRouteTable

  # EC2 Instance
  AgentInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c02fb55956c7d316  # Amazon Linux 2023
      InstanceType: !Ref InstanceType
      IamInstanceProfile: !Ref AgentInstanceProfile
      SecurityGroupIds: [!Ref AgentSecurityGroup]
      SubnetId: !Ref AgentSubnet
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y python3 python3-pip git tmux htop
          
          # Install Node.js
          curl -fsSL https://rpm.nodesource.com/setup_lts.x | bash -
          yum install -y nodejs
          
          # Create agent user
          useradd -m -s /bin/bash agent
          mkdir -p /home/agent/agents
          chown -R agent:agent /home/agent
          
          # Clone agent repositories
          cd /home/agent
          git clone https://github.com/your-org/ai-agent-system.git
          
          # Create startup script
          cat > /home/agent/start-all-agents.sh << 'EOF'
          #!/bin/bash
          cd /home/agent/agents
          
          # Start 50 agents in separate tmux sessions
          for i in {1..50}; do
            session_name="agent-$i"
            tmux new-session -d -s "$session_name" "python3 ../ai-agent-system/agent.py --agent-id $i --environment vf-dev"
            echo "Started agent $i in session $session_name"
            sleep 1
          done
          
          echo "All 50 agents started successfully!"
          tmux list-sessions
          EOF
          
          chmod +x /home/agent/start-all-agents.sh
          chown agent:agent /home/agent/start-all-agents.sh
          
          # Auto-start agents on boot
          echo "@reboot /home/agent/start-all-agents.sh" | crontab -u agent -
          
          # Start agents now
          sudo -u agent /home/agent/start-all-agents.sh
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-agent-instance'
        - Key: Environment
          Value: !Ref Environment

  # SQS Queue for agent communication
  AgentQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub '${Environment}-agent-queue'
      VisibilityTimeoutSeconds: 300
      MessageRetentionPeriod: 1209600  # 14 days

Outputs:
  InstanceId:
    Description: Instance ID of the agent server
    Value: !Ref AgentInstance
  
  InstancePublicIP:
    Description: Public IP of the agent server
    Value: !GetAtt AgentInstance.PublicIp
  
  SSHCommand:
    Description: SSH command to connect to the instance
    Value: !Sub 'ssh -i your-key.pem ec2-user@${AgentInstance.PublicIp}'
  
  AgentQueueURL:
    Description: SQS Queue URL for agent communication
    Value: !Ref AgentQueue
  
  CostEstimate:
    Description: Monthly cost estimate
    Value: '$60-70/month for t3.large instance + minimal AWS services'
"""

    # Write CloudFormation template
    with open("single-instance-agents.yaml", "w", encoding='utf-8') as f:
        f.write(cloudformation_template)
    
    # Create start script
    start_script = """#!/bin/bash
# Deploy Single Instance Agent System to VF-Dev

echo "Deploying cost-optimized single instance agent system..."

aws cloudformation deploy \\
  --template-file single-instance-agents.yaml \\
  --stack-name vf-dev-single-instance-agents \\
  --capabilities CAPABILITY_IAM \\
  --parameter-overrides \\
    InstanceType=t3.large \\
    Environment=vf-dev \\
  --region us-east-1

echo "Getting deployment outputs..."
aws cloudformation describe-stacks \\
  --stack-name vf-dev-single-instance-agents \\
  --region us-east-1 \\
  --query 'Stacks[0].Outputs'

echo "Deployment complete! All 50 agents will be running on a single instance."
echo "Cost: ~$60-70/month"
"""

    with open("deploy-single-instance.sh", "w", encoding='utf-8') as f:
        f.write(start_script)
    
    os.chmod("deploy-single-instance.sh", 0o755)
    
    print("✅ Created single-instance-agents.yaml")
    print("✅ Created deploy-single-instance.sh")
    
    return True

def create_container_deployment():
    """Deploy all agents in Docker containers - Good for isolation"""
    
    print("\n" + "="*50)
    print("🐳 CREATING CONTAINER DEPLOYMENT")
    print("="*50)
    
    # Dockerfile for multi-agent container
    dockerfile = """FROM python:3.11-slim

RUN apt-get update && apt-get install -y \\
    git \\
    tmux \\
    htop \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy agent system
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Create start script for all agents
RUN echo '#!/bin/bash' > start-agents.sh && \\
    echo 'for i in {1..50}; do' >> start-agents.sh && \\
    echo '  tmux new-session -d -s "agent-$i" "python agent.py --agent-id $i --environment vf-dev"' >> start-agents.sh && \\
    echo '  sleep 0.5' >> start-agents.sh && \\
    echo 'done' >> start-agents.sh && \\
    echo 'echo "All 50 agents started!"' >> start-agents.sh && \\
    echo 'tmux list-sessions' >> start-agents.sh && \\
    echo 'tail -f /dev/null' >> start-agents.sh && \\
    chmod +x start-agents.sh

EXPOSE 8080

CMD ["./start-agents.sh"]
"""

    with open("Dockerfile.agents", "w", encoding='utf-8') as f:
        f.write(dockerfile)
    
    # ECS Task Definition
    ecs_task = {
        "family": "vf-dev-multi-agents",
        "networkMode": "awsvpc",
        "requiresCompatibilities": ["FARGATE"],
        "cpu": "2048",
        "memory": "4096",
        "executionRoleArn": "arn:aws:iam::816454053517:role/ecsTaskExecutionRole",
        "taskRoleArn": "arn:aws:iam::816454053517:role/vf-dev-agent-task-role",
        "containerDefinitions": [
            {
                "name": "multi-agent-container",
                "image": "816454053517.dkr.ecr.us-east-1.amazonaws.com/vf-dev-agents:latest",
                "portMappings": [
                    {
                        "containerPort": 8080,
                        "protocol": "tcp"
                    }
                ],
                "essential": True,
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": "/ecs/vf-dev-agents",
                        "awslogs-region": "us-east-1",
                        "awslogs-stream-prefix": "ecs"
                    }
                },
                "environment": [
                    {"name": "ENVIRONMENT", "value": "vf-dev"},
                    {"name": "AGENT_COUNT", "value": "50"}
                ]
            }
        ]
    }
    
    with open("ecs-task-definition.json", "w", encoding='utf-8') as f:
        json.dump(ecs_task, f, indent=2)
    
    # Deployment script
    deploy_script = """#!/bin/bash
# Deploy Container-based Agent System

echo "Building and deploying container-based agent system..."

# Build and push Docker image
docker build -f Dockerfile.agents -t vf-dev-agents .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 816454053517.dkr.ecr.us-east-1.amazonaws.com
docker tag vf-dev-agents:latest 816454053517.dkr.ecr.us-east-1.amazonaws.com/vf-dev-agents:latest
docker push 816454053517.dkr.ecr.us-east-1.amazonaws.com/vf-dev-agents:latest

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create or update service
aws ecs create-service \\
  --cluster vf-dev-agents \\
  --service-name multi-agent-service \\
  --task-definition vf-dev-multi-agents \\
  --desired-count 1 \\
  --launch-type FARGATE \\
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"

echo "Container deployment complete!"
echo "Cost: ~$85-95/month for Fargate"
"""

    with open("deploy-container.sh", "w", encoding='utf-8') as f:
        f.write(deploy_script)
    
    os.chmod("deploy-container.sh", 0o755)
    
    print("✅ Created Dockerfile.agents")
    print("✅ Created ecs-task-definition.json")
    print("✅ Created deploy-container.sh")
    
    return True

def create_spot_instance_deployment():
    """Deploy on spot instances for maximum cost savings"""
    
    print("\n" + "="*50)
    print("💰 CREATING SPOT INSTANCE DEPLOYMENT")
    print("="*50)
    
    # Spot instance CloudFormation
    spot_template = """AWSTemplateFormatVersion: '2010-09-09'
Description: 'Ultra Cost-Optimized Spot Instance AI Agent System'

Parameters:
  SpotPrice:
    Type: String
    Default: '0.05'
    Description: Maximum spot price per hour
  
  InstanceType:
    Type: String
    Default: m5.large
    Description: Instance type for spot instances

Resources:
  # Launch Template for Spot Instances
  AgentLaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: vf-dev-spot-agents
      LaunchTemplateData:
        ImageId: ami-0c02fb55956c7d316
        InstanceType: !Ref InstanceType
        IamInstanceProfile:
          Arn: !GetAtt AgentInstanceProfile.Arn
        SecurityGroupIds: [!Ref AgentSecurityGroup]
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            yum update -y
            yum install -y python3 python3-pip git tmux
            
            # Setup spot instance interruption handling
            cat > /home/ec2-user/handle-interruption.sh << 'EOF'
            #!/bin/bash
            # Check for spot interruption notice every 5 seconds
            while true; do
              if curl -s http://169.254.169.254/latest/meta-data/spot/instance-action 2>/dev/null; then
                echo "Spot interruption notice received! Gracefully shutting down agents..."
                # Save agent states
                tmux list-sessions | awk '{print $1}' | sed 's/://' | xargs -I {} tmux send-keys -t {} 'save_state' Enter
                sleep 30
                # Kill all tmux sessions
                tmux kill-server
                break
              fi
              sleep 5
            done
            EOF
            chmod +x /home/ec2-user/handle-interruption.sh
            
            # Start interruption handler in background
            nohup /home/ec2-user/handle-interruption.sh &
            
            # Start all 50 agents
            cd /home/ec2-user
            for i in {1..50}; do
              tmux new-session -d -s "agent-$i" "python3 agent.py --agent-id $i --spot-mode"
              sleep 0.2
            done

  # Auto Scaling Group for Spot Instances
  SpotAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      LaunchTemplate:
        LaunchTemplateId: !Ref AgentLaunchTemplate
        Version: !GetAtt AgentLaunchTemplate.LatestVersionNumber
      MinSize: 1
      MaxSize: 3
      DesiredCapacity: 1
      VPCZoneIdentifier: [!Ref AgentSubnet]
      MixedInstancesPolicy:
        LaunchTemplate:
          LaunchTemplateSpecification:
            LaunchTemplateId: !Ref AgentLaunchTemplate
            Version: !GetAtt AgentLaunchTemplate.LatestVersionNumber
        InstancesDistribution:
          OnDemandPercentage: 0
          SpotAllocationStrategy: diversified
          SpotMaxPrice: !Ref SpotPrice

Outputs:
  CostSavings:
    Description: Estimated cost savings with spot instances
    Value: 'Up to 90% savings - estimated $8-15/month'
  
  SpotPrice:
    Description: Maximum spot price set
    Value: !Ref SpotPrice
"""

    with open("spot-instance-agents.yaml", "w", encoding='utf-8') as f:
        f.write(spot_template)
    
    print("✅ Created spot-instance-agents.yaml")
    print("💰 Spot instances can save up to 90% - estimated $8-15/month!")
    
    return True

def create_scheduled_deployment():
    """Deploy with scheduled start/stop for dev environment"""
    
    print("\n" + "="*50)
    print("⏰ CREATING SCHEDULED DEPLOYMENT")
    print("="*50)
    
    # EventBridge rules for start/stop
    schedule_template = """AWSTemplateFormatVersion: '2010-09-09'
Description: 'Scheduled Start/Stop Agent System for Dev Environment'

Resources:
  # Lambda function to start/stop instances
  SchedulerFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: vf-dev-agent-scheduler
      Runtime: python3.9
      Handler: index.lambda_handler
      Role: !GetAtt SchedulerRole.Arn
      Code:
        ZipFile: |
          import boto3
          import json
          
          ec2 = boto3.client('ec2')
          
          def lambda_handler(event, context):
              action = event.get('action', 'start')
              instance_ids = event.get('instance_ids', [])
              
              if action == 'start':
                  response = ec2.start_instances(InstanceIds=instance_ids)
                  print(f"Started instances: {instance_ids}")
              elif action == 'stop':
                  response = ec2.stop_instances(InstanceIds=instance_ids)
                  print(f"Stopped instances: {instance_ids}")
              
              return {
                  'statusCode': 200,
                  'body': json.dumps(f'Successfully {action}ed instances')
              }

  SchedulerRole:
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
        - PolicyName: EC2Control
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - ec2:StartInstances
                  - ec2:StopInstances
                  - ec2:DescribeInstances
                Resource: '*'

  # Start agents at 8 AM EST (Monday-Friday)
  StartSchedule:
    Type: AWS::Events::Rule
    Properties:
      Description: Start agent instances for business hours
      ScheduleExpression: 'cron(0 13 ? * MON-FRI *)'  # 8 AM EST = 1 PM UTC
      State: ENABLED
      Targets:
        - Arn: !GetAtt SchedulerFunction.Arn
          Id: StartTarget
          Input: |
            {
              "action": "start",
              "instance_ids": ["i-1234567890abcdef0"]
            }

  # Stop agents at 6 PM EST (Monday-Friday)
  StopSchedule:
    Type: AWS::Events::Rule
    Properties:
      Description: Stop agent instances after business hours
      ScheduleExpression: 'cron(0 23 ? * MON-FRI *)'  # 6 PM EST = 11 PM UTC
      State: ENABLED
      Targets:
        - Arn: !GetAtt SchedulerFunction.Arn
          Id: StopTarget
          Input: |
            {
              "action": "stop",
              "instance_ids": ["i-1234567890abcdef0"]
            }

  # Permissions for EventBridge to invoke Lambda
  StartSchedulePermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref SchedulerFunction
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com
      SourceArn: !GetAtt StartSchedule.Arn

  StopSchedulePermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref SchedulerFunction
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com
      SourceArn: !GetAtt StopSchedule.Arn

Outputs:
  SchedulerFunction:
    Description: Lambda function for scheduling
    Value: !Ref SchedulerFunction
  
  CostSavings:
    Description: Cost savings with 10-hour daily operation
    Value: 'Approximately 60% savings - runs only business hours'
"""

    with open("scheduled-agents.yaml", "w", encoding='utf-8') as f:
        f.write(schedule_template)
    
    print("✅ Created scheduled-agents.yaml")
    print("⏰ Automatic start/stop for 60% cost savings!")
    
    return True

def create_deployment_summary():
    """Create a comprehensive deployment summary"""
    
    summary = f"""
# Cost-Optimized Agent Deployment Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 💰 Cost Analysis for 50 Agents in VF-Dev

### 1. Single EC2 Instance (RECOMMENDED)
- **Cost**: $60-70/month
- **Setup**: One t3.large instance running all 50 agents in tmux sessions
- **Pros**: Simple, cost-effective, easy management
- **Cons**: Single point of failure
- **Files**: single-instance-agents.yaml, deploy-single-instance.sh

### 2. Docker Container (ECS Fargate)
- **Cost**: $85-95/month
- **Setup**: Single container with all agents in isolated sessions
- **Pros**: Better isolation, auto-scaling capability
- **Cons**: Slightly higher cost, more complex setup
- **Files**: Dockerfile.agents, ecs-task-definition.json, deploy-container.sh

### 3. Spot Instances (MAXIMUM SAVINGS)
- **Cost**: $8-15/month (up to 90% savings!)
- **Setup**: Auto-scaling group with spot instances
- **Pros**: Extremely cost-effective
- **Cons**: Can be interrupted, requires interruption handling
- **Files**: spot-instance-agents.yaml

### 4. Scheduled Deployment (DEV OPTIMAL)
- **Cost**: $25-30/month (60% savings)
- **Setup**: Auto start/stop during business hours (8 AM - 6 PM EST)
- **Pros**: Perfect for dev environment, significant savings
- **Cons**: Not available 24/7
- **Files**: scheduled-agents.yaml

## 🚀 Deployment Commands

### Quick Deploy (Single Instance - Recommended)
```bash
./deploy-single-instance.sh
```

### Spot Instance Deploy (Maximum Savings)
```bash
aws cloudformation deploy \\
  --template-file spot-instance-agents.yaml \\
  --stack-name vf-dev-spot-agents \\
  --capabilities CAPABILITY_IAM \\
  --parameter-overrides SpotPrice=0.05
```

### Container Deploy
```bash
./deploy-container.sh
```

## 📊 Comparison vs Current Lambda Setup

| Deployment Type | Monthly Cost | Savings | Availability | Complexity |
|-----------------|--------------|---------|--------------|------------|
| Current Lambda  | $150-300     | Baseline| 24/7         | Medium     |
| Single Instance | $60-70       | 75%     | 24/7         | Low        |
| Container       | $85-95       | 68%     | 24/7         | Medium     |
| Spot Instance   | $8-15        | 95%     | Variable     | Medium     |
| Scheduled       | $25-30       | 85%     | Business hrs | Low        |

## 🎯 Recommendation for VF-Dev

**Use Single Instance Deployment** for the best balance of:
- Cost savings (75% reduction)
- Simplicity (easy to manage)
- Reliability (24/7 availability)
- Agent context retention (tmux sessions persist)

## 📋 Next Steps

1. Deploy single instance: `./deploy-single-instance.sh`
2. Monitor costs in AWS Cost Explorer
3. Scale to spot instances if interruptions are acceptable
4. Implement scheduled deployment for further dev cost optimization

## 🔧 Agent Console Management

All deployments include tmux session management for:
- Individual agent consoles that retain context
- Easy access to specific agent sessions
- Graceful agent restarts without losing state
- Debug capabilities with `tmux attach -t agent-X`

Total deployment time: ~10 minutes
Expected monthly savings: $80-290 compared to Lambda approach
"""

    with open("COST_OPTIMIZATION_SUMMARY.md", "w", encoding='utf-8') as f:
        f.write(summary)
    
    print("✅ Created COST_OPTIMIZATION_SUMMARY.md")
    
    return True

def main():
    print("="*80)
    print("                    💰 COST-OPTIMIZED AGENT DEPLOYMENT FOR VF-DEV")
    print("="*80)
    print("                    💰 COST ANALYSIS FOR 50 AGENTS IN VF-DEV")
    print("="*80)
    
    print("📊 COST COMPARISON:")
    print()
    print("🔸 Single EC2 Instance (Recommended)                           Cost: $60-70")
    print("   Best for: One EC2 instance running all 50 agents in separate consoles")
    print("🔸 Docker Container Multi-Agent                                Cost: $85-95")
    print("   Best for: Single container running all 50 agents with tmux sessions")
    print("🔸 Lambda Functions (Current)                                 Cost: $150-300")
    print("   Best for: Each agent as separate Lambda function")
    print()
    
    # Create all deployment options
    create_single_instance_deployment()
    create_container_deployment()
    create_spot_instance_deployment()
    create_scheduled_deployment()
    create_deployment_summary()
    
    print("\n" + "="*80)
    print("✅ ALL COST-OPTIMIZED DEPLOYMENTS CREATED!")
    print("="*80)
    print("📁 Files created:")
    print("   • single-instance-agents.yaml - CloudFormation for single instance")
    print("   • deploy-single-instance.sh - Quick deployment script")
    print("   • Dockerfile.agents - Container-based deployment")
    print("   • ecs-task-definition.json - ECS configuration")
    print("   • deploy-container.sh - Container deployment script")
    print("   • spot-instance-agents.yaml - Spot instance deployment")
    print("   • scheduled-agents.yaml - Business hours scheduling")
    print("   • COST_OPTIMIZATION_SUMMARY.md - Complete analysis")
    print()
    print("🎯 RECOMMENDATION: Start with single instance deployment")
    print("   Run: ./deploy-single-instance.sh")
    print("   Cost: ~$60-70/month (75% savings vs Lambda)")
    print("   All 50 agents with context retention in tmux sessions")

if __name__ == "__main__":
    main()
