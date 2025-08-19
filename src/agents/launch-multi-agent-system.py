#!/usr/bin/env python3
"""
Multi-Agent System Launcher
Coordinates all AI agents for autonomous business operations
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from pathlib import Path
import subprocess
import sys
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_agent_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MultiAgentLauncher')

class MultiAgentSystemLauncher:
    """Launches and manages all AI agents in the system"""
    
    def __init__(self):
        self.orchestrator_process = None
        self.agent_processes = {}
        self.running = False
        
        # Define all agents to launch
        self.available_agents = {
            # Core Development Team (Already Built)
            "ai-architect-agent": {"file": "ai-architect-agent.py", "priority": 1, "status": "built"},
            "ai-developer-agent": {"file": "ai-developer-agent.py", "priority": 1, "status": "built"},
            "ai-qa-agent": {"file": "ai-qa-agent.py", "priority": 1, "status": "built"},
            "ai-devops-agent": {"file": "ai-devops-agent.py", "priority": 1, "status": "built"},
            
            # Management Team (TO BE BUILT BY OPUS)
            "ai-manager-agent": {"file": "ai-manager-agent.py", "priority": 2, "status": "template"},
            "ai-project-manager-agent": {"file": "ai-project-manager-agent.py", "priority": 2, "status": "pending"},
            
            # Business Team (TO BE BUILT BY OPUS)
            "ai-marketing-agent": {"file": "ai-marketing-agent.py", "priority": 3, "status": "pending"},
            "ai-sales-agent": {"file": "ai-sales-agent.py", "priority": 3, "status": "pending"},
            "ai-support-agent": {"file": "ai-support-agent.py", "priority": 3, "status": "pending"},
            "ai-customer-success-agent": {"file": "ai-customer-success-agent.py", "priority": 3, "status": "pending"},
            
            # Intelligence Team (TO BE BUILT BY OPUS)
            "ai-analytics-agent": {"file": "ai-analytics-agent.py", "priority": 4, "status": "pending"},
            "ai-finance-agent": {"file": "ai-finance-agent.py", "priority": 4, "status": "pending"},
            
            # Operations Team (TO BE BUILT BY OPUS)
            "ai-operations-agent": {"file": "ai-operations-agent.py", "priority": 5, "status": "pending"},
            "ai-security-agent": {"file": "ai-security-agent.py", "priority": 5, "status": "pending"}
        }
        
        logger.info("🚀 Multi-Agent System Launcher initialized")
    
    def check_agent_files(self):
        """Check which agent files exist and are ready to launch"""
        ready_agents = []
        missing_agents = []
        
        for agent_name, config in self.available_agents.items():
            file_path = Path(config["file"])
            if file_path.exists():
                ready_agents.append(agent_name)
                config["status"] = "ready"
            else:
                missing_agents.append(agent_name)
                if config["status"] == "built":
                    config["status"] = "missing"
        
        logger.info(f"✅ Ready agents: {len(ready_agents)}")
        logger.info(f"⏳ Missing agents: {len(missing_agents)}")
        
        return ready_agents, missing_agents
    
    def start_orchestrator(self):
        """Start the orchestration system"""
        try:
            logger.info("🎯 Starting Agent Orchestrator...")
            self.orchestrator_process = subprocess.Popen([
                sys.executable, "agent-orchestration-system.py"
            ])
            time.sleep(2)  # Give orchestrator time to start
            logger.info("✅ Orchestrator started")
            return True
        except Exception as e:
            logger.error(f"Failed to start orchestrator: {e}")
            return False
    
    def start_agent(self, agent_name: str, config: Dict[str, Any]):
        """Start a single agent"""
        try:
            logger.info(f"🤖 Starting {agent_name}...")
            process = subprocess.Popen([
                sys.executable, config["file"]
            ])
            self.agent_processes[agent_name] = process
            logger.info(f"✅ {agent_name} started (PID: {process.pid})")
            return True
        except Exception as e:
            logger.error(f"Failed to start {agent_name}: {e}")
            return False
    
    def start_ready_agents(self):
        """Start all agents that are ready"""
        ready_agents, missing_agents = self.check_agent_files()
        
        if missing_agents:
            logger.warning(f"⚠️ Missing agents: {missing_agents}")
            logger.info("These agents need to be built by Opus")
        
        # Start agents by priority
        for priority in range(1, 6):
            priority_agents = [
                (name, config) for name, config in self.available_agents.items()
                if config["priority"] == priority and config["status"] == "ready"
            ]
            
            if priority_agents:
                logger.info(f"🚀 Starting Priority {priority} agents...")
                for agent_name, config in priority_agents:
                    success = self.start_agent(agent_name, config)
                    if success:
                        time.sleep(1)  # Stagger starts
                    else:
                        logger.error(f"❌ Failed to start {agent_name}")
    
    def monitor_agents(self):
        """Monitor running agents"""
        while self.running:
            # Check orchestrator
            if self.orchestrator_process and self.orchestrator_process.poll() is not None:
                logger.error("🚨 Orchestrator stopped unexpectedly!")
                self.restart_orchestrator()
            
            # Check agents
            for agent_name, process in list(self.agent_processes.items()):
                if process.poll() is not None:
                    logger.warning(f"⚠️ Agent {agent_name} stopped")
                    # Attempt restart
                    config = self.available_agents[agent_name]
                    if self.start_agent(agent_name, config):
                        logger.info(f"🔄 Restarted {agent_name}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def restart_orchestrator(self):
        """Restart the orchestrator"""
        logger.info("🔄 Restarting orchestrator...")
        if self.orchestrator_process:
            self.orchestrator_process.terminate()
        self.start_orchestrator()
    
    def stop_all(self):
        """Stop all agents and orchestrator"""
        logger.info("🛑 Stopping all agents...")
        self.running = False
        
        # Stop agents
        for agent_name, process in self.agent_processes.items():
            try:
                process.terminate()
                logger.info(f"🛑 Stopped {agent_name}")
            except Exception as e:
                logger.error(f"Error stopping {agent_name}: {e}")
        
        # Stop orchestrator
        if self.orchestrator_process:
            try:
                self.orchestrator_process.terminate()
                logger.info("🛑 Stopped orchestrator")
            except Exception as e:
                logger.error(f"Error stopping orchestrator: {e}")
    
    def get_system_status(self):
        """Get status of the entire system"""
        ready_agents, missing_agents = self.check_agent_files()
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "orchestrator_running": self.orchestrator_process and self.orchestrator_process.poll() is None,
            "total_agents": len(self.available_agents),
            "ready_agents": len(ready_agents),
            "running_agents": len([p for p in self.agent_processes.values() if p.poll() is None]),
            "missing_agents": len(missing_agents),
            "agent_details": {}
        }
        
        for agent_name, config in self.available_agents.items():
            process = self.agent_processes.get(agent_name)
            status["agent_details"][agent_name] = {
                "status": config["status"],
                "priority": config["priority"],
                "running": process and process.poll() is None if process else False,
                "pid": process.pid if process and process.poll() is None else None
            }
        
        return status
    
    async def run(self):
        """Main launcher loop"""
        logger.info("🚀 Starting Multi-Agent System...")
        
        try:
            # Start orchestrator first
            if not self.start_orchestrator():
                logger.error("❌ Failed to start orchestrator - aborting")
                return
            
            # Start all ready agents
            self.start_ready_agents()
            
            # Begin monitoring
            self.running = True
            
            # Log initial status
            status = self.get_system_status()
            logger.info(f"📊 System Status: {status['running_agents']}/{status['total_agents']} agents running")
            
            # Monitor loop
            while self.running:
                await asyncio.sleep(30)
                
                # Log periodic status
                status = self.get_system_status()
                logger.info(f"📊 {status['running_agents']}/{status['total_agents']} agents running")
                
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested...")
        except Exception as e:
            logger.error(f"System error: {e}")
        finally:
            self.stop_all()


def create_example_work_items():
    """Create some example work items for testing"""
    try:
        from agent_orchestration_system import get_orchestrator, Priority
        
        orchestrator = get_orchestrator()
        
        # Add test work items
        orchestrator.add_work_item(
            title="Design user authentication system",
            description="Create technical specifications for secure user authentication with AWS Cognito",
            item_type="architecture",
            priority=Priority.HIGH
        )
        
        orchestrator.add_work_item(
            title="Create marketing campaign for Q4",
            description="Develop comprehensive marketing strategy for product launch",
            item_type="marketing",
            priority=Priority.MEDIUM
        )
        
        orchestrator.add_work_item(
            title="Implement customer feedback system",
            description="Build automated system for collecting and analyzing customer feedback",
            item_type="development",
            priority=Priority.MEDIUM
        )
        
        logger.info("✅ Created example work items")
        
    except Exception as e:
        logger.warning(f"Could not create example work items: {e}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 MULTI-AGENT AUTONOMOUS BUSINESS SYSTEM")
    print("="*80)
    print("Launching coordinated AI agents for complete business automation")
    print("AWS Serverless-First Architecture")
    print("Opus: Build missing agents using the template and plan provided")
    print("="*80 + "\n")
    
    launcher = MultiAgentSystemLauncher()
    
    # Show current status
    status = launcher.get_system_status()
    print(f"📊 System Status:")
    print(f"   Total Agents: {status['total_agents']}")
    print(f"   Ready Agents: {status['ready_agents']}")
    print(f"   Missing Agents: {status['missing_agents']}")
    
    if status['missing_agents'] > 0:
        print(f"\n⚠️ Missing agents need to be built by Opus:")
        for agent_name, config in launcher.available_agents.items():
            if config['status'] == 'pending':
                print(f"   - {agent_name} (Priority {config['priority']})")
        print(f"\n📋 Instructions: See OPUS_AGENT_DEVELOPMENT_PLAN.md")
        print(f"🔧 Template: Use ai-agent-template.py as base")
    
    print(f"\n🚀 Launching available agents...")
    
    try:
        # Create some example work
        create_example_work_items()
        
        # Run the system
        asyncio.run(launcher.run())
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")
        logging.error(f"System error: {e}")
