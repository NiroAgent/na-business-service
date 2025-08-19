#!/usr/bin/env python3
"""
Dev + Global Failsafe Dashboard
Shows dev-focused testing with comprehensive safety monitoring
"""

import json
import time
import os
import subprocess
from datetime import datetime
from pathlib import Path

class DevFailsafeDashboard:
    def __init__(self):
        self.log_dir = Path("E:/Projects/agent_logs")
        
    def get_orchestrator_status(self):
        """Get status from dev-focused orchestrator"""
        try:
            result = subprocess.run([
                'E:/Projects/.venv/Scripts/python.exe',
                'E:/Projects/dev-focused-orchestrator.py',
                '--status'
            ], capture_output=True, text=True, cwd='E:/Projects')
            
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return None
        
    def display_dashboard(self):
        """Display real-time dashboard"""
        while True:
            try:
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print("=" * 80)
                print("🚀 DEV-FOCUSED ORCHESTRATOR + GLOBAL FAILSAFE DASHBOARD")
                print("=" * 80)
                print(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                
                # Get orchestrator status
                status = self.get_orchestrator_status()
                
                if status:
                    print("📊 ORCHESTRATOR STATUS:")
                    print(f"   Mode: {status.get('mode', 'Unknown')}")
                    print(f"   Emergency Shutdown: {'🚨 YES' if status.get('emergency_shutdown') else '✅ NO'}")
                    print(f"   Global Failsafe: {'🛡️ ACTIVE' if status.get('global_failsafe_active') else '❌ INACTIVE'}")
                    print()
                    
                    print("🧪 DEV ENVIRONMENT AGENTS:")
                    dev_agents = status.get('active_dev_agents', {})
                    if dev_agents:
                        for name, info in dev_agents.items():
                            status_icon = "🟢" if info['running'] else "🔴"
                            print(f"   {status_icon} {name} (PID: {info['pid']}) - Started: {info['start_time'][:19]}")
                    else:
                        print("   📭 No dev agents running")
                    print()
                    
                    print("🛡️ GLOBAL FAILSAFE LIMITS:")
                    global_limits = status.get('global_limits', {})
                    print(f"   💰 Max Total Cost: ${global_limits.get('max_total_hourly_cost', 0)}/hour")
                    print(f"   📈 Max Cost Increase: {global_limits.get('max_cost_increase_percent', 0)}%")
                    print(f"   ⏱️ Check Interval: {global_limits.get('check_interval_seconds', 0)} seconds")
                    print()
                    
                    print("🏗️ ENVIRONMENT PROTECTION LEVELS:")
                    env_limits = status.get('environment_limits', {})
                    for env_name, limits in env_limits.items():
                        icon = "🟢" if env_name == "dev" else "🟡" if env_name == "staging" else "🔴"
                        print(f"   {icon} {env_name.upper()}: ${limits.get('max_hourly_cost', 0)}/hr, {limits.get('cost_increase_threshold', 0)}% threshold")
                    
                else:
                    print("❌ ORCHESTRATOR NOT RUNNING")
                    print()
                    print("To start:")
                    print("   python dev-focused-orchestrator.py")
                
                print()
                print("=" * 80)
                print("🎯 STRATEGY: Focus on DEV testing with ALL environment safety")
                print("🛡️ PROTECTION: Global failsafe monitors ALL AWS costs")
                print("🚨 EMERGENCY: Any environment spike triggers global shutdown")
                print("=" * 80)
                print()
                
                # Check for emergency reports
                emergency_files = list(self.log_dir.glob("GLOBAL_EMERGENCY_*.json"))
                if emergency_files:
                    latest_emergency = max(emergency_files, key=lambda f: f.stat().st_mtime)
                    print("🚨 RECENT EMERGENCY SHUTDOWN:")
                    print(f"   File: {latest_emergency.name}")
                    print(f"   Time: {datetime.fromtimestamp(latest_emergency.stat().st_mtime)}")
                    print()
                
                print("Press Ctrl+C to exit | Updates every 5 seconds")
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n👋 Dashboard stopped")
                break
            except Exception as e:
                print(f"Dashboard error: {e}")
                time.sleep(5)

def main():
    dashboard = DevFailsafeDashboard()
    dashboard.display_dashboard()

if __name__ == "__main__":
    main()
