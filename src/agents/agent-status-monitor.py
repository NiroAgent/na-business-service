#!/usr/bin/env python3
"""
Agent Status Monitor - Simple script to check agent status and generate reports
"""

import json
import subprocess
import time
import psutil
from pathlib import Path
from datetime import datetime
import requests

def check_agent_processes():
    """Check what agent processes are running"""
    running_agents = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            
            # Check for our agent scripts
            if any(script in cmdline for script in [
                'gh-copilot-orchestrator.py',
                'local-orchestrator.py', 
                'run-gh-copilot-tests.py',
                'simple-agent-dashboard.py'
            ]):
                script_name = None
                for script in ['gh-copilot-orchestrator.py', 'local-orchestrator.py', 
                              'run-gh-copilot-tests.py', 'simple-agent-dashboard.py']:
                    if script in cmdline:
                        script_name = script
                        break
                
                running_agents.append({
                    'script': script_name,
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'started': datetime.fromtimestamp(proc.create_time()).isoformat()
                })
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return running_agents

def check_dashboard_health():
    """Check if dashboard is responding"""
    try:
        response = requests.get('http://localhost:5000/api/system/metrics', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_github_issues():
    """Check recent GitHub issues created by agents"""
    try:
        # Try to get issues using gh CLI
        result = subprocess.run([
            'gh', 'issue', 'list', 
            '--label', 'agent-finding',
            '--limit', '10',
            '--json', 'title,url,createdAt,labels'
        ], capture_output=True, text=True, cwd='E:/Projects')
        
        if result.returncode == 0:
            return json.loads(result.stdout)
    except:
        pass
    
    return []

def get_system_metrics():
    """Get current system metrics"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('E:').percent,
        'timestamp': datetime.now().isoformat()
    }

def check_recent_results():
    """Check for recent orchestration results"""
    projects_dir = Path('E:/Projects')
    results_dir = projects_dir / 'orchestration_results'
    
    recent_results = []
    if results_dir.exists():
        # Get files from last 24 hours
        cutoff = time.time() - (24 * 60 * 60)  # 24 hours ago
        
        for result_file in results_dir.glob('*.json'):
            if result_file.stat().st_mtime > cutoff:
                try:
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                        recent_results.append({
                            'file': result_file.name,
                            'service': data.get('service', 'unknown'),
                            'timestamp': data.get('timestamp', ''),
                            'tests_count': len(data.get('tests', []))
                        })
                except:
                    pass
    
    return recent_results

def generate_status_report():
    """Generate comprehensive status report"""
    
    print("🔍 AGENT STATUS REPORT")
    print("=" * 50)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check running processes
    print("🤖 RUNNING AGENTS:")
    running_agents = check_agent_processes()
    if running_agents:
        for agent in running_agents:
            print(f"   ✅ {agent['script']} (PID: {agent['pid']})")
            print(f"      Started: {agent['started']}")
    else:
        print("   ❌ No agents currently running")
    print()
    
    # Check dashboard
    print("📊 DASHBOARD STATUS:")
    if check_dashboard_health():
        print("   ✅ Dashboard responding at http://localhost:5000")
    else:
        print("   ❌ Dashboard not responding")
    print()
    
    # System metrics
    print("💻 SYSTEM METRICS:")
    metrics = get_system_metrics()
    print(f"   CPU: {metrics['cpu_percent']:.1f}%")
    print(f"   Memory: {metrics['memory_percent']:.1f}%") 
    print(f"   Disk: {metrics['disk_percent']:.1f}%")
    print()
    
    # Recent results
    print("📁 RECENT RESULTS (24h):")
    recent_results = check_recent_results()
    if recent_results:
        for result in recent_results[-5:]:  # Show last 5
            print(f"   📄 {result['service']} - {result['tests_count']} tests")
            print(f"      File: {result['file']}")
    else:
        print("   📄 No recent results found")
    print()
    
    # GitHub issues
    print("🐛 RECENT GITHUB ISSUES:")
    issues = check_github_issues()
    if issues:
        for issue in issues[:5]:  # Show first 5
            print(f"   🔗 {issue['title']}")
            print(f"      Created: {issue['createdAt']}")
            print(f"      URL: {issue['url']}")
    else:
        print("   📝 No recent agent issues found")
    print()
    
    # Summary
    print("📋 SUMMARY:")
    print(f"   Agents running: {len(running_agents)}")
    print(f"   Dashboard: {'✅' if check_dashboard_health() else '❌'}")
    print(f"   Recent results: {len(recent_results)}")
    print(f"   System load: {metrics['cpu_percent']:.1f}% CPU, {metrics['memory_percent']:.1f}% RAM")
    print()
    
    # Save report
    report_file = Path(f"E:/Projects/agent_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_file, 'w') as f:
        # Redirect stdout to file temporarily
        import sys
        old_stdout = sys.stdout
        sys.stdout = f
        generate_status_report()
        sys.stdout = old_stdout
    
    print(f"💾 Report saved to: {report_file}")

def monitor_continuously():
    """Monitor agents continuously"""
    print("🔄 Starting continuous monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Checking agents...")
            
            running_agents = check_agent_processes()
            dashboard_ok = check_dashboard_health()
            metrics = get_system_metrics()
            
            print(f"   Agents: {len(running_agents)} running")
            print(f"   Dashboard: {'✅' if dashboard_ok else '❌'}")
            print(f"   System: {metrics['cpu_percent']:.1f}% CPU, {metrics['memory_percent']:.1f}% RAM")
            
            # Alert if high resource usage
            if metrics['cpu_percent'] > 80:
                print("   ⚠️  HIGH CPU USAGE!")
            if metrics['memory_percent'] > 80:
                print("   ⚠️  HIGH MEMORY USAGE!")
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        monitor_continuously()
    else:
        generate_status_report()
