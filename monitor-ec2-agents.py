#!/usr/bin/env python3
"""
EC2 Agent Monitor
Continuously monitors AI agents running on EC2
"""

import subprocess
import json
import time
from datetime import datetime
import sys

class EC2AgentMonitor:
    def __init__(self):
        self.instance_id = "i-0af59b7036f7b0b77"
        self.agents = {
            "ai-qa-agent": {"status": "unknown", "pid": None},
            "ai-developer-agent": {"status": "unknown", "pid": None},
            "ai-operations-agent": {"status": "unknown", "pid": None}
        }
        
    def check_agents(self):
        """Check agent status on EC2"""
        try:
            # Send command to check processes
            cmd = [
                "aws", "ssm", "send-command",
                "--instance-ids", self.instance_id,
                "--document-name", "AWS-RunShellScript",
                "--parameters", 'commands=["ps aux | grep python3.*agent | grep -v grep"]',
                "--query", "Command.CommandId",
                "--output", "text"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            command_id = result.stdout.strip()
            
            # Wait for command to complete
            time.sleep(3)
            
            # Get command output
            get_cmd = [
                "aws", "ssm", "get-command-invocation",
                "--command-id", command_id,
                "--instance-id", self.instance_id,
                "--query", "StandardOutputContent",
                "--output", "text"
            ]
            
            result = subprocess.run(get_cmd, capture_output=True, text=True)
            output = result.stdout
            
            # Parse process list
            for agent_name in self.agents:
                if agent_name in output:
                    self.agents[agent_name]["status"] = "running"
                    # Extract PID
                    for line in output.split('\n'):
                        if agent_name in line:
                            parts = line.split()
                            if len(parts) > 1:
                                self.agents[agent_name]["pid"] = parts[1]
                else:
                    self.agents[agent_name]["status"] = "stopped"
                    self.agents[agent_name]["pid"] = None
                    
        except Exception as e:
            print(f"Error checking agents: {e}")
            
    def check_logs(self):
        """Check agent logs for recent activity"""
        try:
            cmd = [
                "aws", "ssm", "send-command",
                "--instance-ids", self.instance_id,
                "--document-name", "AWS-RunShellScript",
                "--parameters", 'commands=["tail -5 /opt/ai-agents/logs/qa.log 2>/dev/null","tail -5 /opt/ai-agents/logs/dev.log 2>/dev/null","tail -5 /opt/ai-agents/logs/ops.log 2>/dev/null"]',
                "--query", "Command.CommandId",
                "--output", "text"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            command_id = result.stdout.strip()
            
            time.sleep(3)
            
            get_cmd = [
                "aws", "ssm", "get-command-invocation",
                "--command-id", command_id,
                "--instance-id", self.instance_id,
                "--query", "StandardOutputContent",
                "--output", "text"
            ]
            
            result = subprocess.run(get_cmd, capture_output=True, text=True)
            return result.stdout
            
        except Exception as e:
            print(f"Error checking logs: {e}")
            return ""
            
    def display_status(self):
        """Display agent status"""
        print("\n" + "="*60)
        print(f"EC2 AGENT STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print(f"Instance: {self.instance_id}")
        print(f"Status: {'OPERATIONAL' if any(a['status'] == 'running' for a in self.agents.values()) else 'OFFLINE'}")
        print()
        
        print("AGENT STATUS:")
        print("-"*40)
        for agent_name, info in self.agents.items():
            status_icon = "[OK]" if info["status"] == "running" else "[FAIL]"
            pid_info = f"PID: {info['pid']}" if info['pid'] else "Not running"
            print(f"{status_icon} {agent_name:25} {info['status']:10} {pid_info}")
        
        # Get logs
        logs = self.check_logs()
        if logs:
            print("\nRECENT ACTIVITY:")
            print("-"*40)
            for line in logs.split('\n')[:10]:
                if line.strip():
                    print(f"  {line[:70]}")
        
        # Check for issues
        stopped_agents = [name for name, info in self.agents.items() if info["status"] == "stopped"]
        if stopped_agents:
            print("\nALERTS:")
            print("-"*40)
            for agent in stopped_agents:
                print(f"  - {agent} is not running!")
            print("\nTo restart agents, run: ./start-real-agents-ec2.sh")
        else:
            print("\n[OK] All agents are running!")
            
    def monitor_continuously(self, interval=60):
        """Monitor agents continuously"""
        print("Starting continuous monitoring (Ctrl+C to stop)")
        print(f"Checking every {interval} seconds...")
        
        while True:
            try:
                self.check_agents()
                self.display_status()
                
                # Save status to file
                status_data = {
                    "timestamp": datetime.now().isoformat(),
                    "instance_id": self.instance_id,
                    "agents": self.agents
                }
                
                with open("ec2_agent_status.json", "w") as f:
                    json.dump(status_data, f, indent=2)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped.")
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    monitor = EC2AgentMonitor()
    
    # Check once or continuously
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        monitor.check_agents()
        monitor.display_status()
    else:
        monitor.monitor_continuously(interval=60)