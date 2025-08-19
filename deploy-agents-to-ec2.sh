#!/bin/bash

echo "Deploying real AI agents to EC2 instance..."

INSTANCE_ID="i-0af59b7036f7b0b77"

# First, stop the placeholder agents
echo "Stopping placeholder agents..."
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["sudo pkill -f agent.py","tmux kill-server 2>/dev/null || true"]' \
    --output text

sleep 5

# Create directory structure
echo "Setting up agent directories..."
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["sudo mkdir -p /opt/ai-agents","sudo chown agent:agent /opt/ai-agents","sudo mkdir -p /opt/ai-agents/logs","sudo mkdir -p /opt/ai-agents/scripts"]' \
    --output text

# Deploy the actual agent scripts
echo "Deploying AI agent scripts..."

# Create a deployment script on the EC2 instance
cat << 'EOF' > deploy-script.sh
#!/bin/bash
cd /opt/ai-agents

# Install required Python packages
sudo pip3 install requests boto3 github pygithub pytest playwright

# Download agent scripts from GitHub
wget https://raw.githubusercontent.com/VisualForgeMediaV2/ai-agents/main/ai-qa-agent.py
wget https://raw.githubusercontent.com/VisualForgeMediaV2/ai-agents/main/ai-developer-agent.py
wget https://raw.githubusercontent.com/VisualForgeMediaV2/ai-agents/main/ai-operations-agent.py

# Create configuration
cat << 'CONFIG' > config.json
{
  "github_repo": "VisualForgeMediaV2/business-operations",
  "services": [
    "vf-dashboard-service",
    "vf-audio-service",
    "vf-video-service",
    "vf-text-service",
    "ns-auth",
    "ns-dashboard",
    "ns-shell"
  ],
  "test_locations": {
    "vf-dashboard-service": "mfe/tests",
    "vf-audio-service": "mfe/tests",
    "vf-video-service": "mfe/tests",
    "vf-text-service": "mfe/tests",
    "ns-shell": "tests"
  }
}
CONFIG

# Create agent launcher
cat << 'LAUNCHER' > start-real-agents.sh
#!/bin/bash

export GITHUB_TOKEN=$(aws secretsmanager get-secret-value --secret-id github-token --query SecretString --output text 2>/dev/null || echo "")

# Start QA Agent
tmux new-session -d -s qa-agent "python3 /opt/ai-agents/ai-qa-agent.py --monitor --run-tests"

# Start Developer Agent
tmux new-session -d -s dev-agent "python3 /opt/ai-agents/ai-developer-agent.py --monitor --fix-bugs"

# Start Operations Agent
tmux new-session -d -s ops-agent "python3 /opt/ai-agents/ai-operations-agent.py --monitor"

echo "Real AI agents started in tmux sessions"
echo "Use 'tmux ls' to see sessions"
echo "Use 'tmux attach -t qa-agent' to view QA agent"
LAUNCHER

chmod +x start-real-agents.sh
EOF

# Upload and execute deployment script
aws s3 cp deploy-script.sh s3://vf-dev-deployment/deploy-script.sh 2>/dev/null || {
    echo "Direct S3 upload failed, using SSM instead..."
    
    # Send the script content via SSM
    aws ssm send-command \
        --instance-ids $INSTANCE_ID \
        --document-name "AWS-RunShellScript" \
        --parameters "commands=[\"$(cat deploy-script.sh | sed 's/"/\\"/g')\"]" \
        --output text
}

echo "Deployment initiated. Agents will start on EC2 instance."
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: 98.81.93.132"