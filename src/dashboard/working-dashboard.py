#!/usr/bin/env python3
"""
Working Dashboard - Phase 5 DevOps Agent Monitoring
"""

import sys
import os
import time
import json
import psutil
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import glob

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dashboard_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class WorkingDashboard:
    def __init__(self):
        self.agent_data = {}
        self.system_metrics = {}
        self.team_metrics = {
            "active_agents": 0,
            "work_in_progress": 0,
            "completed_today": 0,
            "phase_status": "Phase 5: DevOps Agent - In Development",
            "devops_progress": 0,
            "deployment_status": "Waiting for DevOps Agent"
        }
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background monitoring"""
        Thread(target=self.collect_data, daemon=True).start()
    
    def collect_data(self):
        """Collect system and agent data"""
        while True:
            try:
                # System metrics
                self.system_metrics = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Check for agents
                self.scan_for_agents()
                
                # Update team metrics
                self.update_team_metrics()
                
                time.sleep(3)
            except Exception as e:
                print(f"Error collecting data: {e}")
                time.sleep(5)
    
    def scan_for_agents(self):
        """Scan for running agent processes"""
        try:
            agents = {}
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if any(agent in cmdline for agent in ['ai-architect', 'ai-developer', 'ai-qa', 'ai-devops', 'github-issues']):
                            agent_name = None
                            agent_type = None
                            
                            if 'ai-architect' in cmdline:
                                agent_name = 'ai-architect-001'
                                agent_type = 'architect'
                            elif 'ai-developer' in cmdline:
                                agent_name = 'ai-developer-001'
                                agent_type = 'developer'
                            elif 'ai-qa' in cmdline:
                                agent_name = 'ai-qa-001'
                                agent_type = 'qa'
                            elif 'ai-devops' in cmdline:
                                agent_name = 'ai-devops-001'
                                agent_type = 'devops'
                            elif 'github-issues' in cmdline:
                                agent_name = 'github-issues-001'
                                agent_type = 'github'
                            
                            if agent_name:
                                agents[agent_name] = {
                                    'status': 'running',
                                    'type': agent_type,
                                    'pid': proc.info['pid'],
                                    'uptime': datetime.now().timestamp() - proc.info['create_time'],
                                    'cmdline': cmdline
                                }
                except:
                    continue
            
            self.agent_data = agents
            
            # Check for DevOps agent file to update progress
            self.check_devops_progress()
            
        except Exception as e:
            print(f"Error scanning agents: {e}")
    
    def check_devops_progress(self):
        """Check DevOps agent development progress"""
        try:
            devops_file = "ai-devops-agent.py"
            if os.path.exists(devops_file):
                with open(devops_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    self.team_metrics['devops_progress'] = min(100, (lines / 10))  # Progress based on lines
                    self.team_metrics['deployment_status'] = f"DevOps Agent: {lines} lines developed"
            else:
                self.team_metrics['devops_progress'] = 0
                self.team_metrics['deployment_status'] = "Waiting for Opus to create DevOps Agent"
        except Exception as e:
            print(f"Error checking DevOps progress: {e}")
    
    def update_team_metrics(self):
        """Update team metrics"""
        self.team_metrics['active_agents'] = len(self.agent_data)
        self.team_metrics['timestamp'] = datetime.now().isoformat()

dashboard = WorkingDashboard()

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>AI Development Team Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #1a1a1a; color: white; }
        .header { background: #2d3748; padding: 20px; text-align: center; }
        .phase-status { font-size: 1.2em; font-weight: bold; }
        .devops-status { color: #f6e05e; font-size: 0.9em; margin-top: 5px; }
        .tabs { display: flex; background: #2d3748; }
        .tab { padding: 15px 30px; cursor: pointer; background: #4a5568; margin-right: 2px; }
        .tab.active { background: #2b6cb0; }
        .tab:hover { background: #3182ce; }
        .content { padding: 20px; min-height: 500px; }
        .metric-card { background: #2d3748; padding: 20px; margin: 10px; border-radius: 8px; display: inline-block; min-width: 200px; }
        .metric-value { font-size: 2em; font-weight: bold; color: #4fd1c7; }
        .metric-label { color: #a0aec0; }
        .agent-card { background: #2d3748; padding: 15px; margin: 10px; border-radius: 8px; border-left: 4px solid #4fd1c7; }
        .status-running { border-left-color: #48bb78; }
        .status-stopped { border-left-color: #f56565; }
        .status-developing { border-left-color: #f6e05e; }
        .progress-bar { background: #4a5568; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { background: #48bb78; height: 100%; transition: width 0.3s; }
        .devops-progress { background: #f6e05e; height: 100%; transition: width 0.3s; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AI Development Team Dashboard</h1>
        <div class="phase-status" id="phase-status">Phase 5: DevOps Agent - In Development 🔄</div>
        <div class="devops-status" id="devops-status">⏳ Waiting for Opus to create DevOps Agent...</div>
    </div>
    
    <div class="tabs">
        <div class="tab active" onclick="showTab('overview')">📊 Overview</div>
        <div class="tab" onclick="showTab('agents')">🤖 Agents</div>
        <div class="tab" onclick="showTab('system')">⚙️ System</div>
        <div class="tab" onclick="showTab('pipeline')">🔄 Pipeline</div>
        <div class="tab" onclick="showTab('devops')">🚀 DevOps</div>
    </div>
    
    <div class="content">
        <div id="overview" class="tab-content">
            <h2>Team Overview</h2>
            <div class="metric-card">
                <div class="metric-value" id="active-agents">0</div>
                <div class="metric-label">Active Agents</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="phase-progress">83%</div>
                <div class="metric-label">Pipeline Complete</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="files-generated">25+</div>
                <div class="metric-label">Files Generated</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="qa-score">93.8</div>
                <div class="metric-label">QA Score</div>
            </div>
        </div>
        
        <div id="agents" class="tab-content" style="display: none;">
            <h2>AI Agents Status</h2>
            <div id="agents-list">
                <div class="agent-card status-running">
                    <h3>✅ AI Architect Agent</h3>
                    <div>Status: <strong>Complete</strong></div>
                    <div>Phase: 2 - Architecture & Design</div>
                </div>
                <div class="agent-card status-running">
                    <h3>✅ AI Developer Agent</h3>
                    <div>Status: <strong>Complete</strong></div>
                    <div>Phase: 3 - Code Generation</div>
                    <div>Generated: 21 files, 812 lines</div>
                </div>
                <div class="agent-card status-running">
                    <h3>✅ AI QA Agent</h3>
                    <div>Status: <strong>Complete</strong></div>
                    <div>Phase: 4 - Quality Assurance</div>
                    <div>Quality Score: 93.8/100 (EXCELLENT)</div>
                    <div>Tests: 2/2 passed</div>
                </div>
                <div class="agent-card status-developing">
                    <h3>🔄 AI DevOps Agent</h3>
                    <div>Status: <strong id="devops-agent-status">In Development</strong></div>
                    <div>Phase: 5 - Deployment Automation</div>
                    <div>Progress: <span id="devops-progress-text">0%</span></div>
                </div>
            </div>
        </div>
        
        <div id="system" class="tab-content" style="display: none;">
            <h2>System Metrics</h2>
            <div class="metric-card">
                <div class="metric-value" id="cpu-usage">0%</div>
                <div class="metric-label">CPU Usage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="memory-usage">0%</div>
                <div class="metric-label">Memory Usage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="dashboard-status">🟢</div>
                <div class="metric-label">Dashboard Status</div>
            </div>
        </div>
        
        <div id="pipeline" class="tab-content" style="display: none;">
            <h2>Development Pipeline</h2>
            <div style="margin: 20px 0;">
                <h3>✅ Phase 1: GitHub Foundation</h3>
                <div class="progress-bar"><div class="progress-fill" style="width: 100%;"></div></div>
                
                <h3>✅ Phase 2: AI Architect Agent</h3>
                <div class="progress-bar"><div class="progress-fill" style="width: 100%;"></div></div>
                
                <h3>✅ Phase 3: AI Developer Agent</h3>
                <div class="progress-bar"><div class="progress-fill" style="width: 100%;"></div></div>
                
                <h3>✅ Phase 4: AI QA Agent</h3>
                <div class="progress-bar"><div class="progress-fill" style="width: 100%;"></div></div>
                <div style="color: #48bb78; margin: 10px 0;">🎉 Complete! Quality Score: 93.8/100</div>
                
                <h3>🔄 Phase 5: DevOps Agent</h3>
                <div class="progress-bar"><div class="devops-progress" id="devops-progress-bar" style="width: 0%;"></div></div>
                <div style="color: #f6e05e; margin: 10px 0;" id="devops-progress-status">⏳ Waiting for Opus to implement</div>
            </div>
        </div>
        
        <div id="devops" class="tab-content" style="display: none;">
            <h2>DevOps Agent Development</h2>
            <div style="margin: 20px 0;">
                <h3>🚀 Deployment Automation Status</h3>
                <div class="progress-bar">
                    <div class="devops-progress" id="deployment-progress" style="width: 0%;"></div>
                </div>
                <div id="deployment-status">⏳ Waiting for DevOps Agent creation</div>
                
                <h3>📊 Development Metrics</h3>
                <div class="metric-card">
                    <div class="metric-value" id="devops-lines">0</div>
                    <div class="metric-label">Lines of Code</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="deployment-features">0</div>
                    <div class="metric-label">Features Implemented</div>
                </div>
                
                <h3>🎯 Target Capabilities</h3>
                <ul style="color: #a0aec0; line-height: 1.6;">
                    <li>🐳 Docker containerization</li>
                    <li>⚙️ CI/CD pipeline automation</li>
                    <li>🏗️ Infrastructure as Code</li>
                    <li>📊 Monitoring and alerting</li>
                    <li>🚀 Automated deployment</li>
                    <li>🔄 Rollback procedures</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = 'none';
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).style.display = 'block';
            
            // Add active class to clicked tab
            document.querySelectorAll('.tab').forEach((tab, index) => {
                if (tab.textContent.includes(getTabDisplayName(tabName))) {
                    tab.classList.add('active');
                }
            });
        }
        
        function getTabDisplayName(tabName) {
            const tabNames = {
                'overview': '📊 Overview',
                'agents': '🤖 Agents', 
                'system': '⚙️ System',
                'pipeline': '🔄 Pipeline',
                'devops': '🚀 DevOps'
            };
            return tabNames[tabName] || tabName;
        }
        
        socket.on('dashboard_update', function(data) {
            // Update metrics
            if (data.system_metrics) {
                document.getElementById('cpu-usage').textContent = Math.round(data.system_metrics.cpu_percent) + '%';
                document.getElementById('memory-usage').textContent = Math.round(data.system_metrics.memory_percent) + '%';
            }
            
            // Update agent count
            const agentCount = Object.keys(data.agents || {}).length;
            document.getElementById('active-agents').textContent = agentCount;
            
            // Update DevOps progress
            if (data.team_metrics) {
                const devopsProgress = data.team_metrics.devops_progress || 0;
                document.getElementById('devops-progress-bar').style.width = devopsProgress + '%';
                document.getElementById('devops-progress-text').textContent = Math.round(devopsProgress) + '%';
                document.getElementById('devops-status').textContent = data.team_metrics.deployment_status || 'Waiting for DevOps Agent';
                document.getElementById('deployment-status').textContent = data.team_metrics.deployment_status || 'Waiting for DevOps Agent';
                
                if (devopsProgress > 0) {
                    document.getElementById('devops-agent-status').textContent = 'In Development (' + Math.round(devopsProgress) + '%)';
                    document.getElementById('devops-progress-status').textContent = '🔄 Opus is building DevOps Agent...';
                }
            }
            
            // Update timestamp
            document.getElementById('phase-status').textContent = 
                'Phase 5: DevOps Agent - Updated: ' + new Date().toLocaleTimeString();
        });
        
        socket.on('connect', function() {
            console.log('Connected to dashboard');
            socket.emit('request_update');
        });
        
        // Request updates every 5 seconds
        setInterval(() => {
            socket.emit('request_update');
        }, 5000);
    </script>
</body>
</html>'''

@socketio.on('request_update')
def handle_update_request():
    """Handle client request for dashboard update"""
    emit_dashboard_update()

def emit_dashboard_update():
    """Emit dashboard update to all connected clients"""
    data = {
        'agents': dashboard.agent_data,
        'system_metrics': dashboard.system_metrics,
        'team_metrics': dashboard.team_metrics,
        'timestamp': datetime.now().isoformat()
    }
    socketio.emit('dashboard_update', data)

def background_task():
    """Background task to emit updates every 5 seconds"""
    while True:
        socketio.sleep(5)
        emit_dashboard_update()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI DEVELOPMENT TEAM DASHBOARD - PHASE 5")
    print("=" * 60)
    print("📊 URL: http://localhost:5003")
    print("🔄 Real-time DevOps Agent monitoring")
    print("📋 Overview | 🤖 Agents | ⚙️ System | 🔄 Pipeline | 🚀 DevOps")
    print("✅ Phase 4 Complete: AI QA Agent (93.8/100)")
    print("🔄 Phase 5 Active: DevOps Agent (waiting for Opus)")
    print("=" * 60)
    
    # Start background task
    socketio.start_background_task(background_task)
    
    socketio.run(app, host='0.0.0.0', port=5003, debug=False)
