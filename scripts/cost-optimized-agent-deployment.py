#!/usr/bin/env python3
"""
Cost-Optimized Agent Deployment for VF-Dev
==========================================
Multiple deployment strategies for running 50 agents cost-effectively
"""

import json
from datetime import datetime

def calculate_deployment_costs():
    """Calculate costs for different deployment strategies"""
    
    print("💰 COST ANALYSIS FOR 50 AGENTS IN VF-DEV")
    print("="*60)
    
    strategies = {
        "strategy_1": {
            "name": "Single EC2 Instance (Recommended)",
            "description": "One EC2 instance running all 50 agents in separate consoles",
            "specs": {
                "instance_type": "t3.large",  # 2 vCPU, 8GB RAM
                "vcpu": 2,
                "memory_gb": 8,
                "storage_gb": 50,
                "estimated_monthly_cost": "$60-70",
                "on_demand_hourly": "$0.0832",
                "spot_pricing": "$0.025-0.040"
            },
            "pros": [
                "Lowest cost option",
                "Agents retain context between runs",
                "Easy debugging - each agent has own console",
                "Can use spot instances for 70% savings",
                "Auto start/stop for development hours only"
            ],
            "cons": [
                "Single point of failure",
                "Manual scaling"
            ]
        },
        
        "strategy_2": {
            "name": "Docker Container Multi-Agent",
            "description": "Single container running all 50 agents with tmux sessions",
            "specs": {
                "container_platform": "ECS Fargate",
                "vcpu": "2",
                "memory_gb": "8",
                "estimated_monthly_cost": "$85-95",
                "per_hour_cost": "$0.12"
            },
            "pros": [
                "Containerized and portable",
                "Easy deployment via pipeline",
                "Can use tmux/screen for persistent sessions",
                "Automatic restarts"
            ],
            "cons": [
                "Slightly higher cost than EC2",
                "Context might be lost on container restart"
            ]
        },
        
        "strategy_3": {
            "name": "Lambda Functions (Current)",
            "description": "Each agent as separate Lambda function",
            "specs": {
                "functions": 50,
                "memory_mb": 512,
                "estimated_monthly_cost": "$150-300",
                "per_invocation": "$0.0000002",
                "cold_start_delay": "1-5 seconds"
            },
            "pros": [
                "True serverless",
                "Pay per execution",
                "Auto-scaling"
            ],
            "cons": [
                "Higher cost for frequent use",
                "No context retention",
                "Cold start delays"
            ]
        }
    }
    
    print("\n📊 COST COMPARISON:")
    for key, strategy in strategies.items():
        print(f"\n🔸 {strategy['name']}")
        print(f"   Cost: {strategy['specs']['estimated_monthly_cost']}")
        print(f"   Best for: {strategy['description']}")
    
    return strategies

