#!/usr/bin/env python3
"""
Environment-Aware AWS Cost Monitor
Monitors costs per environment with selective emergency shutdown
"""

import boto3
import json
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class EnvironmentAwareCostMonitor:
    def __init__(self, config_file="E:/Projects/environment-cost-config.json"):
        self.config_file = Path(config_file)
        self.load_config()
        
        self.log_dir = Path("E:/Projects/agent_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_file = self.log_dir / "environment_cost_monitor.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("env-cost-monitor")
        
        # Initialize AWS clients
        try:
            self.ce_client = boto3.client('ce', region_name=self.config['aws']['region'])
            self.logger.info("AWS Cost Explorer client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize AWS Cost Explorer: {e}")
            self.ce_client = None
            
        # Environment cost tracking
        self.environment_costs = {}
        self.cost_history = {}
        
    def load_config(self):
        """Load environment monitoring configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Create default config
            self.config = {
                "environments": {
                    "dev": {
                        "enabled": True,
                        "cost_threshold_percent": 2.0,
                        "time_window_minutes": 30,
                        "tags": {"Environment": "dev", "Project": "testing"},
                        "shutdown_agents": ["dev-agents"],
                        "max_hourly_cost": 5.0
                    },
                    "staging": {
                        "enabled": True, 
                        "cost_threshold_percent": 1.5,
                        "time_window_minutes": 45,
                        "tags": {"Environment": "staging"},
                        "shutdown_agents": ["staging-agents"],
                        "max_hourly_cost": 10.0
                    },
                    "production": {
                        "enabled": False,
                        "cost_threshold_percent": 0.5,
                        "time_window_minutes": 60,
                        "tags": {"Environment": "production"},
                        "shutdown_agents": [],
                        "max_hourly_cost": 50.0
                    }
                },
                "aws": {
                    "region": "us-east-1",
                    "profile": "default"
                },
                "global": {
                    "total_cost_threshold_percent": 1.0,
                    "emergency_shutdown_all": True,
                    "max_total_hourly_cost": 100.0
                }
            }
            self.save_config()
            
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def get_environment_costs(self, environment: str) -> Optional[float]:
        """Get costs for specific environment using tags"""
        if not self.ce_client:
            return None
            
        env_config = self.config['environments'].get(environment)
        if not env_config or not env_config['enabled']:
            return None
            
        try:
            now = datetime.now()
            start_time = now - timedelta(hours=1)  # Last hour
            
            # Build tag filters for this environment
            tag_filters = []
            for key, value in env_config['tags'].items():
                tag_filters.append({
                    'Key': key,
                    'Values': [value]
                })
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_time.strftime('%Y-%m-%d'),
                    'End': now.strftime('%Y-%m-%d')
                },
                Granularity='HOURLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'TAG', 'Key': 'Environment'},
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ],
                Filter={
                    'And': [
                        {'Dimensions': {
                            'Key': 'RECORD_TYPE',
                            'Values': ['Usage']
                        }},
                        {'Tags': {
                            'Key': list(env_config['tags'].keys())[0],
                            'Values': [list(env_config['tags'].values())[0]]
                        }}
                    ]
                } if tag_filters else None
            )
            
            total_cost = 0.0
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += cost
                    
            self.logger.info(f"Environment {environment} hourly cost: ${total_cost:.4f}")
            return total_cost
            
        except Exception as e:
            self.logger.error(f"Error fetching costs for {environment}: {e}")
            return None
            
    def check_environment_thresholds(self, environment: str, current_cost: float) -> Dict:
        """Check if environment exceeds its thresholds"""
        env_config = self.config['environments'][environment]
        
        # Initialize history for this environment
        if environment not in self.cost_history:
            self.cost_history[environment] = []
            
        current_time = datetime.now()
        
        # Add current cost to history
        self.cost_history[environment].append({
            'timestamp': current_time,
            'cost': current_cost
        })
        
        # Clean old entries
        cutoff_time = current_time - timedelta(minutes=env_config['time_window_minutes'])
        self.cost_history[environment] = [
            entry for entry in self.cost_history[environment]
            if entry['timestamp'] > cutoff_time
        ]
        
        alerts = {
            'environment': environment,
            'current_cost': current_cost,
            'alerts': [],
            'shutdown_recommended': False
        }
        
        # Check percentage increase
        if len(self.cost_history[environment]) >= 2:
            oldest_cost = min(self.cost_history[environment], key=lambda x: x['timestamp'])['cost']
            
            if oldest_cost > 0:
                percent_increase = ((current_cost - oldest_cost) / oldest_cost) * 100
                
                if percent_increase > env_config['cost_threshold_percent']:
                    alerts['alerts'].append({
                        'type': 'percentage_increase',
                        'value': percent_increase,
                        'threshold': env_config['cost_threshold_percent'],
                        'severity': 'high'
                    })
                    alerts['shutdown_recommended'] = True
                    
        # Check absolute cost limit
        if current_cost > env_config['max_hourly_cost']:
            alerts['alerts'].append({
                'type': 'absolute_limit',
                'value': current_cost,
                'threshold': env_config['max_hourly_cost'],
                'severity': 'critical'
            })
            alerts['shutdown_recommended'] = True
            
        return alerts
        
    def environment_specific_shutdown(self, environment: str, alerts: Dict):
        """Shutdown agents specific to an environment"""
        env_config = self.config['environments'][environment]
        
        self.logger.critical(f"ENVIRONMENT SHUTDOWN: {environment}")
        self.logger.critical(f"Alerts: {alerts['alerts']}")
        
        # Kill environment-specific agents
        import psutil
        killed_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    
                    # Check if this process belongs to this environment
                    if f"--env {environment}" in cmdline or f"--environment {environment}" in cmdline:
                        proc.kill()
                        killed_processes.append(f"PID {proc.info['pid']}: {environment} agent")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        # Create environment-specific report
        report = {
            'timestamp': datetime.now().isoformat(),
            'environment': environment,
            'alerts': alerts,
            'killed_processes': killed_processes,
            'config': env_config
        }
        
        report_file = self.log_dir / f"env_shutdown_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        self.logger.critical(f"Environment shutdown report: {report_file}")
        
    def monitor_all_environments(self):
        """Monitor all enabled environments"""
        self.logger.info("Starting environment-aware cost monitoring")
        
        while True:
            try:
                total_alerts = []
                total_current_cost = 0.0
                
                # Check each environment
                for env_name, env_config in self.config['environments'].items():
                    if not env_config['enabled']:
                        continue
                        
                    current_cost = self.get_environment_costs(env_name)
                    if current_cost is not None:
                        total_current_cost += current_cost
                        
                        # Check environment-specific thresholds
                        alerts = self.check_environment_thresholds(env_name, current_cost)
                        
                        if alerts['shutdown_recommended']:
                            total_alerts.append(alerts)
                            self.environment_specific_shutdown(env_name, alerts)
                            
                # Check global thresholds
                global_config = self.config['global']
                if total_current_cost > global_config['max_total_hourly_cost']:
                    self.logger.critical(f"GLOBAL SHUTDOWN: Total cost ${total_current_cost:.2f} exceeds ${global_config['max_total_hourly_cost']}")
                    if global_config['emergency_shutdown_all']:
                        self.global_emergency_shutdown()
                        
                # Wait before next check
                time.sleep(180)  # Check every 3 minutes
                
            except KeyboardInterrupt:
                self.logger.info("Environment monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)
                
    def global_emergency_shutdown(self):
        """Emergency shutdown of all environments"""
        self.logger.critical("GLOBAL EMERGENCY SHUTDOWN")
        
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(script in cmdline for script in [
                        'monitorable-agent.py', 'gh-copilot-orchestrator.py',
                        'local-orchestrator.py', 'cost-aware-orchestrator.py'
                    ]):
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    def get_status(self) -> Dict:
        """Get current monitoring status for all environments"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'environments': {},
            'global_config': self.config['global']
        }
        
        for env_name, env_config in self.config['environments'].items():
            if env_config['enabled']:
                recent_cost = None
                if env_name in self.cost_history and self.cost_history[env_name]:
                    recent_cost = self.cost_history[env_name][-1]['cost']
                    
                status['environments'][env_name] = {
                    'enabled': True,
                    'recent_cost': recent_cost,
                    'threshold_percent': env_config['cost_threshold_percent'],
                    'max_hourly_cost': env_config['max_hourly_cost'],
                    'history_entries': len(self.cost_history.get(env_name, []))
                }
            else:
                status['environments'][env_name] = {'enabled': False}
                
        return status

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Environment-Aware AWS Cost Monitor')
    parser.add_argument('--config', default='E:/Projects/environment-cost-config.json',
                       help='Configuration file path')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--environment', help='Monitor specific environment only')
    
    args = parser.parse_args()
    
    monitor = EnvironmentAwareCostMonitor(args.config)
    
    if args.status:
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
        return
        
    monitor.monitor_all_environments()

if __name__ == "__main__":
    main()
