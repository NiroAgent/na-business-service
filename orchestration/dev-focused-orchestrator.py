#!/usr/bin/env python3
"""
Dev-Focused Orchestrator with Global Failsafe
Primary: Test dev environment aggressively
Failsafe: Monitor all environments for safety
"""

import json
import os
import sys
import time
import threading
import logging
import subprocess
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class DevFocusedOrchestrator:
    def __init__(self):
        self.log_dir = Path("E:/Projects/agent_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_file = self.log_dir / "dev_focused_orchestrator.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("dev-orchestrator")
        
        # Primary dev agents
        self.dev_agents = [
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
            },
            {
                'name': 'dev-log-monitor',
                'script': 'E:/Projects/log-monitor.py',
                'args': ['--environment', 'dev'],
                'priority': 3
            }
        ]
        
        self.active_agents = {}
        self.emergency_shutdown = False
        self.global_failsafe_active = True
        
        # Global monitoring settings
        self.global_limits = {
            'max_total_hourly_cost': 25.0,  # Global failsafe limit
            'max_cost_increase_percent': 1.0,  # Global emergency threshold
            'time_window_minutes': 60,
            'check_interval_seconds': 120  # Check every 2 minutes
        }
        
        # Environment-specific limits
        self.environment_limits = {
            'dev': {
                'max_hourly_cost': 8.0,  # Higher limit for dev testing
                'cost_increase_threshold': 3.0,  # More tolerant for dev
                'time_window_minutes': 20  # Faster response for dev
            },
            'staging': {
                'max_hourly_cost': 5.0,  # Moderate limit for staging
                'cost_increase_threshold': 1.5,  # Medium tolerance
                'time_window_minutes': 30
            },
            'production': {
                'max_hourly_cost': 2.0,  # Strict limit for production
                'cost_increase_threshold': 0.5,  # Very strict tolerance
                'time_window_minutes': 60
            }
        }
        
    def start_global_failsafe_monitor(self):
        """Start comprehensive monitoring of all environments"""
        def global_monitor_thread():
            try:
                import boto3
                ce_client = boto3.client('ce')
                self.logger.info("GLOBAL FAILSAFE: Monitoring ALL environments")
                
                cost_history = []
                
                while not self.emergency_shutdown:
                    try:
                        # Get total AWS costs (all environments)
                        now = datetime.now()
                        start_time = now - timedelta(hours=1)
                        
                        response = ce_client.get_cost_and_usage(
                            TimePeriod={
                                'Start': start_time.strftime('%Y-%m-%d'),
                                'End': now.strftime('%Y-%m-%d')
                            },
                            Granularity='HOURLY',
                            Metrics=['BlendedCost'],
                            GroupBy=[
                                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                                {'Type': 'TAG', 'Key': 'Environment'}
                            ]
                        )
                        
                        # Calculate total and per-environment costs
                        total_cost = 0.0
                        env_costs = {'dev': 0.0, 'staging': 0.0, 'production': 0.0, 'untagged': 0.0}
                        
                        for result in response['ResultsByTime']:
                            for group in result['Groups']:
                                cost = float(group['Metrics']['BlendedCost']['Amount'])
                                total_cost += cost
                                
                                # Try to categorize by environment tag
                                env_tag = 'untagged'
                                if len(group['Keys']) > 1 and group['Keys'][1]:
                                    env_tag = group['Keys'][1].lower()
                                
                                if env_tag in env_costs:
                                    env_costs[env_tag] += cost
                                else:
                                    env_costs['untagged'] += cost
                        
                        # Log current costs
                        self.logger.info(f"GLOBAL COSTS: Total=${total_cost:.4f}/hr | Dev=${env_costs['dev']:.4f} | Staging=${env_costs['staging']:.4f} | Prod=${env_costs['production']:.4f} | Untagged=${env_costs['untagged']:.4f}")
                        
                        # Add to history
                        cost_history.append({
                            'timestamp': now,
                            'total_cost': total_cost,
                            'env_costs': env_costs.copy()
                        })
                        
                        # Keep only recent history
                        cutoff_time = now - timedelta(minutes=self.global_limits['time_window_minutes'])
                        cost_history = [h for h in cost_history if h['timestamp'] > cutoff_time]
                        
                        # Check global failsafe triggers
                        failsafe_triggered = False
                        
                        # 1. Absolute cost limit
                        if total_cost > self.global_limits['max_total_hourly_cost']:
                            self.logger.critical(f"GLOBAL FAILSAFE: Total cost ${total_cost:.2f} exceeds limit ${self.global_limits['max_total_hourly_cost']}")
                            failsafe_triggered = True
                            
                        # 2. Rapid cost increase
                        if len(cost_history) >= 2:
                            oldest_cost = min(cost_history, key=lambda x: x['timestamp'])['total_cost']
                            if oldest_cost > 0:
                                percent_increase = ((total_cost - oldest_cost) / oldest_cost) * 100
                                if percent_increase > self.global_limits['max_cost_increase_percent']:
                                    self.logger.critical(f"GLOBAL FAILSAFE: Cost increase {percent_increase:.2f}% exceeds {self.global_limits['max_cost_increase_percent']}%")
                                    failsafe_triggered = True
                        
                        # 3. Check individual environment limits
                        for env_name, env_cost in env_costs.items():
                            if env_name in self.environment_limits:
                                env_limit = self.environment_limits[env_name]
                                if env_cost > env_limit['max_hourly_cost']:
                                    self.logger.critical(f"GLOBAL FAILSAFE: {env_name.upper()} cost ${env_cost:.2f} exceeds limit ${env_limit['max_hourly_cost']}")
                                    failsafe_triggered = True
                        
                        # 4. Untagged resource protection
                        if env_costs['untagged'] > 5.0:  # $5/hr limit for untagged resources
                            self.logger.critical(f"GLOBAL FAILSAFE: Untagged resources cost ${env_costs['untagged']:.2f} exceeds $5.00 (possible wrong environment usage)")
                            failsafe_triggered = True
                        
                        # Trigger emergency shutdown if needed
                        if failsafe_triggered:
                            self.trigger_global_emergency_shutdown({
                                'total_cost': total_cost,
                                'env_costs': env_costs,
                                'cost_history': cost_history[-5:]  # Last 5 readings
                            })
                            break
                            
                        # Sleep before next check
                        time.sleep(self.global_limits['check_interval_seconds'])
                        
                    except Exception as e:
                        self.logger.error(f"Global monitoring error: {e}")
                        time.sleep(30)
                        
            except Exception as e:
                self.logger.error(f"Global failsafe monitor failed to start: {e}")
                
        # Start monitor thread
        monitor_thread = threading.Thread(target=global_monitor_thread, daemon=True)
        monitor_thread.start()
        self.logger.info("Global failsafe monitor started")
        
    def trigger_global_emergency_shutdown(self, cost_data: Dict):
        """Emergency shutdown of ALL processes across ALL environments"""
        self.logger.critical("🚨 GLOBAL EMERGENCY SHUTDOWN TRIGGERED 🚨")
        self.emergency_shutdown = True
        
        # Kill ALL Python agents (across all environments)
        killed_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    
                    # Kill any process running our agent scripts
                    agent_scripts = [
                        'monitorable-agent.py', 'gh-copilot-orchestrator.py',
                        'local-orchestrator.py', 'log-monitor.py',
                        'run-gh-copilot-tests.py'
                    ]
                    
                    for script in agent_scripts:
                        if script in cmdline:
                            proc.kill()
                            killed_processes.append(f"PID {proc.info['pid']}: {script}")
                            self.logger.critical(f"KILLED: {script} (PID: {proc.info['pid']})")
                            break
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Stop all Docker containers
        try:
            result = subprocess.run(['docker', 'stop', '$(docker ps -q)'], 
                                 shell=True, capture_output=True, text=True)
            self.logger.critical("DOCKER: Stopped all containers")
        except Exception as e:
            self.logger.error(f"Failed to stop Docker containers: {e}")
            
        # Create comprehensive emergency report
        emergency_report = {
            'timestamp': datetime.now().isoformat(),
            'trigger': 'global_failsafe',
            'cost_data': cost_data,
            'killed_processes': killed_processes,
            'global_limits': self.global_limits,
            'environment_limits': self.environment_limits
        }
        
        report_file = self.log_dir / f"GLOBAL_EMERGENCY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(emergency_report, f, indent=2)
            
        self.logger.critical(f"Emergency report saved: {report_file}")
        
        # Stop all active agents
        for agent_key in list(self.active_agents.keys()):
            self.stop_agent(agent_key)
            
    def start_dev_agent(self, config: Dict) -> Optional[subprocess.Popen]:
        """Start a dev environment agent"""
        try:
            cmd = [
                'E:/Projects/.venv/Scripts/python.exe',
                config['script']
            ] + config['args']
            
            self.logger.info(f"Starting DEV agent: {config['name']}")
            
            # Set environment variables to ensure dev context
            env_vars = os.environ.copy()
            env_vars['AGENT_ENVIRONMENT'] = 'dev'
            env_vars['AGENT_NAME'] = config['name']
            env_vars['AWS_DEFAULT_TAGS'] = '{"Environment":"dev","Project":"testing"}'
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env_vars
            )
            
            self.active_agents[config['name']] = {
                'process': process,
                'config': config,
                'start_time': datetime.now()
            }
            
            self.logger.info(f"Started DEV agent: {config['name']} (PID: {process.pid})")
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start DEV agent {config['name']}: {e}")
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
            
    def monitor_dev_agents(self):
        """Monitor dev agent health and restart if needed"""
        while not self.emergency_shutdown:
            try:
                for agent_name, agent_info in list(self.active_agents.items()):
                    process = agent_info['process']
                    
                    if process.poll() is not None:  # Process has ended
                        self.logger.warning(f"DEV agent {agent_name} stopped (exit code: {process.returncode})")
                        del self.active_agents[agent_name]
                        
                        # Restart if not in emergency shutdown
                        if not self.emergency_shutdown:
                            self.logger.info(f"Restarting DEV agent: {agent_name}")
                            self.start_dev_agent(agent_info['config'])
                            
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring DEV agents: {e}")
                time.sleep(10)
                
    def get_status(self) -> Dict:
        """Get current orchestrator status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'mode': 'dev-focused-with-global-failsafe',
            'emergency_shutdown': self.emergency_shutdown,
            'global_failsafe_active': self.global_failsafe_active,
            'active_dev_agents': {
                name: {
                    'pid': info['process'].pid,
                    'running': info['process'].poll() is None,
                    'start_time': info['start_time'].isoformat()
                }
                for name, info in self.active_agents.items()
            },
            'global_limits': self.global_limits,
            'environment_limits': self.environment_limits
        }
        
    def run(self):
        """Main orchestrator execution"""
        self.logger.info("🚀 Starting Dev-Focused Orchestrator with Global Failsafe")
        self.logger.info("PRIMARY: Aggressive dev environment testing")
        self.logger.info("FAILSAFE: Monitoring ALL environments for safety")
        
        try:
            # Start global failsafe monitoring first
            self.start_global_failsafe_monitor()
            time.sleep(2)
            
            # Start dev agents
            self.logger.info("Starting DEV environment agents...")
            for config in sorted(self.dev_agents, key=lambda x: x['priority']):
                if not self.emergency_shutdown:
                    self.start_dev_agent(config)
                    time.sleep(3)  # Stagger startup
                    
            # Monitor dev agents
            self.monitor_dev_agents()
            
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
            final_status = self.get_status()
            status_file = self.log_dir / f"dev_orchestrator_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(final_status, f, indent=2)
                
            self.logger.info(f"Final status saved: {status_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Dev-Focused Orchestrator with Global Failsafe')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--stop', action='store_true', help='Stop all agents')
    
    args = parser.parse_args()
    
    orchestrator = DevFocusedOrchestrator()
    
    if args.status:
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2))
        return
        
    if args.stop:
        # Kill any running agents
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'dev-focused-orchestrator.py' in cmdline:
                        proc.kill()
                        print(f"Stopped orchestrator (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return
        
    orchestrator.run()

if __name__ == "__main__":
    main()
