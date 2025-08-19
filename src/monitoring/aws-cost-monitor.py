#!/usr/bin/env python3
"""
AWS Cost Monitor - Real-time cost tracking with emergency shutdown
Monitors AWS costs and automatically kills testing processes if costs increase >1% in <1 hour
"""

import boto3
import json
import os
import sys
import time
import logging
import psutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class AWSCostMonitor:
    def __init__(self, threshold_percent=1.0, time_window_minutes=60):
        self.threshold_percent = threshold_percent
        self.time_window_minutes = time_window_minutes
        self.log_dir = Path("E:/Projects/agent_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_file = self.log_dir / "aws_cost_monitor.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("aws-cost-monitor")
        
        # Initialize AWS clients
        try:
            self.ce_client = boto3.client('ce')  # Cost Explorer
            self.logger.info("AWS Cost Explorer client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize AWS Cost Explorer: {e}")
            self.ce_client = None
            
        # Cost tracking
        self.cost_history = []
        self.baseline_cost = None
        self.emergency_shutdown_triggered = False
        
        # Process tracking for emergency shutdown
        self.monitored_processes = [
            "monitorable-agent.py",
            "gh-copilot-orchestrator.py", 
            "local-orchestrator.py",
            "run-gh-copilot-tests.py"
        ]
        
    def get_current_aws_costs(self) -> Optional[float]:
        """Get current month-to-date AWS costs"""
        if not self.ce_client:
            return None
            
        try:
            # Get current month costs
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_of_month.strftime('%Y-%m-%d'),
                    'End': now.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            total_cost = 0.0
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += cost
                    
            self.logger.info(f"Current AWS MTD cost: ${total_cost:.2f}")
            return total_cost
            
        except Exception as e:
            self.logger.error(f"Error fetching AWS costs: {e}")
            return None
    
    def check_cost_increase(self, current_cost: float) -> bool:
        """Check if cost increase exceeds threshold within time window"""
        current_time = datetime.now()
        
        # Add current cost to history
        self.cost_history.append({
            'timestamp': current_time,
            'cost': current_cost
        })
        
        # Clean old entries outside time window
        cutoff_time = current_time - timedelta(minutes=self.time_window_minutes)
        self.cost_history = [
            entry for entry in self.cost_history 
            if entry['timestamp'] > cutoff_time
        ]
        
        # Need at least 2 data points to compare
        if len(self.cost_history) < 2:
            return False
            
        # Find oldest cost in time window
        oldest_cost = min(self.cost_history, key=lambda x: x['timestamp'])['cost']
        
        # Calculate percentage increase
        if oldest_cost > 0:
            percent_increase = ((current_cost - oldest_cost) / oldest_cost) * 100
            self.logger.info(f"Cost change in last {self.time_window_minutes}min: {percent_increase:.2f}%")
            
            if percent_increase > self.threshold_percent:
                self.logger.warning(f"COST ALERT: {percent_increase:.2f}% increase exceeds {self.threshold_percent}% threshold!")
                return True
                
        return False
    
    def emergency_shutdown(self):
        """Emergency shutdown of all testing processes"""
        self.logger.critical("EMERGENCY SHUTDOWN: Killing all testing processes due to cost spike!")
        self.emergency_shutdown_triggered = True
        
        # Kill Python processes running our agents
        killed_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    for monitored in self.monitored_processes:
                        if monitored in cmdline:
                            proc.kill()
                            killed_processes.append(f"PID {proc.info['pid']}: {monitored}")
                            self.logger.info(f"Killed process: {monitored} (PID: {proc.info['pid']})")
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        # Stop Docker containers to reduce costs
        try:
            subprocess.run(['docker', 'stop', '$(docker ps -q)'], 
                         shell=True, capture_output=True)
            self.logger.info("Stopped all Docker containers")
        except Exception as e:
            self.logger.error(f"Failed to stop Docker containers: {e}")
            
        # Create emergency report
        self.create_emergency_report(killed_processes)
        
    def create_emergency_report(self, killed_processes: List[str]):
        """Create emergency shutdown report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'trigger': 'cost_spike',
            'threshold_percent': self.threshold_percent,
            'time_window_minutes': self.time_window_minutes,
            'killed_processes': killed_processes,
            'cost_history': [
                {
                    'timestamp': entry['timestamp'].isoformat(),
                    'cost': entry['cost']
                }
                for entry in self.cost_history
            ]
        }
        
        report_file = self.log_dir / f"emergency_shutdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        self.logger.critical(f"Emergency report saved to: {report_file}")
        
    def monitor_continuously(self, check_interval_seconds=300):
        """Continuously monitor AWS costs"""
        self.logger.info(f"Starting continuous AWS cost monitoring (threshold: {self.threshold_percent}% in {self.time_window_minutes}min)")
        
        while not self.emergency_shutdown_triggered:
            try:
                current_cost = self.get_current_aws_costs()
                
                if current_cost is not None:
                    if self.check_cost_increase(current_cost):
                        self.emergency_shutdown()
                        break
                else:
                    self.logger.warning("Could not retrieve AWS costs - continuing monitoring")
                    
                # Wait before next check
                time.sleep(check_interval_seconds)
                
            except KeyboardInterrupt:
                self.logger.info("Cost monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in cost monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying
                
    def get_status(self) -> Dict:
        """Get current monitoring status"""
        latest_cost = self.cost_history[-1]['cost'] if self.cost_history else None
        
        return {
            'monitoring_active': not self.emergency_shutdown_triggered,
            'threshold_percent': self.threshold_percent,
            'time_window_minutes': self.time_window_minutes,
            'latest_cost': latest_cost,
            'history_entries': len(self.cost_history),
            'emergency_triggered': self.emergency_shutdown_triggered
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='AWS Cost Monitor with Emergency Shutdown')
    parser.add_argument('--threshold', type=float, default=1.0, 
                       help='Cost increase threshold percentage (default: 1.0)')
    parser.add_argument('--window', type=int, default=60,
                       help='Time window in minutes (default: 60)')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    parser.add_argument('--status', action='store_true',
                       help='Show current status and exit')
    
    args = parser.parse_args()
    
    monitor = AWSCostMonitor(
        threshold_percent=args.threshold,
        time_window_minutes=args.window
    )
    
    if args.status:
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
        return
        
    try:
        monitor.monitor_continuously(check_interval_seconds=args.interval)
    except KeyboardInterrupt:
        print("\nCost monitoring stopped.")

if __name__ == "__main__":
    main()
