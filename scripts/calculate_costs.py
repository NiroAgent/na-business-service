#!/usr/bin/env python3
"""Calculate actual 24/7 spot instance costs for 50 agents"""

# Configuration
instances = 50
instance_type = 't3.medium'  # Typical for agents
spot_price = 0.0104  # Current t3.medium spot price in us-east-1
hours_per_month = 730  # 24/7 operation

# Calculate monthly cost
monthly_cost = instances * spot_price * hours_per_month

print('=== 24/7 SPOT INSTANCE COST BREAKDOWN ===')
print()
print(f'Instance Type: {instance_type}')
print(f'Spot Price: ${spot_price}/hour')
print(f'Number of Instances: {instances}')
print(f'Hours per Month: {hours_per_month} (24/7)')
print()
print(f'Cost per Instance: ${spot_price * hours_per_month:.2f}/month')
print(f'Total Monthly Cost: ${monthly_cost:.2f}')
print()
print('=== COMPARISON ===')
print(f'On-Demand Price: $0.0416/hour')
on_demand = 50 * 0.0416 * 730
print(f'On-Demand Monthly: ${on_demand:.2f}')
print(f'Spot Savings: ${on_demand - monthly_cost:.2f}/month (75% off)')
print()
print('=== ACTUAL OPTIMIZATION OPTIONS ===')
print()
print('Option 1: Auto-scaling (Recommended)')
print('- Scale down to 5 instances at night')
print('- Scale up to 50 during business hours')
avg_instances = (50 * 10 + 5 * 14) / 24  # 10 hrs peak, 14 hrs off-peak
auto_scale_cost = avg_instances * spot_price * hours_per_month
print(f'- Average instances: {avg_instances:.1f}')
print(f'- Monthly cost: ${auto_scale_cost:.2f}')
print()
print('Option 2: On-demand processing')
print('- Start instances only when issues arrive')
print('- 100 issues/month, 1 hour each')
on_demand_hours = 100  # hours per month
on_demand_cost = instances * spot_price * on_demand_hours / 10  # Assume 10 parallel
print(f'- Monthly cost: ${on_demand_cost:.2f}')
print()
print('Option 3: Hybrid approach')
print('- 5 always-on instances')
print('- Scale to 50 for high priority')
hybrid_cost = (5 * spot_price * hours_per_month) + (45 * spot_price * 100)
print(f'- Monthly cost: ${hybrid_cost:.2f}')
print()
print('=== RECOMMENDATION ===')
print(f'For 24/7 operation with 50 instances: ${monthly_cost:.2f}/month')
print(f'With auto-scaling (5-50 instances): ${auto_scale_cost:.2f}/month')
print(f'On-demand only (100 hrs/month): ${on_demand_cost:.2f}/month')