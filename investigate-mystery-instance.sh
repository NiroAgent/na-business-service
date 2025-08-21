#!/bin/bash

INSTANCE_ID="i-0af59b7036f7b0b77"

echo "====================================="
echo "INVESTIGATING MYSTERY m5.large INSTANCE"
echo "====================================="

echo "Instance Details:"
echo "- ID: $INSTANCE_ID"
echo "- Type: m5.large"
echo "- Cost: \$2.30/day (\$69/month)"
echo "- Created: Aug 19, 2025 at 9:04 AM"
echo "- Running for: ~10 hours"
echo "- Public IP: 35.174.174.116"
echo ""

echo "Checking if anything is running on it..."
# Try to connect via SSM if available
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["ps aux | head -20","docker ps 2>/dev/null || echo No Docker","ls -la /opt/","netstat -tlpn | head -10"]' \
    --output text 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Cannot connect via SSM. Instance may not have SSM agent."
    echo ""
    echo "OPTIONS:"
    echo "1. SAFE: Stop it first to see if anything breaks"
    echo "   aws ec2 stop-instances --instance-ids $INSTANCE_ID"
    echo ""
    echo "2. If nothing breaks after stopping, terminate it:"
    echo "   aws ec2 terminate-instances --instance-ids $INSTANCE_ID"
    echo ""
    echo "3. Or restart if needed:"
    echo "   aws ec2 start-instances --instance-ids $INSTANCE_ID"
else
    echo "Check the output above to see what's running."
fi

echo ""
echo "RECOMMENDATION: Stop it first since you don't recognize it."
echo "This will save \$2.30/day immediately."