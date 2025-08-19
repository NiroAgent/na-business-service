#!/usr/bin/env python3
"""
Ultra Simple Agent Dashboard - Minimal web interface that definitely works
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
import psutil
import urllib.parse

class AgentDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/agents':
            self.serve_agents()
        elif self.path == '/api/metrics':
            self.serve_metrics()
        elif self.path == '/api/status':
            self.serve_status()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path.startswith('/api/agents/') and self.path.endswith('/start'):
            agent_id = self.path.split('/')[-2]
            self.start_agent(agent_id)
        elif self.path.startswith('/api/agents/') and self.path.endswith('/stop'):
            agent_id = self.path.split('/')[-2]
            self.stop_agent(agent_id)
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Simple Agent Dashboard</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .agent-card { background: #f9f9f9; padding: 15px; border-radius: 6px; border: 1px solid #ddd; }
        .status-running { background: #4CAF50; color: white; padding: 4px 8px; border-radius: 4px; }
        .status-stopped { background: #f44336; color: white; padding: 4px 8px; border-radius: 4px; }
        .btn { padding: 8px 16px; margin: 4px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-start { background: #4CAF50; color: white; }
        .btn-stop { background: #f44336; color: white; }
        .btn:hover { opacity: 0.8; }
        .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #333; }
        .log-area { background: #1e1e1e; color: #fff; padding: 15px; border-radius: 4px; max-height: 300px; overflow-y: auto; font-family: monospace; }
        .refresh-btn { background: #008CBA; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Simple Agent Dashboard</h1>
            <p>Monitor and control your AI agents</p>
            <button class="refresh-btn" onclick="refreshAll()">🔄 Refresh All</button>
        </div>
        
        <div class="section">
            <h3>System Metrics</h3>
            <div class="metrics" id="metrics">
                <div><div class="metric-value" id="cpu">Loading...</div><div>CPU %</div></div>
                <div><div class="metric-value" id="memory">Loading...</div><div>Memory %</div></div>
                <div><div class="metric-value" id="disk">Loading...</div><div>Disk %</div></div>
            </div>
        </div>
        
        <div class="section">
            <h3>Agents</h3>
            <div class="agents-grid" id="agents">
                Loading agents...
            </div>
        </div>
        
        <div class="section">
            <h3>System Status</h3>
            <div class="log-area" id="status">
                Loading status...
            </div>
        </div>
    </div>

    <script>
        function refreshAll() {
            loadMetrics();
            loadAgents();
            loadStatus();
        }
        
        function loadMetrics() {
            fetch('/api/metrics')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('cpu').textContent = data.cpu.toFixed(1);
                    document.getElementById('memory').textContent = data.memory.toFixed(1);
                    document.getElementById('disk').textContent = data.disk.toFixed(1);
                })
                .catch(e => console.error('Error loading metrics:', e));
        }
        
        function loadAgents() {
            fetch('/api/agents')
                .then(r => r.json())
                .then(agents => {
                    const container = document.getElementById('agents');
                    container.innerHTML = agents.map(agent => `
                        <div class="agent-card">
                            <h4>${agent.name}</h4>
                            <p>${agent.description}</p>
                            <div class="status-${agent.status}">${agent.status.toUpperCase()}</div>
                            <br>
                            <button class="btn btn-start" onclick="startAgent('${agent.id}')">Start</button>
                            <button class="btn btn-stop" onclick="stopAgent('${agent.id}')">Stop</button>
                        </div>
                    `).join('');
                })
                .catch(e => console.error('Error loading agents:', e));
        }
        
        function loadStatus() {
            fetch('/api/status')
                .then(r => r.text())
                .then(status => {
                    document.getElementById('status').textContent = status;
                })
                .catch(e => console.error('Error loading status:', e));
        }
        
        function startAgent(agentId) {
            fetch(`/api/agents/${agentId}/start`, { method: 'POST' })
                .then(r => r.text())
                .then(result => {
                    alert(result);
                    loadAgents();
                });
        }
        
        function stopAgent(agentId) {
            fetch(`/api/agents/${agentId}/stop`, { method: 'POST' })
                .then(r => r.text())
                .then(result => {
                    alert(result);
                    loadAgents();
                });
        }
        
        // Auto refresh every 10 seconds
        setInterval(refreshAll, 10000);
        
        // Initial load
        refreshAll();
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_metrics(self):
        try:
            metrics = {
                'cpu': psutil.cpu_percent(interval=0.1),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('E:').percent,
                'timestamp': datetime.now().isoformat()
            }
            self.send_json_response(metrics)
        except Exception as e:
            self.send_error_response(str(e))
    
    def serve_agents(self):
        agents = [
            {
                'id': 'gh-copilot-orchestrator',
                'name': 'GitHub Copilot Orchestrator',
                'description': 'Interactive GitHub Copilot testing',
                'status': self.get_process_status('gh-copilot-orchestrator.py')
            },
            {
                'id': 'local-orchestrator',
                'name': 'Local Orchestrator', 
                'description': 'Resource-aware local testing',
                'status': self.get_process_status('local-orchestrator.py')
            },
            {
                'id': 'run-gh-copilot-tests',
                'name': 'Automated Copilot Tests',
                'description': 'Batch testing with remediation',
                'status': self.get_process_status('run-gh-copilot-tests.py')
            }
        ]
        self.send_json_response(agents)
    
    def serve_status(self):
        try:
            # Get running processes
            python_procs = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        python_procs.append(f"PID {proc.info['pid']}: {cmdline}")
                except:
                    continue
            
            # Get recent results
            results_dir = Path('E:/Projects/orchestration_results')
            recent_files = []
            if results_dir.exists():
                for f in sorted(results_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                    recent_files.append(f.name)
            
            status = f"""Agent Dashboard Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Running Python Processes:
{chr(10).join(python_procs) if python_procs else 'No Python processes found'}

