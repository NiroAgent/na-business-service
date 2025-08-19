#!/usr/bin/env python3
"""
Simple Dashboard - Phase 5 DevOps Agent Monitoring
"""
import os
import time
import json
from datetime import datetime
from flask import Flask, jsonify, render_template_string
import threading

app = Flask(__name__)

class DevOpsMonitor:
    def __init__(self):
        self.data = {
            "phase": "Phase 5: DevOps Agent",
            "status": "Monitoring",
            "devops_agent_lines": 0,
            "devops_exists": False,
            "last_update": datetime.now().isoformat()
        }
        self.update_data()
    
    def update_data(self):
        """Update monitoring data"""
        try:
            # Check for ai-devops-agent.py
            devops_file = "ai-devops-agent.py"
            if os.path.exists(devops_file):
                with open(devops_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    self.data['devops_agent_lines'] = lines
                    self.data['devops_exists'] = True
                    self.data['status'] = f"DevOps Agent Active: {lines} lines"
            else:
                self.data['devops_exists'] = False
                self.data['status'] = "Waiting for DevOps Agent..."
                
            self.data['last_update'] = datetime.now().isoformat()
        except Exception as e:
            print(f"Error updating data: {e}")

monitor = DevOpsMonitor()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Phase 5 DevOps Monitor</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .header { background: #2d5aa0; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .status { background: #333; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .green { color: #4CAF50; }
        .yellow { color: #FFC107; }
        .red { color: #F44336; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Phase 5: DevOps Agent Monitor</h1>
        <p>Real-time monitoring of Opus's DevOps Agent development</p>
    </div>
    
    <div class="status">
        <h3>Current Status</h3>
        <p class="{{ 'green' if data.devops_exists else 'yellow' }}">{{ data.status }}</p>
        <p>Last Update: {{ data.last_update }}</p>
    </div>
    
    {% if data.devops_exists %}
    <div class="status">
        <h3>✅ DevOps Agent Details</h3>
        <p>Lines of Code: {{ data.devops_agent_lines }}</p>
        <p class="green">Agent Status: Active and Developing</p>
    </div>
    {% else %}
    <div class="status">
        <h3>⏳ Waiting for DevOps Agent</h3>
        <p class="yellow">Opus is working on creating the DevOps Agent...</p>
    </div>
    {% endif %}
    
    <div class="status">
        <h3>Parallel Tasks Status</h3>
        <p>✅ Dashboard Monitoring: Active</p>
        <p>✅ Integration Testing: Framework Ready</p>
        <p>✅ Phase 5 Instructions: Delivered to Opus</p>
        <p>🔄 Real-time Monitoring: Online</p>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    monitor.update_data()
    return render_template_string(HTML_TEMPLATE, data=monitor.data)

@app.route('/api/status')
def api_status():
    monitor.update_data()
    return jsonify(monitor.data)

def background_monitor():
    """Background monitoring thread"""
    while True:
        monitor.update_data()
        time.sleep(5)

if __name__ == '__main__':
    # Start background monitoring
    thread = threading.Thread(target=background_monitor, daemon=True)
    thread.start()
    
    print("🚀 Phase 5 DevOps Monitor starting on http://localhost:5004")
    print("📊 Monitoring Opus's DevOps Agent development...")
    
    app.run(host='0.0.0.0', port=5004, debug=False)
