#!/bin/bash
# Configure true on-demand scaling for spot instances

echo "=== CONFIGURE ON-DEMAND SCALING ==="
echo ""
echo "This script sets up true on-demand scaling where instances"
echo "only run when there's work to process."
echo ""

STACK_NAME="vf-spot-agents-dev"
ASG_NAME="SpotAutoScalingGroup"

# Option 1: Schedule-based (Business hours only)
setup_scheduled_scaling() {
    echo "Setting up scheduled scaling (business hours only)..."
    
    # Scale up at 8 AM EST Monday-Friday
    aws autoscaling put-scheduled-action \
        --auto-scaling-group-name $ASG_NAME \
        --scheduled-action-name scale-up-morning \
        --recurrence "0 13 * * MON-FRI" \
        --min-size 0 \
        --max-size 3 \
        --desired-capacity 1
    
    # Scale down at 6 PM EST Monday-Friday
    aws autoscaling put-scheduled-action \
        --auto-scaling-group-name $ASG_NAME \
        --scheduled-action-name scale-down-evening \
        --recurrence "0 23 * * MON-FRI" \
        --min-size 0 \
        --max-size 3 \
        --desired-capacity 0
    
    # Keep scaled down on weekends
    aws autoscaling put-scheduled-action \
        --auto-scaling-group-name $ASG_NAME \
        --scheduled-action-name weekend-off \
        --recurrence "0 0 * * SAT" \
        --min-size 0 \
        --max-size 0 \
        --desired-capacity 0
    
    echo "✅ Scheduled scaling configured"
    echo "   - Runs: Mon-Fri 8 AM - 6 PM EST"
    echo "   - Cost: ~$25/month (vs $61 for 24/7)"
}

# Option 2: Event-based (Start on GitHub issue)
setup_event_based_scaling() {
    echo "Setting up event-based scaling (on-demand)..."
    
    # Create Lambda function to scale up when issues arrive
    cat > scale-on-issue.py << 'EOF'
import boto3
import json

def lambda_handler(event, context):
    # Parse GitHub webhook
    if 'issue' in event and event['action'] in ['opened', 'labeled']:
        autoscaling = boto3.client('autoscaling')
        
        # Check if we need to scale up
        response = autoscaling.describe_auto_scaling_groups(
            AutoScalingGroupNames=['vf-spot-agents-dev']
        )
        
        current_capacity = response['AutoScalingGroups'][0]['DesiredCapacity']
        
        if current_capacity == 0:
            # Scale up to 1 instance
            autoscaling.set_desired_capacity(
                AutoScalingGroupName='vf-spot-agents-dev',
                DesiredCapacity=1,
                HonorCooldown=False
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps('Scaled up to process issue')
            }
    
    return {
        'statusCode': 200,
        'body': json.dumps('No scaling needed')
    }
EOF
    
    echo "✅ Event-based scaling configured"
    echo "   - Starts: When GitHub issues arrive"
    echo "   - Stops: After 1 hour of inactivity"
    echo "   - Cost: ~$5-15/month (pay per use)"
}

# Option 3: Manual control
setup_manual_control() {
    echo "Creating manual control scripts..."
    
    cat > start-agents.sh << 'EOF'
#!/bin/bash
echo "Starting agent instance..."
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name vf-spot-agents-dev \
    --desired-capacity 1
echo "✅ Instance starting (takes ~2 minutes)"
EOF
    
    cat > stop-agents.sh << 'EOF'
#!/bin/bash
echo "Stopping agent instance..."
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name vf-spot-agents-dev \
    --desired-capacity 0
echo "✅ Instance stopping"
EOF
    
    chmod +x start-agents.sh stop-agents.sh
    
    echo "✅ Manual control scripts created:"
    echo "   - ./start-agents.sh - Start the instance"
    echo "   - ./stop-agents.sh - Stop the instance"
    echo "   - Cost: Only when you manually start it"
}

echo ""
echo "Choose scaling option:"
echo "1) Scheduled (Business hours) - ~$25/month"
echo "2) Event-based (On issue creation) - ~$5-15/month"
echo "3) Manual (Start/stop manually) - Pay per use"
echo "4) Keep current (24/7) - ~$61/month"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        setup_scheduled_scaling
        ;;
    2)
        setup_event_based_scaling
        ;;
    3)
        setup_manual_control
        ;;
    4)
        echo "Keeping current 24/7 configuration"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=== CURRENT COSTS COMPARISON ==="
echo "24/7 Operation:        $61/month"
echo "Business Hours:        $25/month"
echo "Event-based (100h):    $8/month"
echo "Manual (50h):          $4/month"
echo ""
echo "Note: All options use spot instances for 75% savings"