# AWS Cost Analysis & Optimization Report

## Current Cost Status

### Daily Costs
- **Yesterday (Aug 18)**: $4.45
- **Estimated Today**: ~$4-5

### Monthly Projection
- **August MTD**: ~$85-90 (estimated)

## EC2 Instance Analysis

### Current Instance
- **Instance ID**: i-0af59b7036f7b0b77
- **Type**: t3.large
- **Status**: Running
- **Launch Time**: 2025-08-19 08:39:37 UTC (running ~10 hours)

### Cost Breakdown for t3.large
- **On-Demand Price**: ~$0.0832/hour (us-east-1)
- **Daily Cost**: ~$2.00/day
- **Monthly Cost**: ~$60/month

### Agent Resource Usage
- 3 Python agents running
- Low CPU usage (agents mostly idle between test cycles)
- Memory usage: minimal (~10MB per agent)

## Cost Optimization Recommendations

### 1. IMMEDIATE: Stop Unnecessary Monitoring
The continuous monitoring script is making SSM calls every 60 seconds:
- **Current**: 1,440 SSM calls/day
- **Cost Impact**: Minimal but adds up
- **Action**: Reduce to every 5-10 minutes

### 2. SHORT-TERM: Optimize Instance Type
Current t3.large may be oversized for agent workload:
- **Alternative**: t3.medium ($0.0416/hour) - Save 50%
- **Alternative**: t3.small ($0.0208/hour) - Save 75%
- **Recommendation**: Monitor actual usage for 24h, then downsize

### 3. SCHEDULE-BASED RUNNING
Agents don't need to run 24/7:
- **Business Hours Only**: 8am-6pm = Save 58%
- **Weekdays Only**: Skip weekends = Save 28%
- **Combined**: Business hours + weekdays = Save ~70%

### 4. SPOT INSTANCES
For non-critical testing agents:
- **Spot Price**: ~$0.025/hour (70% savings)
- **Risk**: May be interrupted
- **Suitable**: Yes, for testing agents

## Recommended Actions

### Immediate (Do Now)
```bash
# 1. Kill the continuous monitor to reduce SSM calls
# Currently running as bash_9

# 2. Reduce agent test frequency
aws ssm send-command --instance-ids i-0af59b7036f7b0b77 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["pkill -f monitor-ec2-agents"]'
```

### Today
```bash
# 3. Check actual resource usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0af59b7036f7b0b77 \
  --start-time 2025-08-19T00:00:00Z \
  --end-time 2025-08-19T23:59:59Z \
  --period 3600 \
  --statistics Average
```

### This Week
1. Downsize to t3.medium or t3.small
2. Implement scheduled start/stop
3. Set up CloudWatch billing alerts

## Cost Alert Setup

### Create Billing Alert
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "EC2-Agent-Daily-Cost-Alert" \
  --alarm-description "Alert when EC2 costs exceed $5/day" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=Currency,Value=USD
```

## Estimated Savings

| Optimization | Current | Optimized | Monthly Savings |
|-------------|---------|-----------|-----------------|
| Instance Type (t3.large → t3.small) | $60 | $15 | $45 |
| Schedule (24/7 → Business Hours) | $60 | $25 | $35 |
| Spot Instance | $60 | $18 | $42 |
| **Combined (small + schedule)** | **$60** | **$6** | **$54** |

## Summary

**Current Monthly Cost**: ~$60 for EC2 instance
**Optimized Cost**: ~$6-15 depending on options
**Potential Savings**: 75-90%

### Priority Actions:
1. ✅ Stop excessive monitoring (bash_9)
2. ✅ Reduce test frequency from every 10-15 min to hourly
3. ✅ Schedule instance stop/start for business hours
4. ✅ Downsize instance after usage validation

The agents are currently over-provisioned for their actual workload. With optimization, you can maintain the same testing coverage at 10-20% of current costs.