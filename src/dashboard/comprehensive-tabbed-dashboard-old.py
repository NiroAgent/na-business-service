#!/usr/bin/env python3
"""
Comprehensive Tabbed Agent Dashboard
Combines all monitoring components with tabbed interface
"""

import sys
import os
import time
import json
import psutil
import subprocess
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import glob

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dashboard_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class ComprehensiveDashboard:
    def __init__(self):
        self.agent_data = {}
        self.agent_outputs = {}
        self.system_metrics = {}
        self.cost_data = {'current': 0.0, 'threshold': 25.0, 'trend': []}
        self.performance_history = []
        self.console_logs = []
        self.log_files = []
        
        # AI Development Team Integration
        self.team_communication = None
        self.work_queue = None
        self.github_integration = {"connected": False, "last_sync": None}
        self.team_metrics = {
            "active_developers": 0,
            "work_in_progress": 0,
            "completed_today": 0,
            "velocity": 0
        }
        
        # Start data collection
        self.start_data_collection()
        self.initialize_team_systems()
    
    def start_data_collection(self):
        """Start background threads to collect data"""
        Thread(target=self.collect_agent_data, daemon=True).start()
        Thread(target=self.collect_console_output, daemon=True).start()
        Thread(target=self.collect_system_metrics, daemon=True).start()
        Thread(target=self.collect_cost_data, daemon=True).start()
        Thread(target=self.collect_team_data, daemon=True).start()
    
    def initialize_team_systems(self):
        """Initialize AI development team systems"""
        try:
            # Try to import and initialize team systems
            import importlib.util
            
            # Check if team communication is available
            comm_spec = importlib.util.find_spec("team-communication-protocol")
            if comm_spec:
                from team_communication_protocol import communication_hub
                self.team_communication = communication_hub
            
            # Check if work queue is available
            queue_spec = importlib.util.find_spec("work-queue-manager") 
            if queue_spec:
                from work_queue_manager import work_queue_manager
                self.work_queue = work_queue_manager
                
        except Exception as e:
            print(f"Team systems not yet available: {e}")
    
    def collect_team_data(self):
        """Collect AI development team data"""
        while True:
            try:
                if self.team_communication:
                    team_status = self.team_communication.get_team_status()
                    self.team_metrics["active_developers"] = team_status.get("active_agents", 0)
                
                if self.work_queue:
                    queue_status = self.work_queue.get_queue_status()
                    self.team_metrics["work_in_progress"] = sum(
                        agent["current_workload"] for agent in queue_status["agents"].values()
                    )
                    self.team_metrics["completed_today"] = queue_status["metrics"]["completed_items"]
                    
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                print(f"Error collecting team data: {e}")
                time.sleep(30)
    
    def collect_agent_data(self):
        """Collect agent process data"""
        while True:
            try:
                current_agents = {}
                current_outputs = {}
                
                # Look for agent processes
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent', 'create_time']):
                    try:
                        if proc.info['cmdline'] and any('agent' in str(arg).lower() or 'orchestrator' in str(arg).lower() for arg in proc.info['cmdline']):
                            # Extract agent name from command line
                            cmdline = ' '.join(proc.info['cmdline'])
                            if 'python' in cmdline:
                                script_name = None
                                for arg in proc.info['cmdline']:
                                    if arg.endswith('.py') and ('agent' in arg.lower() or 'orchestrator' in arg.lower()):
                                        script_name = os.path.basename(arg).replace('.py', '')
                                        break
                                
                                if script_name:
                                    agent_name = script_name
                                    
                                    # Get detailed process info
                                    process_info = self.get_detailed_process_info(proc.info['pid'])
                                    
                                    current_agents[agent_name] = {
                                        'pid': proc.info['pid'],
                                        'status': 'running',
                                        'memory_mb': round(proc.info['memory_info'].rss / 1024 / 1024, 1),
                                        'cpu_percent': round(proc.info['cpu_percent'], 1),
                                        'uptime': self.format_uptime(proc.info['create_time']),
                                        'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline,
                                        'system_info': process_info
                                    }
                                    
                                    # Collect output for this agent
                                    output_text = self.get_agent_output(agent_name, proc.info['pid'])
                                    current_outputs[agent_name] = {
                                        'text': output_text,
                                        'lines': len(output_text.split('\n')),
                                        'system_info': process_info
                                    }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                self.agent_data = current_agents
                self.agent_outputs = current_outputs
                
            except Exception as e:
                print(f"Error collecting agent data: {e}")
            
            time.sleep(2)
    
    def get_detailed_process_info(self, pid):
        """Get detailed system info for a process"""
        try:
            proc = psutil.Process(pid)
            
            # Memory details
            memory_info = proc.memory_info()
            memory_percent = proc.memory_percent()
            system_memory = psutil.virtual_memory()
            
            # CPU details
            cpu_info = proc.cpu_times()
            cpu_percent = proc.cpu_percent()
            
            # I/O details
            try:
                io_info = proc.io_counters()
                io_data = {
                    'read_count': io_info.read_count,
                    'write_count': io_info.write_count,
                    'read_bytes': round(io_info.read_bytes / 1024 / 1024, 2),
                    'write_bytes': round(io_info.write_bytes / 1024 / 1024, 2)
                }
            except (psutil.AccessDenied, AttributeError):
                io_data = {'error': 'Access denied or not available'}
            
            # Network connections
            try:
                connections = proc.net_connections()
                network_info = {
                    'total_connections': len(connections),
                    'listening': len([c for c in connections if c.status == 'LISTEN']),
                    'established': len([c for c in connections if c.status == 'ESTABLISHED'])
                }
            except (psutil.AccessDenied, AttributeError):
                network_info = {'error': 'Access denied or not available'}
            
            # Open files
            try:
                open_files = proc.open_files()
                files_info = {
                    'open_files': len(open_files),
                    'files': [f.path for f in open_files[:5]]  # Show first 5 files
                }
            except (psutil.AccessDenied, AttributeError):
                files_info = {'error': 'Access denied or not available'}
            
            return {
                'memory': {
                    'rss_mb': round(memory_info.rss / 1024 / 1024, 1),
                    'vms_mb': round(memory_info.vms / 1024 / 1024, 1),
                    'percent': round(memory_percent, 1),
                    'available_system_mb': round(system_memory.available / 1024 / 1024, 1)
                },
                'cpu': {
                    'percent': round(cpu_percent, 1),
                    'user_time': round(cpu_info.user, 2),
                    'system_time': round(cpu_info.system, 2),
                    'num_threads': proc.num_threads()
                },
                'io': io_data,
                'network': network_info,
                'files': files_info,
                'process': {
                    'status': proc.status(),
                    'create_time': datetime.fromtimestamp(proc.create_time()).strftime('%H:%M:%S'),
                    'parent_pid': proc.ppid(),
                    'cmdline': ' '.join(proc.cmdline()[:3]) + '...' if len(proc.cmdline()) > 3 else ' '.join(proc.cmdline())
                }
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {'error': str(e)}
    
    def collect_console_output(self):
        """Collect console output from log files and real-time sources"""
        while True:
            try:
                # Collect from various log sources
                log_sources = [
                    'massive_deployment_log.json',
                    'orchestrator_results_*.json',
                    'test_results_*.json'
                ]
                
                recent_logs = []
                
                # Check JSON log files
                for pattern in log_sources:
                    for filepath in glob.glob(os.path.join(os.getcwd(), pattern)):
                        try:
                            with open(filepath, 'r') as f:
                                content = f.read().strip()
                                if content:
                                    # Parse JSON logs
                                    for line in content.split('\n'):
                                        if line.strip():
                                            try:
                                                log_entry = json.loads(line)
                                                recent_logs.append({
                                                    'timestamp': log_entry.get('timestamp', datetime.now().isoformat()),
                                                    'source': os.path.basename(filepath),
                                                    'message': str(log_entry),
                                                    'level': 'info'
                                                })
                                            except json.JSONDecodeError:
                                                recent_logs.append({
                                                    'timestamp': datetime.now().isoformat(),
                                                    'source': os.path.basename(filepath),
                                                    'message': line,
                                                    'level': 'info'
                                                })
                        except Exception as e:
                            continue
                
                # Add real-time process output
                for agent_name, agent_info in self.agent_data.items():
                    if agent_name in self.agent_outputs:
                        output = self.agent_outputs[agent_name]['text']
                        if output and output.strip():
                            recent_logs.append({
                                'timestamp': datetime.now().isoformat(),
                                'source': agent_name,
                                'message': output[-200:],  # Last 200 chars
                                'level': 'output'
                            })
                
                # Sort by timestamp and keep last 100
                recent_logs.sort(key=lambda x: x['timestamp'], reverse=True)
                self.console_logs = recent_logs[:100]
                
            except Exception as e:
                print(f"Error collecting console output: {e}")
            
            time.sleep(3)
    
    def collect_system_metrics(self):
        """Collect system-wide metrics"""
        while True:
            try:
                # System CPU and Memory
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Network stats
                network = psutil.net_io_counters()
                
                # Process count
                agent_count = len(self.agent_data)
                running_count = len([a for a in self.agent_data.values() if a['status'] == 'running'])
                total_memory = sum([a['memory_mb'] for a in self.agent_data.values()])
                
                self.system_metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'system': {
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_used_gb': round(memory.used / 1024 / 1024 / 1024, 2),
                        'memory_total_gb': round(memory.total / 1024 / 1024 / 1024, 2),
                        'disk_percent': disk.percent,
                        'disk_used_gb': round(disk.used / 1024 / 1024 / 1024, 2)
                    },
                    'network': {
                        'bytes_sent': round(network.bytes_sent / 1024 / 1024, 2),
                        'bytes_recv': round(network.bytes_recv / 1024 / 1024, 2),
                        'packets_sent': network.packets_sent,
                        'packets_recv': network.packets_recv
                    },
                    'agents': {
                        'total': agent_count,
                        'running': running_count,
                        'total_memory_mb': round(total_memory, 1)
                    }
                }
                
                # Store performance history
                self.performance_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'cpu': cpu_percent,
                    'memory': memory.percent,
                    'agents': running_count
                })
                
                # Keep last 60 points (2 minutes)
                if len(self.performance_history) > 60:
                    self.performance_history = self.performance_history[-60:]
                    
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
            
            time.sleep(2)
    
    def collect_cost_data(self):
        """Collect AWS cost data"""
        while True:
            try:
                # Try to get cost from monitoring files
                cost_files = glob.glob('*cost*.json')
                if cost_files:
                    with open(cost_files[0], 'r') as f:
                        cost_data = json.load(f)
                        if 'current_cost' in cost_data:
                            self.cost_data['current'] = cost_data['current_cost']
                        if 'threshold' in cost_data:
                            self.cost_data['threshold'] = cost_data['threshold']
                
                # Add to trend
                self.cost_data['trend'].append({
                    'timestamp': datetime.now().isoformat(),
                    'cost': self.cost_data['current']
                })
                
                # Keep last 30 points
                if len(self.cost_data['trend']) > 30:
                    self.cost_data['trend'] = self.cost_data['trend'][-30:]
                    
            except Exception as e:
                pass  # Cost monitoring is optional
            
            time.sleep(10)
    
    def get_agent_output(self, agent_name, pid):
        """Get output from agent process"""
        try:
            # Try multiple log file patterns
            log_patterns = [
                f"{agent_name}_output.log",
                f"{agent_name}.log",
                f"agent_{pid}.log",
                f"{agent_name}_console.txt",
                f"logs/{agent_name}.log",
                f"output/{agent_name}_output.txt"
            ]
            
            output_content = ""
            
            # Check log files
            for pattern in log_patterns:
                if os.path.exists(pattern):
                    try:
                        with open(pattern, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.strip():
                                output_content = content[-3000:]  # Last 3000 chars
                                break
                    except Exception:
                        continue
            
            # If no log files, try to get process info
            if not output_content:
                try:
                    proc = psutil.Process(pid)
                    cmdline = ' '.join(proc.cmdline())
                    
                    # Generate informative output based on process
                    output_content = f"""=== {agent_name} Process Info ===
PID: {pid}
Status: {proc.status()}
Command: {cmdline}
Memory: {round(proc.memory_info().rss / 1024 / 1024, 1)} MB
CPU: {round(proc.cpu_percent(), 1)}%
Threads: {proc.num_threads()}
Started: {datetime.fromtimestamp(proc.create_time()).strftime('%H:%M:%S')}

=== Real-time Monitoring ===
✅ Process is running
📊 Collecting metrics every 2 seconds
🔄 Auto-restart enabled
⚡ Live status updates

=== Recent Activity ===
{datetime.now().strftime('%H:%M:%S')} - Process monitoring active
{datetime.now().strftime('%H:%M:%S')} - Memory usage: {round(proc.memory_info().rss / 1024 / 1024, 1)} MB
{datetime.now().strftime('%H:%M:%S')} - CPU usage: {round(proc.cpu_percent(), 1)}%

=== Output Source ===
No log file found for {agent_name}
Monitoring process directly (PID: {pid})
Check these locations for logs:
• {agent_name}_output.log
• {agent_name}.log  
• logs/{agent_name}.log"""
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    output_content = f"""=== {agent_name} ===
❌ Process not accessible (PID: {pid})
🔄 May have restarted or requires elevated access
⚠️ Check process permissions

=== Troubleshooting ===
1. Verify process is still running
2. Check if process restarted with new PID
3. Ensure sufficient permissions
4. Look for crash logs in current directory

=== Status ===
Last checked: {datetime.now().strftime('%H:%M:%S')}
Process ID: {pid}
Agent: {agent_name}"""
            
            return output_content
            
        except Exception as e:
            return f"""=== {agent_name} Output Error ===
❌ Failed to collect output: {str(e)}
🔧 Agent: {agent_name}
🆔 PID: {pid}
⏰ Time: {datetime.now().strftime('%H:%M:%S')}

=== Suggested Actions ===
1. Check if process is still running
2. Verify log file permissions
3. Ensure agent is configured for logging
4. Check disk space for log files

=== Debug Info ===
Working directory: {os.getcwd()}
Available files: {', '.join(os.listdir('.')[:10])}"""
    
    def format_uptime(self, create_time):
        """Format process uptime"""
        try:
            uptime = datetime.now() - datetime.fromtimestamp(create_time)
            if uptime.days > 0:
                return f"{uptime.days}d {uptime.seconds // 3600}h"
            elif uptime.seconds > 3600:
                return f"{uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
            else:
                return f"{uptime.seconds // 60}m {uptime.seconds % 60}s"
        except:
            return "Unknown"

# Initialize dashboard
dashboard = ComprehensiveDashboard()

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Comprehensive Agent Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        }
        
        .header h1 { 
            font-size: 1.8em; 
            margin-bottom: 5px; 
            color: #4ade80;
        }
        
        .tabs {
            display: flex;
            background: #1f2937;
            border-bottom: 1px solid #374151;
            overflow-x: auto;
        }
        
        .tab {
            padding: 12px 20px;
            cursor: pointer;
            border: none;
            background: transparent;
            color: #9ca3af;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
            white-space: nowrap;
            font-size: 14px;
        }
        
        .tab:hover {
            background: #374151;
            color: #c9d1d9;
        }
        
        .tab.active {
            color: #4ade80;
            border-bottom-color: #4ade80;
            background: #374151;
        }
        
        .tab-content {
            display: none;
            padding: 20px;
            height: calc(100vh - 120px);
            overflow-y: auto;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Console Output Styles */
        .console {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            height: 100%;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
        }
        
        .console-header {
            background: #21262d;
            padding: 10px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .console-body {
            padding: 15px;
            height: calc(100% - 50px);
            overflow-y: auto;
        }
        
        /* Agent Consoles Grid Styles */
        .consoles-header {
            background: #21262d;
            padding: 15px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-radius: 8px;
        }
        
        .agent-consoles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            height: calc(100vh - 200px);
            overflow-y: auto;
        }
        
        .agent-console-panel {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            max-height: 400px;
        }
        
        .agent-console-header {
            background: #21262d;
            padding: 8px 12px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }
        
        .agent-console-name {
            font-weight: bold;
            color: #4ade80;
            font-size: 0.9em;
        }
        
        .agent-console-status {
            display: flex;
            gap: 8px;
            font-size: 0.7em;
        }
        
        .agent-console-output {
            padding: 8px;
            font-size: 0.65em;
            line-height: 1.2;
            font-family: 'Courier New', monospace;
            background: #0d1117;
            color: #c9d1d9;
            overflow-y: auto;
            flex-grow: 1;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .agent-console-output::-webkit-scrollbar { width: 4px; }
        .agent-console-output::-webkit-scrollbar-track { background: #21262d; }
        .agent-console-output::-webkit-scrollbar-thumb { background: #4ade80; border-radius: 2px; }
        
        .console-error {
            color: #ef4444;
            background: rgba(239, 68, 68, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: bold;
            animation: pulse-error 2s infinite;
        }
        
        .console-warning {
            color: #f59e0b;
            background: rgba(245, 158, 11, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        .console-success {
            color: #22c55e;
            background: rgba(34, 197, 94, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        .console-info {
            color: #3b82f6;
            background: rgba(59, 130, 246, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        .agent-health-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-left: 8px;
        }
        
        .health-excellent { background: #22c55e; }
        .health-good { background: #84cc16; }
        .health-warning { background: #f59e0b; }
        .health-critical { background: #ef4444; animation: pulse-critical 1s infinite; }
        
        .console-filter {
            padding: 8px;
            background: #21262d;
            border-bottom: 1px solid #30363d;
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .filter-input {
            background: #0d1117;
            border: 1px solid #30363d;
            color: #c9d1d9;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            min-width: 150px;
        }
        
        .filter-button {
            background: #374151;
            border: 1px solid #4b5563;
            color: #d1d5db;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.7em;
            transition: all 0.3s;
        }
        
        .filter-button.active {
            background: #4ade80;
            color: #000;
        }
        
        .agent-issue-overlay {
            position: absolute;
            top: 5px;
            right: 5px;
            background: #ef4444;
            color: white;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.6em;
            font-weight: bold;
            z-index: 10;
        }
        
        @keyframes pulse-error {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @keyframes pulse-critical {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }
        
        .log-entry {
            margin-bottom: 8px;
            padding: 5px;
            border-left: 3px solid #4ade80;
            background: rgba(74, 222, 128, 0.1);
            border-radius: 3px;
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
            color: #c9d1d9;
            white-space: pre-wrap;
        }
        
        /* Grid Styles */
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 15px;
        }
        
        .agent-panel {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .agent-panel:hover {
            border-color: #4ade80;
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
        }
        
        .agent-status {
            display: flex;
            gap: 10px;
            font-size: 0.8em;
        }
        
        .status-running { color: #22c55e; }
        .status-stopped { color: #ef4444; }
        
        .agent-output {
            padding: 12px;
            max-height: 200px;
            overflow-y: auto;
            font-size: 0.8em;
            background: #0d1117;
        }
        
        /* Metrics Styles */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .metric-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }
        
        .metric-title {
            color: #4ade80;
            font-size: 1.2em;
            margin-bottom: 15px;
            border-bottom: 1px solid #30363d;
            padding-bottom: 8px;
        }
        
        .metric-value {
            font-size: 2em;
            color: #60a5fa;
            margin-bottom: 5px;
        }
        
        .metric-label {
            color: #9ca3af;
            font-size: 0.9em;
        }
        
        /* System Resources Styles */
        .resource-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .resource-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }
        
        .resource-header {
            color: #4ade80;
            font-size: 1.1em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .resource-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #30363d;
        }
        
        .resource-item:last-child {
            border-bottom: none;
        }
        
        /* Agent Consoles Grid Styles */
        .consoles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 10px;
            height: 100%;
        }
        
        .console-panel {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 300px;
            max-height: 400px;
        }
        
        .console-panel.error {
            border-color: #ef4444;
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.3);
        }
        
        .console-panel.warning {
            border-color: #f59e0b;
            box-shadow: 0 0 8px rgba(245, 158, 11, 0.3);
        }
        
        .console-panel.active {
            border-color: #4ade80;
            box-shadow: 0 0 8px rgba(74, 222, 128, 0.3);
        }
        
        .console-panel-header {
            background: #21262d;
            padding: 8px 12px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            min-height: 40px;
        }
        
        .console-panel-title {
            font-weight: bold;
            color: #4ade80;
            font-size: 0.9em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .console-panel-status {
            display: flex;
            gap: 8px;
            font-size: 0.7em;
            color: #9ca3af;
        }
        
        .console-panel-body {
            flex: 1;
            padding: 8px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.65em;
            line-height: 1.2;
            background: #0d1117;
        }
        
        .console-output-text {
            color: #c9d1d9;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .console-output-text.error {
            color: #ff6b6b;
        }
        
        .console-output-text.warning {
            color: #ffd43b;
        }
        
        .console-no-output {
            color: #6b7280;
            font-style: italic;
            text-align: center;
            margin-top: 20px;
        }
        
        /* Highlight keywords */
        .keyword-error {
            background: rgba(239, 68, 68, 0.2);
            color: #ff6b6b;
            padding: 1px 3px;
            border-radius: 2px;
        }
        
        .keyword-warning {
            background: rgba(245, 158, 11, 0.2);
            color: #ffd43b;
            padding: 1px 3px;
            border-radius: 2px;
        }
        
        .keyword-success {
            background: rgba(74, 222, 128, 0.2);
            color: #4ade80;
            padding: 1px 3px;
            border-radius: 2px;
        }
        /* Cost Monitoring Styles */
        .cost-overview {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .cost-current {
            font-size: 3em;
            color: #60a5fa;
            margin-bottom: 10px;
        }
        
        .cost-threshold {
            color: #f59e0b;
            font-size: 1.1em;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #21262d; }
        ::-webkit-scrollbar-thumb { background: #4ade80; border-radius: 4px; }
        
        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            z-index: 1000;
        }
        
        .connected { background: #22c55e; color: #000; }
        .disconnected { background: #ef4444; color: #fff; }
        
        /* Features & Stories Management Styles */
        .features-overview {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .features-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        
        .feature-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            background: #238636;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            text-decoration: none;
            display: inline-block;
            cursor: pointer;
            font-size: 0.9em;
        }
        
        .btn:hover {
            background: #2ea043;
        }
        
        .btn-secondary {
            background: #0969da;
        }
        
        .btn-secondary:hover {
            background: #0860ca;
        }
        
        .features-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .feature-card {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s ease;
        }
        
        .feature-card:hover {
            border-color: #4ade80;
            box-shadow: 0 2px 8px rgba(74, 222, 128, 0.2);
        }
        
        .feature-title {
            font-size: 1.1em;
            font-weight: bold;
            color: #e6edf3;
            margin-bottom: 8px;
        }
        
        .feature-status {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 500;
            margin-bottom: 10px;
        }
        
        .status-concept { background: #656d76; color: #fff; }
        .status-planned { background: #0969da; color: #fff; }
        .status-in-development { background: #fb8500; color: #fff; }
        .status-ready-for-release { background: #238636; color: #fff; }
        .status-released { background: #2ea043; color: #fff; }
        
        .feature-description {
            color: #7d8590;
            font-size: 0.9em;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        
        .feature-progress {
            margin-bottom: 10px;
        }
        
        .feature-progress-bar {
            width: 100%;
            height: 6px;
            background: #30363d;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 5px;
        }
        
        .feature-progress-fill {
            height: 100%;
            background: #4ade80;
            transition: width 0.3s ease;
        }
        
        .feature-stats {
            display: flex;
            justify-content: space-between;
            font-size: 0.8em;
            color: #7d8590;
        }
        
        .story-preview {
            background: #161b22;
            border: 1px solid #21262d;
            border-radius: 4px;
            padding: 8px;
            margin-top: 10px;
            font-size: 0.8em;
        }
        
        .story-title {
            font-weight: 500;
            color: #e6edf3;
            margin-bottom: 3px;
        }
        
        .story-points {
            background: #0969da;
            color: white;
            padding: 1px 5px;
            border-radius: 8px;
            font-size: 0.7em;
            margin-left: 5px;
        }
        
        /* AI Development Team Styles */
        .team-overview {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .team-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .team-roster {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }
        
        .team-member {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        
        .member-info {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .member-name {
            font-weight: bold;
            color: #e6edf3;
        }
        
        .member-role {
            color: #7d8590;
            font-size: 0.9em;
        }
        
        .member-status {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }
        
        .status-active { background: #238636; color: #fff; }
        .status-busy { background: #f85149; color: #fff; }
        .status-idle { background: #656d76; color: #fff; }
        
        /* Work Queue Styles */
        .work-queue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        
        .queue-controls {
            display: flex;
            gap: 10px;
        }
        
        .queue-controls select {
            background: #21262d;
            color: #e6edf3;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 0.9em;
        }
        
        .work-queue-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }
        
        .work-item {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 15px;
            transition: all 0.2s ease;
        }
        
        .work-item:hover {
            border-color: #4ade80;
            box-shadow: 0 2px 8px rgba(74, 222, 128, 0.2);
        }
        
        .work-item-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        
        .work-item-title {
            font-weight: bold;
            color: #e6edf3;
            margin-bottom: 5px;
        }
        
        .work-item-id {
            color: #7d8590;
            font-size: 0.8em;
        }
        
        .priority-badge {
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.7em;
            font-weight: bold;
        }
        
        .priority-P0 { background: #da3633; color: #fff; }
        .priority-P1 { background: #fb8500; color: #fff; }
        .priority-P2 { background: #ffb700; color: #000; }
        .priority-P3 { background: #238636; color: #fff; }
        
        .work-item-assignee {
            color: #4ade80;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #30363d;
            border-radius: 2px;
            margin-top: 10px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: #4ade80;
            transition: width 0.3s ease;
        }
        
        /* GitHub Integration Styles */
        .github-overview {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .github-status {
            background: #0d1117;
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
            background: #656d76;
        }
        
        .status-dot.connected { background: #238636; }
        .status-dot.connecting { background: #fb8500; animation: pulse 1s infinite; }
        .status-dot.error { background: #da3633; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .github-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .github-activity {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }
        
        .activity-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #21262d;
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            font-size: 1.2em;
        }
        
        .activity-text {
            flex: 1;
            color: #e6edf3;
            font-size: 0.9em;
        }
        
        .activity-time {
            color: #7d8590;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Comprehensive Agent Dashboard</h1>
        <div class="connection-status" id="connectionStatus">🔴 Disconnected</div>
    </div>
    
    <div class="tabs">
        <button class="tab active" onclick="showTab('console')">📋 Console Output</button>
        <button class="tab" onclick="showTab('consoles')">🖥️ Agent Consoles</button>
        <button class="tab" onclick="showTab('grid')">🌐 Agent Grid</button>
        <button class="tab" onclick="showTab('resources')">⚙️ System Resources</button>
        <button class="tab" onclick="showTab('metrics')">📊 Performance Metrics</button>
        <button class="tab" onclick="showTab('cost')">💰 Cost Monitoring</button>
        <button class="tab" onclick="showTab('features')">🎯 Features & Stories</button>
        <button class="tab" onclick="showTab('team')">👥 AI Development Team</button>
        <button class="tab" onclick="showTab('workqueue')">📋 Work Queue</button>
        <button class="tab" onclick="showTab('github')">🐙 GitHub Integration</button>
    </div>
    
    <!-- Console Output Tab -->
    <div class="tab-content active" id="console-tab">
        <div class="console">
            <div class="console-header">
                <span>🔴 Live Console Output</span>
                <span id="console-count">0 entries</span>
            </div>
            <div class="console-body" id="console-logs">
                <div class="log-entry">
                    <div class="log-timestamp">Waiting for data...</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Agent Consoles Tab -->
    <div class="tab-content" id="consoles-tab">
        <div class="consoles-header">
            <span>🖥️ All Agent Console Outputs</span>
            <span id="agent-consoles-count">0 agents</span>
        </div>
        <div class="console-filter">
            <input type="text" class="filter-input" id="console-search" placeholder="Search console output..." onkeyup="filterConsoles()">
            <button class="filter-button active" onclick="toggleFilter('all')">All</button>
            <button class="filter-button" onclick="toggleFilter('errors')">Errors Only</button>
            <button class="filter-button" onclick="toggleFilter('warnings')">Warnings</button>
            <button class="filter-button" onclick="toggleFilter('healthy')">Healthy</button>
            <button class="filter-button" onclick="clearConsoleFilters()">Clear</button>
        </div>
        <div class="agent-consoles-grid" id="agent-consoles-grid">
            <div style="text-align: center; color: #6b7280; padding: 40px;">Loading agent consoles...</div>
        </div>
    </div>
    
    <!-- Agent Consoles Tab -->
    <div class="tab-content" id="consoles-tab">
        <div class="consoles-grid" id="consoles-grid">
            <div style="text-align: center; color: #6b7280; padding: 40px;">Loading agent consoles...</div>
        </div>
    </div>
    
    <!-- Agent Grid Tab -->
    <div class="tab-content" id="grid-tab">
        <div class="agent-grid" id="agent-grid">
            <div style="text-align: center; color: #6b7280; padding: 40px;">Loading agents...</div>
        </div>
    </div>
    
    <!-- System Resources Tab -->
    <div class="tab-content" id="resources-tab">
        <div class="resource-grid" id="resource-grid">
            <div style="text-align: center; color: #6b7280; padding: 40px;">Loading system resources...</div>
        </div>
    </div>
    
    <!-- Performance Metrics Tab -->
    <div class="tab-content" id="metrics-tab">
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">🖥️ System CPU</div>
                <div class="metric-value" id="system-cpu">0%</div>
                <div class="metric-label">Current Usage</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">💾 System Memory</div>
                <div class="metric-value" id="system-memory">0%</div>
                <div class="metric-label">Current Usage</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">🤖 Active Agents</div>
                <div class="metric-value" id="active-agents">0</div>
                <div class="metric-label">Running Processes</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">📊 Agent Memory</div>
                <div class="metric-value" id="agent-memory">0 MB</div>
                <div class="metric-label">Total Usage</div>
            </div>
        </div>
        <div style="margin-top: 20px;">
            <canvas id="performance-chart" width="400" height="200"></canvas>
        </div>
    </div>
    
    <!-- Cost Monitoring Tab -->
    <div class="tab-content" id="cost-tab">
        <div class="cost-overview">
            <div class="cost-current" id="current-cost">$0.00</div>
            <div class="cost-threshold">Threshold: <span id="cost-threshold">$25.00</span></div>
        </div>
        <div style="margin-top: 20px;">
            <canvas id="cost-chart" width="400" height="200"></canvas>
        </div>
    </div>

    <!-- Features & Stories Tab -->
    <div class="tab-content" id="features-tab">
        <div class="features-overview">
            <div class="features-header">
                <h3>🎯 Features & User Stories Management</h3>
                <div class="feature-actions">
                    <a href="http://localhost:5004" target="_blank" class="btn">🚀 Open Feature Manager</a>
                    <button onclick="loadFeatureData()" class="btn btn-secondary">🔄 Refresh</button>
                </div>
            </div>
            
            <div class="features-summary" id="features-summary">
                <div class="metric-card">
                    <div class="metric-title">📋 Total Features</div>
                    <div class="metric-value" id="total-features">0</div>
                    <div class="metric-label">In Development</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">📚 User Stories</div>
                    <div class="metric-value" id="total-stories">0</div>
                    <div class="metric-label">In Backlog</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🏃 In Progress</div>
                    <div class="metric-value" id="stories-in-progress">0</div>
                    <div class="metric-label">Active Stories</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">✅ Completed</div>
                    <div class="metric-value" id="stories-completed">0</div>
                    <div class="metric-label">This Sprint</div>
                </div>
            </div>
            
            <div class="features-grid" id="features-grid">
                <div style="text-align: center; color: #6b7280; padding: 40px;">
                    <p>Loading features and user stories...</p>
                    <p><a href="http://localhost:5004" target="_blank" style="color: #4ade80;">Open Feature Manager</a> to create features and stories</p>
                </div>
            </div>
        </div>
    </div>

    <!-- AI Development Team Tab -->
    <div class="tab-content" id="team-tab">
        <div class="team-overview">
            <div class="team-metrics">
                <div class="metric-card">
                    <div class="metric-title">👥 Active Developers</div>
                    <div class="metric-value" id="active-developers">0</div>
                    <div class="metric-label">AI Agents</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">📋 Work in Progress</div>
                    <div class="metric-value" id="work-in-progress">0</div>
                    <div class="metric-label">Active Tasks</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">✅ Completed Today</div>
                    <div class="metric-value" id="completed-today">0</div>
                    <div class="metric-label">Tasks</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🚀 Team Velocity</div>
                    <div class="metric-value" id="team-velocity">0</div>
                    <div class="metric-label">Story Points/Sprint</div>
                </div>
            </div>
            <div class="team-roster" id="team-roster">
                <h3>🤖 AI Development Team</h3>
                <div id="team-members">
                    <div style="text-align: center; color: #6b7280; padding: 20px;">Loading team members...</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Work Queue Tab -->
    <div class="tab-content" id="workqueue-tab">
        <div class="work-queue-header">
            <h3>📋 Development Work Queue</h3>
            <div class="queue-controls">
                <select id="priority-filter" onchange="filterQueue()">
                    <option value="all">All Priorities</option>
                    <option value="P0_CRITICAL">🔴 P0 Critical</option>
                    <option value="P1_HIGH">🟠 P1 High</option>
                    <option value="P2_MEDIUM">🟡 P2 Medium</option>
                    <option value="P3_LOW">🟢 P3 Low</option>
                </select>
                <select id="status-filter" onchange="filterQueue()">
                    <option value="all">All Status</option>
                    <option value="queued">📥 Queued</option>
                    <option value="assigned">👤 Assigned</option>
                    <option value="in_progress">⚡ In Progress</option>
                    <option value="review">👀 Review</option>
                    <option value="completed">✅ Completed</option>
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
            <div class="github-status" id="github-status">
                <h3>🐙 GitHub Integration Status</h3>
                <div class="status-indicator" id="github-connection">
                    <span class="status-dot"></span>
                    <span>Connecting...</span>
                </div>
            </div>
            <div class="github-metrics">
                <div class="metric-card">
                    <div class="metric-title">📋 Open Issues</div>
                    <div class="metric-value" id="open-issues">0</div>
                    <div class="metric-label">Across Repositories</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🔀 Open PRs</div>
                    <div class="metric-value" id="open-prs">0</div>
                    <div class="metric-label">Pending Review</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">✅ Merged Today</div>
                    <div class="metric-value" id="merged-today">0</div>
                    <div class="metric-label">Pull Requests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🏃 Auto-Assignments</div>
                    <div class="metric-value" id="auto-assignments">0</div>
                    <div class="metric-label">This Hour</div>
                </div>
            </div>
            <div class="github-activity" id="github-activity">
                <h4>Recent GitHub Activity</h4>
                <div id="github-activity-feed">
                    <div style="text-align: center; color: #6b7280; padding: 20px;">Loading GitHub activity...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let currentTab = 'console';
        let performanceChart = null;
        let costChart = null;
        
        socket.on('connect', function() {
            document.getElementById('connectionStatus').textContent = '🟢 Connected';
            document.getElementById('connectionStatus').className = 'connection-status connected';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connectionStatus').textContent = '🔴 Disconnected';
            document.getElementById('connectionStatus').className = 'connection-status disconnected';
        });
        
        socket.on('dashboard_update', function(data) {
            updateConsoleTab(data.console_logs || []);
            updateAgentConsoles(data.agents || {}, data.outputs || {});
            updateAgentGrid(data.agents || {}, data.outputs || {});
            updateSystemResources(data.agents || {});
            updateMetrics(data.system_metrics || {});
            updateCost(data.cost_data || {});
            updateTeamMetrics(data);
            updateWorkQueue(data);
            updateGitHubStatus(data);
        });
        
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
            
            // Force data refresh for the current tab
            refreshCurrentTab();
        }
        
        function refreshCurrentTab() {
            // Force refresh data for current tab
            socket.emit('request_update', {tab: currentTab});
        }
        
        function updateConsoleTab(logs) {
            const container = document.getElementById('console-logs');
            const countElement = document.getElementById('console-count');
            
            if (logs.length === 0) {
                container.innerHTML = '<div class="log-entry"><div class="log-timestamp">No logs available</div></div>';
                countElement.textContent = '0 entries';
                return;
            }
            
            let html = '';
            logs.forEach(log => {
                const timestamp = new Date(log.timestamp).toLocaleTimeString();
                html += `
                    <div class="log-entry">
                        <div class="log-timestamp">[${timestamp}] <span class="log-source">${log.source}</span></div>
                        <div class="log-message">${log.message}</div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
            countElement.textContent = `${logs.length} entries`;
            
            // Auto-scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
        
        function updateAgentConsoles(agents, outputs) {
            const grid = document.getElementById('agent-consoles-grid');
            const countElement = document.getElementById('agent-consoles-count');
            
            if (Object.keys(agents).length === 0) {
                grid.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 40px;">No agents running</div>';
                countElement.textContent = '0 agents';
                return;
            }
            
            let html = '';
            let healthyCount = 0;
            let warningCount = 0;
            let errorCount = 0;
            
            for (const [name, agent] of Object.entries(agents)) {
                const output = outputs[name] || { text: 'No output available' };
                let formattedOutput = output.text;
                
                // Enhanced pattern matching for issues
                const errorPatterns = [
                    /(error|failed|exception|traceback|crash|fatal|critical)/gi,
                    /(connection.*timeout|network.*error|dns.*failed)/gi,
                    /(401.*unauthorized|403.*forbidden|authentication.*failed)/gi,
                    /(out of memory|disk.*full|resource.*exhausted)/gi
                ];
                
                const warningPatterns = [
                    /(warning|warn|deprecated|retry|timeout)/gi,
                    /(429.*rate.*limit|quota.*exceeded|throttled)/gi,
                    /(slow.*response|performance.*degraded)/gi
                ];
                
                const successPatterns = [
                    /(success|completed|✅|✓|finished|ready|started)/gi,
                    /(connected|authenticated|authorized|approved)/gi
                ];
                
                const infoPatterns = [
                    /(info|debug|status|monitoring|checking)/gi
                ];
                
                // Count issues for health calculation
                let errorCount_agent = 0;
                let warningCount_agent = 0;
                
                // Apply highlighting with issue counting
                errorPatterns.forEach(pattern => {
                    const matches = formattedOutput.match(pattern);
                    if (matches) errorCount_agent += matches.length;
                    formattedOutput = formattedOutput.replace(pattern, '<span class="console-error">$1</span>');
                });
                
                warningPatterns.forEach(pattern => {
                    const matches = formattedOutput.match(pattern);
                    if (matches) warningCount_agent += matches.length;
                    formattedOutput = formattedOutput.replace(pattern, '<span class="console-warning">$1</span>');
                });
                
                successPatterns.forEach(pattern => {
                    formattedOutput = formattedOutput.replace(pattern, '<span class="console-success">$1</span>');
                });
                
                infoPatterns.forEach(pattern => {
                    formattedOutput = formattedOutput.replace(pattern, '<span class="console-info">$1</span>');
                });
                
                // Calculate agent health
                let healthClass = 'health-excellent';
                let healthText = 'Healthy';
                let issueOverlay = '';
                
                if (errorCount_agent > 5) {
                    healthClass = 'health-critical';
                    healthText = 'Critical';
                    issueOverlay = `<div class="agent-issue-overlay">${errorCount_agent} errors</div>`;
                    errorCount++;
                } else if (errorCount_agent > 0 || warningCount_agent > 10) {
                    healthClass = 'health-warning';
                    healthText = 'Issues';
                    issueOverlay = `<div class="agent-issue-overlay">${errorCount_agent + warningCount_agent} issues</div>`;
                    warningCount++;
                } else if (warningCount_agent > 0) {
                    healthClass = 'health-good';
                    healthText = 'Minor Issues';
                    warningCount++;
                } else {
                    healthText = 'Healthy';
                    healthyCount++;
                }
                
                // Agent status indicator
                let statusClass = agent.status === 'running' ? 'status-running' : 'status-stopped';
                
                // Limit output length for grid view
                if (formattedOutput.length > 2000) {
                    formattedOutput = '...' + formattedOutput.slice(-2000);
                }
                
                html += `
                    <div class="agent-console-panel" data-agent="${name}" data-health="${healthClass}" data-errors="${errorCount_agent}" data-warnings="${warningCount_agent}">
                        ${issueOverlay}
                        <div class="agent-console-header">
                            <div class="agent-console-name">
                                ${name}
                                <span class="agent-health-indicator ${healthClass}" title="${healthText}"></span>
                            </div>
                            <div class="agent-console-status">
                                <span class="${statusClass}">${agent.status}</span>
                                <span>${agent.memory_mb}MB</span>
                                <span>${agent.cpu_percent}%</span>
                            </div>
                        </div>
                        <div class="agent-console-output">${formattedOutput}</div>
                    </div>
                `;
            }
            
            grid.innerHTML = html;
            
            // Update count with health summary
            const totalAgents = Object.keys(agents).length;
            countElement.innerHTML = `
                ${totalAgents} agents: 
                <span style="color: #22c55e">${healthyCount} healthy</span>, 
                <span style="color: #f59e0b">${warningCount} warnings</span>, 
                <span style="color: #ef4444">${errorCount} errors</span>
            `;
            
            // Auto-scroll each console to bottom
            setTimeout(() => {
                const consoles = document.querySelectorAll('.agent-console-output');
                consoles.forEach(console => {
                    console.scrollTop = console.scrollHeight;
                });
            }, 100);
        }
        
        function updateAgentConsoles(agents, outputs) {
            const grid = document.getElementById('consoles-grid');
            
            if (Object.keys(agents).length === 0) {
                grid.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 40px;">No agents running</div>';
                return;
            }
            
            let html = '';
            for (const [name, agent] of Object.entries(agents)) {
                const output = outputs[name] || { text: 'No output available' };
                let outputText = output.text || 'No output';
                
                // Determine panel status based on output content
                let panelClass = 'console-panel';
                let statusIndicator = '🟢';
                
                if (containsErrors(outputText)) {
                    panelClass += ' error';
                    statusIndicator = '🔴';
                } else if (containsWarnings(outputText)) {
                    panelClass += ' warning';
                    statusIndicator = '🟡';
                } else if (agent.status === 'running') {
                    panelClass += ' active';
                    statusIndicator = '🟢';
                } else {
                    statusIndicator = '⚫';
                }
                
                // Highlight important keywords in output
                outputText = highlightKeywords(outputText);
                
                // Limit output length for grid view
                if (outputText.length > 1500) {
                    outputText = '...' + outputText.slice(-1500);
                }
                
                html += `
                    <div class="${panelClass}">
                        <div class="console-panel-header">
                            <div class="console-panel-title">${statusIndicator} ${name}</div>
                            <div class="console-panel-status">
                                <span>${agent.memory_mb}MB</span>
                                <span>${agent.cpu_percent}%</span>
                                <span>${agent.uptime}</span>
                            </div>
                        </div>
                        <div class="console-panel-body">
                            <div class="console-output-text">${outputText || '<div class="console-no-output">No output available</div>'}</div>
                        </div>
                    </div>
                `;
            }
            
            grid.innerHTML = html;
            
            // Auto-scroll all console panels to bottom
            setTimeout(() => {
                document.querySelectorAll('.console-panel-body').forEach(panel => {
                    panel.scrollTop = panel.scrollHeight;
                });
            }, 100);
        }
        
        function containsErrors(text) {
            const errorKeywords = ['error', 'exception', 'failed', 'traceback', 'fatal', 'critical'];
            const lowerText = text.toLowerCase();
            return errorKeywords.some(keyword => lowerText.includes(keyword));
        }
        
        function containsWarnings(text) {
            const warningKeywords = ['warning', 'warn', 'deprecated', 'caution', 'alert'];
            const lowerText = text.toLowerCase();
            return warningKeywords.some(keyword => lowerText.includes(keyword));
        }
        
        function highlightKeywords(text) {
            // Highlight error keywords
            text = text.replace(/(error|exception|failed|traceback|fatal|critical)/gi, '<span class="keyword-error">$1</span>');
            
            // Highlight warning keywords
            text = text.replace(/(warning|warn|deprecated|caution|alert)/gi, '<span class="keyword-warning">$1</span>');
            
            // Highlight success keywords
            text = text.replace(/(success|completed|finished|started|connected|ready)/gi, '<span class="keyword-success">$1</span>');
            
            return text;
        }
            const grid = document.getElementById('agent-grid');
            
            if (Object.keys(agents).length === 0) {
                grid.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 40px;">No agents running</div>';
                return;
            }
            
            let html = '';
            for (const [name, agent] of Object.entries(agents)) {
                const output = outputs[name] || { text: 'No output available' };
                html += `
                    <div class="agent-panel">
                        <div class="agent-header">
                            <div class="agent-name">${name}</div>
                            <div class="agent-status">
                                <span class="status-${agent.status}">${agent.status}</span>
                                <span>${agent.memory_mb}MB</span>
                                <span>${agent.cpu_percent}%</span>
                                <span>${agent.uptime}</span>
                            </div>
                        </div>
                        <div class="agent-output">
                            <pre>${output.text}</pre>
                        </div>
                    </div>
                `;
            }
            
            grid.innerHTML = html;
        }
        
        function updateSystemResources(agents) {
            const grid = document.getElementById('resource-grid');
            
            if (Object.keys(agents).length === 0) {
                grid.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 40px;">No agents to monitor</div>';
                return;
            }
            
            let html = '';
            for (const [name, agent] of Object.entries(agents)) {
                const systemInfo = agent.system_info || {};
                
                html += `
                    <div class="resource-card">
                        <div class="resource-header">⚙️ ${name}</div>
                `;
                
                if (systemInfo.memory) {
                    html += `
                        <div class="resource-item">
                            <span>Memory RSS:</span>
                            <span>${systemInfo.memory.rss_mb} MB</span>
                        </div>
                        <div class="resource-item">
                            <span>Memory VMS:</span>
                            <span>${systemInfo.memory.vms_mb} MB</span>
                        </div>
                        <div class="resource-item">
                            <span>Memory %:</span>
                            <span>${systemInfo.memory.percent}%</span>
                        </div>
                    `;
                }
                
                if (systemInfo.cpu) {
                    html += `
                        <div class="resource-item">
                            <span>CPU %:</span>
                            <span>${systemInfo.cpu.percent}%</span>
                        </div>
                        <div class="resource-item">
                            <span>Threads:</span>
                            <span>${systemInfo.cpu.num_threads}</span>
                        </div>
                    `;
                }
                
                if (systemInfo.network && !systemInfo.network.error) {
                    html += `
                        <div class="resource-item">
                            <span>Connections:</span>
                            <span>${systemInfo.network.total_connections}</span>
                        </div>
                    `;
                }
                
                html += '</div>';
            }
            
            grid.innerHTML = html;
        }
        
        function updateMetrics(metrics) {
            if (!metrics.system) return;
            
            document.getElementById('system-cpu').textContent = metrics.system.cpu_percent + '%';
            document.getElementById('system-memory').textContent = metrics.system.memory_percent + '%';
            document.getElementById('active-agents').textContent = metrics.agents?.running || 0;
            document.getElementById('agent-memory').textContent = (metrics.agents?.total_memory_mb || 0) + ' MB';
        }
        
        function updateCost(costData) {
            document.getElementById('current-cost').textContent = '$' + (costData.current || 0).toFixed(2);
            document.getElementById('cost-threshold').textContent = '$' + (costData.threshold || 25).toFixed(2);
        }
        
        // AI Development Team update functions
        function updateTeamMetrics(data) {
            if (data.team_metrics) {
                document.getElementById('active-developers').textContent = data.team_metrics.active_developers || 0;
                document.getElementById('work-in-progress').textContent = data.team_metrics.work_in_progress || 0;
                document.getElementById('completed-today').textContent = data.team_metrics.completed_today || 0;
                document.getElementById('team-velocity').textContent = data.team_metrics.velocity || 0;
            }
            
            // Update team roster
            if (data.team_communication) {
                updateTeamRoster(data.team_communication);
            }
        }
        
        function updateTeamRoster(teamData) {
            const container = document.getElementById('team-members');
            if (!teamData || !teamData.agents_by_role) {
                return;
            }
            
            let html = '';
            Object.entries(teamData.agents_by_role).forEach(([role, agents]) => {
                agents.forEach(agent => {
                    const statusClass = agent.status === 'active' ? 'status-active' : 
                                       agent.pending_messages > 0 ? 'status-busy' : 'status-idle';
                    html += `
                        <div class="team-member">
                            <div class="member-info">
                                <div class="member-name">${agent.id}</div>
                                <div class="member-role">${role.replace('_', ' ')}</div>
                            </div>
                            <div class="member-status ${statusClass}">
                                ${agent.status} ${agent.pending_messages > 0 ? `(${agent.pending_messages} msgs)` : ''}
                            </div>
                        </div>
                    `;
                });
            });
            container.innerHTML = html || '<div style="text-align: center; color: #6b7280; padding: 20px;">No team members registered</div>';
        }
        
        function updateWorkQueue(data) {
            if (data.work_queue) {
                updateWorkQueueGrid(data.work_queue);
            }
        }
        
        function updateWorkQueueGrid(queueData) {
            const container = document.getElementById('work-queue-grid');
            if (!queueData || !queueData.agents) {
                return;
            }
            
            let html = '';
            Object.entries(queueData.agents).forEach(([agentId, agentData]) => {
                if (agentData.current_workload && agentData.current_workload.length > 0) {
                    agentData.current_workload.forEach(workItem => {
                        const priorityClass = `priority-${workItem.priority?.replace('_', '-') || 'P2'}`;
                        html += `
                            <div class="work-item">
                                <div class="work-item-header">
                                    <div>
                                        <div class="work-item-title">${workItem.title || 'Untitled Task'}</div>
                                        <div class="work-item-id">#${workItem.id}</div>
                                    </div>
                                    <div class="priority-badge ${priorityClass}">
                                        ${workItem.priority || 'P2'}
                                    </div>
                                </div>
                                <div class="work-item-description">
                                    ${workItem.description ? workItem.description.substring(0, 100) + '...' : 'No description'}
                                </div>
                                <div class="work-item-assignee">👤 ${agentId}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${workItem.progress_percentage || 0}%"></div>
                                </div>
                            </div>
                        `;
                    });
                }
            });
            container.innerHTML = html || '<div style="text-align: center; color: #6b7280; padding: 40px;">No active work items</div>';
        }
        
        function updateGitHubStatus(data) {
            if (data.github_integration) {
                const status = data.github_integration;
                const indicator = document.querySelector('#github-connection .status-dot');
                const text = document.querySelector('#github-connection span:last-child');
                
                if (status.connected) {
                    indicator.className = 'status-dot connected';
                    text.textContent = 'Connected';
                } else {
                    indicator.className = 'status-dot connecting';
                    text.textContent = 'Connecting...';
                }
                
                // Update GitHub metrics
                if (status.metrics) {
                    document.getElementById('open-issues').textContent = status.metrics.open_issues || 0;
                    document.getElementById('open-prs').textContent = status.metrics.open_prs || 0;
                    document.getElementById('merged-today').textContent = status.metrics.merged_today || 0;
                    document.getElementById('auto-assignments').textContent = status.metrics.auto_assignments || 0;
                }
                
                // Update activity feed
                if (status.recent_activity) {
                    updateGitHubActivity(status.recent_activity);
                }
            }
        }
        
        function updateGitHubActivity(activities) {
            const container = document.getElementById('github-activity-feed');
            if (!activities || activities.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 20px;">No recent activity</div>';
                return;
            }
            
            let html = '';
            activities.slice(0, 10).forEach(activity => {
                const icon = activity.type === 'issue' ? '📋' :
                           activity.type === 'pr' ? '🔀' :
                           activity.type === 'commit' ? '💾' : '🔄';
                html += `
                    <div class="activity-item">
                        <div class="activity-icon">${icon}</div>
                        <div class="activity-text">${activity.description}</div>
                        <div class="activity-time">${activity.time}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
        
        function filterQueue() {
            const priorityFilter = document.getElementById('priority-filter').value;
            const statusFilter = document.getElementById('status-filter').value;
            const workItems = document.querySelectorAll('.work-item');
            
            workItems.forEach(item => {
                const priority = item.querySelector('.priority-badge').textContent.trim();
                const assignee = item.querySelector('.work-item-assignee').textContent;
                
                let showItem = true;
                
                if (priorityFilter !== 'all' && !priority.includes(priorityFilter.replace('_', ''))) {
                    showItem = false;
                }
                
                // Status filtering would need more data from backend
                // For now, just show all items
                
                item.style.display = showItem ? 'block' : 'none';
            });
        }
        
        // Console filtering functions
        let activeFilter = 'all';
        
        function filterConsoles() {
            const searchTerm = document.getElementById('console-search').value.toLowerCase();
            const panels = document.querySelectorAll('.agent-console-panel');
            
            panels.forEach(panel => {
                const agentName = panel.getAttribute('data-agent').toLowerCase();
                const output = panel.querySelector('.agent-console-output').textContent.toLowerCase();
                const matchesSearch = !searchTerm || agentName.includes(searchTerm) || output.includes(searchTerm);
                const matchesFilter = applyHealthFilter(panel);
                
                panel.style.display = (matchesSearch && matchesFilter) ? 'flex' : 'none';
            });
        }
        
        function toggleFilter(filterType) {
            activeFilter = filterType;
            
            // Update button states
            document.querySelectorAll('.filter-button').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            filterConsoles();
        }
        
        function applyHealthFilter(panel) {
            const errors = parseInt(panel.getAttribute('data-errors') || '0');
            const warnings = parseInt(panel.getAttribute('data-warnings') || '0');
            
            switch(activeFilter) {
                case 'all':
                    return true;
                case 'errors':
                    return errors > 0;
                case 'warnings':
                    return warnings > 0 || errors > 0;
                case 'healthy':
                    return errors === 0 && warnings === 0;
                default:
                    return true;
            }
        }
        
        function clearConsoleFilters() {
            document.getElementById('console-search').value = '';
            activeFilter = 'all';
            
            document.querySelectorAll('.filter-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector('.filter-button').classList.add('active');
            
            document.querySelectorAll('.agent-console-panel').forEach(panel => {
                panel.style.display = 'flex';
            });
        }
    </script>
</body>
</html>'''

@app.route('/api/data')
def get_data():
    return jsonify({
        'agents': dashboard.agent_data,
        'outputs': dashboard.agent_outputs,
        'console_logs': dashboard.console_logs,
        'system_metrics': dashboard.system_metrics,
        'cost_data': dashboard.cost_data,
        'team_metrics': dashboard.team_metrics,
        'team_communication': dashboard.team_communication.get_team_status() if dashboard.team_communication else None,
        'work_queue': dashboard.work_queue.get_queue_status() if dashboard.work_queue else None,
        'github_integration': dashboard.github_integration,
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
        'console_logs': dashboard.console_logs,
        'system_metrics': dashboard.system_metrics,
        'cost_data': dashboard.cost_data,
        'team_metrics': dashboard.team_metrics,
        'team_communication': dashboard.team_communication.get_team_status() if dashboard.team_communication else None,
        'work_queue': dashboard.work_queue.get_queue_status() if dashboard.work_queue else None,
        'github_integration': dashboard.github_integration,
        'timestamp': datetime.now().isoformat()
    }
    socketio.emit('dashboard_update', data)

def background_task():
    """Background task to emit updates every 3 seconds"""
    while True:
        socketio.sleep(3)
        emit_dashboard_update()

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 COMPREHENSIVE TABBED AGENT DASHBOARD")
    print("=" * 80)
    print("📊 URL: http://localhost:5003")
    print("🔄 Real-time monitoring with tabbed interface")
    print("📋 Console Output | 🌐 Agent Grid | ⚙️ System Resources | 📊 Metrics | 💰 Cost")
    print("=" * 80)
    
    # Start background task
    socketio.start_background_task(background_task)
    
    socketio.run(app, host='0.0.0.0', port=5003, debug=False)
