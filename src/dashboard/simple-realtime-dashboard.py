#!/usr/bin/env python3
"""
Simplified Real-Time Dashboard - More reliable process detection
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import json
import os
import psutil
import threading
import time
from datetime import datetime
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple-dashboard'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class SimpleDashboard:
    def __init__(self):
        self.running = True
        self.agent_data = {
            'agents': {},
            'summary': {
                'total': 0,
                'running': 0,
                'memory_total': 0,
                'cpu_avg': 0
            },
            'last_update': datetime.now().isoformat()
        }
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring thread"""
        def monitor():
            while self.running:
                try:
                    self.update_agent_data()
                    socketio.emit('update', self.agent_data)
                    time.sleep(1)  # Update every second
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def update_agent_data(self):
        """Update agent data from system processes"""
        agents = {}
        total_memory = 0
        total_cpu = 0
        running_count = 0
        
        try:
            # Get all python processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'cpu_percent', 'memory_info', 'create_time']):
                try:
                    if proc.info['name'] in ['python.exe', 'python3.exe', 'python'] and proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        
                        # Look for our agent scripts
                        agent_files = [
                            'monitorable-agent.py', 'aws-cost-monitor.py', 'environment-aware-cost-monitor.py',
                            'gh-copilot-agent-integration.py', 'local-agent-system.py', 'issue-driven-local-agent.py',
                            'sdlc-iterator-agent.py', 'orchestrator-agent.py', 'agent-orchestrator-ai-integration.py',
                            'massive-agent-deployment.py', 'real-time-agent-dashboard.py', 'gh-copilot-orchestrator.py'
                        ]
                        
                        for agent_file in agent_files:
                            if agent_file in cmdline:
                                agent_name = self.get_agent_name(cmdline, agent_file)
                                
                                memory_mb = round(proc.info['memory_info'].rss / 1024 / 1024, 1)
                                cpu_percent = proc.info['cpu_percent'] or 0
                                
                                agents[agent_name] = {
                                    'pid': proc.info['pid'],
                                    'name': agent_name,
                                    'script': agent_file,
                                    'status': proc.info['status'],
                                    'memory_mb': memory_mb,
                                    'cpu_percent': cpu_percent,
                                    'uptime': self.get_uptime(proc.info['create_time']),
                                    'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline
                                }
                                
                                total_memory += memory_mb
                                total_cpu += cpu_percent
                                if proc.info['status'] == 'running':
                                    running_count += 1
                                break
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Update summary
            total_agents = len(agents)
            avg_cpu = round(total_cpu / max(1, total_agents), 1)
            
            self.agent_data = {
                'agents': agents,
                'summary': {
                    'total': total_agents,
                    'running': running_count,
                    'memory_total': round(total_memory, 1),
                    'cpu_avg': avg_cpu
                },
                'last_update': datetime.now().isoformat(),
                'system_info': self.get_system_info()
            }
            
        except Exception as e:
            print(f"Error updating agent data: {e}")
    
    def get_agent_name(self, cmdline, script):
        """Extract agent name from command line"""
        if 'massive-agent-deployment.py' in script:
            return 'massive-deployment'
        elif 'real-time-agent-dashboard.py' in script:
            return 'dashboard'
        elif 'monitorable-agent.py' in script:
            # Try to get service name from args
            parts = cmdline.split()
            if len(parts) > 2:
                service = parts[-1]
                if service not in ['single', 'cycle', '.py']:
                    return f"monitor-{service}"
            return 'monitor-agent'
        else:
            return script.replace('.py', '').replace('-', '_')
    
    def get_uptime(self, create_time):
        """Get process uptime"""
        try:
            uptime = datetime.now() - datetime.fromtimestamp(create_time)
            if uptime.days > 0:
                return f"{uptime.days}d {uptime.seconds//3600}h"
            elif uptime.seconds > 3600:
                return f"{uptime.seconds//3600}h {(uptime.seconds%3600)//60}m"
            else:
                return f"{uptime.seconds//60}m"
        except:
            return "Unknown"
    
    def get_system_info(self):
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'memory_used_gb': round(memory.used / 1024**3, 1),
                'memory_total_gb': round(memory.total / 1024**3, 1)
            }
        except:
            return {}

