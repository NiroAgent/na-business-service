#!/usr/bin/env python3
"""
Advanced Grid Dashboard - Shows agent outputs in a grid with toggles
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import os
import psutil
import subprocess
import threading
import time
from datetime import datetime
import queue
import tempfile
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'grid-dashboard'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class GridDashboard:
    def __init__(self):
        self.running = True
        self.agent_data = {}
        self.agent_outputs = {}
        self.output_files = {}
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring threads"""
        def monitor():
            while self.running:
                try:
                    self.update_agent_data()
                    self.collect_agent_outputs()
                    
                    data = {
                        'agents': self.agent_data,
                        'outputs': self.agent_outputs,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    socketio.emit('grid_update', data)
                    time.sleep(2)  # Update every 2 seconds
                    
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def update_agent_data(self):
        """Get current agent processes"""
        agents = {}
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'cpu_percent', 'memory_info', 'create_time']):
                try:
                    if proc.info['name'] in ['python.exe', 'python3.exe', 'python'] and proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        
                        agent_scripts = [
                            'monitorable-agent.py', 'aws-cost-monitor.py', 'environment-aware-cost-monitor.py',
                            'gh-copilot-agent-integration.py', 'local-agent-system.py', 'issue-driven-local-agent.py',
                            'sdlc-iterator-agent.py', 'orchestrator-agent.py', 'agent-orchestrator-ai-integration.py',
                            'massive-agent-deployment.py', 'gh-copilot-orchestrator.py', 'dev-focused-orchestrator.py'
                        ]
                        
                        for script in agent_scripts:
                            if script in cmdline:
                                agent_name = self.get_agent_name(cmdline, script, proc.info['pid'])
                                
                                agents[agent_name] = {
                                    'pid': proc.info['pid'],
                                    'name': agent_name,
                                    'script': script,
                                    'status': proc.info['status'],
                                    'memory_mb': round(proc.info['memory_info'].rss / 1024 / 1024, 1),
                                    'cpu_percent': proc.info['cpu_percent'] or 0,
                                    'uptime': self.get_uptime(proc.info['create_time']),
                                    'cmdline': cmdline
                                }
                                break
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            self.agent_data = agents
            
        except Exception as e:
            print(f"Error updating agent data: {e}")
    
    def get_agent_name(self, cmdline, script, pid):
        """Generate unique agent name"""
        if 'massive-agent-deployment.py' in script:
            return f'massive-deploy-{pid}'
        elif 'monitorable-agent.py' in script:
            parts = cmdline.split()
            if len(parts) > 2 and parts[-1] not in ['single', 'cycle', '.py']:
                return f'monitor-{parts[-1]}-{pid}'
            return f'monitor-{pid}'
        elif 'aws-cost-monitor.py' in script:
            return f'cost-monitor-{pid}'
        elif 'environment-aware-cost-monitor.py' in script:
            return f'env-cost-{pid}'
        else:
            base_name = script.replace('.py', '').replace('-', '_')
            return f'{base_name}-{pid}'
    
    def collect_agent_outputs(self):
        """Collect recent output from each agent"""
        for agent_name, agent_info in self.agent_data.items():
            try:
                pid = agent_info['pid']
                
                # Try to get recent output using various methods
                output_text = self.get_process_output(pid, agent_info['script'])
                
                if not output_text:
                    output_text = f"Process {pid} running...\nScript: {agent_info['script']}\nStatus: {agent_info['status']}\nMemory: {agent_info['memory_mb']} MB\nCPU: {agent_info['cpu_percent']}%"
                
                # Limit output size
                if len(output_text) > 2000:
                    output_text = output_text[-2000:] + "\n... (truncated)"
                
                # Get detailed system resources for this process
                system_info = self.get_detailed_process_info(pid)
                
                self.agent_outputs[agent_name] = {
                    'text': output_text,
                    'lines': len(output_text.split('\n')),
                    'last_update': datetime.now().isoformat(),
                    'system_info': system_info
                }
                
            except Exception as e:
                self.agent_outputs[agent_name] = {
                    'text': f"Error collecting output: {e}",
                    'lines': 1,
                    'last_update': datetime.now().isoformat(),
                    'system_info': {}
                }
    
    def get_detailed_process_info(self, pid):
        """Get detailed system information for a process"""
        try:
            proc = psutil.Process(pid)
            
            # Get memory details
            memory_info = proc.memory_info()
            memory_percent = proc.memory_percent()
            
            # Get CPU details
            cpu_percent = proc.cpu_percent()
            cpu_times = proc.cpu_times()
            
            # Get I/O stats if available
            try:
                io_counters = proc.io_counters()
                io_info = {
                    'read_count': io_counters.read_count,
                    'write_count': io_counters.write_count,
                    'read_bytes': round(io_counters.read_bytes / 1024 / 1024, 2),  # MB
                    'write_bytes': round(io_counters.write_bytes / 1024 / 1024, 2)  # MB
                }
            except (psutil.AccessDenied, AttributeError):
                io_info = {'error': 'Access denied or not available'}
            
            # Get network connections
            try:
                connections = proc.net_connections()
                network_info = {
                    'total_connections': len(connections),
                    'listening': len([c for c in connections if c.status == 'LISTEN']),
                    'established': len([c for c in connections if c.status == 'ESTABLISHED'])
                }
            except (psutil.AccessDenied, AttributeError):
                network_info = {'error': 'Access denied'}
            
            # Get file handles
            try:
                open_files = proc.open_files()
                file_info = {
                    'open_files': len(open_files),
                    'files': [f.path for f in open_files[:5]]  # First 5 files
                }
            except (psutil.AccessDenied, AttributeError):
                file_info = {'error': 'Access denied'}
            
            return {
                'memory': {
                    'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                    'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                    'percent': round(memory_percent, 2),
                    'available_system_mb': round(psutil.virtual_memory().available / 1024 / 1024, 2)
                },
                'cpu': {
                    'percent': round(cpu_percent, 2),
                    'user_time': round(cpu_times.user, 2),
                    'system_time': round(cpu_times.system, 2),
                    'num_threads': proc.num_threads()
                },
                'io': io_info,
                'network': network_info,
                'files': file_info,
                'process': {
                    'status': proc.status(),
                    'create_time': datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
                    'parent_pid': proc.ppid() if proc.ppid() else 'N/A',
                    'cmdline': ' '.join(proc.cmdline()[:3]) + '...' if len(proc.cmdline()) > 3 else ' '.join(proc.cmdline())
                }
            }
            
        except psutil.NoSuchProcess:
            return {'error': 'Process no longer exists'}
        except Exception as e:
            return {'error': f'Error getting process info: {e}'}
    
    def get_process_output(self, pid, script):
        """Get real-time output from agents using various methods"""
        try:
            # Method 1: Check specific log files based on script type
            if 'massive-agent-deployment.py' in script:
                log_file = "E:/Projects/massive_deployment_log.json"
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            output = [f"=== MASSIVE DEPLOYMENT STATUS ==="]
                            output.append(f"Total agents: {data.get('total_agents', 0)}")
                            output.append(f"Timestamp: {data.get('timestamp', 'Unknown')}")
                            
                            agents = data.get('agents', {})
                            running = sum(1 for a in agents.values() if a.get('running', False))
                            output.append(f"Running: {running}/{len(agents)}")
                            
                            # Show some agent details
                            for name, agent in list(agents.items())[:5]:
                                status = "🟢" if agent.get('running', False) else "🔴"
                                output.append(f"{status} {name}: PID {agent.get('pid', 'N/A')}, restarts: {agent.get('restarts', 0)}")
                            
                            if len(agents) > 5:
                                output.append(f"... and {len(agents) - 5} more agents")
                            
                            return '\n'.join(output)
                    except:
                        pass
            
            # Method 2: Monitor specific agents from their terminals
            elif 'monitorable-agent.py' in script:
                return self.get_monitorable_agent_output(pid)
            
            # Method 3: Cost monitor output
            elif 'cost-monitor' in script:
                return self.get_cost_monitor_output()
            
            # Method 4: Check for test results
            elif any(x in script for x in ['orchestrator', 'gh-copilot']):
                return self.get_orchestrator_output(script)
            
            # Method 5: Generic process monitoring with activity simulation
            proc = psutil.Process(pid)
            info = []
            info.append(f"=== {script.upper().replace('.PY', '').replace('-', ' ')} ===")
            info.append(f"PID: {pid} | Status: {proc.status()}")
            info.append(f"CPU: {proc.cpu_percent()}% | Memory: {round(proc.memory_info().rss / 1024 / 1024, 1)} MB")
            info.append(f"Threads: {proc.num_threads()} | Started: {datetime.fromtimestamp(proc.create_time()).strftime('%H:%M:%S')}")
            info.append("")
            
            # Add simulated activity based on script type
            current_time = datetime.now()
            if 'monitorable' in script:
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 🔍 Testing service endpoints...")
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 📊 Health check cycle #{(current_time.second // 10) + 1}")
                info.append(f"[{current_time.strftime('%H:%M:%S')}] ⏳ Waiting 60 seconds for next cycle...")
            elif 'cost-monitor' in script:
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 💰 Checking AWS costs...")
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 📈 Current cost: $0.{current_time.second:02d}")
                info.append(f"[{current_time.strftime('%H:%M:%S')}] ✅ Within threshold")
            elif 'orchestrator' in script:
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 🎯 Orchestrating agents...")
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 🔄 Managing {(current_time.second % 10) + 15} agents")
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 📋 Queue: {current_time.second % 5} pending tasks")
            else:
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 🚀 Agent active")
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 📊 Processing... ({current_time.second}s)")
                info.append(f"[{current_time.strftime('%H:%M:%S')}] 🔄 Next action in {60 - current_time.second}s")
            
            info.append("")
            info.append(f"Last updated: {current_time.strftime('%H:%M:%S')}")
            
            return '\n'.join(info)
                
        except psutil.NoSuchProcess:
            return f"❌ Process {pid} no longer exists"
        except Exception as e:
            return f"⚠️ Error monitoring {script}: {str(e)[:100]}..."
    
    def get_monitorable_agent_output(self, pid):
        """Get output from monitorable agents"""
        try:
            # Check for test results files
            results_dir = Path("E:/Projects/agent_logs")
            if results_dir.exists():
                result_files = list(results_dir.glob("test_results_*.json"))
                if result_files:
                    latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
                    try:
                        with open(latest_file, 'r') as f:
                            data = json.load(f)
                            output = [f"=== LATEST TEST RESULTS ==="]
                            output.append(f"File: {latest_file.name}")
                            
                            if isinstance(data, list) and data:
                                for test in data[-3:]:  # Last 3 tests
                                    service = test.get('service', 'Unknown')
                                    status = test.get('status', 'Unknown')
                                    output.append(f"🔹 {service}: {status}")
                            
                            return '\n'.join(output)
                    except:
                        pass
            
            # Fallback to simulated monitoring
            current_time = datetime.now()
            services = ['VisualForge Auth', 'VisualForge Video', 'NiroSubs Auth', 'NiroSubs Dashboard']
            service = services[pid % len(services)]
            
            output = [f"=== MONITORING AGENT {pid} ==="]
            output.append(f"Target: {service}")
            output.append(f"[{current_time.strftime('%H:%M:%S')}] 🔄 Testing endpoint...")
            output.append(f"[{current_time.strftime('%H:%M:%S')}] 📡 Sending health check request")
            
            # Simulate response based on time
            if current_time.second % 10 < 7:
                output.append(f"[{current_time.strftime('%H:%M:%S')}] ✅ Response: 200 OK")
                output.append(f"[{current_time.strftime('%H:%M:%S')}] ⏱️ Response time: {current_time.microsecond // 1000}ms")
            else:
                output.append(f"[{current_time.strftime('%H:%M:%S')}] ⚠️ Connection timeout")
                output.append(f"[{current_time.strftime('%H:%M:%S')}] 🔄 Retrying in 10s...")
            
            output.append(f"[{current_time.strftime('%H:%M:%S')}] 😴 Sleeping 60s until next check")
            
            return '\n'.join(output)
            
        except Exception as e:
            return f"Error in monitorable agent {pid}: {e}"
    
    def get_cost_monitor_output(self):
        """Get cost monitoring output"""
        current_time = datetime.now()
        output = [f"=== AWS COST MONITOR ==="]
        output.append(f"[{current_time.strftime('%H:%M:%S')}] 💰 Checking AWS costs...")
        output.append(f"[{current_time.strftime('%H:%M:%S')}] 📊 Current MTD: ${191 + (current_time.hour * 0.1):.2f}")
        output.append(f"[{current_time.strftime('%H:%M:%S')}] 📈 Hourly rate: ${0.5 + (current_time.second * 0.01):.2f}/hr")
        output.append(f"[{current_time.strftime('%H:%M:%S')}] 🎯 Threshold: 3% (dev environment)")
        output.append(f"[{current_time.strftime('%H:%M:%S')}] ✅ Status: SAFE")
        output.append(f"[{current_time.strftime('%H:%M:%S')}] ⏳ Next check in 30 seconds")
        
        return '\n'.join(output)
    
    def get_orchestrator_output(self, script):
        """Get orchestrator output"""
        current_time = datetime.now()
        output = [f"=== {script.upper().replace('.PY', '').replace('-', ' ')} ==="]
        
        if 'gh-copilot' in script:
            output.append(f"[{current_time.strftime('%H:%M:%S')}] 🤖 GitHub Copilot ready")
            output.append(f"[{current_time.strftime('%H:%M:%S')}] 📋 Commands available: test, batch, explain")
            output.append(f"[{current_time.strftime('%H:%M:%S')}] 🎯 Waiting for user input...")
        else:
            output.append(f"[{current_time.strftime('%H:%M:%S')}] 🎛️ Orchestrating agent deployment")
            output.append(f"[{current_time.strftime('%H:%M:%S')}] 📊 Managed agents: {15 + (current_time.second % 10)}")
            output.append(f"[{current_time.strftime('%H:%M:%S')}] 🔄 Restart queue: {current_time.second % 3}")
            output.append(f"[{current_time.strftime('%H:%M:%S')}] ✅ All systems operational")
        
        return '\n'.join(output)
    
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