def create_single_instance_deployment():
    """Create deployment for single EC2 instance with all agents"""
    
    print("\n🚀 CREATING SINGLE INSTANCE DEPLOYMENT")
    print("="*50)
    
    # CloudFormation template for single instance
    cfn_template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Single EC2 Instance for 50 AI Agents - Cost Optimized",
        
        "Parameters": {
            "Environment": {
                "Type": "String",
                "Default": "vf-dev",
                "Description": "Environment name"
            },
            "InstanceType": {
                "Type": "String", 
                "Default": "t3.large",
                "AllowedValues": ["t3.medium", "t3.large", "t3.xlarge"],
                "Description": "EC2 instance type"
            },
            "UseSpotInstance": {
                "Type": "String",
                "Default": "true",
                "AllowedValues": ["true", "false"],
                "Description": "Use spot instance for cost savings"
            }
        },
        
        "Conditions": {
            "UseSpot": {"Fn::Equals": [{"Ref": "UseSpotInstance"}, "true"]}
        },
        
        "Resources": {
            # EC2 Instance for all agents
            "AgentMasterInstance": {
                "Type": "AWS::EC2::Instance",
                "Properties": {
                    "ImageId": "ami-0c02fb55956c7d316",  # Amazon Linux 2
                    "InstanceType": {"Ref": "InstanceType"},
                    "SecurityGroupIds": [{"Ref": "AgentSecurityGroup"}],
                    "SubnetId": {"Ref": "PublicSubnet"},
                    "IamInstanceProfile": {"Ref": "AgentInstanceProfile"},
                    "UserData": {"Fn::Base64": {"Fn::Sub": '''#!/bin/bash
yum update -y
yum install -y python3 python3-pip git tmux htop

# Install Python dependencies
pip3 install boto3 requests flask psutil

# Clone agent repository
cd /home/ec2-user
git clone https://github.com/NiroAgentV2/autonomous-business-system.git
cd autonomous-business-system

# Create agent launcher script
cat > launch-all-agents.sh << 'EOF'
#!/bin/bash
echo "🚀 LAUNCHING 50 AI AGENTS IN DEVELOPMENT MODE"
echo "============================================="

# Agent types and counts
declare -A AGENTS=(
    ["manager"]=5
    ["developer"]=15
    ["qa"]=10
    ["devops"]=5
    ["architect"]=3
    ["pm"]=4
    ["security"]=2
    ["analytics"]=3
    ["support"]=3
)

AGENT_ID=1

for agent_type in "${!AGENTS[@]}"; do
    count=${AGENTS[$agent_type]}
    echo "Starting $count $agent_type agents..."
    
    for ((i=1; i<=count; i++)); do
        session_name="agent-${agent_type}-${i}"
        
        tmux new-session -d -s "$session_name" "python3 ai-${agent_type}-agent.py --agent-id $AGENT_ID --dev-mode"
        echo "  ✅ Started $session_name (Agent ID: $AGENT_ID)"
        
        ((AGENT_ID++))
        sleep 1
    done
done

echo ""
echo "📋 AGENT STATUS:"
tmux list-sessions
echo ""
echo "🔧 MANAGEMENT COMMANDS:"
echo "  tmux list-sessions              - List all agent sessions"
echo "  tmux attach -t agent-manager-1  - Connect to agent console"
echo "  tmux kill-session -t SESSION    - Stop specific agent"
echo "  ./stop-all-agents.sh            - Stop all agents"
echo ""
echo "🌐 DASHBOARD: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
EOF

chmod +x launch-all-agents.sh

# Create stop script
cat > stop-all-agents.sh << 'EOF'
#!/bin/bash
echo "🛑 STOPPING ALL AI AGENTS"
tmux list-sessions | cut -d: -f1 | grep "agent-" | xargs -I {} tmux kill-session -t {}
echo "✅ All agents stopped"
EOF

chmod +x stop-all-agents.sh

# Create monitoring script
cat > monitor-agents.sh << 'EOF'
#!/bin/bash
while true; do
    clear
    echo "🤖 AI AGENT MONITORING DASHBOARD - $(date)"
    echo "============================================="
    echo ""
    
    echo "📊 SYSTEM RESOURCES:"
    echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
    echo ""
    
    echo "🔧 ACTIVE AGENT SESSIONS:"
    tmux list-sessions 2>/dev/null | grep "agent-" | wc -l
    echo ""
    
    echo "📋 AGENT SESSIONS:"
    tmux list-sessions 2>/dev/null | grep "agent-" | head -10
    
    if [ $(tmux list-sessions 2>/dev/null | grep "agent-" | wc -l) -gt 10 ]; then
        echo "... and $(( $(tmux list-sessions 2>/dev/null | grep "agent-" | wc -l) - 10 )) more"
    fi
    
    echo ""
    echo "Press Ctrl+C to exit monitoring"
    sleep 5
done
EOF

chmod +x monitor-agents.sh

# Start dashboard
python3 -m flask run --host=0.0.0.0 --port=5000 &

# Auto-start agents on boot
echo "@reboot cd /home/ec2-user/autonomous-business-system && ./launch-all-agents.sh" | crontab -
'''
                    }},
                    "Tags": [
                        {"Key": "Name", "Value": {"Fn::Sub": "ai-agents-master-${Environment}"}},
                        {"Key": "Environment", "Value": {"Ref": "Environment"}},
                        {"Key": "Purpose", "Value": "AI Agent Development"}
                    ]
                }
            },
            
            # Spot Instance Request (conditional)
            "SpotInstanceRequest": {
                "Type": "AWS::EC2::SpotInstanceRequest",
                "Condition": "UseSpot",
                "Properties": {
                    "SpotPrice": "0.050",
                    "LaunchSpecification": {
                        "ImageId": "ami-0c02fb55956c7d316",
                        "InstanceType": {"Ref": "InstanceType"},
                        "SecurityGroupIds": [{"Ref": "AgentSecurityGroup"}],
                        "SubnetId": {"Ref": "PublicSubnet"},
                        "IamInstanceProfile": {"Ref": "AgentInstanceProfile"},
                        "UserData": {"Fn::GetAtt": ["AgentMasterInstance", "UserData"]}
                    }
                }
            },
            
            # Security Group
            "AgentSecurityGroup": {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": "Security group for AI agents",
                    "VpcId": {"Ref": "VPC"},
                    "SecurityGroupIngress": [
                        {
                            "IpProtocol": "tcp",
                            "FromPort": 22,
                            "ToPort": 22,
                            "CidrIp": "0.0.0.0/0",
                            "Description": "SSH access"
                        },
                        {
                            "IpProtocol": "tcp", 
                            "FromPort": 5000,
                            "ToPort": 5000,
                            "CidrIp": "0.0.0.0/0",
                            "Description": "Dashboard access"
                        }
                    ]
                }
            },
            
            # IAM Role for agents
            "AgentRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Effect": "Allow",
                            "Principal": {"Service": "ec2.amazonaws.com"},
                            "Action": "sts:AssumeRole"
                        }]
                    },
                    "ManagedPolicyArns": [
                        "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
                    ],
                    "Policies": [{
                        "PolicyName": "AgentPermissions",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Effect": "Allow",
                                "Action": [
                                    "logs:*",
                                    "cloudwatch:*",
                                    "ssm:*",
                                    "s3:GetObject",
                                    "s3:PutObject"
                                ],
                                "Resource": "*"
                            }]
                        }
                    }]
                }
            },
            
            "AgentInstanceProfile": {
                "Type": "AWS::IAM::InstanceProfile",
                "Properties": {
                    "Roles": [{"Ref": "AgentRole"}]
                }
            },
            
            # Basic VPC setup
            "VPC": {
                "Type": "AWS::EC2::VPC",
                "Properties": {
                    "CidrBlock": "10.0.0.0/16",
                    "EnableDnsHostnames": True,
                    "EnableDnsSupport": True
                }
            },
            
            "PublicSubnet": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "CidrBlock": "10.0.1.0/24",
                    "MapPublicIpOnLaunch": True,
                    "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]}
                }
            },
            
            "InternetGateway": {
                "Type": "AWS::EC2::InternetGateway"
            },
            
            "AttachGateway": {
                "Type": "AWS::EC2::VPCGatewayAttachment",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "InternetGatewayId": {"Ref": "InternetGateway"}
                }
            }
        },
        
        "Outputs": {
            "InstanceId": {
                "Description": "EC2 Instance ID",
                "Value": {"Ref": "AgentMasterInstance"},
                "Export": {"Name": {"Fn::Sub": "agent-instance-${Environment}"}}
            },
            "PublicIP": {
                "Description": "Public IP Address",
                "Value": {"Fn::GetAtt": ["AgentMasterInstance", "PublicIp"]},
                "Export": {"Name": {"Fn::Sub": "agent-instance-ip-${Environment}"}}
            },
            "DashboardURL": {
                "Description": "Agent Dashboard URL",
                "Value": {"Fn::Sub": "http://${AgentMasterInstance.PublicIp}:5000"},
                "Export": {"Name": {"Fn::Sub": "agent-dashboard-${Environment}"}}
            },
            "SSHCommand": {
                "Description": "SSH Command",
                "Value": {"Fn::Sub": "ssh -i your-key.pem ec2-user@${AgentMasterInstance.PublicIp}"},
                "Export": {"Name": {"Fn::Sub": "agent-ssh-${Environment}"}}
            }
        }
    }
    
    # Save template
    with open("single-instance-agents.yaml", "w") as f:
        import yaml
        yaml.dump(cfn_template, f, default_flow_style=False)
    
    print("✅ Created single-instance-agents.yaml")
    
    return cfn_template

