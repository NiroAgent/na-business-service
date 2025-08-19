#!/bin/bash

# Deploy Real AI Agents to EC2 - Replace Placeholder Agents
set -e

# Configuration
EC2_INSTANCE="i-0af59b7036f7b0b77"
EC2_USER="ubuntu"
KEY_PATH="~/.ssh/id_rsa"  # Update with your actual SSH key path
LOCAL_AGENT_DIR="./ai-agent-deployment"
REMOTE_AGENT_DIR="/home/ubuntu/ai-agents"
REMOTE_PROJECT_DIR="/home/ubuntu/Projects"

echo "🚀 Deploying Real AI Agents to EC2 Instance: $EC2_INSTANCE"
echo "=================================================="

# Function to execute commands on EC2
execute_remote() {
    local cmd="$1"
    echo "Executing on EC2: $cmd"
    ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_INSTANCE" "$cmd"
}

# Function to copy files to EC2
copy_to_ec2() {
    local local_file="$1"
    local remote_file="$2"
    echo "Copying $local_file to EC2:$remote_file"
    scp -i "$KEY_PATH" -o StrictHostKeyChecking=no "$local_file" "$EC2_USER@$EC2_INSTANCE:$remote_file"
}

# Step 1: Check EC2 connectivity
echo "🔍 Checking EC2 connectivity..."
if ! execute_remote "echo 'Connected successfully'"; then
    echo "❌ Failed to connect to EC2 instance"
    exit 1
fi

# Step 2: Stop existing placeholder agents
echo "🛑 Stopping existing placeholder agents..."
execute_remote "pkill -f 'ai-qa-agent.py' || true"
execute_remote "pkill -f 'ai-developer-agent.py' || true"
execute_remote "pkill -f 'ai-architect-agent.py' || true"
echo "✅ Placeholder agents stopped"

# Step 3: Create directories on EC2
echo "📁 Creating directories on EC2..."
execute_remote "mkdir -p $REMOTE_AGENT_DIR"
execute_remote "mkdir -p $REMOTE_PROJECT_DIR"
execute_remote "mkdir -p /home/ubuntu/qa_reports"
execute_remote "mkdir -p /home/ubuntu/dev_reports"
execute_remote "mkdir -p /home/ubuntu/logs"

# Step 4: Copy the repository to EC2 (if not already there)
echo "📦 Ensuring project repository is on EC2..."
execute_remote "if [ ! -d '$REMOTE_PROJECT_DIR/VisualForgeMediaV2' ]; then echo 'Repository not found on EC2. Please clone the VisualForgeMediaV2 repository first.'; fi"

# Step 5: Copy real agent scripts to EC2
echo "📤 Copying real agent scripts to EC2..."
copy_to_ec2 "$LOCAL_AGENT_DIR/ai-qa-agent-real.py" "$REMOTE_AGENT_DIR/ai-qa-agent.py"
copy_to_ec2 "$LOCAL_AGENT_DIR/ai-developer-agent-real.py" "$REMOTE_AGENT_DIR/ai-developer-agent.py"
copy_to_ec2 "$LOCAL_AGENT_DIR/requirements.txt" "$REMOTE_AGENT_DIR/requirements.txt"

# Step 6: Install dependencies on EC2
echo "📦 Installing dependencies on EC2..."
execute_remote "cd $REMOTE_AGENT_DIR && python3 -m pip install -r requirements.txt --user"

# Step 7: Install Node.js and Playwright if not present
echo "🎭 Ensuring Playwright is installed on EC2..."
execute_remote "
if ! command -v node &> /dev/null; then
    echo 'Installing Node.js...'
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

if ! command -v npx &> /dev/null; then
    echo 'Installing npm...'
    sudo apt-get install -y npm
fi

# Install Playwright globally
sudo npm install -g playwright
sudo npm install -g @playwright/test

# Install Playwright browsers
npx playwright install --with-deps || echo 'Browser installation completed with warnings'
"

# Step 8: Set up environment variables
echo "🔧 Setting up environment variables..."
execute_remote "
# Create environment file
cat > /home/ubuntu/.env << EOL
GITHUB_TOKEN=\${GITHUB_TOKEN}
QA_BASE_DIR=/home/ubuntu/Projects
DEV_BASE_DIR=/home/ubuntu/Projects
TEST_LIMIT_PER_SERVICE=3
NODE_PATH=/usr/local/lib/node_modules
PATH=\$PATH:/usr/local/bin
EOL

# Add to bashrc
echo 'source ~/.env' >> ~/.bashrc
"

# Step 9: Create startup scripts
echo "🏃‍♂️ Creating agent startup scripts..."
execute_remote "
# Create QA Agent startup script
cat > $REMOTE_AGENT_DIR/start-qa-agent.sh << 'EOL'
#!/bin/bash
cd $REMOTE_AGENT_DIR
source ~/.env
export PYTHONPATH=\$PYTHONPATH:$REMOTE_AGENT_DIR
nohup python3 ai-qa-agent.py > /home/ubuntu/logs/qa-agent.log 2>&1 &
echo \$! > /home/ubuntu/logs/qa-agent.pid
echo \"QA Agent started with PID \$!\"
EOL

