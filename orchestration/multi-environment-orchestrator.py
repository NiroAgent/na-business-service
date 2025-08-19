#!/usr/bin/env python3
"""
Multi-Environment Agent Orchestrator
Manages agents across different environments with selective cost monitoring
"""

import json
import os
import sys
import time
import threading
import logging
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class MultiEnvironmentOrchestrator:
    def __init__(self, target_environments=None):
        self.target_environments = target_environments or ['dev']
        self.log_dir = Path("E:/Projects/agent_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_file = self.log_dir / "multi_env_orchestrator.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("multi-env-orchestrator")
        
        # Environment-specific agent configurations
        self.environment_configs = {
            'dev': {
                'agents': [
                    {
                        'name': 'dev-monitorable-agent',
                        'script': 'E:/Projects/monitorable-agent.py',
                        'args': ['--environment', 'dev'],
                        'priority': 1
                    },
                    {
                        'name': 'dev-gh-copilot',
                        'script': 'E:/Projects/gh-copilot-orchestrator.py',
                        'args': ['--batch', 'dev'],
                        'priority': 2
                    }
                ],
                'cost_threshold': 2.0,
                'max_agents': 3
            },
            'staging': {
                'agents': [
                    {
                        'name': 'staging-monitorable-agent',
                        'script': 'E:/Projects/monitorable-agent.py',
                        'args': ['--environment', 'staging'],
                        'priority': 1
                    },
                    {
                        'name': 'staging-gh-copilot',
                        'script': 'E:/Projects/gh-copilot-orchestrator.py',
                        'args': ['--batch', 'staging'],
                        'priority': 2
                    }
                ],
                'cost_threshold': 1.5,
                'max_agents': 2
            },
            'production': {
                'agents': [
                    {
                        'name': 'prod-monitor-only',
                        'script': 'E:/Projects/monitorable-agent.py',
                        'args': ['--environment', 'production', '--read-only'],
                        'priority': 1
                    }
                ],
                'cost_threshold': 0.5,
                'max_agents': 1
            }
        }
        
        self.active_agents = {}
        self.shutdown_environments = set()
        
    def start_environment_agents(self, environment: str):
        """Start all agents for a specific environment"""
        if environment not in self.environment_configs:
            self.logger.error(f"Unknown environment: {environment}")
            return
            
        if environment in self.shutdown_environments:
            self.logger.warning(f"Environment {environment} is in shutdown state")
            return
            
        env_config = self.environment_configs[environment]
        self.logger.info(f"Starting agents for environment: {environment}")
        
        for agent_config in env_config['agents']:
            self.start_agent(agent_config, environment)
            time.sleep(2)  # Stagger startup
            
    def start_agent(self, config: Dict, environment: str) -> Optional[subprocess.Popen]:
        """Start an individual agent with environment context"""
        try:
            cmd = [
                'E:/Projects/.venv/Scripts/python.exe',
                config['script']
            ] + config['args']
            
            self.logger.info(f"Starting {config['name']} for {environment}")
            
            # Set environment variables
            env_vars = os.environ.copy()
            env_vars['AGENT_ENVIRONMENT'] = environment
            env_vars['AGENT_NAME'] = config['name']
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env_vars
            )
            
            agent_key = f"{environment}_{config['name']}"
            self.active_agents[agent_key] = {
                'process': process,
                'config': config,
                'environment': environment,
                'start_time': datetime.now()
            }
            
            self.logger.info(f"Started {config['name']} for {environment} (PID: {process.pid})")
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start {config['name']} for {environment}: {e}")
            return None
            
    def stop_environment_agents(self, environment: str, reason="manual"):
        """Stop all agents for a specific environment"""
        self.logger.warning(f"Stopping all agents for environment: {environment} (reason: {reason})")
        self.shutdown_environments.add(environment)
        
        agents_to_stop = [
            key for key, info in self.active_agents.items()
            if info['environment'] == environment
        ]
        
        for agent_key in agents_to_stop:
            self.stop_agent(agent_key)
            
    def stop_agent(self, agent_key: str):
        """Stop a specific agent"""
        if agent_key in self.active_agents:
            agent_info = self.active_agents[agent_key]
            process = agent_info['process']
            
            try:
                process.terminate()
                process.wait(timeout=10)
                self.logger.info(f"Stopped agent: {agent_key}")
            except subprocess.TimeoutExpired:
                process.kill()
                self.logger.warning(f"Force killed agent: {agent_key}")
            except Exception as e:
                self.logger.error(f"Error stopping {agent_key}: {e}")
                
            del self.active_agents[agent_key]
            
    def start_cost_monitoring(self):
        """Start environment-aware cost monitoring"""
        def cost_monitor_thread():
            try:
                # Import and start environment cost monitor
                import importlib.util
                monitor_path = Path(__file__).parent / "environment-aware-cost-monitor.py"
                spec = importlib.util.spec_from_file_location("env_cost_monitor", monitor_path)
                env_cost_monitor = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(env_cost_monitor)
                
                monitor = env_cost_monitor.EnvironmentAwareCostMonitor()
                
                # Custom monitoring loop that can shut down specific environments
                while True:
                    status = monitor.get_status()
                    
                    for env_name, env_status in status['environments'].items():
                        if env_status.get('enabled') and env_status.get('recent_cost'):
                            # Check if environment should be shut down
                            # This would be expanded with actual cost increase logic
                            pass
                            
                    time.sleep(180)  # Check every 3 minutes
                    
            except Exception as e:
                self.logger.error(f"Cost monitoring error: {e}")
                
        cost_thread = threading.Thread(target=cost_monitor_thread, daemon=True)
        cost_thread.start()
        self.logger.info("Environment-aware cost monitoring started")
        
    def monitor_agents(self):
        """Monitor agent health and restart if needed"""
        while True:
            try:
                for agent_key, agent_info in list(self.active_agents.items()):
                    process = agent_info['process']
                    environment = agent_info['environment']
                    
                    if process.poll() is not None:  # Process has ended
                        self.logger.warning(f"Agent {agent_key} has stopped (exit code: {process.returncode})")
                        del self.active_agents[agent_key]
                        
                        # Restart if environment is not in shutdown
                        if environment not in self.shutdown_environments:
                            self.logger.info(f"Restarting {agent_key}")
                            self.start_agent(agent_info['config'], environment)
                            
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in agent monitoring: {e}")
                time.sleep(10)
                
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'target_environments': self.target_environments,
            'shutdown_environments': list(self.shutdown_environments),
            'active_agents': {
                key: {
                    'environment': info['environment'],
                    'name': info['config']['name'],
                    'pid': info['process'].pid,
                    'running': info['process'].poll() is None,
                    'start_time': info['start_time'].isoformat()
                }
                for key, info in self.active_agents.items()
            }
        }
        
    def run(self):
        """Main orchestrator run"""
        self.logger.info(f"Starting Multi-Environment Orchestrator for: {self.target_environments}")
        
        try:
            # Start cost monitoring
            self.start_cost_monitoring()
            
            # Start agents for target environments
            for environment in self.target_environments:
                self.start_environment_agents(environment)
                time.sleep(5)
                
            # Monitor agents
            self.monitor_agents()
            
        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
        finally:
            # Cleanup
            for agent_key in list(self.active_agents.keys()):
                self.stop_agent(agent_key)

def main():
    parser = argparse.ArgumentParser(description='Multi-Environment Agent Orchestrator')
    parser.add_argument('--environments', nargs='+', 
                       choices=['dev', 'staging', 'production'],
                       default=['dev'],
                       help='Target environments to monitor')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--stop-env', help='Stop agents for specific environment')
    
    args = parser.parse_args()
    
    orchestrator = MultiEnvironmentOrchestrator(args.environments)
    
    if args.status:
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2))
        return
        
    if args.stop_env:
        orchestrator.stop_environment_agents(args.stop_env, "manual_stop")
        return
        
    orchestrator.run()

if __name__ == "__main__":
    main()