# Global dashboard
dashboard = SimpleDashboard()

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Simple Agent Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .status { background: #2a2a2a; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .agents { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
        .agent { background: #333; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50; }
        .agent.stopped { border-left-color: #f44336; opacity: 0.7; }
        .agent-name { font-weight: bold; color: #81c784; font-size: 1.1em; margin-bottom: 8px; }
        .agent-info { font-size: 0.9em; color: #bbb; line-height: 1.4; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat { background: #333; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 1.8em; font-weight: bold; color: #64b5f6; }
        .stat-label { color: #bbb; margin-top: 5px; }
        .connected { color: #4CAF50; }
        .disconnected { color: #f44336; }
        .refresh-btn { background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        .refresh-btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Agent Dashboard</h1>
        <p>Real-time monitoring | Status: <span id="status" class="disconnected">Connecting...</span></p>
        <p>Last Update: <span id="lastUpdate">--</span></p>
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
    </div>
    
    <div class="status">
        <div class="summary" id="summary">
            <div class="stat">
                <div class="stat-value" id="totalAgents">--</div>
                <div class="stat-label">Total Agents</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="runningAgents">--</div>
                <div class="stat-label">Running</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="totalMemory">--</div>
                <div class="stat-label">Memory (MB)</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="avgCpu">--</div>
                <div class="stat-label">Avg CPU %</div>
            </div>
        </div>
    </div>
    
    <div class="agents" id="agents">
        <div style="grid-column: 1/-1; text-align: center; color: #666; padding: 20px;">
            Loading agents...
        </div>
    </div>
    
    <script>
        const socket = io();
        
        socket.on('connect', function() {
            document.getElementById('status').textContent = 'Connected';
            document.getElementById('status').className = 'connected';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('status').textContent = 'Disconnected';
            document.getElementById('status').className = 'disconnected';
        });
        
        socket.on('update', function(data) {
            updateDashboard(data);
        });
        
        function updateDashboard(data) {
            // Update timestamp
            document.getElementById('lastUpdate').textContent = new Date(data.last_update).toLocaleTimeString();
            
            // Update summary
            document.getElementById('totalAgents').textContent = data.summary.total;
            document.getElementById('runningAgents').textContent = data.summary.running;
            document.getElementById('totalMemory').textContent = data.summary.memory_total;
            document.getElementById('avgCpu').textContent = data.summary.cpu_avg + '%';
            
            // Update agents
            const agentsDiv = document.getElementById('agents');
            if (Object.keys(data.agents).length === 0) {
                agentsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #666; padding: 20px;">No agents running</div>';
                return;
            }
            
            let html = '';
            for (const [name, agent] of Object.entries(data.agents)) {
                const statusClass = agent.status === 'running' ? 'agent' : 'agent stopped';
                html += `
                    <div class="${statusClass}">
                        <div class="agent-name">${agent.name}</div>
                        <div class="agent-info">
                            PID: ${agent.pid}<br>
                            Status: ${agent.status}<br>
                            Memory: ${agent.memory_mb} MB<br>
                            CPU: ${agent.cpu_percent}%<br>
                            Uptime: ${agent.uptime}<br>
                            Script: ${agent.script}
                        </div>
                    </div>
                `;
            }
            agentsDiv.innerHTML = html;
        }
        
        // Request initial data
        fetch('/api/data')
            .then(response => response.json())
            .then(data => updateDashboard(data));
    </script>
</body>
</html>'''

@app.route('/api/data')
def get_data():
    return jsonify(dashboard.agent_data)

@socketio.on('connect')
def handle_connect():
    emit('update', dashboard.agent_data)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SIMPLIFIED AGENT DASHBOARD")
    print("=" * 60)
    print("📊 URL: http://localhost:5001")
    print("🔄 Real-time updates via WebSocket")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
