#!/usr/bin/env python3
"""
Agent Controller - Manages running agents with optimized reporting
Reduces noise while maintaining monitoring capability
"""

import subprocess
import time
import json
import os
from datetime import datetime
import signal
import sys

class AgentController:
    def __init__(self):
        self.agents = {}
        self.report_interval = 300  # 5 minutes instead of 10 seconds
        self.logs_dir = "logs/agent-reports"
        os.makedirs(self.logs_dir, exist_ok=True)
        
    def register_agent(self, name, process):
        """Register a running agent process"""
        self.agents[name] = {
            'process': process,
            'started': datetime.now(),
            'last_report': None,
            'status': 'running'
        }
        
    def start_agents(self):
        """Start essential monitoring agents with reduced reporting"""
        
        # Start intelligent issue detector (hourly reports)
        print("🔍 Starting Intelligent Issue Detector...")
        issue_detector = subprocess.Popen([
            sys.executable, 'intelligent-issue-detector.py',
            '--report-interval', '3600'  # 1 hour
        ], cwd='/e/Projects')
        self.register_agent('issue-detector', issue_detector)
        
        # Start self-healing agent (30 min reports)  
        print("🔧 Starting Self-Healing Agent...")
        self_healing = subprocess.Popen([
            sys.executable, 'agent-self-healing.py',
            '--report-interval', '1800'  # 30 minutes
        ], cwd='/e/Projects')
        self.register_agent('self-healing', self_healing)
        
        # Start communication hub (always running, minimal logs)
        print("📡 Starting Communication Hub...")
        comm_hub = subprocess.Popen([
            sys.executable, 'agent-communication-hub.py',
            '--quiet-mode'
        ], cwd='/e/Projects')
        self.register_agent('communication-hub', comm_hub)
        
        print(f"✅ Started {len(self.agents)} agents with optimized reporting")
        
    def stop_all_agents(self):
        """Gracefully stop all agents"""
        print("🛑 Stopping all agents...")
        for name, agent_info in self.agents.items():
            try:
                process = agent_info['process']
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {name}")
            except:
                try:
                    process.kill()
                    print(f"⚠️  Force killed {name}")
                except:
                    print(f"❌ Could not stop {name}")
                    
    def status_report(self):
        """Generate consolidated status report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'agents': {},
            'summary': {}
        }
        
        active_count = 0
        for name, agent_info in self.agents.items():
            process = agent_info['process']
            is_running = process.poll() is None
            
            report['agents'][name] = {
                'status': 'running' if is_running else 'stopped',
                'started': agent_info['started'].isoformat(),
                'pid': process.pid if is_running else None
            }
            
            if is_running:
                active_count += 1
                
        report['summary'] = {
            'total_agents': len(self.agents),
            'active_agents': active_count,
            'report_interval_minutes': self.report_interval // 60
        }
        
        # Save consolidated report
        report_file = f"{self.logs_dir}/agent_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
        
    def monitor(self):
        """Main monitoring loop with reduced frequency"""
        print(f"📊 Monitoring agents (reports every {self.report_interval//60} minutes)...")
        
        try:
            while True:
                # Check agent health
                report = self.status_report()
                
                # Console summary (minimal)
                active = report['summary']['active_agents']
                total = report['summary']['total_agents']
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Agents: {active}/{total} active")
                
                # Sleep for report interval
                time.sleep(self.report_interval)
                
        except KeyboardInterrupt:
            print("\n🔄 Shutting down agent controller...")
            self.stop_all_agents()
            
def main():
    print("🚀 Agent Controller Starting...")
    
    # Stop any existing noisy agents first
    print("🧹 Cleaning up existing agent processes...")
    try:
        subprocess.run(['pkill', '-f', 'python.*agent'], check=False)
        time.sleep(2)
    except:
        pass
        
    controller = AgentController()
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        controller.stop_all_agents()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start optimized agents
    controller.start_agents()
    
    # Begin monitoring
    controller.monitor()

if __name__ == "__main__":
    main()
