#!/usr/bin/env python3
"""
Cost-Aware Agent Orchestrator
Integrates AWS cost monitoring with agent orchestration for safe testing
"""

import json
import os
import sys
import time
import threading
import logging
import subprocess
import psutil
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import our cost monitor
import importlib.util
cost_monitor_path = Path(__file__).parent / "aws-cost-monitor.py"
spec = importlib.util.spec_from_file_location("aws_cost_monitor", cost_monitor_path)
aws_cost_monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aws_cost_monitor)
AWSCostMonitor = aws_cost_monitor.AWSCostMonitor

class CostAwareOrchestrator:
    def __init__(self, cost_threshold=1.0, cost_window_minutes=60):
        self.log_dir = Path("E:/Projects/agent_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_file = self.log_dir / "cost_aware_orchestrator.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("cost-orchestrator")
        
        # Initialize cost monitor
        self.cost_monitor = AWSCostMonitor(
            threshold_percent=cost_threshold,
            time_window_minutes=cost_window_minutes
        )
        
        # Agent management
        self.active_agents = {}
        self.shutdown_requested = False
        
        # Agent configurations
        self.agent_configs = [
            {
                'name': 'monitorable-agent',
                'script': 'E:/Projects/monitorable-agent.py',
                'args': [],
                'priority': 1
            },
            {
                'name': 'gh-copilot-orchestrator',
                'script': 'E:/Projects/gh-copilot-orchestrator.py',
                'args': ['--batch', 'dev'],
                'priority': 2
            },
            {
                'name': 'log-monitor',
                'script': 'E:/Projects/log-monitor.py',
                'args': [],
                'priority': 3
            }
        ]
        
    def start_cost_monitoring_thread(self):
        """Start cost monitoring in background thread"""
        def cost_monitor_wrapper():
            try:
                self.cost_monitor.monitor_continuously(check_interval_seconds=180)  # Check every 3 minutes
                
                # If cost monitor triggers emergency shutdown
                if self.cost_monitor.emergency_shutdown_triggered:
                    self.logger.critical("Cost monitor triggered emergency shutdown!")
                    self.emergency_shutdown()
                    
            except Exception as e:
                self.logger.error(f"Cost monitoring thread error: {e}")
                
        cost_thread = threading.Thread(target=cost_monitor_wrapper, daemon=True)
        cost_thread.start()
        self.logger.info("Cost monitoring thread started")
        return cost_thread
        
    def start_agent(self, config: Dict) -> Optional[subprocess.Popen]:
        """Start an individual agent process"""
        try:
            cmd = [
                'E:/Projects/.venv/Scripts/python.exe',
                config['script']
            ] + config['args']
            
            self.logger.info(f"Starting agent: {config['name']}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.active_agents[config['name']] = {
                'process': process,
                'config': config,
                'start_time': datetime.now()
            }
            
            self.logger.info(f"Started {config['name']} (PID: {process.pid})")
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start {config['name']}: {e}")
            return None
            
    def stop_agent(self, agent_name: str):
        """Stop a specific agent"""
        if agent_name in self.active_agents:
            agent_info = self.active_agents[agent_name]
            process = agent_info['process']
            
            try:
                process.terminate()
                process.wait(timeout=10)
                self.logger.info(f"Stopped agent: {agent_name}")
            except subprocess.TimeoutExpired:
                process.kill()
                self.logger.warning(f"Force killed agent: {agent_name}")
            except Exception as e:
                self.logger.error(f"Error stopping {agent_name}: {e}")
                
            del self.active_agents[agent_name]
            
    def emergency_shutdown(self):
        """Emergency shutdown of all agents"""
        self.logger.critical("EMERGENCY SHUTDOWN: Stopping all agents due to cost alert!")
        self.shutdown_requested = True
        
        # Stop all active agents
        for agent_name in list(self.active_agents.keys()):
            self.stop_agent(agent_name)
            
        # Create emergency status file
        emergency_status = {
            'timestamp': datetime.now().isoformat(),
            'trigger': 'aws_cost_spike',
            'cost_monitor_status': self.cost_monitor.get_status(),
            'stopped_agents': list(self.active_agents.keys())
        }
        
        emergency_file = self.log_dir / f"emergency_shutdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(emergency_file, 'w', encoding='utf-8') as f:
            json.dump(emergency_status, f, indent=2)
            
        self.logger.critical(f"Emergency status saved to: {emergency_file}")
        
    def monitor_agents(self):
        """Monitor agent health and restart if needed"""
        while not self.shutdown_requested:
            try:
                # Check agent health
                for agent_name, agent_info in list(self.active_agents.items()):
                    process = agent_info['process']
                    
                    if process.poll() is not None:  # Process has ended
                        self.logger.warning(f"Agent {agent_name} has stopped (exit code: {process.returncode})")
                        del self.active_agents[agent_name]
                        
                        # Restart if not shutdown requested
                        if not self.shutdown_requested:
                            self.logger.info(f"Restarting {agent_name}")
                            self.start_agent(agent_info['config'])
                            
                # Check cost monitor status
                cost_status = self.cost_monitor.get_status()
                if cost_status['emergency_triggered']:
                    self.emergency_shutdown()
                    break
                    
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in agent monitoring: {e}")
                time.sleep(10)
                
    def get_orchestrator_status(self) -> Dict:
        """Get current orchestrator status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'shutdown_requested': self.shutdown_requested,
            'active_agents': {
                name: {
                    'pid': info['process'].pid,
                    'running': info['process'].poll() is None,
                    'start_time': info['start_time'].isoformat()
                }
                for name, info in self.active_agents.items()
            },
            'cost_monitor_status': self.cost_monitor.get_status()
        }
        
    def run(self):
        """Main orchestrator run loop"""
        self.logger.info("Starting Cost-Aware Agent Orchestrator")
        self.logger.info(f"Cost threshold: {self.cost_monitor.threshold_percent}% in {self.cost_monitor.time_window_minutes} minutes")
        
        try:
            # Start cost monitoring
            cost_thread = self.start_cost_monitoring_thread()
            
            # Start agents in priority order
            sorted_configs = sorted(self.agent_configs, key=lambda x: x['priority'])
            for config in sorted_configs:
                if not self.shutdown_requested:
                    self.start_agent(config)
                    time.sleep(5)  # Stagger startup
                    
            # Monitor agents
            self.monitor_agents()
            
        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
        except Exception as e:
            self.logger.error(f"Orchestrator error: {e}")
        finally:
            # Cleanup
            self.logger.info("Shutting down orchestrator")
            for agent_name in list(self.active_agents.keys()):
                self.stop_agent(agent_name)
                
            # Save final status
            final_status = self.get_orchestrator_status()
            status_file = self.log_dir / f"orchestrator_final_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(final_status, f, indent=2)
                
            self.logger.info(f"Final status saved to: {status_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Cost-Aware Agent Orchestrator')
    parser.add_argument('--cost-threshold', type=float, default=1.0,
                       help='AWS cost increase threshold percentage (default: 1.0)')
    parser.add_argument('--cost-window', type=int, default=60,
                       help='Cost monitoring time window in minutes (default: 60)')
    parser.add_argument('--status', action='store_true',
                       help='Show current status and exit')
    
    args = parser.parse_args()
    
    orchestrator = CostAwareOrchestrator(
        cost_threshold=args.cost_threshold,
        cost_window_minutes=args.cost_window
    )
    
    if args.status:
        status = orchestrator.get_orchestrator_status()
        print(json.dumps(status, indent=2))
        return
        
    orchestrator.run()

if __name__ == "__main__":
    main()