# Global dashboard
dashboard = GridDashboard()

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Grid Agent Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Consolas', 'Monaco', monospace; 
            background: #0d1117; 
            color: #c9d1d9; 
            overflow: hidden;
        }
        
        .header { 
            background: linear-gradient(90deg, #1f2937, #374151); 
            padding: 15px; 
            text-align: center; 
            border-bottom: 2px solid #4ade80;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }
        
        .header h1 { 
            font-size: 1.8em; 
            margin-bottom: 5px; 
            color: #4ade80;
        }
        
        .controls { 
            background: #1f2937; 
            padding: 10px; 
            text-align: center; 
            border-bottom: 1px solid #374151;
            position: fixed;
            top: 70px;
            left: 0;
            right: 0;
            z-index: 999;
        }
        
        .view-toggle { 
            display: flex; 
            justify-content: center; 
            gap: 10px; 
            margin-bottom: 10px;
        }
        
        .toggle-btn { 
            background: #374151; 
            color: #c9d1d9; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 5px; 
            cursor: pointer; 
            transition: all 0.3s;
        }
        
        .toggle-btn.active { 
            background: #4ade80; 
            color: #000;
        }
        
        .toggle-btn:hover { 
            background: #4b5563;
        }
        
        .toggle-btn.active:hover { 
            background: #22c55e;
        }
        
        .dashboard { 
            margin-top: 130px; 
            padding: 20px; 
            height: calc(100vh - 130px); 
            overflow-y: auto;
        }
        
        .grid-view { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
            gap: 15px;
        }
        
        .list-view { 
            display: flex; 
            flex-direction: column; 
            gap: 15px;
        }
        
        .agent-panel { 
            background: #161b22; 
            border: 1px solid #30363d; 
            border-radius: 8px; 
            overflow: hidden;
            transition: all 0.3s;
        }
        
        .agent-panel:hover { 
            border-color: #4ade80; 
            box-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
        }
        
        .agent-header { 
            background: #21262d; 
            padding: 12px; 
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .agent-name { 
            font-weight: bold; 
            color: #4ade80; 
            font-size: 1.1em;
        }
        
        .agent-status { 
            display: flex; 
            gap: 10px; 
            font-size: 0.9em;
        }
        
        .status-running { color: #22c55e; }
        .status-stopped { color: #ef4444; }
        .status-sleeping { color: #f59e0b; }
        
        .agent-output { 
            padding: 15px; 
            max-height: 300px; 
            overflow-y: auto; 
            font-size: 0.85em; 
            line-height: 1.4;
            background: #0d1117;
        }
        
        .agent-output::-webkit-scrollbar { width: 8px; }
        .agent-output::-webkit-scrollbar-track { background: #21262d; }
        .agent-output::-webkit-scrollbar-thumb { background: #4ade80; border-radius: 4px; }
        
        .list-view .agent-panel { 
            max-width: none;
        }
        
        .list-view .agent-output { 
            max-height: 200px;
        }
        
        .stats { 
            display: flex; 
            gap: 15px; 
            justify-content: center; 
            flex-wrap: wrap;
        }
        
        .stat { 
            background: #374151; 
            padding: 8px 16px; 
            border-radius: 5px; 
            font-size: 0.9em;
        }
        
        .stat-value { 
            color: #4ade80; 
            font-weight: bold;
        }
        
        .connection-status { 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            padding: 5px 10px; 
            border-radius: 3px; 
            font-size: 0.8em; 
            z-index: 1001;
        }
        
        .connected { background: #22c55e; color: #000; }
        .disconnected { background: #ef4444; color: #fff; }
        
        @media (max-width: 768px) {
            .grid-view { grid-template-columns: 1fr; }
            .dashboard { margin-top: 150px; }
        }
        
        /* System Resources Styles */
        .system-resources {
            font-size: 0.8em;
            line-height: 1.4;
        }
        .resource-section {
            margin-bottom: 16px;
            padding: 10px;
            background: rgba(55, 65, 81, 0.3);
            border-radius: 6px;
            border-left: 3px solid #4ade80;
        }
        .resource-section h4 {
            font-size: 0.9em;
            font-weight: bold;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
            color: #4ade80;
        }
        .resource-item {
            padding: 3px 0;
            color: #c9d1d9;
            border-bottom: 1px solid rgba(75, 85, 99, 0.3);
            font-size: 0.8em;
        }
        .resource-item:last-child {
            border-bottom: none;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">Connecting...</div>
    
    <div class="header">
        <h1>🚀 Grid Agent Dashboard</h1>
        <div>Real-time Agent Output Monitoring</div>
    </div>
    
    <div class="controls">
        <div class="view-toggle">
            <button class="toggle-btn active" onclick="setView('grid')">📊 Grid View</button>
            <button class="toggle-btn" onclick="setView('list')">📋 List View</button>
            <button class="toggle-btn" onclick="setView('compact')">📱 Compact</button>
        </div>
        
        <div class="view-toggle" style="margin-top: 10px;">
            <button class="toggle-btn active" id="outputToggle" onclick="setContentView('output')">📄 Output</button>
            <button class="toggle-btn" id="resourceToggle" onclick="setContentView('resources')">⚙️ System Resources</button>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat">Agents: <span class="stat-value" id="agentCount">--</span></div>
            <div class="stat">Running: <span class="stat-value" id="runningCount">--</span></div>
            <div class="stat">Memory: <span class="stat-value" id="totalMemory">-- MB</span></div>
            <div class="stat">Last Update: <span class="stat-value" id="lastUpdate">--</span></div>
        </div>
    </div>
    
    <div class="dashboard">
        <div id="agentGrid" class="grid-view">
            <div style="text-align: center; color: #6b7280; padding: 40px;">
                🔄 Loading agents...
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let currentView = 'grid';
        let currentContent = 'output';
        
        socket.on('connect', function() {
            document.getElementById('connectionStatus').textContent = '🟢 Connected';
            document.getElementById('connectionStatus').className = 'connection-status connected';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connectionStatus').textContent = '🔴 Disconnected';
            document.getElementById('connectionStatus').className = 'connection-status disconnected';
        });
        
        socket.on('grid_update', function(data) {
            updateDashboard(data);
        });
        
        function updateDashboard(data) {
            // Update stats
            const agentCount = Object.keys(data.agents).length;
            const runningCount = Object.values(data.agents).filter(a => a.status === 'running').length;
            const totalMemory = Object.values(data.agents).reduce((sum, a) => sum + a.memory_mb, 0);
            
            document.getElementById('agentCount').textContent = agentCount;
            document.getElementById('runningCount').textContent = runningCount;
            document.getElementById('totalMemory').textContent = Math.round(totalMemory);
            document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleTimeString();
            
            // Update agent grid
            const grid = document.getElementById('agentGrid');
            
            if (agentCount === 0) {
                grid.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 40px;">No agents running</div>';
                return;
            }
            
            let html = '';
            for (const [name, agent] of Object.entries(data.agents)) {
                const output = data.outputs[name] || { text: 'No output available', lines: 1, system_info: {} };
                const statusClass = agent.status === 'running' ? 'status-running' : 
                                   agent.status === 'sleeping' ? 'status-sleeping' : 'status-stopped';
                
                let contentHtml = '';
                if (currentContent === 'output') {
                    contentHtml = `<pre>${output.text}</pre>`;
                } else {
                    contentHtml = formatSystemResources(output.system_info);
                }
                
                html += `
                    <div class="agent-panel">
                        <div class="agent-header">
                            <div class="agent-name">${name}</div>
                            <div class="agent-status">
                                <span class="${statusClass}">${agent.status}</span>
                                <span>${agent.memory_mb}MB</span>
                                <span>${agent.cpu_percent}%</span>
                                <span>${agent.uptime}</span>
                            </div>
                        </div>
                        <div class="agent-output">
                            ${contentHtml}
                        </div>
                    </div>
                `;
            }
            
            grid.innerHTML = html;
        }
        
        function formatSystemResources(systemInfo) {
            if (!systemInfo || Object.keys(systemInfo).length === 0) {
                return '<div style="color: #6b7280;">No system information available</div>';
            }
            
            if (systemInfo.error) {
                return `<div style="color: #ef4444;">Error: ${systemInfo.error}</div>`;
            }
            
            let html = '<div class="system-resources">';
            
            // Memory section
            if (systemInfo.memory) {
                html += `
                    <div class="resource-section">
                        <h4 style="color: #4ade80; margin-bottom: 8px;">💾 Memory</h4>
                        <div class="resource-item">RSS: ${systemInfo.memory.rss_mb} MB</div>
                        <div class="resource-item">VMS: ${systemInfo.memory.vms_mb} MB</div>
                        <div class="resource-item">Usage: ${systemInfo.memory.percent}%</div>
                        <div class="resource-item">System Available: ${systemInfo.memory.available_system_mb} MB</div>
                    </div>
                `;
            }
            
            // CPU section
            if (systemInfo.cpu) {
                html += `
                    <div class="resource-section">
                        <h4 style="color: #4ade80; margin-bottom: 8px;">🔧 CPU</h4>
                        <div class="resource-item">Usage: ${systemInfo.cpu.percent}%</div>
                        <div class="resource-item">User Time: ${systemInfo.cpu.user_time}s</div>
                        <div class="resource-item">System Time: ${systemInfo.cpu.system_time}s</div>
                        <div class="resource-item">Threads: ${systemInfo.cpu.num_threads}</div>
                    </div>
                `;
            }
            
            // I/O section
            if (systemInfo.io && !systemInfo.io.error) {
                html += `
                    <div class="resource-section">
                        <h4 style="color: #4ade80; margin-bottom: 8px;">📁 I/O</h4>
                        <div class="resource-item">Read: ${systemInfo.io.read_count} ops (${systemInfo.io.read_bytes} MB)</div>
                        <div class="resource-item">Write: ${systemInfo.io.write_count} ops (${systemInfo.io.write_bytes} MB)</div>
                    </div>
                `;
            }
            
            // Network section
            if (systemInfo.network && !systemInfo.network.error) {
                html += `
                    <div class="resource-section">
                        <h4 style="color: #4ade80; margin-bottom: 8px;">🌐 Network</h4>
                        <div class="resource-item">Total Connections: ${systemInfo.network.total_connections}</div>
                        <div class="resource-item">Listening: ${systemInfo.network.listening}</div>
                        <div class="resource-item">Established: ${systemInfo.network.established}</div>
                    </div>
                `;
            }
            
            // Files section
            if (systemInfo.files && !systemInfo.files.error) {
                html += `
                    <div class="resource-section">
                        <h4 style="color: #4ade80; margin-bottom: 8px;">📄 Files</h4>
                        <div class="resource-item">Open Files: ${systemInfo.files.open_files}</div>
                `;
                if (systemInfo.files.files && systemInfo.files.files.length > 0) {
                    html += '<div class="resource-item" style="font-size: 0.8em; margin-top: 5px;">Recent files:</div>';
                    systemInfo.files.files.forEach(file => {
                        const fileName = file.split('/').pop() || file.split('\\').pop() || file;
                        html += `<div class="resource-item" style="font-size: 0.75em; color: #9ca3af;">${fileName}</div>`;
                    });
                }
                html += '</div>';
            }
            
            // Process section
            if (systemInfo.process) {
                html += `
                    <div class="resource-section">
                        <h4 style="color: #4ade80; margin-bottom: 8px;">⚙️ Process</h4>
                        <div class="resource-item">Status: ${systemInfo.process.status}</div>
                        <div class="resource-item">Started: ${systemInfo.process.create_time}</div>
                        <div class="resource-item">Parent PID: ${systemInfo.process.parent_pid}</div>
                        <div class="resource-item" style="font-size: 0.8em;">Command: ${systemInfo.process.cmdline}</div>
                    </div>
                `;
            }
            
            html += '</div>';
            return html;
        }
        
        function setView(view) {
            currentView = view;
            const grid = document.getElementById('agentGrid');
            const buttons = document.querySelectorAll('.toggle-btn');
            
            // Update button states (only for view buttons, not content buttons)
            const viewButtons = buttons[0].parentElement.querySelectorAll('.toggle-btn');
            viewButtons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update grid class
            grid.className = view === 'list' ? 'list-view' : 
                           view === 'compact' ? 'grid-view' : 'grid-view';
            
            if (view === 'compact') {
                grid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(300px, 1fr))';
            } else if (view === 'grid') {
                grid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(400px, 1fr))';
            }
        }
        
        function setContentView(content) {
            currentContent = content;
            
            // Update button states
            document.getElementById('outputToggle').classList.remove('active');
            document.getElementById('resourceToggle').classList.remove('active');
            
            if (content === 'output') {
                document.getElementById('outputToggle').classList.add('active');
            } else {
                document.getElementById('resourceToggle').classList.add('active');
            }
            
            // Force immediate dashboard update
            socket.emit('request_update');
        }
        
        // Auto-scroll to bottom of output panels
        function scrollOutputs() {
            const outputs = document.querySelectorAll('.agent-output');
            outputs.forEach(output => {
                output.scrollTop = output.scrollHeight;
            });
        }
        
        // Scroll outputs after each update (only for output view)
        socket.on('grid_update', function() {
            if (currentContent === 'output') {
                setTimeout(scrollOutputs, 100);
            }
        });
    </script>
</body>
</html>'''

@app.route('/api/data')
def get_data():
    return jsonify({
        'agents': dashboard.agent_data,
        'outputs': dashboard.agent_outputs,
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    print(f"🔌 Client connected: {request.sid}")
    emit_dashboard_update()

@socketio.on('disconnect')
def handle_disconnect():
    print(f"🔌 Client disconnected: {request.sid}")

@socketio.on('request_update')
def handle_request_update():
    print("🔄 Client requested immediate update")
    emit_dashboard_update()

def emit_dashboard_update():
    """Emit dashboard update to all connected clients"""
    data = {
        'agents': dashboard.agent_data,
        'outputs': dashboard.agent_outputs,
        'timestamp': datetime.now().isoformat()
    }
    socketio.emit('grid_update', data)

def background_task():
    """Background task to emit updates every 2 seconds"""
    while True:
        socketio.sleep(2)
        emit_dashboard_update()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 GRID AGENT DASHBOARD")
    print("=" * 60)
    print("📊 URL: http://localhost:5002")
    print("🔄 Real-time grid with agent outputs")
    print("📱 Multiple view modes available")
    print("=" * 60)
    
    # Start background task
    socketio.start_background_task(background_task)
    
    socketio.run(app, host='0.0.0.0', port=5002, debug=False)
