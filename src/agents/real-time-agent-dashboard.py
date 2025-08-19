#!/usr/bin/env python3
"""
Real-Time Agent Dashboard - Web interface to monitor all running agents
Features: Live process monitoring, log streaming, cost tracking, emergency controls
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import os
import psutil
import subprocess
import threading
import time
from datetime import datetime, timedelta
import queue
import logging
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'agent-dashboard-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class AgentDashboard:
    def __init__(self):
        self.base_dir = Path("E:/Projects")
        self.python_exe = self.base_dir / ".venv/Scripts/python.exe"
        self.running = True
        self.log_queue = queue.Queue()
        
        # Agent monitoring
        self.agents = {}
        self.process_logs = {}
        self.cost_data = {}
        
        # Start monitoring threads
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start all monitoring threads"""
        threading.Thread(target=self.monitor_agents, daemon=True).start()
        threading.Thread(target=self.monitor_costs, daemon=True).start()
        threading.Thread(target=self.collect_logs, daemon=True).start()
        threading.Thread(target=self.broadcast_updates, daemon=True).start()
    
    def monitor_agents(self):
        """Monitor all running agents"""
        while self.running:
            try:
                # Get all python processes
                current_agents = {}
                
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'cpu_percent', 'memory_info', 'create_time']):
                    try:
                        if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            
                            # Check if it's one of our agent scripts
                            agent_scripts = [
                                'monitorable-agent.py', 'aws-cost-monitor.py', 'environment-aware-cost-monitor.py',
                                'gh-copilot-agent-integration.py', 'local-agent-system.py', 'issue-driven-local-agent.py',
                                'sdlc-iterator-agent.py', 'orchestrator-agent.py', 'agent-orchestrator-ai-integration.py',
                                'gh-copilot-orchestrator.py', 'dev-focused-orchestrator.py', 'massive-agent-deployment.py'
                            ]
                            
                            for script in agent_scripts:
                                if script in cmdline:
                                    agent_name = self.extract_agent_name(cmdline, script)
                                    
                                    current_agents[agent_name] = {
                                        'pid': proc.info['pid'],
                                        'script': script,
                                        'cmdline': cmdline,
                                        'status': proc.info['status'],
                                        'cpu_percent': proc.info['cpu_percent'],
                                        'memory_mb': round(proc.info['memory_info'].rss / 1024 / 1024, 1),
                                        'uptime': self.format_uptime(proc.info['create_time']),
                                        'last_seen': datetime.now().isoformat()
                                    }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                self.agents = current_agents
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Agent monitoring error: {e}")
                time.sleep(5)
    
    def extract_agent_name(self, cmdline, script):
        """Extract meaningful agent name from command line"""
        if 'massive-agent-deployment.py' in cmdline:
            return 'massive-deployment'
        elif 'monitorable-agent.py' in cmdline:
            # Extract service name if specified
            parts = cmdline.split()
            if len(parts) > 2:
                return f"monitor-{parts[-1]}"
            return 'monitor-agent'
        elif 'cost-monitor' in script:
            return 'cost-monitor'
        elif 'gh-copilot' in script:
            return 'gh-copilot'
        else:
            return script.replace('.py', '').replace('-', '_')
    
    def format_uptime(self, create_time):
        """Format process uptime"""
        uptime = datetime.now() - datetime.fromtimestamp(create_time)
        if uptime.days > 0:
            return f"{uptime.days}d {uptime.seconds//3600}h"
        elif uptime.seconds > 3600:
            return f"{uptime.seconds//3600}h {(uptime.seconds%3600)//60}m"
        else:
            return f"{uptime.seconds//60}m {uptime.seconds%60}s"
    
    def monitor_costs(self):
        """Monitor AWS costs"""
        while self.running:
            try:
                # Try to get cost data from our cost monitor
                cost_file = self.base_dir / "cost_monitor_status.json"
                if cost_file.exists():
                    with open(cost_file, 'r') as f:
                        self.cost_data = json.load(f)
                else:
                    # Default cost data
                    self.cost_data = {
                        'current_cost': 0.0,
                        'threshold': 25.0,
                        'percentage_used': 0.0,
                        'last_check': datetime.now().isoformat(),
                        'status': 'monitoring'
                    }
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                print(f"Cost monitoring error: {e}")
                time.sleep(60)
    
    def collect_logs(self):
        """Collect logs from various sources"""
        while self.running:
            try:
                # Check for log files
                log_files = [
                    self.base_dir / "massive_deployment_log.json",
                    self.base_dir / "agent_logs" / f"test_results_{datetime.now().strftime('%Y%m%d')}_*.json"
                ]
                
                for log_pattern in log_files:
                    if '*' in str(log_pattern):
                        # Handle glob patterns
                        import glob
                        for log_file in glob.glob(str(log_pattern)):
                            self.process_log_file(log_file)
                    elif log_pattern.exists():
                        self.process_log_file(log_pattern)
                
                time.sleep(5)
                
            except Exception as e:
                print(f"Log collection error: {e}")
                time.sleep(10)
    
    def process_log_file(self, log_file):
        """Process a single log file"""
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
                
            filename = os.path.basename(log_file)
            self.process_logs[filename] = {
                'data': data,
                'last_modified': os.path.getmtime(log_file),
                'size': os.path.getsize(log_file)
            }
        except Exception as e:
            print(f"Error processing {log_file}: {e}")
    
    def broadcast_updates(self):
        """Broadcast updates to all connected clients"""
        while self.running:
            try:
                update_data = {
                    'timestamp': datetime.now().isoformat(),
                    'agents': self.agents,
                    'costs': self.cost_data,
                    'logs': self.process_logs,
                    'summary': {
                        'total_agents': len(self.agents),
                        'running_agents': len([a for a in self.agents.values() if a['status'] == 'running']),
                        'total_memory': sum(a['memory_mb'] for a in self.agents.values()),
                        'avg_cpu': round(sum(a['cpu_percent'] for a in self.agents.values()) / max(1, len(self.agents)), 1)
                    }
                }
                
                socketio.emit('dashboard_update', update_data)
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"Broadcast error: {e}")
                time.sleep(5)
    
    def emergency_stop_all(self):
        """Emergency stop all agents"""
        stopped = []
        for agent_name, agent_info in self.agents.items():
            try:
                proc = psutil.Process(agent_info['pid'])
                proc.terminate()
                stopped.append(agent_name)
            except:
                pass
        return stopped
    
    def restart_agent(self, agent_name):
        """Restart a specific agent"""
        if agent_name in self.agents:
            agent_info = self.agents[agent_name]
            try:
                # Stop the current process
                proc = psutil.Process(agent_info['pid'])
                proc.terminate()
                
                # Wait a bit
                time.sleep(2)
                
                # Start new process
                script_path = self.base_dir / agent_info['script']
                subprocess.Popen([str(self.python_exe), str(script_path)], 
                               cwd=str(self.base_dir))
                return True
            except Exception as e:
                print(f"Restart error for {agent_name}: {e}")
                return False
        return False

