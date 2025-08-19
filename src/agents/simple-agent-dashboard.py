#!/usr/bin/env python3
"""
Simple Agent Dashboard - Web interface for monitoring and controlling agents
Uses Flask for simplicity instead of Node.js to avoid dependency issues
"""

import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import psutil
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'agent-dashboard-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class SimpleAgentManager:
    def __init__(self):
        self.projects_dir = Path("E:/Projects")
        self.agents = {}
        self.running_processes = {}
        self.initialize_agents()
    
    def initialize_agents(self):
        """Initialize available agents"""
        self.agents = {
            'gh-copilot-orchestrator': {
                'id': 'gh-copilot-orchestrator',
                'name': 'GitHub Copilot Orchestrator',
                'script': 'gh-copilot-orchestrator.py',
                'status': 'stopped',
                'description': 'Interactive GitHub Copilot testing orchestrator'
            },
            'local-orchestrator': {
                'id': 'local-orchestrator', 
                'name': 'Local Orchestrator',
                'script': 'local-orchestrator.py',
                'status': 'stopped',
                'description': 'Local system resource-aware orchestrator'
            },
            'run-gh-copilot-tests': {
                'id': 'run-gh-copilot-tests',
                'name': 'Automated Copilot Tests',
                'script': 'run-gh-copilot-tests.py', 
                'status': 'stopped',
                'description': 'Automated test orchestrator with remediation'
            }
        }
    
    def get_agent_status(self, agent_id):
        """Check if agent is actually running"""
        if agent_id in self.running_processes:
            proc = self.running_processes[agent_id]
            if proc.poll() is None:  # Still running
                return 'running'
            else:
                # Process ended
                del self.running_processes[agent_id]
                return 'stopped'
        return 'stopped'
    
    def start_agent(self, agent_id):
        """Start an agent"""
        if agent_id not in self.agents:
            return {'success': False, 'error': 'Agent not found'}
        
        if self.get_agent_status(agent_id) == 'running':
            return {'success': False, 'error': 'Agent already running'}
        
        agent = self.agents[agent_id]
        script_path = self.projects_dir / agent['script']
        
        if not script_path.exists():
            return {'success': False, 'error': f'Script not found: {agent["script"]}'}
        
        try:
            # Start the process
            python_exe = self.projects_dir / '.venv' / 'Scripts' / 'python.exe'
            cmd = [str(python_exe), str(script_path)]
            
            # Add specific arguments for different agents
            if agent_id == 'gh-copilot-orchestrator':
                cmd.append('--interactive')
            elif agent_id == 'local-orchestrator':
                cmd.extend(['--auto', '--env', 'dev'])
            
            proc = subprocess.Popen(
                cmd,
                cwd=str(self.projects_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.running_processes[agent_id] = proc
            self.agents[agent_id]['status'] = 'running'
            self.agents[agent_id]['started_at'] = datetime.now().isoformat()
            
            # Start output monitoring thread
            threading.Thread(
                target=self._monitor_output,
                args=(agent_id, proc),
                daemon=True
            ).start()
            
            return {'success': True, 'message': f'Agent {agent_id} started'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def stop_agent(self, agent_id):
        """Stop an agent"""
        if agent_id not in self.running_processes:
            return {'success': False, 'error': 'Agent not running'}
        
        try:
            proc = self.running_processes[agent_id]
            proc.terminate()
            proc.wait(timeout=5)
            
            del self.running_processes[agent_id]
            self.agents[agent_id]['status'] = 'stopped'
            
            return {'success': True, 'message': f'Agent {agent_id} stopped'}
            
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't terminate
            proc.kill()
            del self.running_processes[agent_id]
            self.agents[agent_id]['status'] = 'stopped'
            return {'success': True, 'message': f'Agent {agent_id} force stopped'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _monitor_output(self, agent_id, proc):
        """Monitor agent output and broadcast via websockets"""
        while proc.poll() is None:
            try:
                line = proc.stdout.readline()
                if line:
                    socketio.emit('agent_output', {
                        'agent_id': agent_id,
                        'data': line.strip(),
                        'timestamp': datetime.now().isoformat()
                    })
                time.sleep(0.1)
            except:
                break
        
        # Process ended
        if agent_id in self.running_processes:
            del self.running_processes[agent_id]
            self.agents[agent_id]['status'] = 'stopped'
            socketio.emit('agent_status_changed', {
                'agent_id': agent_id,
                'status': 'stopped'
            })
    
    def get_all_agents(self):
        """Get all agents with current status"""
        for agent_id in self.agents:
            self.agents[agent_id]['status'] = self.get_agent_status(agent_id)
        return list(self.agents.values())

# Initialize manager
agent_manager = SimpleAgentManager()

def get_system_metrics():
    """Get system resource metrics"""
    return {
        'cpu': psutil.cpu_percent(interval=0.1),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
        'timestamp': datetime.now().isoformat()
    }

# HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Agent Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .agent-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .agent-status { padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; display: inline-block; }
        .status-running { background: #4CAF50; }
        .status-stopped { background: #f44336; }
        .btn { padding: 8px 16px; margin: 4px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .btn-start { background: #4CAF50; color: white; }
        .btn-stop { background: #f44336; color: white; }
        .btn:hover { opacity: 0.8; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .metrics { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .metric { text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; }
        .log-panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .log-output { background: #1e1e1e; color: #fff; padding: 15px; border-radius: 4px; max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 14px; }
        .log-line { margin-bottom: 5px; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Agent Dashboard</h1>
            <p>Monitor and control your AI agents</p>
        </div>
        
        <div class="metrics">
            <h3>System Metrics</h3>
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value" id="cpu-metric">--</div>
                    <div>CPU %</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="memory-metric">--</div>
                    <div>Memory %</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="disk-metric">--</div>
                    <div>Disk %</div>
                </div>
            </div>
        </div>
        
        <div id="agents-container" class="agents-grid">
            <!-- Agents will be populated here -->
        </div>
        
        <div class="log-panel">
            <h3>Agent Output</h3>
            <div id="log-output" class="log-output">
                <div class="log-line">Dashboard ready. Start an agent to see output...</div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        
        // Connect to socket
        socket.on('connect', function() {
            console.log('Connected to dashboard');
            loadAgents();
        });
        
        // Handle agent status updates
        socket.on('agents_status', function(agents) {
            renderAgents(agents);
        });
        
        // Handle system metrics
        socket.on('system_metrics', function(metrics) {
            document.getElementById('cpu-metric').textContent = metrics.cpu.toFixed(1);
            document.getElementById('memory-metric').textContent = metrics.memory.toFixed(1);
            document.getElementById('disk-metric').textContent = metrics.disk.toFixed(1);
        });
        
        // Handle agent output
        socket.on('agent_output', function(data) {
            const logOutput = document.getElementById('log-output');
            const logLine = document.createElement('div');
            logLine.className = 'log-line';
            logLine.innerHTML = `<span style="color: #888">[${data.agent_id}]</span> ${data.data}`;
            logOutput.appendChild(logLine);
            logOutput.scrollTop = logOutput.scrollHeight;
            
            // Keep only last 100 lines
            while (logOutput.children.length > 100) {
                logOutput.removeChild(logOutput.firstChild);
            }
        });
        
        // Load agents
        function loadAgents() {
            fetch('/api/agents')
                .then(r => r.json())
                .then(agents => renderAgents(agents));
        }
        
        // Render agents
        function renderAgents(agents) {
            const container = document.getElementById('agents-container');
            container.innerHTML = agents.map(agent => `
                <div class="agent-card">
                    <h3>
                        <span class="status-indicator ${agent.status === 'running' ? 'status-running' : 'status-stopped'}"></span>
                        ${agent.name}
                    </h3>
                    <p>${agent.description}</p>
                    <div class="agent-status status-${agent.status}">${agent.status.toUpperCase()}</div>
                    <div style="margin-top: 15px;">
                        <button class="btn btn-start" onclick="startAgent('${agent.id}')" 
                                ${agent.status === 'running' ? 'disabled' : ''}>
                            Start
                        </button>
                        <button class="btn btn-stop" onclick="stopAgent('${agent.id}')"
                                ${agent.status === 'stopped' ? 'disabled' : ''}>
                            Stop
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        // Start agent
        function startAgent(agentId) {
            fetch(`/api/agents/${agentId}/start`, { method: 'POST' })
                .then(r => r.json())
                .then(result => {
                    if (result.success) {
                        addLogLine(`Started agent: ${agentId}`);
                    } else {
                        addLogLine(`Failed to start ${agentId}: ${result.error}`);
                    }
                    loadAgents();
                });
        }
        
        // Stop agent
        function stopAgent(agentId) {
            fetch(`/api/agents/${agentId}/stop`, { method: 'POST' })
                .then(r => r.json())
                .then(result => {
                    if (result.success) {
                        addLogLine(`Stopped agent: ${agentId}`);
                    } else {
                        addLogLine(`Failed to stop ${agentId}: ${result.error}`);
                    }
                    loadAgents();
                });
        }
        
        // Add log line
        function addLogLine(message) {
            const logOutput = document.getElementById('log-output');
            const logLine = document.createElement('div');
            logLine.className = 'log-line';
            logLine.innerHTML = `<span style="color: #0f0">[dashboard]</span> ${message}`;
            logOutput.appendChild(logLine);
            logOutput.scrollTop = logOutput.scrollHeight;
        }
        
        // Load initial data
        loadAgents();
        
        // Request metrics updates
        setInterval(() => {
            fetch('/api/system/metrics')
                .then(r => r.json())
                .then(metrics => {
                    socket.emit('system_metrics', metrics);
                });
        }, 2000);
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/agents')
def get_agents():
    return jsonify(agent_manager.get_all_agents())

@app.route('/api/agents/<agent_id>/start', methods=['POST'])
def start_agent(agent_id):
    result = agent_manager.start_agent(agent_id)
    socketio.emit('agents_status', agent_manager.get_all_agents())
    return jsonify(result)

@app.route('/api/agents/<agent_id>/stop', methods=['POST'])
def stop_agent(agent_id):
    result = agent_manager.stop_agent(agent_id)
    socketio.emit('agents_status', agent_manager.get_all_agents())
    return jsonify(result)

@app.route('/api/system/metrics')
def system_metrics():
    return jsonify(get_system_metrics())

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('agents_status', agent_manager.get_all_agents())
    emit('system_metrics', get_system_metrics())

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

def broadcast_updates():
    """Background thread to broadcast updates"""
    while True:
        try:
            socketio.emit('system_metrics', get_system_metrics())
            socketio.emit('agents_status', agent_manager.get_all_agents())
            time.sleep(2)
        except:
            pass

if __name__ == '__main__':
    # Start background update thread
    update_thread = threading.Thread(target=broadcast_updates, daemon=True)
    update_thread.start()
    
    print("🚀 Starting Simple Agent Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔧 Monitoring agents in: E:/Projects")
    
    # Run the dashboard
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
