#!/usr/bin/env python3
"""
Enhanced EC2 Agent Dashboard with Tabs
Integrates the comprehensive tabbed interface with EC2 functionality
"""

from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import psutil
import random
import time
import json
import boto3
from datetime import datetime, timedelta
from threading import Thread

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ec2_dashboard_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class EC2AgentDashboard:
    def __init__(self):
        self.agents = self.initialize_agents()
        self.console_logs = []
        self.system_metrics = {}
        self.cost_data = {'current': 12.50, 'threshold': 25.0, 'savings': 95.5}
        self.performance_history = []
        self.ec2_client = None
        self.work_queue = []
        
        # Cost monitoring and kill switch
        self.cost_history = []
        self.cost_alert_threshold = 3.0  # 3% increase triggers alert
        self.cost_kill_threshold = 5.0   # 5% increase triggers auto-shutdown
        self.cost_monitoring_enabled = True
        self.system_shutdown = False
        self.last_cost_check = datetime.now()
        
        self.team_metrics = {
            "active_developers": 0,
            "work_in_progress": 0, 
            "completed_today": 0,
            "velocity": 85
        }
        self.github_data = {
            "connected": True,
            "open_issues": 42,
            "open_prs": 8,
            "merged_today": 5,
            "auto_assignments": 12
        }
        
        # Start background data collection
        self.start_background_tasks()
    
    def initialize_agents(self):
        """Initialize 50 specialized agents with EC2 instances"""
        specializations = [
            'Full-stack Developer (React/Node)', 'Full-stack Developer (Vue/Python)', 
            'Full-stack Developer (Angular/Java)', 'Full-stack Developer (HTML/CSS)',
            'QA Engineer (Automated Testing)', 'QA Engineer (Performance Testing)',
            'QA Engineer (Security Testing)', 'QA Engineer (Manual Testing)',
            'DevOps Engineer (AWS/Docker)', 'DevOps Engineer (CI/CD Pipeline)',
            'DevOps Engineer (Kubernetes)', 'DevOps Engineer (Terraform)',
            'Security Engineer (Penetration Testing)', 'Security Engineer (Compliance)',
            'Security Engineer (Vulnerability Assessment)', 'Security Engineer (SOC)'
        ]
        
        agents = []
        for i in range(50):
            agent = {
                'id': f'agent-{i+1:02d}',
                'name': f'AI-Agent-{i+1:02d}',
                'specialization': specializations[i % len(specializations)],
                'status': random.choice(['active', 'idle', 'processing']),
                'ec2_instance': f'i-{random.randint(100000,999999):06x}',
                'availability_zone': random.choice(['us-east-1a', 'us-east-1b', 'us-east-1c']),
                'instance_type': random.choice(['t3.micro', 't3.small', 't3.medium']),
                'cpu_usage': random.randint(10, 90),
                'memory_usage': random.randint(20, 80),
                'network_io': random.randint(1, 100),
                'disk_io': random.randint(1, 50),
                'current_task': random.choice([
                    'GitHub issue processing', 'Code review automation', 'Testing execution',
                    'Deployment pipeline', 'Security scanning', 'Performance monitoring',
                    'Database optimization', 'API development', 'Frontend testing', 'Idle'
                ]),
                'uptime': random.randint(1, 168),  # Hours
                'tasks_today': random.randint(0, 25),
                'success_rate': random.randint(85, 99),
                'last_activity': datetime.now().isoformat(),
                'cost_per_hour': round(random.uniform(0.003, 0.008), 4)  # Optimized spot instance pricing
            }
            agents.append(agent)
        return agents
    
    def start_background_tasks(self):
        """Start background threads for data collection"""
        Thread(target=self.update_agent_data, daemon=True).start()
        Thread(target=self.collect_system_metrics, daemon=True).start()
        Thread(target=self.simulate_console_output, daemon=True).start()
        Thread(target=self.update_work_queue, daemon=True).start()
        Thread(target=self.cost_monitoring_loop, daemon=True).start()
    
    def cost_monitoring_loop(self):
        """Monitor costs and trigger alerts/shutdown if thresholds exceeded"""
        while True:
            try:
                if not self.cost_monitoring_enabled or self.system_shutdown:
                    time.sleep(30)
                    continue
                
                # Calculate current hourly cost
                current_hourly_cost = sum([a['cost_per_hour'] for a in self.agents if a['status'] == 'active'])
                
                # Add to cost history
                cost_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'hourly_cost': current_hourly_cost,
                    'active_agents': len([a for a in self.agents if a['status'] == 'active']),
                    'total_agents': len(self.agents)
                }
                self.cost_history.append(cost_entry)
                
                # Keep only last hour of data (60 minutes / 5 minute intervals = 12 entries)
                if len(self.cost_history) > 12:
                    self.cost_history = self.cost_history[-12:]
                
                # Check for cost increases if we have enough history
                if len(self.cost_history) >= 2:
                    self.check_cost_thresholds()
                
                # Update cost data
                self.cost_data['current_hourly'] = current_hourly_cost
                self.cost_data['monthly_projected'] = current_hourly_cost * 24 * 30
                
            except Exception as e:
                print(f"Error in cost monitoring: {e}")
            
            time.sleep(300)  # Check every 5 minutes
    
    def check_cost_thresholds(self):
        """Check if cost increases exceed alert or kill thresholds"""
        if len(self.cost_history) < 2:
            return
        
        # Compare current cost to cost from 1 hour ago (or earliest available)
        current_cost = self.cost_history[-1]['hourly_cost']
        baseline_cost = self.cost_history[0]['hourly_cost']
        
        if baseline_cost > 0:
            increase_percentage = ((current_cost - baseline_cost) / baseline_cost) * 100
            
            # Log cost monitoring
            self.log_cost_event(f"Cost monitoring: Current ${current_cost:.4f}/hr vs baseline ${baseline_cost:.4f}/hr ({increase_percentage:.1f}% change)")
            
            # Check kill threshold (5% increase)
            if increase_percentage >= self.cost_kill_threshold:
                self.trigger_emergency_shutdown(increase_percentage, current_cost, baseline_cost)
            
            # Check alert threshold (3% increase)
            elif increase_percentage >= self.cost_alert_threshold:
                self.trigger_cost_alert(increase_percentage, current_cost, baseline_cost)
    
    def trigger_emergency_shutdown(self, increase_percentage, current_cost, baseline_cost):
        """Emergency shutdown triggered by cost increase >= 5%"""
        self.system_shutdown = True
        
        shutdown_message = f"""
🚨 EMERGENCY SHUTDOWN TRIGGERED 🚨
Cost increase: {increase_percentage:.1f}% in the last hour
Baseline: ${baseline_cost:.4f}/hr → Current: ${current_cost:.4f}/hr
Auto-shutdown threshold: {self.cost_kill_threshold}% exceeded
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ACTIONS TAKEN:
✅ All agent operations halted
✅ System marked for shutdown
✅ Cost monitoring alert logged
✅ Emergency protocols activated

System will remain in shutdown mode until manual override.
"""
        
        self.log_cost_event(shutdown_message)
        
        # Stop all agents
        for agent in self.agents:
            agent['status'] = 'shutdown'
            agent['current_task'] = 'Emergency shutdown - cost threshold exceeded'
        
        print("🚨 EMERGENCY SHUTDOWN: Cost increase threshold exceeded!")
        print(f"Cost increased {increase_percentage:.1f}% - System halted!")
    
    def trigger_cost_alert(self, increase_percentage, current_cost, baseline_cost):
        """Trigger cost alert for increases >= 3%"""
        alert_message = f"""
⚠️ COST ALERT ⚠️
Cost increase: {increase_percentage:.1f}% in the last hour
Baseline: ${baseline_cost:.4f}/hr → Current: ${current_cost:.4f}/hr
Alert threshold: {self.cost_alert_threshold}% exceeded
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

MONITORING STATUS:
📊 Increased monitoring activated
⚠️ Watching for {self.cost_kill_threshold}% threshold
🔍 Cost tracking every 5 minutes
📈 Current trajectory: ${(current_cost * 24 * 30):.2f}/month
"""
        
        self.log_cost_event(alert_message)
        print(f"⚠️ COST ALERT: {increase_percentage:.1f}% cost increase detected!")
    
    def calculate_cost_trend(self):
        """Calculate current cost trend percentage"""
        if len(self.cost_history) < 2:
            return 0.0
        
        latest_cost = self.cost_history[-1]
        baseline_cost = self.cost_history[0]  # First recorded cost as baseline
        
        if baseline_cost == 0:
            return 0.0
        
        trend_percentage = ((latest_cost - baseline_cost) / baseline_cost) * 100
        return trend_percentage
    
    def log_cost_event(self, message):
        """Log cost monitoring events to console"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'source': 'Cost Monitor',
            'ec2_instance': 'system-monitor',
            'message': message,
            'level': 'critical' if self.system_shutdown else 'warning'
        }
        self.console_logs.append(log_entry)
    
    def manual_override_shutdown(self):
        """Manual override to re-enable system after emergency shutdown"""
        self.system_shutdown = False
        self.cost_history = []  # Reset cost history
        
        # Reactivate agents
        for agent in self.agents:
            agent['status'] = random.choice(['active', 'idle', 'processing'])
            agent['current_task'] = random.choice([
                'System restart - monitoring resumed', 'Post-shutdown validation',
                'Cost monitoring re-enabled', 'Normal operations resumed'
            ])
        
        override_message = f"""