# Create Developer Agent startup script  
cat > $REMOTE_AGENT_DIR/start-dev-agent.sh << 'EOL'
#!/bin/bash
cd $REMOTE_AGENT_DIR
source ~/.env
export PYTHONPATH=\$PYTHONPATH:$REMOTE_AGENT_DIR
nohup python3 ai-developer-agent.py > /home/ubuntu/logs/dev-agent.log 2>&1 &
echo \$! > /home/ubuntu/logs/dev-agent.pid
echo \"Developer Agent started with PID \$!\"
EOL

# Make scripts executable
chmod +x $REMOTE_AGENT_DIR/start-qa-agent.sh
chmod +x $REMOTE_AGENT_DIR/start-dev-agent.sh
"

# Step 10: Create monitoring script
echo "📊 Creating monitoring script..."
execute_remote "
cat > $REMOTE_AGENT_DIR/monitor-agents.sh << 'EOL'
#!/bin/bash
echo '=================================='
echo '🤖 Real AI Agents Status Monitor'
echo '=================================='

# Check QA Agent
if [ -f /home/ubuntu/logs/qa-agent.pid ]; then
    QA_PID=\$(cat /home/ubuntu/logs/qa-agent.pid)
    if ps -p \$QA_PID > /dev/null; then
        echo \"✅ QA Agent running (PID: \$QA_PID)\"
    else
        echo \"❌ QA Agent not running\"
    fi
else
    echo \"❌ QA Agent not started\"
fi

# Check Developer Agent  
if [ -f /home/ubuntu/logs/dev-agent.pid ]; then
    DEV_PID=\$(cat /home/ubuntu/logs/dev-agent.pid)
    if ps -p \$DEV_PID > /dev/null; then
        echo \"✅ Developer Agent running (PID: \$DEV_PID)\"
    else
        echo \"❌ Developer Agent not running\"
    fi
else
    echo \"❌ Developer Agent not started\"
fi

echo \"\"
echo \"📁 Recent Reports:\"
ls -la /home/ubuntu/qa_reports/*.json 2>/dev/null | tail -3 || echo \"No QA reports found\"
ls -la /home/ubuntu/dev_reports/*.json 2>/dev/null | tail -3 || echo \"No dev reports found\"

echo \"\"
echo \"📊 Log Status:\"
echo \"QA Agent log (last 3 lines):\"
tail -3 /home/ubuntu/logs/qa-agent.log 2>/dev/null || echo \"No QA log found\"
echo \"\"
echo \"Developer Agent log (last 3 lines):\"
tail -3 /home/ubuntu/logs/dev-agent.log 2>/dev/null || echo \"No dev log found\"
EOL

chmod +x $REMOTE_AGENT_DIR/monitor-agents.sh
"

# Step 11: Start the real agents
echo "🚀 Starting real AI agents..."
execute_remote "$REMOTE_AGENT_DIR/start-qa-agent.sh"
sleep 2
execute_remote "$REMOTE_AGENT_DIR/start-dev-agent.sh"

# Step 12: Verify deployment
echo "🔍 Verifying deployment..."
sleep 5
execute_remote "$REMOTE_AGENT_DIR/monitor-agents.sh"

# Step 13: Create a test execution script
echo "🧪 Creating test execution script..."
execute_remote "
cat > $REMOTE_AGENT_DIR/run-test-cycle.sh << 'EOL'
#!/bin/bash
echo '🧪 Running Real AI Agent Test Cycle'
echo '===================================='

# Run QA Agent once
echo '1. Running QA Agent...'
cd $REMOTE_AGENT_DIR
python3 ai-qa-agent.py

echo ''
echo '2. Running Developer Agent...'  
python3 ai-developer-agent.py

echo ''
echo '3. Checking results...'
echo 'QA Reports:'
ls -la /home/ubuntu/qa_reports/ 2>/dev/null || echo 'No QA reports found'
echo ''
echo 'Dev Reports:'  
ls -la /home/ubuntu/dev_reports/ 2>/dev/null || echo 'No dev reports found'

echo ''
echo '✅ Test cycle complete!'
EOL

chmod +x $REMOTE_AGENT_DIR/run-test-cycle.sh
"

echo ""
echo "🎉 REAL AI AGENTS DEPLOYMENT COMPLETE!"
echo "======================================"
echo ""
echo "✅ Placeholder agents stopped"
echo "✅ Real agents deployed and started"
echo "✅ Environment configured"
echo "✅ Monitoring scripts created"
echo ""
echo "📋 Next Steps:"
echo "1. SSH to EC2: ssh -i $KEY_PATH $EC2_USER@$EC2_INSTANCE"
echo "2. Monitor agents: ./ai-agents/monitor-agents.sh"
echo "3. Run test cycle: ./ai-agents/run-test-cycle.sh"  
echo "4. Check logs: tail -f logs/qa-agent.log"
echo ""
echo "🔗 The agents will now:"
echo "   • Execute REAL Playwright tests"
echo "   • Perform ACTUAL code analysis"  
echo "   • Create GitHub issues for failures"
echo "   • Generate comprehensive reports"
echo ""
echo "⚠️  Important: Make sure to set GITHUB_TOKEN in ~/.env on EC2"
echo "⚠️  Important: Clone VisualForgeMediaV2 repo to $REMOTE_PROJECT_DIR if not present"