# Global dashboard instance
dashboard = AgentDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/agents')
def get_agents():
    """Get all agent data"""
    return jsonify({
        'agents': dashboard.agents,
        'summary': {
            'total': len(dashboard.agents),
            'running': len([a for a in dashboard.agents.values() if a['status'] == 'running'])
        }
    })

@app.route('/api/costs')
def get_costs():
    """Get cost data"""
    return jsonify(dashboard.cost_data)

@app.route('/api/logs')
def get_logs():
    """Get log data"""
    return jsonify(dashboard.process_logs)

@app.route('/api/emergency_stop', methods=['POST'])
def emergency_stop():
    """Emergency stop all agents"""
    stopped = dashboard.emergency_stop_all()
    return jsonify({'stopped': stopped, 'count': len(stopped)})

@app.route('/api/restart/<agent_name>', methods=['POST'])
def restart_agent(agent_name):
    """Restart specific agent"""
    success = dashboard.restart_agent(agent_name)
    return jsonify({'success': success, 'agent': agent_name})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'status': 'Connected to Agent Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

# Create templates directory and HTML template
def create_template():
    """Create the HTML template"""
    template_dir = Path("E:/Projects/templates")
    template_dir.mkdir(exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Dashboard - Real-Time Monitoring</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #1a1a1a; 
            color: #fff; 
            overflow-x: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 20px; 
            text-align: center; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header .subtitle { opacity: 0.9; font-size: 1.1em; }
        .controls { 
            background: #2a2a2a; 
            padding: 15px; 
            text-align: center; 
            border-bottom: 1px solid #444;
        }
        .btn { 
            background: #4CAF50; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            margin: 0 10px; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 14px;
            transition: all 0.3s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .btn.danger { background: #f44336; }
        .btn.warning { background: #ff9800; }
        .dashboard { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px; 
            padding: 20px; 
            max-width: 1400px; 
            margin: 0 auto;
        }
        .panel { 
            background: #2a2a2a; 
            border-radius: 10px; 
            padding: 20px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            border: 1px solid #444;
        }
        .panel h2 { 
            margin-bottom: 15px; 
            color: #64b5f6; 
            border-bottom: 2px solid #64b5f6; 
            padding-bottom: 5px;
        }
        .agent-grid { 
            display: grid; 
            gap: 10px; 
            max-height: 400px; 
            overflow-y: auto;
        }
        .agent-item { 
            background: #333; 
            padding: 15px; 
            border-radius: 8px; 
            border-left: 4px solid #4CAF50;
            transition: all 0.3s;
        }
        .agent-item:hover { transform: translateX(5px); }
        .agent-item.stopped { border-left-color: #f44336; opacity: 0.7; }
        .agent-name { 
            font-weight: bold; 
            color: #81c784; 
            margin-bottom: 5px;
            font-size: 1.1em;
        }
        .agent-details { 
            font-size: 0.9em; 
            color: #bbb; 
            line-height: 1.4;
        }
        .status-indicator { 
            display: inline-block; 
            width: 10px; 
            height: 10px; 
            border-radius: 50%; 
            margin-right: 8px;
        }
        .status-running { background: #4CAF50; }
        .status-stopped { background: #f44336; }
        .summary-stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); 
            gap: 15px; 
            margin-bottom: 20px;
        }
        .stat-box { 
            background: #333; 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center;
        }
        .stat-value { 
            font-size: 2em; 
            font-weight: bold; 
            color: #64b5f6; 
            display: block;
        }
        .stat-label { 
            font-size: 0.9em; 
            color: #bbb; 
            margin-top: 5px;
        }
        .cost-display { 
            background: linear-gradient(135deg, #ff6b6b, #ee5a24); 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
            margin-bottom: 20px;
        }
        .cost-amount { 
            font-size: 3em; 
            font-weight: bold; 
            margin-bottom: 10px;
        }
        .cost-threshold { 
            opacity: 0.8; 
            font-size: 1.1em;
        }
        .log-container { 
            background: #1a1a1a; 
            border: 1px solid #444; 
            border-radius: 5px; 
            max-height: 300px; 
            overflow-y: auto; 
            padding: 10px; 
            font-family: 'Courier New', monospace; 
            font-size: 0.9em;
        }
        .log-entry { 
            padding: 5px 0; 
            border-bottom: 1px solid #333;
        }
        .timestamp { 
            color: #64b5f6; 
            margin-right: 10px;
        }
        .connection-status { 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            padding: 10px 15px; 
            border-radius: 5px; 
            font-weight: bold;
            z-index: 1000;
        }
        .connected { background: #4CAF50; }
        .disconnected { background: #f44336; }
        @media (max-width: 768px) {
            .dashboard { grid-template-columns: 1fr; }
            .header h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">Connecting...</div>
    
    <div class="header">
        <h1>🚀 Agent Dashboard</h1>
        <div class="subtitle">Real-Time Process Monitoring | Last Update: <span id="lastUpdate">--</span></div>
    </div>
    
    <div class="controls">
        <button class="btn danger" onclick="emergencyStop()">🛑 Emergency Stop All</button>
        <button class="btn warning" onclick="refreshData()">🔄 Refresh</button>
        <button class="btn" onclick="exportLogs()">📋 Export Logs</button>
    </div>
    
    <div class="dashboard">
        <div class="panel">
            <h2>📊 System Overview</h2>
            <div class="summary-stats" id="summaryStats">
                <div class="stat-box">
                    <span class="stat-value" id="totalAgents">--</span>
                    <div class="stat-label">Total Agents</div>
                </div>
                <div class="stat-box">
                    <span class="stat-value" id="runningAgents">--</span>
                    <div class="stat-label">Running</div>
                </div>
                <div class="stat-box">
                    <span class="stat-value" id="totalMemory">--</span>
                    <div class="stat-label">Memory (MB)</div>
                </div>
                <div class="stat-box">
                    <span class="stat-value" id="avgCpu">--</span>
                    <div class="stat-label">Avg CPU %</div>
                </div>
            </div>
            
            <div class="cost-display">
                <div class="cost-amount" id="currentCost">$0.00</div>
                <div class="cost-threshold">Threshold: <span id="costThreshold">$25.00</span></div>
            </div>
        </div>
        
        <div class="panel">
            <h2>🤖 Active Agents</h2>
            <div class="agent-grid" id="agentGrid">
                <div style="text-align: center; color: #666; padding: 20px;">
                    Loading agents...
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2>📋 Recent Logs</h2>
            <div class="log-container" id="logContainer">
                <div class="log-entry">
                    <span class="timestamp">[Starting]</span>
                    <span>Dashboard initializing...</span>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2>📈 Performance Metrics</h2>
            <canvas id="performanceChart" width="400" height="200"></canvas>
        </div>
    </div>

    <script>
        const socket = io();
        let performanceChart;
        
        // Connection status
        socket.on('connect', function() {
            document.getElementById('connectionStatus').textContent = '🟢 Connected';
            document.getElementById('connectionStatus').className = 'connection-status connected';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connectionStatus').textContent = '🔴 Disconnected';
            document.getElementById('connectionStatus').className = 'connection-status disconnected';
        });
        
        // Dashboard updates
        socket.on('dashboard_update', function(data) {
            updateDashboard(data);
        });
        
        function updateDashboard(data) {
            // Update timestamp
            document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleTimeString();
            
            // Update summary stats
            if (data.summary) {
                document.getElementById('totalAgents').textContent = data.summary.total_agents;
                document.getElementById('runningAgents').textContent = data.summary.running_agents;
                document.getElementById('totalMemory').textContent = data.summary.total_memory;
                document.getElementById('avgCpu').textContent = data.summary.avg_cpu + '%';
            }
            
            // Update cost display
            if (data.costs) {
                document.getElementById('currentCost').textContent = '$' + (data.costs.current_cost || 0).toFixed(2);
                document.getElementById('costThreshold').textContent = '$' + (data.costs.threshold || 25).toFixed(2);
            }
            
            // Update agents
            updateAgentGrid(data.agents);
            
            // Update logs
            updateLogs(data.logs);
        }
        
        function updateAgentGrid(agents) {
            const grid = document.getElementById('agentGrid');
            if (!agents || Object.keys(agents).length === 0) {
                grid.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">No agents running</div>';
                return;
            }
            
            let html = '';
            for (const [name, agent] of Object.entries(agents)) {
                const statusClass = agent.status === 'running' ? 'status-running' : 'status-stopped';
                const itemClass = agent.status === 'running' ? 'agent-item' : 'agent-item stopped';
                
                html += `
                    <div class="${itemClass}">
                        <div class="agent-name">
                            <span class="status-indicator ${statusClass}"></span>
                            ${name}
                        </div>
                        <div class="agent-details">
                            PID: ${agent.pid} | CPU: ${agent.cpu_percent}% | Memory: ${agent.memory_mb}MB<br>
                            Status: ${agent.status} | Uptime: ${agent.uptime}<br>
                            Script: ${agent.script}
                        </div>
                    </div>
                `;
            }
            grid.innerHTML = html;
        }
        
        function updateLogs(logs) {
            const container = document.getElementById('logContainer');
            let html = '';
            
            if (logs && Object.keys(logs).length > 0) {
                for (const [filename, logData] of Object.entries(logs)) {
                    html += `
                        <div class="log-entry">
                            <span class="timestamp">[${new Date(logData.last_modified * 1000).toLocaleTimeString()}]</span>
                            <span>${filename} (${(logData.size / 1024).toFixed(1)}KB)</span>
                        </div>
                    `;
                }
            } else {
                html = '<div class="log-entry"><span class="timestamp">[--]</span><span>No logs available</span></div>';
            }
            
            container.innerHTML = html;
        }
        
        function emergencyStop() {
            if (confirm('Are you sure you want to stop ALL agents? This cannot be undone.')) {
                fetch('/api/emergency_stop', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert(`Stopped ${data.count} agents: ${data.stopped.join(', ')}`);
                    });
            }
        }
        
        function refreshData() {
            location.reload();
        }
        
        function exportLogs() {
            fetch('/api/logs')
                .then(response => response.json())
                .then(data => {
                    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'agent_logs_' + new Date().toISOString().slice(0,19).replace(/:/g, '-') + '.json';
                    a.click();
                });
        }
        
        // Initialize performance chart
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Total Memory (MB)',
                        data: [],
                        borderColor: '#64b5f6',
                        tension: 0.1
                    }, {
                        label: 'Running Agents',
                        data: [],
                        borderColor: '#4CAF50',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#fff'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#fff'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#fff'
                            }
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>'''
    
    with open(template_dir / "dashboard.html", 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    # Create template
    create_template()
    
    print("=" * 80)
    print("🚀 REAL-TIME AGENT DASHBOARD STARTING")
    print("=" * 80)
    print("📊 Dashboard URL: http://localhost:5000")
    print("🔄 Real-time updates every second")
    print("🛡️ Emergency controls available")
    print("📋 Log monitoring and export")
    print("=" * 80)
    
    # Start the dashboard
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