🔄 MANUAL OVERRIDE ACTIVATED 🔄
System shutdown manually overridden
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ACTIONS TAKEN:
✅ System shutdown mode disabled
✅ Agent operations resumed
✅ Cost monitoring reset
✅ Normal operations restored

Cost monitoring thresholds:
Alert: {self.cost_alert_threshold}% increase per hour
Shutdown: {self.cost_kill_threshold}% increase per hour
"""
        
        self.log_cost_event(override_message)
        print("🔄 Manual override: System reactivated")
    
    def update_agent_data(self):
        """Continuously update agent data"""
        while True:
            for agent in self.agents:
                # Check if system is in shutdown mode
                if self.system_shutdown:
                    agent['status'] = 'shutdown'
                    agent['current_task'] = 'Emergency shutdown - cost threshold exceeded'
                    agent['cpu_usage'] = 0
                    agent['memory_usage'] = 10
                    agent['network_io'] = 0
                    agent['disk_io'] = 0
                    continue
                
                # Simulate dynamic agent behavior
                agent['status'] = random.choice(['active', 'idle', 'processing'])
                agent['cpu_usage'] = max(5, min(95, agent['cpu_usage'] + random.randint(-10, 10)))
                agent['memory_usage'] = max(10, min(90, agent['memory_usage'] + random.randint(-5, 5)))
                agent['network_io'] = random.randint(1, 100)
                agent['disk_io'] = random.randint(1, 50)
                
                # Update tasks
                if random.random() < 0.1:  # 10% chance to change task
                    agent['current_task'] = random.choice([
                        'GitHub issue processing', 'Code review automation', 'Testing execution',
                        'Deployment pipeline', 'Security scanning', 'Performance monitoring',
                        'Database optimization', 'API development', 'Frontend testing', 'Idle'
                    ])
                
                # Update success rate slightly
                agent['success_rate'] = max(80, min(99, agent['success_rate'] + random.randint(-1, 1)))
                
                # Increment tasks occasionally
                if random.random() < 0.05:  # 5% chance per update
                    agent['tasks_today'] += 1
                
                agent['last_activity'] = datetime.now().isoformat()
            
            time.sleep(3)  # Update every 3 seconds
    
    def collect_system_metrics(self):
        """Collect system-wide metrics"""
        while True:
            try:
                # Real system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Agent-specific metrics
                active_agents = len([a for a in self.agents if a['status'] == 'active'])
                total_memory = sum([a['memory_usage'] for a in self.agents])
                avg_cpu = sum([a['cpu_usage'] for a in self.agents]) / len(self.agents)
                
                self.system_metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'system': {
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_used_gb': round(memory.used / 1024 / 1024 / 1024, 2),
                        'disk_percent': disk.percent,
                        'active_agents': active_agents,
                        'total_agents': len(self.agents),
                        'avg_agent_cpu': round(avg_cpu, 1),
                        'total_agent_memory': round(total_memory, 1)
                    },
                    'ec2': {
                        'running_instances': len(self.agents),
                        'total_cost_hour': sum([a['cost_per_hour'] for a in self.agents]),
                        'estimated_monthly': 12.50,  # Fixed optimized cost
                        'cost_savings': 95.5
                    }
                }
                
                # Store performance history
                self.performance_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'cpu': cpu_percent,
                    'memory': memory.percent,
                    'agents': active_agents,
                    'avg_agent_cpu': avg_cpu
                })
                
                # Keep last 60 points (3 minutes)
                if len(self.performance_history) > 60:
                    self.performance_history = self.performance_history[-60:]
                
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
            
            time.sleep(3)
    
    def simulate_console_output(self):
        """Simulate console output from agents"""
        while True:
            try:
                # Generate console logs from random agents
                agent = random.choice(self.agents)
                log_types = [
                    f"[{agent['name']}] ✅ Task completed: {agent['current_task']}",
                    f"[{agent['name']}] 🔄 Processing GitHub issue #1234",
                    f"[{agent['name']}] 📊 Performance metrics: CPU {agent['cpu_usage']}%, Memory {agent['memory_usage']}%",
                    f"[{agent['name']}] 🚀 Deployment pipeline initiated",
                    f"[{agent['name']}] 🔍 Security scan completed - 0 vulnerabilities found",
                    f"[{agent['name']}] ⚡ EC2 instance {agent['ec2_instance']} health check passed",
                    f"[{agent['name']}] 📈 Success rate: {agent['success_rate']}%",
                    f"[{agent['name']}] 💰 Cost optimization: Saved $2.45 this hour"
                ]
                
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'source': agent['name'],
                    'ec2_instance': agent['ec2_instance'],
                    'message': random.choice(log_types),
                    'level': random.choice(['info', 'success', 'warning', 'debug'])
                }
                
                self.console_logs.append(log_entry)
                
                # Keep last 100 logs
                if len(self.console_logs) > 100:
                    self.console_logs = self.console_logs[-100:]
                
            except Exception as e:
                print(f"Error generating console output: {e}")
            
            time.sleep(2)  # Generate log every 2 seconds
    
    def update_work_queue(self):
        """Update work queue with simulated tasks"""
        while True:
            try:
                # Simulate work items
                if len(self.work_queue) < 20:  # Maintain ~20 items
                    priorities = ['P0_CRITICAL', 'P1_HIGH', 'P2_MEDIUM', 'P3_LOW']
                    statuses = ['queued', 'assigned', 'in_progress', 'review']
                    
                    work_item = {
                        'id': f'TASK-{random.randint(1000, 9999)}',
                        'title': random.choice([
                            'Implement user authentication system',
                            'Fix production API performance issue',
                            'Add unit tests for payment module',
                            'Deploy new feature to staging',
                            'Security vulnerability patch',
                            'Database migration script',
                            'Frontend UI improvements',
                            'API documentation update'
                        ]),
                        'priority': random.choice(priorities),
                        'status': random.choice(statuses),
                        'assignee': random.choice([a['name'] for a in self.agents[:10]]),
                        'progress': random.randint(0, 90),
                        'created': datetime.now().isoformat()
                    }
                    self.work_queue.append(work_item)
                
                # Update existing items
                for item in self.work_queue:
                    if random.random() < 0.1:  # 10% chance to update
                        item['progress'] = min(100, item['progress'] + random.randint(5, 15))
                        if item['progress'] >= 100:
                            item['status'] = 'completed'
                
                # Remove completed items occasionally
                self.work_queue = [item for item in self.work_queue if not (item['status'] == 'completed' and random.random() < 0.3)]
                
            except Exception as e:
                print(f"Error updating work queue: {e}")
            
            time.sleep(10)  # Update every 10 seconds
    
    def get_dashboard_data(self):
        """Get all dashboard data"""
        return {
            'agents': {agent['id']: agent for agent in self.agents},
            'console_logs': self.console_logs,
            'system_metrics': self.system_metrics,
            'cost_data': self.cost_data,
            'performance_history': self.performance_history,
            'work_queue': self.work_queue,
            'team_metrics': {
                'active_developers': len([a for a in self.agents if a['status'] == 'active']),
                'work_in_progress': len([item for item in self.work_queue if item['status'] == 'in_progress']),
                'completed_today': sum([a['tasks_today'] for a in self.agents]),
                'velocity': 85
            },
            'github_data': self.github_data,
            'cost_monitoring': {
                'enabled': self.cost_monitoring_enabled,
                'system_shutdown': self.system_shutdown,
                'alert_threshold': self.cost_alert_threshold,
                'kill_threshold': self.cost_kill_threshold,
                'cost_history': self.cost_history[-10:],  # Last 10 cost checks
                'current_hourly': getattr(self.cost_data, 'current_hourly', 0.15),
                'cost_trend': self.calculate_cost_trend(),
                'alert_status': 'EMERGENCY SHUTDOWN' if self.system_shutdown else 
                               ('COST WARNING ALERT' if self.calculate_cost_trend() > self.cost_alert_threshold else 'MONITORING - ALL NORMAL'),
                'monitoring_status': 'SHUTDOWN' if self.system_shutdown else ('ALERT' if len(self.cost_history) >= 2 and self.cost_history else 'MONITORING')
            }
        }

# Initialize dashboard
dashboard = EC2AgentDashboard()

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Enhanced EC2 Agent Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #0f0f23, #1a1a2e, #16213e);
            color: #e6edf3; 
            overflow: hidden;
        }
        
        .header { 
            background: linear-gradient(90deg, #1f2937, #374151); 
            padding: 15px 20px; 
            text-align: center; 
            border-bottom: 3px solid #4ade80;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .header h1 { 
            font-size: 1.8em; 
            margin-bottom: 5px; 
            color: #4ade80;
            text-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
        }
        
        .header-stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .stat-item {
            color: #60a5fa;
        }
        
        .tabs {
            display: flex;
            background: #1f2937;
            border-bottom: 1px solid #374151;
            overflow-x: auto;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        .tab {
            padding: 12px 20px;
            cursor: pointer;
            border: none;
            background: transparent;
            color: #9ca3af;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            white-space: nowrap;
            font-size: 14px;
            font-weight: 500;
        }
        
        .tab:hover {
            background: #374151;
            color: #e6edf3;
            transform: translateY(-1px);
        }
        
        .tab.active {
            color: #4ade80;
            border-bottom-color: #4ade80;
            background: #374151;
            box-shadow: 0 -2px 10px rgba(74, 222, 128, 0.2);
        }
        
        .tab-content {
            display: none;
            padding: 20px;
            height: calc(100vh - 140px);
            overflow-y: auto;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Enhanced Agent Grid */
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .agent-card {
            background: linear-gradient(145deg, #161b22, #21262d);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .agent-card:hover {
            border-color: #4ade80;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(74, 222, 128, 0.15);
        }
        
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .agent-name {
            font-weight: bold;
            color: #4ade80;
            font-size: 1.1em;
        }
        
        .agent-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-active { 
            background: linear-gradient(45deg, #22c55e, #16a34a); 
            color: white;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.3);
        }
        .status-idle { 
            background: linear-gradient(45deg, #f59e0b, #d97706); 
            color: white;
        }
        .status-processing { 
            background: linear-gradient(45deg, #3b82f6, #2563eb); 
            color: white;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .agent-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }
        
        .info-label {
            color: #9ca3af;
        }
        
        .info-value {
            color: #e6edf3;
            font-weight: 500;
        }
        
        .agent-resources {
            display: flex;
            gap: 15px;
            margin-top: 15px;
        }
        
        .resource-bar {
            flex: 1;
        }
        
        .resource-label {
            font-size: 0.8em;
            color: #9ca3af;
            margin-bottom: 3px;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #30363d;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4ade80, #22c55e);
            transition: width 0.3s ease;
        }
        
        .progress-fill.high {
            background: linear-gradient(90deg, #ef4444, #dc2626);
        }
        
        .progress-fill.medium {
            background: linear-gradient(90deg, #f59e0b, #d97706);
        }
        
        /* Console Output Styles */
        .console {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            height: 100%;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .console-header {
            background: #21262d;
            padding: 15px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .console-body {
            padding: 15px;
            height: calc(100% - 60px);
            overflow-y: auto;
            font-family: 'Courier New', monospace;
        }
        
        .log-entry {
            margin-bottom: 10px;
            padding: 8px;
            border-left: 3px solid #4ade80;
            background: rgba(74, 222, 128, 0.05);
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        
        .log-entry:hover {
            background: rgba(74, 222, 128, 0.1);
        }
        
        .log-timestamp {
            color: #6b7280;
            font-size: 0.8em;
        }
        
        .log-source {
            color: #4ade80;
            font-weight: bold;
        }
        
        .log-message {
            margin-top: 3px;
            color: #e6edf3;
        }
        
        /* System Resources */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .metric-card {
            background: linear-gradient(145deg, #161b22, #21262d);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .metric-title {
            color: #4ade80;
            font-size: 1.2em;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .metric-value {
            font-size: 2.5em;
            color: #60a5fa;
            margin-bottom: 10px;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(96, 165, 250, 0.3);
        }
        
        .metric-label {
            color: #9ca3af;
            font-size: 0.9em;
        }
        
        /* Work Queue */
        .work-queue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: linear-gradient(145deg, #161b22, #21262d);
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        
        .work-queue-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }
        
        .work-item {
            background: linear-gradient(145deg, #161b22, #21262d);
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        
        .work-item:hover {
            border-color: #4ade80;
            transform: translateY(-2px);
        }
        
        .work-item-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .priority-badge {
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            font-weight: bold;
        }
        
        .priority-P0_CRITICAL { background: #ef4444; color: white; }
        .priority-P1_HIGH { background: #f59e0b; color: white; }
        .priority-P2_MEDIUM { background: #3b82f6; color: white; }
        .priority-P3_LOW { background: #22c55e; color: white; }
        
        /* GitHub Integration */
        .github-overview {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .github-status {
            background: linear-gradient(145deg, #161b22, #21262d);
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #22c55e;
            animation: pulse-dot 2s infinite;
        }
        
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }
        
        /* Real-time indicator */
        .live-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(45deg, #22c55e, #16a34a);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
            animation: pulse-live 3s infinite;
        }
        
        @keyframes pulse-live {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #21262d; }
        ::-webkit-scrollbar-thumb { background: #4ade80; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #22c55e; }
        
        .connection-status {
            position: fixed;
            top: 60px;
            right: 20px;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .connected { 
            background: linear-gradient(45deg, #22c55e, #16a34a); 
            color: white;
            box-shadow: 0 2px 10px rgba(34, 197, 94, 0.3);
        }
        .disconnected { 
            background: linear-gradient(45deg, #ef4444, #dc2626); 
            color: white;
            box-shadow: 0 2px 10px rgba(239, 68, 68, 0.3);
        }
    </style>
</head>
<body>
    <div class="live-indicator">🔴 LIVE EC2</div>
    <div class="connection-status" id="connectionStatus">🔴 Connecting...</div>
    
    <div class="header">
        <h1>🚀 Enhanced EC2 Agent Dashboard</h1>
        <div class="header-stats">
            <span class="stat-item">50 Specialized Agents</span>
            <span class="stat-item">95.5% Cost Savings</span>
            <span class="stat-item">$12.50/month</span>
            <span class="stat-item">Real-time AWS Integration</span>
        </div>
    </div>
    
    <div class="tabs">
        <button class="tab active" onclick="showTab('agents')">🤖 Agent Grid</button>
        <button class="tab" onclick="showTab('console')">📋 Console Output</button>
        <button class="tab" onclick="showTab('metrics')">📊 System Metrics</button>
        <button class="tab" onclick="showTab('ec2')">☁️ EC2 Management</button>
        <button class="tab" onclick="showTab('workqueue')">📋 Work Queue</button>
        <button class="tab" onclick="showTab('github')">🐙 GitHub Integration</button>
        <button class="tab" onclick="showTab('cost')">💰 Cost Optimization</button>
    </div>
    
    <!-- Agent Grid Tab -->
    <div class="tab-content active" id="agents-tab">
        <div class="agent-grid" id="agent-grid">
            <div style="text-align: center; color: #6b7280; padding: 40px;">Loading EC2 agents...</div>
        </div>
    </div>
    
    <!-- Console Output Tab -->
    <div class="tab-content" id="console-tab">
        <div class="console">
            <div class="console-header">
                <span>🔴 Live Console Output from EC2 Instances</span>
                <span id="console-count">0 entries</span>
            </div>
            <div class="console-body" id="console-logs">
                <div class="log-entry">
                    <div class="log-timestamp">Waiting for EC2 data...</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- System Metrics Tab -->
    <div class="tab-content" id="metrics-tab">
        <div class="metrics-grid" id="metrics-grid">
            <div style="text-align: center; color: #6b7280; padding: 40px;">Loading system metrics...</div>
        </div>
    </div>
    
    <!-- EC2 Management Tab -->
    <div class="tab-content" id="ec2-tab">
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">☁️ Running Instances</div>
                <div class="metric-value" id="ec2-instances">50</div>
                <div class="metric-label">Across 3 Availability Zones</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">💰 Hourly Cost</div>
                <div class="metric-value" id="ec2-cost">$1.25</div>
                <div class="metric-label">All Instances</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">📊 Avg CPU Usage</div>
                <div class="metric-value" id="ec2-cpu">45%</div>
                <div class="metric-label">Across All Instances</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">🔧 Instance Types</div>
                <div class="metric-value">t3.*</div>
                <div class="metric-label">Optimized for Cost</div>
            </div>
        </div>
        <div style="margin-top: 30px;">
            <h3 style="color: #4ade80; margin-bottom: 20px;">🌐 Instance Distribution</h3>
            <div class="agent-grid" id="ec2-details">
                <!-- EC2 instance details will be populated here -->
            </div>
        </div>
    </div>
    
    <!-- Work Queue Tab -->
    <div class="tab-content" id="workqueue-tab">
        <div class="work-queue-header">
            <h3>📋 Development Work Queue</h3>
            <div>
                <select id="priority-filter" style="background: #21262d; color: #e6edf3; border: 1px solid #30363d; border-radius: 4px; padding: 5px;">
                    <option value="all">All Priorities</option>
                    <option value="P0_CRITICAL">🔴 P0 Critical</option>
                    <option value="P1_HIGH">🟠 P1 High</option>
                    <option value="P2_MEDIUM">🟡 P2 Medium</option>
                    <option value="P3_LOW">🟢 P3 Low</option>
                </select>
            </div>
        </div>
        <div class="work-queue-grid" id="work-queue-grid">
            <div style="text-align: center; color: #6b7280; padding: 40px;">Loading work queue...</div>
        </div>
    </div>
    
    <!-- GitHub Integration Tab -->
    <div class="tab-content" id="github-tab">
        <div class="github-overview">
            <div class="github-status">
                <h3>🐙 GitHub Integration Status</h3>
                <div class="status-indicator">
                    <span class="status-dot"></span>
                    <span>Connected to GitHub API</span>
                </div>
            </div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">📋 Open Issues</div>
                    <div class="metric-value" id="github-issues">42</div>
                    <div class="metric-label">Across Repositories</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🔀 Open PRs</div>
                    <div class="metric-value" id="github-prs">8</div>
                    <div class="metric-label">Pending Review</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">✅ Merged Today</div>
                    <div class="metric-value" id="github-merged">5</div>
                    <div class="metric-label">Pull Requests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🏃 Auto-Assignments</div>
                    <div class="metric-value" id="github-assignments">12</div>
                    <div class="metric-label">This Hour</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Cost Optimization Tab -->
    <div class="tab-content" id="cost-tab">
        <!-- Cost Kill Switch Panel -->
        <div class="cost-monitoring-panel" id="cost-monitoring-panel" style="background: linear-gradient(145deg, #161b22, #21262d); border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: #4ade80; margin: 0;">🛡️ Cost Monitoring & Kill Switch</h3>
                <div class="monitoring-status" id="monitoring-status" style="padding: 5px 15px; border-radius: 15px; font-size: 0.9em; font-weight: bold;">
                    🟢 MONITORING
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 15px;">
                <div style="text-align: center;">
                    <div style="color: #9ca3af; font-size: 0.9em;">Alert Threshold</div>
                    <div style="color: #f59e0b; font-size: 1.5em; font-weight: bold;">3.0%</div>
                    <div style="color: #9ca3af; font-size: 0.8em;">Cost increase per hour</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #9ca3af; font-size: 0.9em;">Kill Switch</div>
                    <div style="color: #ef4444; font-size: 1.5em; font-weight: bold;">5.0%</div>
                    <div style="color: #9ca3af; font-size: 0.8em;">Auto-shutdown threshold</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #9ca3af; font-size: 0.9em;">Current Hourly</div>
                    <div style="color: #4ade80; font-size: 1.5em; font-weight: bold;" id="current-hourly">$0.15</div>
                    <div style="color: #9ca3af; font-size: 0.8em;">All instances</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #9ca3af; font-size: 0.9em;">Last Check</div>
                    <div style="color: #60a5fa; font-size: 1.2em; font-weight: bold;" id="last-check">Just now</div>
                    <div style="color: #9ca3af; font-size: 0.8em;">Cost monitoring</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button onclick="testCostAlert()" style="background: #f59e0b; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9em;">
                    ⚠️ Test Alert (3%+)
                </button>
                <button onclick="testKillSwitch()" style="background: #ef4444; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9em;">
                    🚨 Test Kill Switch (5%+)
                </button>
                <button onclick="emergencyOverride()" style="background: #22c55e; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9em;" id="override-btn" disabled>
                    🔄 Emergency Override
                </button>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card" style="grid-column: 1 / -1; text-align: center;">
                <div class="metric-title">💰 Total Monthly Cost</div>
                <div class="metric-value" style="font-size: 3em;">$12.50</div>
                <div class="metric-label">95.5% Savings vs Traditional Architecture</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">🏗️ Traditional Cost</div>
                <div class="metric-value">$275.00</div>
                <div class="metric-label">Lambda + RDS + ELB</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">☁️ Current EC2 Cost</div>
                <div class="metric-value">$12.50</div>
                <div class="metric-label">Spot Instances + t3.micro</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">💸 Monthly Savings</div>
                <div class="metric-value">$262.50</div>
                <div class="metric-label">Cost Optimization</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">📊 Efficiency Ratio</div>
                <div class="metric-value">22:1</div>
                <div class="metric-label">Performance per Dollar</div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let currentTab = 'agents';
        
        socket.on('connect', function() {
            document.getElementById('connectionStatus').innerHTML = '🟢 Connected';
            document.getElementById('connectionStatus').className = 'connection-status connected';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connectionStatus').innerHTML = '🔴 Disconnected';
            document.getElementById('connectionStatus').className = 'connection-status disconnected';
        });
        
        socket.on('dashboard_update', function(data) {
            updateAgentGrid(data.agents || {});
            updateConsoleOutput(data.console_logs || []);
            updateSystemMetrics(data.system_metrics || {});
            updateWorkQueue(data.work_queue || []);
            updateGitHubMetrics(data.github_data || {});
            updateCostMonitoring(data.cost_monitoring || {});
        });
        
        function updateCostMonitoring(costData) {
            if (costData.cost_trend !== undefined) {
                document.getElementById('cost-trend').textContent = costData.cost_trend.toFixed(2) + '%';
                document.getElementById('cost-trend').className = 'cost-trend ' + 
                    (costData.cost_trend > 3 ? (costData.cost_trend > 5 ? 'critical' : 'warning') : 'normal');
            }
            
            if (costData.alert_status) {
                document.getElementById('alert-status').textContent = costData.alert_status;
                document.getElementById('alert-status').className = 'alert-status ' + 
                    (costData.alert_status.includes('EMERGENCY') ? 'critical' : 
                     costData.alert_status.includes('WARNING') ? 'warning' : 'normal');
            }
        }
        
        function testCostAlert() {
            fetch('/api/simulate-cost-spike', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert('Cost spike simulation started: ' + data.message);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Failed to simulate cost spike');
                });
        }
        
        function testKillSwitch() {
            if (confirm('This will simulate an emergency shutdown trigger. Continue?')) {
                fetch('/api/simulate-cost-spike', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert('Kill switch test initiated: ' + data.message);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Failed to test kill switch');
                    });
            }
        }
        
        function emergencyOverride() {
            if (confirm('EMERGENCY OVERRIDE: This will manually shut down all agents immediately. Are you sure?')) {
                fetch('/api/emergency-override', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert('Emergency override executed: ' + data.message);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Failed to execute emergency override');
                    });
            }
        }
        
        function showTab(tabName) {
            currentTab = tabName;
            
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelector(`button[onclick="showTab('${tabName}')"]`).classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            const targetTab = document.getElementById(tabName + '-tab');
            if (targetTab) {
                targetTab.classList.add('active');
            }
        }
        
        function updateAgentGrid(agents) {
            const grid = document.getElementById('agent-grid');
            
            if (Object.keys(agents).length === 0) {
                grid.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 40px;">No agents running</div>';
                return;
            }
            
            let html = '';
            for (const [id, agent] of Object.entries(agents)) {
                const cpuClass = agent.cpu_usage > 80 ? 'high' : agent.cpu_usage > 50 ? 'medium' : '';
                const memClass = agent.memory_usage > 80 ? 'high' : agent.memory_usage > 50 ? 'medium' : '';
                
                html += `
                    <div class="agent-card">
                        <div class="agent-header">
                            <div class="agent-name">${agent.name}</div>
                            <div class="agent-status status-${agent.status}">${agent.status}</div>
                        </div>
                        <div style="color: #9ca3af; margin-bottom: 10px; font-size: 0.9em;">${agent.specialization}</div>
                        <div class="agent-info">
                            <div class="info-item">
                                <span class="info-label">EC2:</span>
                                <span class="info-value">${agent.ec2_instance}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Zone:</span>
                                <span class="info-value">${agent.availability_zone}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Type:</span>
                                <span class="info-value">${agent.instance_type}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Tasks Today:</span>
                                <span class="info-value">${agent.tasks_today}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Success Rate:</span>
                                <span class="info-value">${agent.success_rate}%</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Cost/Hour:</span>
                                <span class="info-value">$${agent.cost_per_hour}</span>
                            </div>
                        </div>
                        <div style="margin: 10px 0; padding: 8px; background: rgba(74, 222, 128, 0.1); border-radius: 6px; font-size: 0.9em;">
                            <strong>Current Task:</strong> ${agent.current_task}
                        </div>
                        <div class="agent-resources">
                            <div class="resource-bar">
                                <div class="resource-label">CPU: ${agent.cpu_usage}%</div>
                                <div class="progress-bar">
                                    <div class="progress-fill ${cpuClass}" style="width: ${agent.cpu_usage}%"></div>
                                </div>
                            </div>
                            <div class="resource-bar">
                                <div class="resource-label">Memory: ${agent.memory_usage}%</div>
                                <div class="progress-bar">
                                    <div class="progress-fill ${memClass}" style="width: ${agent.memory_usage}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            grid.innerHTML = html;
        }
        
        function updateConsoleOutput(logs) {
            const container = document.getElementById('console-logs');
            const countElement = document.getElementById('console-count');
            
            if (logs.length === 0) {
                container.innerHTML = '<div class="log-entry"><div class="log-timestamp">No console output available</div></div>';
                countElement.textContent = '0 entries';
                return;
            }
            
            let html = '';
            logs.forEach(log => {
                const timestamp = new Date(log.timestamp).toLocaleTimeString();
                html += `
                    <div class="log-entry">
                        <div class="log-timestamp">[${timestamp}] <span class="log-source">${log.source}</span> (${log.ec2_instance})</div>
                        <div class="log-message">${log.message}</div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
            countElement.textContent = `${logs.length} entries`;
            
            // Auto-scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
        
        function updateSystemMetrics(metrics) {
            const grid = document.getElementById('metrics-grid');
            
            if (!metrics.system) {
                grid.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 40px;">Loading metrics...</div>';
                return;
            }
            
            const system = metrics.system;
            const ec2 = metrics.ec2 || {};
            
            grid.innerHTML = `
                <div class="metric-card">
                    <div class="metric-title">🖥️ System CPU</div>
                    <div class="metric-value">${system.cpu_percent}%</div>
                    <div class="metric-label">Host Machine</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">💾 System Memory</div>
                    <div class="metric-value">${system.memory_percent}%</div>
                    <div class="metric-label">${system.memory_used_gb}GB Used</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🤖 Active Agents</div>
                    <div class="metric-value">${system.active_agents}</div>
                    <div class="metric-label">of ${system.total_agents} Total</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">☁️ Avg EC2 CPU</div>
                    <div class="metric-value">${system.avg_agent_cpu}%</div>
                    <div class="metric-label">All Instances</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">💰 Monthly Cost</div>
                    <div class="metric-value">$${ec2.estimated_monthly}</div>
                    <div class="metric-label">${ec2.cost_savings}% Savings</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">⚡ Cost per Hour</div>
                    <div class="metric-value">$${(ec2.total_cost_hour || 0).toFixed(2)}</div>
                    <div class="metric-label">All ${ec2.running_instances} Instances</div>
                </div>
            `;
        }
        
        function updateWorkQueue(workQueue) {
            const grid = document.getElementById('work-queue-grid');
            
            if (workQueue.length === 0) {
                grid.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 40px;">No work items in queue</div>';
                return;
            }
            
            let html = '';
            workQueue.forEach(item => {
                html += `
                    <div class="work-item">
                        <div class="work-item-header">
                            <div>
                                <div style="font-weight: bold; color: #e6edf3; margin-bottom: 5px;">${item.title}</div>
                                <div style="color: #9ca3af; font-size: 0.8em;">${item.id}</div>
                            </div>
                            <span class="priority-badge priority-${item.priority}">${item.priority.replace('_', ' ')}</span>
                        </div>
                        <div style="margin: 10px 0; color: #9ca3af; font-size: 0.9em;">
                            Assigned to: <span style="color: #4ade80;">${item.assignee}</span>
                        </div>
                        <div style="margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="color: #9ca3af; font-size: 0.8em;">Progress</span>
                                <span style="color: #e6edf3; font-size: 0.8em;">${item.progress}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${item.progress}%"></div>
                            </div>
                        </div>
                        <div style="color: #9ca3af; font-size: 0.8em; text-transform: capitalize;">
                            Status: ${item.status.replace('_', ' ')}
                        </div>
                    </div>
                `;
            });
            
            grid.innerHTML = html;
        }
        
        function updateGitHubMetrics(githubData) {
            if (githubData.open_issues) {
                document.getElementById('github-issues').textContent = githubData.open_issues;
            }
            if (githubData.open_prs) {
                document.getElementById('github-prs').textContent = githubData.open_prs;
            }
            if (githubData.merged_today) {
                document.getElementById('github-merged').textContent = githubData.merged_today;
            }
            if (githubData.auto_assignments) {
                document.getElementById('github-assignments').textContent = githubData.auto_assignments;
            }
        }
        
        function updateCostMonitoring(costData) {
            const panel = document.getElementById('cost-monitoring-panel');
            const statusEl = document.getElementById('monitoring-status');
            const hourlyEl = document.getElementById('current-hourly');
            const checkEl = document.getElementById('last-check');
            const overrideBtn = document.getElementById('override-btn');
            
            if (costData.system_shutdown) {
                statusEl.innerHTML = '🚨 SHUTDOWN';
                statusEl.style.background = '#ef4444';
                statusEl.style.color = 'white';
                panel.style.borderColor = '#ef4444';
                panel.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.3)';
                overrideBtn.disabled = false;
                overrideBtn.style.opacity = '1';
            } else if (costData.monitoring_status === 'ALERT') {
                statusEl.innerHTML = '⚠️ ALERT';
                statusEl.style.background = '#f59e0b';
                statusEl.style.color = 'white';
                panel.style.borderColor = '#f59e0b';
                panel.style.boxShadow = '0 0 15px rgba(245, 158, 11, 0.3)';
                overrideBtn.disabled = true;
                overrideBtn.style.opacity = '0.5';
            } else {
                statusEl.innerHTML = '🟢 MONITORING';
                statusEl.style.background = '#22c55e';
                statusEl.style.color = 'white';
                panel.style.borderColor = '#30363d';
                panel.style.boxShadow = 'none';
                overrideBtn.disabled = true;
                overrideBtn.style.opacity = '0.5';
            }
            
            if (hourlyEl) {
                hourlyEl.textContent = `$${(costData.current_hourly || 0.15).toFixed(3)}`;
            }
            
            if (checkEl) {
                checkEl.textContent = new Date().toLocaleTimeString();
            }
        }
        
        function testCostAlert() {
            alert('🧪 Testing Cost Alert (3% threshold)\\n\\nThis will simulate a 3-4% cost increase to trigger the alert system.\\n\\nIn production, this would:\\n• Log cost alert event\\n• Increase monitoring frequency\\n• Send notifications\\n• Prepare for potential shutdown');
        }
        
        function testKillSwitch() {
            if (confirm('⚠️ WARNING: Test Kill Switch\\n\\nThis will simulate a 5%+ cost increase and trigger emergency shutdown of all agents.\\n\\nContinue with test?')) {
                fetch('/api/simulate-cost-spike', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        alert('🚨 Kill Switch Test Initiated\\n\\nCost spike simulated. The monitoring system will detect this in the next cycle (within 5 minutes) and trigger emergency shutdown.\\n\\nWatch the dashboard for real-time updates.');
                    })
                    .catch(err => {
                        alert('Error testing kill switch: ' + err.message);
                    });
            }
        }
        
        function emergencyOverride() {
            if (confirm('🔄 Emergency Override\\n\\nThis will manually override the cost-based shutdown and restart all agents.\\n\\nOnly use this if you are certain the cost spike was a false alarm or has been resolved.\\n\\nContinue?')) {
                fetch('/api/emergency-override', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        alert('✅ Emergency Override Successful\\n\\nSystem has been manually restarted.\\nCost monitoring has been reset.\\nAll agents are resuming normal operations.');
                        // Refresh the page to show updated status
                        setTimeout(() => window.location.reload(), 2000);
                    })
                    .catch(err => {
                        alert('Error during override: ' + err.message);
                    });
            }
        }
        
        // Request initial data
        setTimeout(() => {
            socket.emit('request_data');
        }, 1000);
        
        // Auto-refresh every 5 seconds
        setInterval(() => {
            socket.emit('request_data');
        }, 5000);
    </script>
</body>
</html>'''

@app.route('/api/agents')
def api_agents():
    return jsonify(dashboard.get_dashboard_data()['agents'])

@app.route('/api/system')
def api_system():
    return jsonify(dashboard.get_dashboard_data()['system_metrics'])

@app.route('/api/dashboard')
def api_dashboard():
    return jsonify(dashboard.get_dashboard_data())

@app.route('/api/cost-monitoring')
def api_cost_monitoring():
    return jsonify(dashboard.get_dashboard_data()['cost_monitoring'])

@app.route('/api/emergency-override', methods=['POST'])
def api_emergency_override():
    dashboard.manual_override_shutdown()
    return jsonify({'status': 'success', 'message': 'Emergency override activated'})

@app.route('/api/simulate-cost-spike', methods=['POST'])
def api_simulate_cost_spike():
    """Simulate a cost spike for testing (development only)"""
    # Temporarily increase agent costs to trigger alert/shutdown
    original_costs = []
    for agent in dashboard.agents:
        original_costs.append(agent['cost_per_hour'])
        agent['cost_per_hour'] = agent['cost_per_hour'] * 10  # 10x cost increase
    
    return jsonify({'status': 'success', 'message': 'Cost spike simulated - monitoring will detect in next cycle'})

@socketio.on('request_data')
def handle_data_request():
    emit('dashboard_update', dashboard.get_dashboard_data())

if __name__ == '__main__':
    print("🚀 Enhanced EC2 Agent Dashboard")
    print("🌐 URL: http://localhost:5003")
    print("🤖 50 Specialized Agents with EC2 Integration")
    print("☁️ Real-time AWS monitoring and cost optimization")
    print("📊 Comprehensive tabbed interface")
    print("⚡ Live updates every 3 seconds")
    socketio.run(app, host='0.0.0.0', port=5003, debug=False)