Recent Results:
{chr(10).join(recent_files) if recent_files else 'No recent results'}

System Info:
CPU: {psutil.cpu_percent()}%
Memory: {psutil.virtual_memory().percent}%
"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(status.encode())
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def get_process_status(self, script_name):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and script_name in ' '.join(proc.info['cmdline']):
                    return 'running'
            except:
                continue
        return 'stopped'
    
    def start_agent(self, agent_id):
        try:
            scripts = {
                'gh-copilot-orchestrator': 'gh-copilot-orchestrator.py',
                'local-orchestrator': 'local-orchestrator.py',
                'run-gh-copilot-tests': 'run-gh-copilot-tests.py'
            }
            
            if agent_id not in scripts:
                self.send_error_response('Unknown agent')
                return
            
            script = scripts[agent_id]
            python_exe = r'E:\Projects\.venv\Scripts\python.exe'
            
            # Start the process in background
            subprocess.Popen(
                [python_exe, script],
                cwd=r'E:\Projects',
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Started {agent_id}'.encode())
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def stop_agent(self, agent_id):
        try:
            scripts = {
                'gh-copilot-orchestrator': 'gh-copilot-orchestrator.py',
                'local-orchestrator': 'local-orchestrator.py', 
                'run-gh-copilot-tests': 'run-gh-copilot-tests.py'
            }
            
            if agent_id not in scripts:
                self.send_error_response('Unknown agent')
                return
            
            script = scripts[agent_id]
            killed = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and script in ' '.join(proc.info['cmdline']):
                        proc.terminate()
                        killed += 1
                except:
                    continue
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Stopped {killed} processes for {agent_id}'.encode())
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, error):
        self.send_response(500)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(f'Error: {error}'.encode())
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

if __name__ == '__main__':
    print("🚀 Starting Ultra Simple Agent Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5001")
    
    server = HTTPServer(('localhost', 5001), AgentDashboardHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard stopped")
        server.server_close()
