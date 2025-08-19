#!/usr/bin/env python3
"""Calculate costs for ONE spot instance running 50 agent containers"""

print('=== SINGLE SPOT INSTANCE WITH 50 CONTAINERS ===')
print()

# Instance sizing for 50 containers
instances = [
    ('t3.2xlarge', 8, 32, 0.0832, '8 vCPUs, 32GB RAM'),
    ('m5.4xlarge', 16, 64, 0.192, '16 vCPUs, 64GB RAM'),
    ('c5.4xlarge', 16, 32, 0.170, '16 vCPUs, 32GB RAM'),
    ('r5.2xlarge', 8, 64, 0.126, '8 vCPUs, 64GB RAM'),
]

hours_per_month = 730  # 24/7

print('Instance Type Options for 50 Containers:')
print('-' * 60)

for instance_type, vcpus, memory, spot_price, desc in instances:
    monthly_cost = spot_price * hours_per_month
    containers_per_vcpu = 50 / vcpus
    memory_per_container = memory / 50
    
    print(f'\n{instance_type}: {desc}')
    print(f'  Spot price: ${spot_price}/hour')
    print(f'  Monthly cost (24/7): ${monthly_cost:.2f}')
    print(f'  Containers per vCPU: {containers_per_vcpu:.1f}')
    print(f'  Memory per container: {memory_per_container:.1f}GB')
    
    if containers_per_vcpu <= 6.5:
        print(f'  [OK] Good CPU allocation')
    else:
        print(f'  [WARN] High CPU contention')

print('\n' + '=' * 60)
print('\n=== RECOMMENDED CONFIGURATION ===')
print()
print('Instance: t3.2xlarge (Most cost-effective)')
print('- 8 vCPUs, 32GB RAM')
print('- 50 lightweight agent containers')
print('- Each container: ~0.6GB RAM, 0.16 vCPU')
print()
print('MONTHLY COSTS:')
spot_cost = 0.0832 * hours_per_month
on_demand_cost = 0.3328 * hours_per_month
print(f'- Spot Instance (24/7): ${spot_cost:.2f}/month')
print(f'- On-Demand (24/7): ${on_demand_cost:.2f}/month')
print(f'- Savings: ${on_demand_cost - spot_cost:.2f}/month (75% off)')
print()
print('WITH SCHEDULING:')
print('- Business hours only (10h/day): ${:.2f}/month'.format(spot_cost * 10/24))
print('- Weekdays only (5d/week): ${:.2f}/month'.format(spot_cost * 5/7))
print()
print('=== ACTUAL ANSWER ===')
print(f'YES! Running ONE t3.2xlarge spot instance 24/7 with')
print(f'50 agent containers costs only ${spot_cost:.2f}/month!')
print()
print('This is WAY cheaper than:')
print('- 50 Lambda functions: $150-300/month')
print('- 50 separate EC2 instances: $380+/month')
print('- GitHub Actions runners: $500+/month')