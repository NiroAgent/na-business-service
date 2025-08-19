#!/usr/bin/env python3
"""
Massive Agent Deployment - Launch maximum number of agents for comprehensive testing
"""

import subprocess
import time
import json
import os
import threading
from datetime import datetime
import psutil

class MassiveAgentDeployment:
    def __init__(self):
        self.python_exe = "E:/Projects/.venv/Scripts/python.exe"
        self.base_dir = "E:/Projects"
        self.running_agents = {}
        self.log_file = f"{self.base_dir}/massive_deployment_log.json"
        
        # Define all available agents
        self.agent_configs = {
            # Monitoring Agents
            "cost-monitor": {"script": "aws-cost-monitor.py", "args": [], "type": "monitoring"},
            "env-cost-monitor": {"script": "environment-aware-cost-monitor.py", "args": [], "type": "monitoring"},
            "monitorable-1": {"script": "monitorable-agent.py", "args": ["single"], "type": "testing"},
            "monitorable-2": {"script": "monitorable-agent.py", "args": ["cycle"], "type": "testing"},
            "monitorable-3": {"script": "monitorable-agent.py", "args": [], "type": "testing"},
            
            # Service Testing Agents
            "gh-copilot-1": {"script": "gh-copilot-agent-integration.py", "args": [], "type": "ai-testing"},
            "local-agent-1": {"script": "local-agent-system.py", "args": [], "type": "local-testing"},
            "local-agent-2": {"script": "local-agent-system.py", "args": ["--parallel"], "type": "local-testing"},
            "issue-agent": {"script": "issue-driven-local-agent.py", "args": [], "type": "issue-testing"},
            "sdlc-agent": {"script": "sdlc-iterator-agent.py", "args": [], "type": "sdlc-testing"},
            
            # Orchestrator Agents
            "orchestrator-1": {"script": "orchestrator-agent.py", "args": [], "type": "orchestration"},
            "ai-integration": {"script": "agent-orchestrator-ai-integration.py", "args": [], "type": "ai-orchestration"},
            
            # Service-Specific Agents (one per service)
            "vf-auth-agent": {"script": "monitorable-agent.py", "args": ["vf-auth"], "type": "service"},
            "vf-video-agent": {"script": "monitorable-agent.py", "args": ["vf-video"], "type": "service"},
            "vf-image-agent": {"script": "monitorable-agent.py", "args": ["vf-image"], "type": "service"},
            "vf-audio-agent": {"script": "monitorable-agent.py", "args": ["vf-audio"], "type": "service"},
            "vf-text-agent": {"script": "monitorable-agent.py", "args": ["vf-text"], "type": "service"},
            "vf-dashboard-agent": {"script": "monitorable-agent.py", "args": ["vf-dashboard"], "type": "service"},
            "vf-bulk-agent": {"script": "monitorable-agent.py", "args": ["vf-bulk"], "type": "service"},
            
            "ns-auth-agent": {"script": "monitorable-agent.py", "args": ["ns-auth"], "type": "service"},
            "ns-dashboard-agent": {"script": "monitorable-agent.py", "args": ["ns-dashboard"], "type": "service"},
            "ns-payments-agent": {"script": "monitorable-agent.py", "args": ["ns-payments"], "type": "service"},
            "ns-user-agent": {"script": "monitorable-agent.py", "args": ["ns-user"], "type": "service"},
        }
    
    def start_agent(self, agent_name, config):
        """Start a single agent"""
        try:
            script_path = os.path.join(self.base_dir, config["script"])
            if not os.path.exists(script_path):
                print(f"⚠️ Script not found: {script_path}")
                return None
            
            cmd = [self.python_exe, script_path] + config["args"]
            
            print(f"🚀 Starting {agent_name} ({config['type']})...")
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.running_agents[agent_name] = {
                "process": process,
                "config": config,
                "started": datetime.now().isoformat(),
                "pid": process.pid,
                "restarts": 0
            }
            
            print(f"✅ {agent_name} started (PID: {process.pid})")
            return process
            
        except Exception as e:
            print(f"❌ Failed to start {agent_name}: {e}")
            return None
    
    def monitor_agents(self):
        """Monitor all agents and restart if needed"""
        while True:
            try:
                for agent_name, agent_info in list(self.running_agents.items()):
                    process = agent_info["process"]
                    
                    if process.poll() is not None:
                        print(f"⚠️ {agent_name} stopped (exit code: {process.returncode})")
                        
                        # Restart the agent
                        if agent_info["restarts"] < 5:  # Max 5 restarts
                            print(f"🔄 Restarting {agent_name}...")
                            new_process = self.start_agent(agent_name, agent_info["config"])
                            if new_process:
                                self.running_agents[agent_name]["restarts"] += 1
                        else:
                            print(f"💀 {agent_name} exceeded restart limit, removing...")
                            del self.running_agents[agent_name]
                
                # Log status
                self.log_status()
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                print("\n🛑 Shutting down all agents...")
                self.stop_all_agents()
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)
    
    def log_status(self):
        """Log current status to file"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.running_agents),
            "agents": {}
        }
        
        for agent_name, agent_info in self.running_agents.items():
            status["agents"][agent_name] = {
                "type": agent_info["config"]["type"],
                "pid": agent_info["pid"],
                "started": agent_info["started"],
                "restarts": agent_info["restarts"],
                "running": agent_info["process"].poll() is None
            }
        
        try:
            with open(self.log_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            print(f"Log error: {e}")
    
    def stop_all_agents(self):
        """Stop all running agents"""
        for agent_name, agent_info in self.running_agents.items():
            try:
                process = agent_info["process"]
                if process.poll() is None:
                    print(f"🛑 Stopping {agent_name}...")
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
            except Exception as e:
                print(f"Error stopping {agent_name}: {e}")
        
        self.running_agents.clear()
    
    def get_status(self):
        """Get current deployment status"""
        status = {
            "total_agents": len(self.running_agents),
            "by_type": {},
            "running": 0,
            "stopped": 0
        }
        
        for agent_name, agent_info in self.running_agents.items():
            agent_type = agent_info["config"]["type"]
            if agent_type not in status["by_type"]:
                status["by_type"][agent_type] = 0
            status["by_type"][agent_type] += 1
            
            if agent_info["process"].poll() is None:
                status["running"] += 1
            else:
                status["stopped"] += 1
        
        return status
    
    def deploy_massive_scale(self):
        """Deploy maximum number of agents"""
        print("=" * 80)
        print("🚀 MASSIVE AGENT DEPLOYMENT STARTING")
        print("=" * 80)
        
        # Start all agents with delays
        started = 0
        for agent_name, config in self.agent_configs.items():
            if self.start_agent(agent_name, config):
                started += 1
            time.sleep(2)  # 2 second delay between starts
        
        print(f"\n🎉 Successfully started {started}/{len(self.agent_configs)} agents!")
        
        # Show status
        status = self.get_status()
        print(f"\n📊 DEPLOYMENT STATUS:")
        print(f"   Total Agents: {status['total_agents']}")
        print(f"   Running: {status['running']}")
        print(f"   By Type:")
        for agent_type, count in status["by_type"].items():
            print(f"     {agent_type}: {count}")
        
        print(f"\n🔄 Starting monitoring thread...")
        monitor_thread = threading.Thread(target=self.monitor_agents, daemon=True)
        monitor_thread.start()
        
        print(f"\n💡 Press Ctrl+C to stop all agents")
        print(f"📋 Status log: {self.log_file}")
        
        try:
            monitor_thread.join()
        except KeyboardInterrupt:
            print("\n👋 Deployment stopped by user")

def main():
    deployment = MassiveAgentDeployment()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        if os.path.exists(deployment.log_file):
            with open(deployment.log_file, 'r') as f:
                status = json.load(f)
            print(json.dumps(status, indent=2))
        else:
            print("No deployment log found")
        return
    
    deployment.deploy_massive_scale()

if __name__ == "__main__":
    main()
