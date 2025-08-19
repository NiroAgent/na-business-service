#!/bin/bash

# Schedule-based instance management for cost savings
INSTANCE_ID="i-0af59b7036f7b0b77"

case "$1" in
    stop)
        echo "Stopping EC2 instance for cost savings..."
        aws ec2 stop-instances --instance-ids $INSTANCE_ID
        echo "Instance stopped. Will save ~$0.08/hour"
        ;;
    
    start)
        echo "Starting EC2 instance..."
        aws ec2 start-instances --instance-ids $INSTANCE_ID
        echo "Instance starting. Agents will resume testing."
        ;;
    
    schedule)
        echo "Setting up automatic schedule (requires cron)..."
        echo "Add to crontab:"
        echo "# Start at 8 AM EST Monday-Friday"
        echo "0 8 * * 1-5 $PWD/instance-scheduler.sh start"
        echo ""
        echo "# Stop at 6 PM EST Monday-Friday"
        echo "0 18 * * 1-5 $PWD/instance-scheduler.sh stop"
        echo ""
        echo "This schedule will save ~70% on EC2 costs"
        ;;
    
    status)
        aws ec2 describe-instances --instance-ids $INSTANCE_ID \
            --query 'Reservations[0].Instances[0].[State.Name, InstanceType]' \
            --output table
        ;;
    
    *)
        echo "Usage: $0 {start|stop|schedule|status}"
        echo ""
        echo "Cost Savings:"
        echo "- Running 24/7: $60/month"
        echo "- Business hours only: $18/month (70% savings)"
        echo "- With t3.small: $6/month (90% savings)"
        ;;
esac