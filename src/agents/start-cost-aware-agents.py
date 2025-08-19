#!/usr/bin/env python3
"""
Quick Start for Cost-Aware Agent Orchestration
Launches all agents with AWS cost monitoring protection
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            print("WARNING: No AWS credentials found!")
            print("Please configure AWS credentials using:")
            print("  aws configure")
            print("  or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
            return False
        print("AWS credentials found ✓")
        return True
    except ImportError:
        print("ERROR: boto3 not installed. Run: pip install boto3")
        return False
    except Exception as e:
        print(f"AWS credential check failed: {e}")
        return False

def create_default_config():
    """Create default configuration if none exists"""
    config_file = Path("E:/Projects/aws-cost-config.json")
    template_file = Path("E:/Projects/aws-cost-config.template.json")
    
    if not config_file.exists() and template_file.exists():
        print("Creating default cost monitoring configuration...")
        template_file.replace(config_file)
        print(f"Created: {config_file}")
        print("Edit this file to customize cost monitoring settings")
        return True
    return config_file.exists()

def kill_existing_agents():
    """Kill any existing agent processes"""
    import psutil
    
    agent_scripts = [
        "monitorable-agent.py",
        "gh-copilot-orchestrator.py", 
        "local-orchestrator.py",
        "cost-aware-orchestrator.py",
        "aws-cost-monitor.py"
    ]
    
    killed = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                for script in agent_scripts:
                    if script in cmdline:
                        proc.kill()
                        killed.append(f"{script} (PID: {proc.info['pid']})")
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if killed:
        print("Stopped existing agents:")
        for item in killed:
            print(f"  - {item}")
        time.sleep(2)

def start_cost_aware_orchestrator():
    """Start the cost-aware orchestrator"""
    print("\n" + "="*60)
    print("🚀 STARTING COST-AWARE AGENT ORCHESTRATION")
    print("="*60)
    print("💰 Cost monitoring: ENABLED (1% threshold in 60 minutes)")
    print("🛡️  Emergency shutdown: ENABLED")
    print("📊 Real-time monitoring: ENABLED")
    print("="*60)
    
    cmd = [
        'E:/Projects/.venv/Scripts/python.exe',
        'E:/Projects/cost-aware-orchestrator.py'
    ]
    
    try:
        process = subprocess.Popen(cmd, cwd='E:/Projects')
        print(f"Cost-aware orchestrator started (PID: {process.pid})")
        print("\nPress Ctrl+C to stop all agents")
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down orchestrator...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"Error starting orchestrator: {e}")

def show_status():
    """Show current agent and cost monitor status"""
    try:
        result = subprocess.run([
            'E:/Projects/.venv/Scripts/python.exe',
            'E:/Projects/cost-aware-orchestrator.py',
            '--status'
        ], capture_output=True, text=True, cwd='E:/Projects')
        
        if result.returncode == 0:
            status = json.loads(result.stdout)
            print("\nCURRENT STATUS:")
            print(json.dumps(status, indent=2))
        else:
            print("No orchestrator currently running")
            
    except Exception as e:
        print(f"Error getting status: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Cost-Aware Agent Quick Start')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--kill', action='store_true', help='Kill existing agents')
    parser.add_argument('--no-aws-check', action='store_true', help='Skip AWS credential check')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
        
    if args.kill:
        kill_existing_agents()
        print("All agents stopped")
        return
    
    print("Cost-Aware Agent Orchestration Quick Start")
    print("==========================================")
    
    # Check prerequisites
    if not args.no_aws_check:
        if not check_aws_credentials():
            print("\nContinuing without AWS cost monitoring...")
            print("Cost monitoring will be disabled")
    
    # Create config if needed
    if not create_default_config():
        print("ERROR: Could not create configuration file")
        return
    
    # Clean up existing processes
    kill_existing_agents()
    
    # Start orchestrator
    start_cost_aware_orchestrator()

if __name__ == "__main__":
    main()
