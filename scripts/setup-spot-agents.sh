#!/bin/bash
# Setup 50 AI Agents on Spot Instance with Interruption Handling

echo "=== SETTING UP 50 AI AGENTS ON SPOT INSTANCE ==="
echo "Instance: i-0c8fef744add7803c"
echo "Public IP: 35.174.174.116"
echo "Spot Price: $0.05/hour"
echo "Monthly Cost: ~$36 (95% savings vs Lambda)"
echo ""

# Update system
sudo yum update -y
sudo yum install -y python3 python3-pip git tmux htop curl jq bc

# Install Python packages
pip3 install boto3 requests pyyaml psutil

# Create agent user
sudo useradd -m -s /bin/bash agent
sudo mkdir -p /home/agent
sudo chown -R agent:agent /home/agent

# Create advanced agent script with state persistence
sudo -u agent cat > /home/agent/spot-agent.py << 'AGENT_SCRIPT'
#!/usr/bin/env python3
"""
Spot Instance AI Agent with State Persistence and Interruption Handling
Ultra Cost-Optimized: $0.05/hour for 50 agents ($36/month vs $150-300 Lambda)
"""

import sys
import time
import json
import boto3
import argparse
import signal
import os
import requests
from datetime import datetime, timezone
import threading

class SpotAgent:
    def __init__(self, agent_id, environment='dev'):
        self.agent_id = agent_id
        self.environment = environment
        self.state_file = f"/home/agent/state/agent-{agent_id}-state.json"
        self.running = True
        self.state = self.load_state()
        self.last_save = time.time()
        
        # Ensure state directory exists
        os.makedirs("/home/agent/state", exist_ok=True)
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print(f"🚀 Spot Agent {agent_id} initialized in {environment}")
    
    def load_state(self):
        """Load agent state from disk"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    print(f"📁 Loaded state: {state.get('processed_tasks', 0)} tasks processed")
                    return state
        except Exception as e:
            print(f"⚠️  Could not load state: {e}")
        
        return {
            "agent_id": self.agent_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "processed_tasks": 0,
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "total_runtime_seconds": 0,
            "interruptions_survived": 0
        }
    
    def save_state(self):
        """Save agent state to disk"""
        try:
            self.state["last_activity"] = datetime.now(timezone.utc).isoformat()
            self.state["total_runtime_seconds"] += (time.time() - self.last_save)
            self.last_save = time.time()
            
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            
            if self.state["processed_tasks"] % 100 == 0:
                print(f"💾 Agent {self.agent_id} state saved - {self.state['processed_tasks']} tasks")
        except Exception as e:
            print(f"❌ Could not save state: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle termination signals gracefully"""
        print(f"🛑 Agent {self.agent_id} received signal {signum}, shutting down gracefully...")
        self.running = False
        self.save_state()
    
    def check_spot_interruption(self):
        """Check for spot instance interruption notice"""
        try:
            response = requests.get(
                'http://169.254.169.254/latest/meta-data/spot/instance-action',
                timeout=2
            )
            if response.status_code == 200:
                print(f"🚨 Spot interruption detected! Agent {self.agent_id} preparing for shutdown...")
                self.state["interruptions_survived"] += 1
                self.save_state()
                return True
        except requests.exceptions.RequestException:
            pass  # No interruption notice
        return False
    
    def process_work(self):
        """Simulate agent work processing"""
        try:
            # Check for spot interruption every 10 tasks
            if self.state["processed_tasks"] % 10 == 0:
                if self.check_spot_interruption():
                    self.running = False
                    return False
            
            # Simulate processing GitHub issues or business tasks
            task_types = ["GitHub Issue", "Customer Support", "Code Review", "Deployment", "Monitoring"]
            task_type = task_types[self.state["processed_tasks"] % len(task_types)]
            
            print(f"🔄 Agent {self.agent_id} processing {task_type} (task #{self.state['processed_tasks'] + 1})")
            
            # Simulate work
            time.sleep(1)
            
            # Update state
            self.state["processed_tasks"] += 1
            
            # Save state every 10 tasks or every 5 minutes
            if (self.state["processed_tasks"] % 10 == 0 or 
                time.time() - self.last_save > 300):
                self.save_state()
            
            return True
            
        except Exception as e:
            print(f"❌ Agent {self.agent_id} error: {e}")
            return False
    
    def get_status(self):
        """Get agent status info"""
        runtime_hours = self.state.get("total_runtime_seconds", 0) / 3600
        return {
            "agent_id": self.agent_id,
            "status": "running" if self.running else "stopped",
            "processed_tasks": self.state["processed_tasks"],
            "runtime_hours": round(runtime_hours, 2),
            "interruptions_survived": self.state.get("interruptions_survived", 0),
            "last_activity": self.state["last_activity"]
        }
    
    def run(self):
        """Main agent loop"""
        print(f"🎯 Starting Spot Agent {self.agent_id} in {self.environment}")
        print(f"📊 Previous state: {self.state['processed_tasks']} tasks processed, "
              f"{self.state.get('interruptions_survived', 0)} interruptions survived")
        
        while self.running:
            try:
                if not self.process_work():
                    break
                
                # Variable sleep time to distribute load
                sleep_time = 25 + (self.agent_id % 10)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                print(f"⏹️  Agent {self.agent_id} interrupted by user")
                break
            except Exception as e:
                print(f"💥 Agent {self.agent_id} unexpected error: {e}")
                time.sleep(5)
        
        print(f"✅ Agent {self.agent_id} shutdown complete")
        self.save_state()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Spot Instance AI Agent')
    parser.add_argument('--agent-id', type=int, required=True, help='Agent ID (1-50)')
    parser.add_argument('--environment', default='dev', help='Environment (dev/stg/prd)')
    parser.add_argument('--status', action='store_true', help='Show agent status')
    
    args = parser.parse_args()
    
    agent = SpotAgent(args.agent_id, args.environment)
    
    if args.status:
        print(json.dumps(agent.get_status(), indent=2))
    else:
        agent.run()
