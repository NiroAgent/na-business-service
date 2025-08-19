#!/bin/bash
INSTANCE_ID="i-0af59b7036f7b0b77"

# Fix the strftime syntax errors and start agents
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
"cd /opt/ai-agents/scripts",
"# Fix the strftime syntax errors",
"cat ai-qa-agent-comprehensive.py | sed '\''s/strftime(%Y%m%d-%H%M%S)/strftime('\''\\'\''%Y%m%d-%H%M%S'\''\\'\'')/g'\'' > qa-fixed.py",
"cat ai-operations-agent-real.py | sed '\''s/strftime(%Y%m%d-%H%M%S)/strftime('\''\\'\''%Y%m%d-%H%M%S'\''\\'\'')/g'\'' > ops-fixed.py",
"mv qa-fixed.py ai-qa-agent-comprehensive.py",
"mv ops-fixed.py ai-operations-agent-real.py",
"chmod +x *.py",
"# Start all agents",
"nohup python3 ai-qa-agent-comprehensive.py > /opt/ai-agents/logs/qa.log 2>&1 &",
"nohup python3 ai-developer-agent-real.py > /opt/ai-agents/logs/dev.log 2>&1 &",
"nohup python3 ai-operations-agent-real.py > /opt/ai-agents/logs/ops.log 2>&1 &",
"sleep 3",
"echo '\''Agents started:'\''",
"ps aux | grep python3 | grep -v grep"
]' \
    --output text

echo "Agents should now be running. Checking status..."
sleep 10

# Check status
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["ps aux | grep python3 | grep -v grep","echo","echo Checking logs:","tail -5 /opt/ai-agents/logs/qa.log 2>/dev/null || echo No QA log","tail -5 /opt/ai-agents/logs/dev.log 2>/dev/null || echo No dev log","tail -5 /opt/ai-agents/logs/ops.log 2>/dev/null || echo No ops log"]' \
    --query 'Command.CommandId' \
    --output text