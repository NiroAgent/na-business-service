#!/usr/bin/env python3
"""
Service Progress Monitor - Track VisualForge and NiroSubs development
Ensures agents continue making progress while Claude Opus works on VF integration
"""

import requests
import json
import time
from datetime import datetime
import subprocess

class ServiceProgressMonitor:
    def __init__(self):
        self.services = {
            'vf-audio-service': {
                'status': 'active',
                'last_update': None,
                'progress_indicators': []
            },
            'vf-video-service': {
                'status': 'active', 
                'last_update': None,
                'progress_indicators': []
            },
            'ns-auth': {
                'status': 'active',
                'last_update': None,
                'progress_indicators': []
            },
            'ns-dashboard': {
                'status': 'active',
                'last_update': None,
                'progress_indicators': []
            }
        }
        
    def check_service_progress(self):
        """Check each service for development progress"""
        progress_report = {
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        for service_name, service_info in self.services.items():
            # Check git commits in service repositories
            git_progress = self.check_git_activity(service_name)
            
            # Check for new files or changes
            file_changes = self.check_file_changes(service_name)
            
            # Check running processes
            process_status = self.check_process_status(service_name)
            
            progress_report['services'][service_name] = {
                'git_activity': git_progress,
                'file_changes': file_changes,
                'process_status': process_status,
                'overall_status': 'progressing' if git_progress or file_changes else 'stable'
            }
            
        return progress_report
        
    def check_git_activity(self, service_name):
        """Check for recent git commits in service repositories"""
        try:
            # Check VisualForge repos
            if service_name.startswith('vf-'):
                repo_path = f"VisualForgeMediaV2/{service_name}"
                if self.path_exists(repo_path):
                    result = subprocess.run([
                        'git', 'log', '--oneline', '--since=1 hour ago'
                    ], cwd=repo_path, capture_output=True, text=True)
                    return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                    
            # Check NiroSubs repos  
            elif service_name.startswith('ns-'):
                repo_path = f"NiroSubs-V2/{service_name}"
                if self.path_exists(repo_path):
                    result = subprocess.run([
                        'git', 'log', '--oneline', '--since=1 hour ago'
                    ], cwd=repo_path, capture_output=True, text=True)
                    return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                    
        except Exception as e:
            print(f"Git check failed for {service_name}: {e}")
            
        return 0
        
    def check_file_changes(self, service_name):
        """Check for recent file modifications"""
        try:
            # Use find to check for files modified in last hour
            result = subprocess.run([
                'find', '.', '-name', f"*{service_name}*", '-mmin', '-60', '-type', 'f'
            ], capture_output=True, text=True)
            
            files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return len([f for f in files if f and not f.endswith('.log')])
            
        except Exception as e:
            print(f"File check failed for {service_name}: {e}")
            return 0
            
    def check_process_status(self, service_name):
        """Check if service processes are running"""
        try:
            result = subprocess.run([
                'ps', 'aux'
            ], capture_output=True, text=True)
            
            processes = [line for line in result.stdout.split('\n') 
                        if service_name in line and 'python' in line]
            return len(processes)
            
        except Exception as e:
            print(f"Process check failed for {service_name}: {e}")
            return 0
            
    def path_exists(self, path):
        """Check if path exists"""
        import os
        return os.path.exists(path)
        
    def generate_progress_report(self):
        """Generate comprehensive progress report"""
        progress = self.check_service_progress()
        
        print("🔍 SERVICE PROGRESS REPORT")
        print("=" * 50)
        print(f"Timestamp: {progress['timestamp']}")
        print()
        
        for service, data in progress['services'].items():
            status_emoji = "🟢" if data['overall_status'] == 'progressing' else "🟡"
            print(f"{status_emoji} {service}")
            print(f"  Git Activity: {data['git_activity']} commits")
            print(f"  File Changes: {data['file_changes']} files")
            print(f"  Processes: {data['process_status']} running")
            print(f"  Status: {data['overall_status']}")
            print()
            
        # Save report
        with open('logs/service_progress_report.json', 'w') as f:
            json.dump(progress, f, indent=2)
            
        return progress
        
    def ensure_agents_active(self):
        """Ensure monitoring agents are still running"""
        try:
            # Check if our optimization is working
            with open('logs/agent-reports/monitoring_summary.json', 'r') as f:
                summary = json.load(f)
                
            active_services = [name for name, status in summary['services'].items() 
                             if '✅' in status]
            
            print(f"✅ {len(active_services)} services actively monitored")
            
            if len(active_services) < 4:
                print("⚠️  Some services may need attention")
                
        except Exception as e:
            print(f"Monitoring check failed: {e}")

def main():
    print("🚀 Starting Service Progress Monitor...")
    monitor = ServiceProgressMonitor()
    
    print("📊 Generating progress report...")
    monitor.generate_progress_report()
    
    print("🔍 Checking agent monitoring...")
    monitor.ensure_agents_active()
    
    print("✅ Service monitoring complete!")

if __name__ == "__main__":
    main()