AGENT_SCRIPT

chmod +x /home/agent/spot-agent.py

# Create global spot interruption handler
sudo -u agent cat > /home/agent/spot-interruption-handler.sh << 'INTERRUPTION_SCRIPT'
#!/bin/bash
# Global Spot Instance Interruption Handler
# Monitors for interruption notice and gracefully shuts down all agents

LOG_FILE="/home/agent/interruption.log"

log_message() {
    echo "[$(date)] $1" | tee -a "$LOG_FILE"
}

log_message "🔍 Starting spot interruption monitoring..."

while true; do
    # Check EC2 metadata for spot instance interruption notice
    if response=$(curl -s -f -m 2 http://169.254.169.254/latest/meta-data/spot/instance-action 2>/dev/null); then
        log_message "🚨 SPOT INTERRUPTION NOTICE RECEIVED!"
        log_message "Response: $response"
        
        # Parse interruption time if available
        interruption_time=$(echo "$response" | jq -r '.time' 2>/dev/null || echo "unknown")
        log_message "Interruption time: $interruption_time"
        
        # Gracefully shut down all agent sessions
        log_message "🛑 Gracefully shutting down all 50 agents..."
        
        # Send SIGTERM to all agent processes first
        session_count=0
        tmux list-sessions 2>/dev/null | grep "agent-" | while read session; do
            session_name=$(echo "$session" | cut -d: -f1)
            log_message "Sending graceful shutdown signal to $session_name"
            tmux send-keys -t "$session_name" C-c 2>/dev/null
            ((session_count++))
        done
        
        log_message "Sent shutdown signals to $session_count agent sessions"
        
        # Wait for agents to save state and shut down gracefully
        log_message "⏳ Waiting 30 seconds for agents to save state..."
        sleep 30
        
        # Force terminate any remaining sessions
        log_message "🔚 Force terminating remaining sessions..."
        tmux kill-server 2>/dev/null || true
        
        # Store interruption information
        echo "{
          \"interrupted_at\": \"$(date -Iseconds)\",
          \"reason\": \"spot_interruption\",
          \"agents_running\": $session_count,
          \"response\": \"$response\"
        }" > /home/agent/interruption-info.json
        
        log_message "✅ Spot interruption handling complete"
        log_message "📊 Interruption info saved to interruption-info.json"
        break
    fi
    
    # Check every 5 seconds
    sleep 5
done
INTERRUPTION_SCRIPT

chmod +x /home/agent/spot-interruption-handler.sh

# Create agent startup script
sudo -u agent cat > /home/agent/start-all-agents.sh << 'STARTUP_SCRIPT'
#!/bin/bash
# Start 50 AI Agents in Ultra Cost-Optimized Spot Instance Mode

AGENT_COUNT=50
echo "🚀 Starting $AGENT_COUNT AI agents in spot instance mode..."
echo "💰 Cost: $0.05/hour (~$36/month vs $150-300 Lambda)"
echo ""

# Check for previous interruption and restore info
if [ -f "/home/agent/interruption-info.json" ]; then
    echo "📋 Previous spot interruption detected:"
    cat /home/agent/interruption-info.json | jq '.'
    echo ""
    echo "🔄 Restoring agents from saved states..."
    mv /home/agent/interruption-info.json /home/agent/last-interruption.json
fi

# Ensure state directory exists
mkdir -p /home/agent/state

# Start agents in tmux sessions
started_count=0
for i in $(seq 1 $AGENT_COUNT); do
    session_name="agent-$i"
    
    # Check if session already exists
    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo "⚠️  Agent $i session already exists, skipping"
        continue
    fi
    
    # Start new agent session
    tmux new-session -d -s "$session_name" "python3 /home/agent/spot-agent.py --agent-id $i --environment dev"
    
    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo "✅ Started agent $i in session $session_name"
        ((started_count++))
    else
        echo "❌ Failed to start agent $i"
    fi
    
    # Small delay to prevent overwhelming the system
    sleep 0.1
