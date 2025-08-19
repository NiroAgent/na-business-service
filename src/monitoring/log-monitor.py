#!/usr/bin/env python3
"""
Real-time Log Monitor - Watch agent logs in real-time
"""

import time
import os
from pathlib import Path
import json
from datetime import datetime

class LogMonitor:
    def __init__(self):
        self.log_dir = Path("E:/Projects/agent_logs")
        self.log_dir.mkdir(exist_ok=True)
        
    def tail_log_file(self, log_file, lines=20):
        """Get last N lines from a log file"""
        try:
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except FileNotFoundError:
            return [f"Log file not found: {log_file}\n"]
        except Exception as e:
            return [f"Error reading log: {e}\n"]
    
    def get_agent_status(self):
        """Get current status of all agents"""
        status_files = list(self.log_dir.glob("*_status.json"))
        statuses = []
        
        for status_file in status_files:
            try:
                with open(status_file, 'r') as f:
                    status = json.load(f)
                    statuses.append(status)
            except Exception as e:
                statuses.append({
                    "agent": status_file.stem.replace('_status', ''),
                    "status": "error",
                    "error": str(e)
                })
        
        return statuses
    
    def display_dashboard(self):
        """Display a simple text dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print(f"🤖 AGENT MONITORING DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Show agent statuses
        print("\n📊 AGENT STATUS:")
        statuses = self.get_agent_status()
        if statuses:
            for status in statuses:
                status_emoji = {
                    "starting": "🟡",
                    "monitoring": "🟢", 
                    "testing_endpoints": "🔍",
                    "checking_docker": "🐳",
                    "running_copilot_tests": "🤖",
                    "completed": "✅",
                    "error": "❌",
                    "stopped": "⏹️"
                }.get(status['status'], "❓")
                
                print(f"  {status_emoji} {status['agent']}: {status['status']}")
                if 'timestamp' in status:
                    print(f"    Last update: {status['timestamp']}")
        else:
            print("  No agents found")
        
        # Show latest log entries
        print(f"\n📝 LATEST LOG ENTRIES:")
        latest_log = self.log_dir / "latest.log"
        if latest_log.exists():
            recent_lines = self.tail_log_file(latest_log, 10)
            for line in recent_lines:
                print(f"  {line.rstrip()}")
        else:
            print("  No recent logs found")
        
        # Show available log files
        print(f"\n📁 AVAILABLE LOGS:")
        log_files = list(self.log_dir.glob("*.log"))
        for log_file in sorted(log_files):
            size = log_file.stat().st_size if log_file.exists() else 0
            print(f"  📄 {log_file.name} ({size} bytes)")
        
        # Show recent test results
        print(f"\n🧪 RECENT TEST RESULTS:")
        result_files = sorted(list(self.log_dir.glob("test_results_*.json")), reverse=True)
        if result_files:
            latest_result = result_files[0]
            try:
                with open(latest_result, 'r') as f:
                    results = json.load(f)
                    success_count = sum(1 for r in results if r.get('status') == 'success')
                    total_count = len(results)
                    print(f"  📊 Latest: {success_count}/{total_count} services passing")
                    print(f"  📅 File: {latest_result.name}")
            except Exception as e:
                print(f"  ❌ Error reading results: {e}")
        else:
            print("  No test results found")
        
        print("\n" + "=" * 80)
        print("Press Ctrl+C to exit | Refreshes every 5 seconds")
        print("=" * 80)
    
    def monitor_continuously(self):
        """Monitor logs in real-time"""
        print("🔄 Starting real-time log monitoring...")
        
        try:
            while True:
                self.display_dashboard()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped")
    
    def show_full_log(self, agent_name):
        """Show full log for a specific agent"""
        log_file = self.log_dir / f"{agent_name}.log"
        
        if not log_file.exists():
            print(f"❌ Log file not found: {log_file}")
            return
        
        print(f"📄 Full log for {agent_name}:")
        print("=" * 60)
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    print(line.rstrip())
        except Exception as e:
            print(f"❌ Error reading log: {e}")

def main():
    import sys
    
    monitor = LogMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'show' and len(sys.argv) > 2:
            # Show specific agent log
            monitor.show_full_log(sys.argv[2])
        else:
            print("Usage:")
            print("  python log-monitor.py          # Real-time monitoring")
            print("  python log-monitor.py show AGENT_NAME  # Show full log")
    else:
        # Real-time monitoring
        monitor.monitor_continuously()

if __name__ == "__main__":
    main()