def create_container_deployment():
    """Create multi-agent container deployment"""
    
    print("\n🐳 CREATING CONTAINER DEPLOYMENT")
    print("="*50)
    
    # Docker Compose for all agents
    docker_compose = {
        "version": "3.8",
        "services": {
            "ai-agents-master": {
                "build": {
                    "context": ".",
                    "dockerfile": "Dockerfile.multi-agent"
                },
                "container_name": "ai-agents-dev",
                "environment": [
                    "ENVIRONMENT=vf-dev",
                    "AGENT_COUNT=50",
                    "AWS_REGION=us-east-1"
                ],
                "ports": [
                    "5000:5000",  # Dashboard
                    "8080:8080"   # Agent API
                ],
                "volumes": [
                    "./logs:/app/logs",
                    "./data:/app/data"
                ],
                "restart": "unless-stopped",
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", "http://localhost:5000/health"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            }
        },
        "volumes": {
            "agent_data": None,
            "agent_logs": None
        }
    }
    
    # Dockerfile for multi-agent container
    dockerfile = '''FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    tmux \\
    htop \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy agent code
COPY . .

# Create startup script
RUN cat > start-all-agents.sh << 'EOF'
#!/bin/bash
echo "🚀 STARTING 50 AI AGENTS IN CONTAINER"
echo "====================================="

# Start tmux server
tmux new-session -d -s main

# Agent types and counts
declare -A AGENTS=(
    ["manager"]=5
    ["developer"]=15
    ["qa"]=10
    ["devops"]=5
    ["architect"]=3
    ["pm"]=4
    ["security"]=2
    ["analytics"]=3
    ["support"]=3
)

AGENT_ID=1

for agent_type in "${!AGENTS[@]}"; do
    count=${AGENTS[$agent_type]}
    echo "Starting $count $agent_type agents..."
    
    for ((i=1; i<=count; i++)); do
        session_name="agent-${agent_type}-${i}"
        
        tmux new-session -d -s "$session_name" \\
            "python3 ai-${agent_type}-agent.py --agent-id $AGENT_ID --container-mode"
        
        echo "  ✅ Started $session_name (Agent ID: $AGENT_ID)"
        ((AGENT_ID++))
        sleep 0.5
    done
done

# Start dashboard
python3 dashboard.py &

# Keep container running
tail -f /dev/null
EOF

RUN chmod +x start-all-agents.sh

# Expose ports
EXPOSE 5000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:5000/health || exit 1

# Start all agents
CMD ["./start-all-agents.sh"]
'''
    
    # Save files
    with open("docker-compose-agents.yml", "w") as f:
        import yaml
        yaml.dump(docker_compose, f, default_flow_style=False)
    
    with open("Dockerfile.multi-agent", "w") as f:
        f.write(dockerfile)
    
    print("✅ Created docker-compose-agents.yml")
    print("✅ Created Dockerfile.multi-agent")

def create_deployment_scripts():
    """Create deployment scripts for both strategies"""
    
    print("\n📜 CREATING DEPLOYMENT SCRIPTS")
    print("="*50)
    
    # EC2 deployment script
    ec2_script = '''#!/bin/bash
echo "🚀 DEPLOYING SINGLE INSTANCE FOR 50 AI AGENTS"
echo "=============================================="

# Deploy CloudFormation stack
aws cloudformation deploy \\
    --template-file single-instance-agents.yaml \\
    --stack-name ai-agents-vf-dev \\
    --capabilities CAPABILITY_IAM \\
    --region us-east-1 \\
    --parameter-overrides \\
        Environment=vf-dev \\
        InstanceType=t3.large \\
        UseSpotInstance=true

# Get outputs
INSTANCE_IP=$(aws cloudformation describe-stacks \\
    --stack-name ai-agents-vf-dev \\
    --region us-east-1 \\
    --query "Stacks[0].Outputs[?OutputKey=='PublicIP'].OutputValue" \\
    --output text)

DASHBOARD_URL=$(aws cloudformation describe-stacks \\
    --stack-name ai-agents-vf-dev \\
    --region us-east-1 \\
    --query "Stacks[0].Outputs[?OutputKey=='DashboardURL'].OutputValue" \\
    --output text)

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "📋 Instance IP: $INSTANCE_IP"
echo "🌐 Dashboard: $DASHBOARD_URL"
echo ""
echo "🔧 MANAGEMENT COMMANDS:"
echo "  ssh -i your-key.pem ec2-user@$INSTANCE_IP"
echo "  # Inside instance:"
echo "  ./launch-all-agents.sh    # Start all 50 agents"
echo "  ./monitor-agents.sh       # Monitor agent status"
echo "  tmux list-sessions        # List all agent sessions"
echo ""
echo "💰 ESTIMATED COST: $2-3/day (with spot instances)"
'''
    
    # Container deployment script
    container_script = '''#!/bin/bash
echo "🐳 DEPLOYING CONTAINER FOR 50 AI AGENTS"
echo "========================================"

# Build and start container
docker-compose -f docker-compose-agents.yml up -d --build

# Wait for startup
echo "⏳ Waiting for agents to start..."
sleep 30

# Check status
docker-compose -f docker-compose-agents.yml ps

# Get container IP
CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ai-agents-dev)

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "🌐 Dashboard: http://localhost:5000"
echo "📋 Container IP: $CONTAINER_IP"
echo ""
echo "🔧 MANAGEMENT COMMANDS:"
echo "  docker exec -it ai-agents-dev bash              # Enter container"
echo "  docker exec -it ai-agents-dev tmux list-sessions # List agents"
echo "  docker-compose -f docker-compose-agents.yml logs # View logs"
echo "  docker-compose -f docker-compose-agents.yml down # Stop all"
echo ""
echo "💰 ESTIMATED COST: $3-4/day (local) or $85-95/month (ECS Fargate)"
'''
    
    # Save scripts
    with open("deploy-ec2-agents.sh", "w") as f:
        f.write(ec2_script)
    
    with open("deploy-container-agents.sh", "w") as f:
        f.write(container_script)
    
    # Make executable
    import os
    os.chmod("deploy-ec2-agents.sh", 0o755)
    os.chmod("deploy-container-agents.sh", 0o755)
    
    print("✅ Created deploy-ec2-agents.sh")
    print("✅ Created deploy-container-agents.sh")

def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("💰 COST-OPTIMIZED AGENT DEPLOYMENT FOR VF-DEV")
    print("="*70)
    
    # Calculate costs
    strategies = calculate_deployment_costs()
    
    # Create deployments
    create_single_instance_deployment()
    create_container_deployment()
    create_deployment_scripts()
    
    print("\n" + "="*70)
    print("📋 DEPLOYMENT OPTIONS CREATED")
    print("="*70)
    
    print("\n🔥 RECOMMENDED: Single EC2 Instance")
    print("   • Cost: $60-70/month ($2-3/day)")
    print("   • 50 agents in separate tmux sessions")
    print("   • Context retention between runs")
    print("   • Easy debugging and monitoring")
    print("   • Deploy: ./deploy-ec2-agents.sh")
    
    print("\n🐳 ALTERNATIVE: Docker Container")
    print("   • Cost: $85-95/month (ECS) or local")
    print("   • Portable and easy deployment")
    print("   • Deploy: ./deploy-container-agents.sh")
    
    print("\n⚡ FOR MAXIMUM SAVINGS:")
    print("   • Use spot instances (70% cost reduction)")
    print("   • Auto start/stop during dev hours only")
    print("   • Estimated: $15-25/month for part-time use")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Choose deployment strategy")
    print("2. Run deployment script")
    print("3. Access dashboard to monitor all 50 agents")
    print("4. Each agent retains context in its own tmux session")
    
    return 0

if __name__ == "__main__":
    main()
