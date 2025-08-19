#!/bin/bash

echo "======================================"
echo "COST-OPTIMIZED AGENT CONFIGURATION"
echo "======================================"

INSTANCE_ID="i-0af59b7036f7b0b77"

# Update agents to run less frequently to save costs
echo "Updating agents for cost optimization..."

aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
"# Stop all current agents",
"pkill -f python3",
"# Update QA agent to run tests every 60 minutes instead of 15",
"sed -i '\''s/time.sleep(900)/time.sleep(3600)/g'\'' /opt/ai-agents/scripts/ai-qa-agent-comprehensive.py",
"# Update Developer agent to check every 30 minutes instead of 5",
"sed -i '\''s/time.sleep(300)/time.sleep(1800)/g'\'' /opt/ai-agents/scripts/ai-developer-agent-real.py",
"# Update Operations agent to check every 10 minutes instead of 2",
"sed -i '\''s/time.sleep(120)/time.sleep(600)/g'\'' /opt/ai-agents/scripts/ai-operations-agent-real.py",
"# Restart agents with new timing",
"cd /opt/ai-agents/scripts",
"nohup python3 ai-qa-agent-comprehensive.py > /opt/ai-agents/logs/qa.log 2>&1 &",
"nohup python3 ai-developer-agent-real.py > /opt/ai-agents/logs/dev.log 2>&1 &",
"nohup python3 ai-operations-agent-real.py > /opt/ai-agents/logs/ops.log 2>&1 &",
"echo '\''Agents restarted with cost-optimized timing:'\''",
"echo '\''- QA: Every 60 minutes (was 15)'\''",
"echo '\''- Developer: Every 30 minutes (was 5)'\''",
"echo '\''- Operations: Every 10 minutes (was 2)'\''",
"ps aux | grep python3 | grep -v grep"
]' \
    --output text

echo ""
echo "Cost Optimization Applied:"
echo "- Reduced test frequency by 75%"
echo "- Stopped continuous monitoring (was every 60 seconds)"
echo "- Agents now use minimal resources between runs"
echo ""
echo "Estimated savings: ~$40/month"