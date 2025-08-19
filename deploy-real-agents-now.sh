#!/bin/bash

echo "========================================="
echo "DEPLOYING REAL AI AGENTS TO EC2"
echo "========================================="

INSTANCE_ID="i-0af59b7036f7b0b77"

# Step 1: Stop placeholder agents
echo "Step 1: Stopping placeholder agents..."
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["sudo pkill -f agent.py","tmux kill-server"]' \
    --output text

sleep 5

# Step 2: Upload real agent scripts
echo "Step 2: Uploading real AI agent scripts..."

# Read the real agent scripts and send them to EC2
COMMAND_ID=$(aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "sudo mkdir -p /opt/ai-agents/scripts",
        "sudo mkdir -p /opt/ai-agents/logs", 
        "cd /opt/ai-agents/scripts",
        "# Download real agents from GitHub",
        "sudo curl -o ai-qa-agent.py https://raw.githubusercontent.com/VisualForgeMediaV2/Projects/main/src/agents/ai-qa-agent.py",
        "sudo curl -o ai-developer-agent.py https://raw.githubusercontent.com/VisualForgeMediaV2/Projects/main/src/agents/ai-developer-agent.py",
        "sudo curl -o ai-operations-agent.py https://raw.githubusercontent.com/VisualForgeMediaV2/Projects/main/src/agents/ai-operations-agent.py",
        "sudo chmod +x *.py",
        "sudo chown -R agent:agent /opt/ai-agents"
    ]' \
    --query 'Command.CommandId' \
    --output text)

echo "Upload command ID: $COMMAND_ID"
sleep 10

# Step 3: Install dependencies
echo "Step 3: Installing Python dependencies..."
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "sudo pip3 install pygithub boto3 requests pytest playwright pandas",
        "sudo npm install -g playwright",
        "sudo npx playwright install-deps",
        "sudo npx playwright install chromium"
    ]' \
    --output text

sleep 10

# Step 4: Set up GitHub token
echo "Step 4: Configuring GitHub token..."
GITHUB_TOKEN=$(gh auth token)

aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters "commands=[
        \"echo 'export GITHUB_TOKEN=$GITHUB_TOKEN' | sudo tee /opt/ai-agents/.env\",
        \"sudo chown agent:agent /opt/ai-agents/.env\"
    ]" \
    --output text

# Step 5: Start real agents
echo "Step 5: Starting real AI agents..."
STARTUP_CMD=$(aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "sudo -u agent bash -c \"source /opt/ai-agents/.env && cd /opt/ai-agents/scripts && tmux new-session -d -s qa-agent python3 ai-qa-agent.py --monitor\"",
        "sudo -u agent bash -c \"source /opt/ai-agents/.env && cd /opt/ai-agents/scripts && tmux new-session -d -s dev-agent python3 ai-developer-agent.py --monitor\"",
        "sudo -u agent bash -c \"source /opt/ai-agents/.env && cd /opt/ai-agents/scripts && tmux new-session -d -s ops-agent python3 ai-operations-agent.py --monitor\"",
        "sudo -u agent tmux list-sessions"
    ]' \
    --query 'Command.CommandId' \
    --output text)

echo "Startup command ID: $STARTUP_CMD"
sleep 10

# Step 6: Verify agents are running
echo "Step 6: Verifying agents are running..."
aws ssm get-command-invocation \
    --command-id $STARTUP_CMD \
    --instance-id $INSTANCE_ID \
    --query 'StandardOutputContent' \
    --output text

echo "========================================="
echo "DEPLOYMENT COMPLETE"
echo "========================================="
echo ""
echo "To check agent status:"
echo "aws ssm send-command --instance-ids $INSTANCE_ID --document-name \"AWS-RunShellScript\" --parameters 'commands=[\"ps aux | grep agent\",\"tmux list-sessions\"]'"
echo ""
echo "To view agent logs:"
echo "aws ssm start-session --target $INSTANCE_ID"
echo "Then: sudo -u agent tmux attach -t qa-agent"