done

echo ""
echo "🎉 Agent startup complete!"
echo "📊 Started: $started_count/$AGENT_COUNT agents"
echo ""

# Display session status
echo "📋 Active agent sessions:"
tmux list-sessions 2>/dev/null | grep "agent-" | wc -l | xargs echo "Running agents:"
echo ""
echo "🔧 Management commands:"
echo "  tmux list-sessions                    # List all agents"
echo "  tmux attach -t agent-5               # Connect to agent 5"
echo "  python3 spot-agent.py --agent-id 5 --status  # Check agent 5 status"
echo "  /home/agent/check-all-status.sh      # Check all agents"
STARTUP_SCRIPT

chmod +x /home/agent/start-all-agents.sh

# Create status check script
sudo -u agent cat > /home/agent/check-all-status.sh << 'STATUS_SCRIPT'
#!/bin/bash
# Check status of all spot instance agents

echo "=============================================="
echo "🎯 SPOT INSTANCE AI AGENT SYSTEM STATUS"
echo "=============================================="

# Instance info
echo "🖥️  Instance Information:"
echo "  Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)"
echo "  Instance Type: $(curl -s http://169.254.169.254/latest/meta-data/instance-type)"
echo "  Public IP: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "  Availability Zone: $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)"
echo ""

# Cost info
echo "💰 Cost Information:"
echo "  Spot Price: $0.05/hour"
echo "  Daily Cost: ~$1.20"
echo "  Monthly Cost: ~$36"
echo "  Savings vs Lambda: 95% ($150-300 → $36)"
echo ""

# Agent sessions
echo "🤖 Agent Sessions:"
session_count=$(tmux list-sessions 2>/dev/null | grep -c "agent-" || echo "0")
echo "  Active agents: $session_count/50"

if [ $session_count -gt 0 ]; then
    echo "  Sessions:"
    tmux list-sessions 2>/dev/null | grep "agent-" | head -5
    if [ $session_count -gt 5 ]; then
        echo "  ... and $((session_count - 5)) more"
    fi
else
    echo "  ⚠️  No agent sessions running"
fi
echo ""

# System resources
echo "📊 System Resources:"
echo "  CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')%"
echo "  Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "  Disk: $(df -h / | awk 'NR==2 {print $5 " used"}')"
echo "  Load Average: $(cat /proc/loadavg | awk '{print $1, $2, $3}')"
echo ""

# Agent state summary
echo "📈 Agent Performance:"
if [ -d "/home/agent/state" ]; then
    total_tasks=0
    total_interruptions=0
    active_agents=0
    
    for state_file in /home/agent/state/agent-*-state.json; do
        if [ -f "$state_file" ]; then
            tasks=$(jq -r '.processed_tasks // 0' "$state_file" 2>/dev/null || echo "0")
            interruptions=$(jq -r '.interruptions_survived // 0' "$state_file" 2>/dev/null || echo "0")
            total_tasks=$((total_tasks + tasks))
            total_interruptions=$((total_interruptions + interruptions))
            active_agents=$((active_agents + 1))
        fi
    done
    
    echo "  Total tasks processed: $total_tasks"
    echo "  Interruptions survived: $total_interruptions"
    echo "  Agents with saved state: $active_agents"
else
    echo "  State directory not found"
fi

# Interruption info
if [ -f "/home/agent/last-interruption.json" ]; then
    echo ""
    echo "📋 Last Interruption:"
    cat /home/agent/last-interruption.json | jq -r '"  Date: " + .interrupted_at + " | Agents: " + (.agents_running | tostring)'
fi

echo ""
echo "🔧 Quick Commands:"
echo "  /home/agent/start-all-agents.sh       # Restart all agents"
echo "  tmux attach -t agent-1               # Connect to agent 1"
echo "  tail -f /home/agent/interruption.log # Monitor interruptions"
echo ""
echo "✅ Status check complete"
STATUS_SCRIPT

chmod +x /home/agent/check-all-status.sh

# Create restart script
sudo -u agent cat > /home/agent/restart-agents.sh << 'RESTART_SCRIPT'
#!/bin/bash
# Restart all agents (useful after interruption recovery)

echo "🔄 Restarting all agents..."

# Kill existing sessions
tmux kill-server 2>/dev/null || true

# Wait a moment
sleep 2

# Start all agents
/home/agent/start-all-agents.sh
RESTART_SCRIPT

chmod +x /home/agent/restart-agents.sh

echo ""
echo "✅ All scripts created successfully!"
echo ""
echo "🚀 READY TO START 50 AGENTS!"
echo "Run: sudo -u agent /home/agent/start-all-agents.sh"
