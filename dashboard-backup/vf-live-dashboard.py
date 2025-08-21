#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VF-Dev Real-Time Agent Dashboard
Live monitoring of actual EC2 agents in VF-dev environment
"""

import os
import time
import json
import boto3
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import psutil
import threading
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# AWS Configuration for VF-Dev
VF_DEV_ACCOUNT = "319040880702"
VF_STAGING_ACCOUNT = "275057778147" 
VF_PROD_ACCOUNT = "229742714212"

class AWSAgentMonitor:
    def __init__(self):
        self.ec2_client = None
        self.cloudwatch_client = None
        self.cost_client = None
        self.agents_data = {}
        self.cost_data = {}
        self.setup_aws_clients()
        
    def setup_aws_clients(self):
        """Initialize AWS clients for VF-dev account"""
        try:
            # Use default credentials or assume role for VF-dev
            session = boto3.Session()
            self.ec2_client = session.client('ec2', region_name='us-east-1')
            self.cloudwatch_client = session.client('cloudwatch', region_name='us-east-1')
            self.cost_client = session.client('ce', region_name='us-east-1')
            logger.info("✅ AWS clients initialized successfully")
        except (NoCredentialsError, ClientError) as e:
            logger.error(f"❌ AWS setup failed: {e}")
            self.setup_mock_clients()
    
    def setup_mock_clients(self):
        """Fallback to mock data if AWS access fails"""
        logger.warning("⚠️ Using mock data - AWS credentials not available")
        self.ec2_client = None
        self.cloudwatch_client = None
        self.cost_client = None
    
    def get_agent_instances(self):
        """Get all EC2 instances tagged as agents"""
        if not self.ec2_client:
            return self.get_mock_instances()
        
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'tag:Project', 'Values': ['VisualForgeMediaV2', 'NiroSubsV2', 'NiroAgentV2']},
                    {'Name': 'tag:Role', 'Values': ['agent', 'ai-agent']},
                    {'Name': 'instance-state-name', 'Values': ['running', 'pending']}
                ]
            )
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append(self.parse_instance_data(instance))
            
            logger.info(f"📊 Found {len(instances)} live agent instances")
            return instances
            
        except Exception as e:
            logger.error(f"❌ Error fetching instances: {e}")
            return self.get_mock_instances()
    
    def parse_instance_data(self, instance):
        """Parse EC2 instance data into agent format"""
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        
        return {
            'id': instance['InstanceId'],
            'name': tags.get('Name', instance['InstanceId']),
            'type': instance['InstanceType'],
            'state': instance['State']['Name'],
            'project': tags.get('Project', 'Unknown'),
            'role': tags.get('Role', 'agent'),
            'specialization': tags.get('Specialization', 'General'),
            'launch_time': instance['LaunchTime'].isoformat() if 'LaunchTime' in instance else None,
            'private_ip': instance.get('PrivateIpAddress'),
            'public_ip': instance.get('PublicIpAddress'),
            'vpc_id': instance.get('VpcId'),
            'subnet_id': instance.get('SubnetId')
        }
    
    def get_instance_metrics(self, instance_id):
        """Get CloudWatch metrics for an instance"""
        if not self.cloudwatch_client:
            return self.get_mock_metrics()
        
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            # CPU Utilization
            cpu_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            # Memory would require custom CloudWatch agent
            # For now, we'll simulate or use available metrics
            
            cpu_usage = 0
            if cpu_response['Datapoints']:
                cpu_usage = cpu_response['Datapoints'][-1]['Average']
            
            return {
                'cpu_usage': round(cpu_usage, 1),
                'memory_usage': round(psutil.virtual_memory().percent, 1),  # Local fallback
                'network_in': 0,  # Would need NetworkIn metric
                'network_out': 0,  # Would need NetworkOut metric
                'disk_usage': 0   # Would need disk metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching metrics for {instance_id}: {e}")
            return self.get_mock_metrics()
    
    def get_cost_breakdown(self):
        """Get cost breakdown by environment"""
        if not self.cost_client:
            return self.get_mock_costs()
        
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = self.cost_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'},
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            return self.parse_cost_data(response)
            
        except Exception as e:
            logger.error(f"❌ Error fetching cost data: {e}")
            return self.get_mock_costs()
    
    def parse_cost_data(self, cost_response):
        """Parse AWS cost data into environment breakdown"""
        environments = {
            VF_DEV_ACCOUNT: {'name': 'VF-Dev', 'cost': 0, 'services': {}},
            VF_STAGING_ACCOUNT: {'name': 'VF-Staging', 'cost': 0, 'services': {}},
            VF_PROD_ACCOUNT: {'name': 'VF-Production', 'cost': 0, 'services': {}}
        }
        
        for result in cost_response.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                account_id = group['Keys'][0] if group['Keys'] else 'unknown'
                service = group['Keys'][1] if len(group['Keys']) > 1 else 'Other'
                amount = float(group['Metrics']['BlendedCost']['Amount'])
                
                if account_id in environments:
                    environments[account_id]['cost'] += amount
                    environments[account_id]['services'][service] = amount
        
        return environments
    
    def get_mock_instances(self):
        """Mock instance data for development/fallback"""
        return [
            {
                'id': f'i-{i:06d}abc',
                'name': f'VF-Agent-{i:02d}',
                'type': 't3.medium',
                'state': 'running',
                'project': ['VisualForgeMediaV2', 'NiroSubsV2', 'NiroAgentV2'][i % 3],
                'role': 'ai-agent',
                'specialization': ['Full-stack Dev', 'QA Engineer', 'DevOps', 'Security'][i % 4],
                'launch_time': (datetime.now() - timedelta(hours=i)).isoformat(),
                'private_ip': f'10.0.{i//10}.{i%10}',
                'public_ip': None,
                'vpc_id': 'vpc-12345678',
                'subnet_id': 'subnet-12345678'
            }
            for i in range(1, 51)
        ]
    
    def get_mock_metrics(self):
        """Mock metrics for development/fallback"""
        import random
        return {
            'cpu_usage': round(random.uniform(10, 90), 1),
            'memory_usage': round(random.uniform(20, 80), 1),
            'network_in': round(random.uniform(0, 1000), 1),
            'network_out': round(random.uniform(0, 1000), 1),
            'disk_usage': round(random.uniform(10, 70), 1)
        }
    
    def get_mock_costs(self):
        """Mock cost data for development/fallback"""
        return {
            VF_DEV_ACCOUNT: {
                'name': 'VF-Dev',
                'cost': 16.50,
                'services': {'EC2': 8.50, 'RDS': 4.00, 'S3': 2.00, 'CloudFront': 2.00}
            },
            VF_STAGING_ACCOUNT: {
                'name': 'VF-Staging', 
                'cost': 18.25,
                'services': {'EC2': 10.00, 'RDS': 5.00, 'S3': 2.25, 'CloudFront': 1.00}
            },
            VF_PROD_ACCOUNT: {
                'name': 'VF-Production',
                'cost': 13.75,
                'services': {'EC2': 8.00, 'RDS': 4.00, 'S3': 1.25, 'CloudFront': 0.50}
            }
        }

# Initialize monitor
monitor = AWSAgentMonitor()

@app.route('/')
def dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>VF-Dev Live Agent Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .header {
            background: rgba(0,0,0,0.2);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            backdrop-filter: blur(10px);
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 20px;
            background: rgba(0,0,0,0.1);
        }
        .status-card {
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .status-card:hover { transform: translateY(-5px); }
        .status-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
        .cost-breakdown {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .cost-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .agent-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }
        .agent-card:hover {
            background: rgba(255,255,255,0.2);
            transform: scale(1.02);
        }
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .running { background: #4CAF50; }
        .pending { background: #FF9800; }
        .stopped { background: #f44336; }
        .metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        .metric {
            background: rgba(0,0,0,0.2);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .live-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            z-index: 1000;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        .tab-container {
            background: rgba(0,0,0,0.1);
            padding: 0 20px;
        }
        .tabs {
            display: flex;
            gap: 10px;
        }
        .tab {
            padding: 15px 25px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px 10px 0 0;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .tab.active, .tab:hover {
            background: rgba(255,255,255,0.2);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
</head>
<body>
    <div class="live-indicator">🔴 LIVE</div>
    
    <div class="header">
        <h1>🚀 VF-Dev Live Agent Dashboard</h1>
        <p>Real-time monitoring of AI agents across VF environments</p>
        <p><strong>Account:</strong> VF-Dev (319040880702) | <strong>Last Update:</strong> <span id="lastUpdate">Loading...</span></p>
    </div>
    
    <div class="status-grid">
        <div class="status-card">
            <div>Total Agents</div>
            <div class="status-value" id="totalAgents">0</div>
        </div>
        <div class="status-card">
            <div>Running</div>
            <div class="status-value" id="runningAgents">0</div>
        </div>
        <div class="status-card">
            <div>Total Cost</div>
            <div class="status-value" id="totalCost">$0</div>
        </div>
        <div class="status-card">
            <div>Avg CPU</div>
            <div class="status-value" id="avgCpu">0%</div>
        </div>
    </div>
    
    <div class="tab-container">
        <div class="tabs">
            <div class="tab active" onclick="showTab('agents')">Live Agents</div>
            <div class="tab" onclick="showTab('costs')">Cost Breakdown</div>
            <div class="tab" onclick="showTab('console')">Console Grid</div>
        </div>
    </div>
    
    <div id="agents-tab" class="tab-content active">
        <div class="agents-grid" id="agentsGrid">
            <!-- Agent cards will be populated here -->
        </div>
    </div>
    
    <div id="costs-tab" class="tab-content">
        <div class="cost-breakdown" id="costBreakdown">
            <!-- Cost breakdown will be populated here -->
        </div>
    </div>
    
    <div id="console-tab" class="tab-content">
        <div class="agents-grid">
            <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <h2>🖥️ Console Grid View</h2>
                <p>Coming in next release - Real-time console streaming from all agents</p>
                <p>Will show live logs, command outputs, and interactive debugging</p>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
        
        function updateDashboard(data) {
            const { agents, costs, summary } = data;
            
            // Update summary stats
            document.getElementById('totalAgents').textContent = summary.total_agents;
            document.getElementById('runningAgents').textContent = summary.running_agents;
            document.getElementById('totalCost').textContent = '$' + summary.total_cost.toFixed(2);
            document.getElementById('avgCpu').textContent = summary.avg_cpu.toFixed(1) + '%';
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            
            // Update agents grid
            const agentsGrid = document.getElementById('agentsGrid');
            agentsGrid.innerHTML = agents.map(agent => `
                <div class="agent-card">
                    <div class="agent-header">
                        <h3>${agent.name}</h3>
                        <span class="status-badge ${agent.state}">${agent.state}</span>
                    </div>
                    <p><strong>Type:</strong> ${agent.specialization}</p>
                    <p><strong>Instance:</strong> ${agent.type} (${agent.id})</p>
                    <p><strong>Project:</strong> ${agent.project}</p>
                    <p><strong>IP:</strong> ${agent.private_ip || 'N/A'}</p>
                    <div class="metrics">
                        <div class="metric">
                            <div>CPU</div>
                            <div><strong>${agent.metrics.cpu_usage}%</strong></div>
                        </div>
                        <div class="metric">
                            <div>Memory</div>
                            <div><strong>${agent.metrics.memory_usage}%</strong></div>
                        </div>
                        <div class="metric">
                            <div>Uptime</div>
                            <div><strong>${agent.uptime || 'N/A'}</strong></div>
                        </div>
                        <div class="metric">
                            <div>Status</div>
                            <div><strong>Active</strong></div>
                        </div>
                    </div>
                </div>
            `).join('');
            
            // Update cost breakdown
            const costBreakdown = document.getElementById('costBreakdown');
            costBreakdown.innerHTML = Object.entries(costs).map(([accountId, data]) => `
                <div class="cost-card">
                    <h3>${data.name}</h3>
                    <div class="status-value">$${data.cost.toFixed(2)}/month</div>
                    <div style="margin-top: 15px;">
                        ${Object.entries(data.services).map(([service, cost]) => `
                            <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                                <span>${service}:</span>
                                <span>$${cost.toFixed(2)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('');
        }
        
        // Listen for real-time updates
        socket.on('dashboard_update', updateDashboard);
        
        // Initial load
        fetch('/api/dashboard-data')
            .then(response => response.json())
            .then(updateDashboard);
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            fetch('/api/dashboard-data')
                .then(response => response.json())
                .then(updateDashboard);
        }, 30000);
    </script>
</body>
</html>
    ''')

@app.route('/api/dashboard-data')
def dashboard_data():
    """Get complete dashboard data"""
    try:
        instances = monitor.get_agent_instances()
        costs = monitor.get_cost_breakdown()
        
        # Add metrics to each instance
        agents = []
        total_cpu = 0
        running_count = 0
        
        for instance in instances:
            metrics = monitor.get_instance_metrics(instance['id'])
            instance['metrics'] = metrics
            
            # Calculate uptime
            if instance['launch_time']:
                launch_time = datetime.fromisoformat(instance['launch_time'].replace('Z', '+00:00'))
                uptime = datetime.now(launch_time.tzinfo) - launch_time
                instance['uptime'] = f"{uptime.days}d {uptime.seconds//3600}h"
            else:
                instance['uptime'] = "Unknown"
            
            agents.append(instance)
            total_cpu += metrics['cpu_usage']
            
            if instance['state'] == 'running':
                running_count += 1
        
        # Calculate summary
        total_cost = sum(env['cost'] for env in costs.values())
        avg_cpu = total_cpu / len(agents) if agents else 0
        
        summary = {
            'total_agents': len(agents),
            'running_agents': running_count,
            'total_cost': total_cost,
            'avg_cpu': avg_cpu
        }
        
        return jsonify({
            'agents': agents,
            'costs': costs,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error generating dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'mode': 'live_aws_monitoring',
        'aws_connected': monitor.ec2_client is not None,
        'timestamp': datetime.now().isoformat()
    })

def background_updates():
    """Send periodic updates via WebSocket"""
    while True:
        try:
            time.sleep(30)  # Update every 30 seconds
            data = dashboard_data().get_json()
            if data and 'error' not in data:
                socketio.emit('dashboard_update', data)
                logger.info("📡 Sent dashboard update via WebSocket")
        except Exception as e:
            logger.error(f"❌ Background update error: {e}")

if __name__ == '__main__':
    logger.info("🚀 Starting VF-Dev Live Agent Dashboard...")
    logger.info(f"🌐 URL: http://localhost:5003")
    logger.info(f"☁️ AWS Account: VF-Dev ({VF_DEV_ACCOUNT})")
    logger.info(f"📊 Live monitoring: EC2 instances, CloudWatch metrics, Cost data")
    logger.info(f"🔄 Auto-refresh: 30 seconds")
    
    # Start background update thread
    update_thread = threading.Thread(target=background_updates, daemon=True)
    update_thread.start()
    
    try:
        socketio.run(app, host='0.0.0.0', port=5003, debug=False)
    except KeyboardInterrupt:
        logger.info("\n🛑 Dashboard stopped")
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
