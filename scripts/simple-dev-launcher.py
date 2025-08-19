#!/usr/bin/env python3
"""
Simple Dev Agent Launcher
Easy way to start dev agents with cost monitoring
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚀 DEV AGENT LAUNCHER WITH COST PROTECTION")
    print("=" * 60)
    print("Starting dev environment agents with AWS cost monitoring...")
    print()

def start_cost_monitor():
    """Start basic cost monitoring in background"""
    print("🛡️ Starting AWS cost monitor...")
    try:
        subprocess.Popen([
            'E:/Projects/.venv/Scripts/python.exe',
            'E:/Projects/aws-cost-monitor.py',
            '--threshold', '3.0',  # More lenient for dev
            '--window', '30'       # 30 minute window
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Cost monitor started (3% threshold, 30min window)")
    except Exception as e:
        print(f"⚠️ Cost monitor failed to start: {e}")
        print("Continuing without cost monitoring...")
    print()

def start_basic_monitoring_agent():
    """Start the basic monitoring agent for dev"""
    print("🔍 Starting dev service monitor...")
    try:
        # Set environment variables for dev
        env = os.environ.copy()
        env['AGENT_ENVIRONMENT'] = 'dev'
        env['AGENT_NAME'] = 'dev-monitor'
        
        process = subprocess.Popen([
            'E:/Projects/.venv/Scripts/python.exe',
            'E:/Projects/monitorable-agent.py',
            '--single'  # Single run mode to test
        ], env=env)
        
        print(f"✅ Dev monitor started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start dev monitor: {e}")
        return None

def start_log_monitor():
    """Start simple log monitoring"""
    print("📊 Starting log monitor...")
    try:
        process = subprocess.Popen([
            'E:/Projects/.venv/Scripts/python.exe',
            'E:/Projects/log-monitor.py'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"✅ Log monitor started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start log monitor: {e}")
        return None

def monitor_processes(processes):
    """Monitor process health"""
    print("\n🔄 Monitoring agent health...")
    print("Press Ctrl+C to stop all agents")
    
    try:
        while True:
            alive_count = 0
            for name, proc in processes.items():
                if proc and proc.poll() is None:
                    alive_count += 1
                elif proc:
                    print(f"⚠️ {name} stopped (exit code: {proc.returncode})")
                    
            if alive_count == 0:
                print("❌ All agents have stopped")
                break
                
            print(f"✅ {alive_count}/{len([p for p in processes.values() if p])} agents running")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all agents...")
        for name, proc in processes.items():
            if proc and proc.poll() is None:
                proc.terminate()
                print(f"✅ Stopped {name}")
        print("👋 All agents stopped")

def main():
    print_banner()
    
    # Start cost monitoring first
    start_cost_monitor()
    
    # Start agents
    processes = {}
    
    # Start basic monitoring
    processes['dev-monitor'] = start_basic_monitoring_agent()
    time.sleep(3)
    
    # Start log monitor
    processes['log-monitor'] = start_log_monitor()
    time.sleep(2)
    
    # Show status
    running_agents = [name for name, proc in processes.items() if proc and proc.poll() is None]
    
    if running_agents:
        print(f"\n🎉 Successfully started: {', '.join(running_agents)}")
        print("\n📋 CURRENT SETUP:")
        print("   🛡️ AWS Cost Monitor: Running (3% threshold)")
        print("   🔍 Dev Service Monitor: Testing endpoints")
        print("   📊 Log Monitor: Real-time log viewing")
        print("\n💡 To view logs: python log-monitor.py")
        print("💡 To check status: python dev-focused-orchestrator.py --status")
        
        # Monitor processes
        monitor_processes(processes)
    else:
        print("❌ No agents started successfully")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if Python virtual environment is active")
        print("2. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("3. Check AWS credentials: aws configure")
        print("4. Try running individual agents manually")

if __name__ == "__main__":
    main()
