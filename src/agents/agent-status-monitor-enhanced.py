#!/usr/bin/env python3
"""
Enhanced Agent Status Monitor
Monitors all agent progress and identifies stuck/blocked agents
Prepares for GitHub Issues transition for SDLC task management
"""

import json
import time
import requests
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import psutil
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AgentMonitor')

class AgentStatusMonitor:
    def __init__(self):
        self.status_file = "agent_status_tracker.json"
        self.work_queue_dir = Path("work_queue")
        self.communication_dir = Path("communication_messages")
        self.agents = {}
        self.stuck_threshold = 300  # 5 minutes without progress
        self.github_transition_ready = False
        
    def load_agent_status(self) -> Dict[str, Any]:
        """Load current agent status from tracker"""
        try:
            if Path(self.status_file).exists():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load agent status: {e}")
            return {}
    
    def check_agent_progress(self) -> Dict[str, Any]:
        """Check progress of all assigned agents"""
        status = self.load_agent_status()
        current_time = datetime.now()
        
        agent_progress = {
            "total_agents": status.get("total_agents", 0),
            "agents": {},
            "stuck_agents": [],
            "critical_issues": [],
            "overall_health": "unknown"
        }
        
        if "agent_status" in status:
            for agent_name, agent_data in status["agent_status"].items():
                # Check last activity
                last_updated = status.get("last_updated", "")
                if last_updated:
                    try:
                        last_update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00').replace('+00:00', ''))
                        time_diff = (current_time - last_update_time).total_seconds()
                        
                        agent_progress["agents"][agent_name] = {
                            "status": agent_data.get("status", "unknown"),
                            "priority": agent_data.get("priority", "unknown"),
                            "progress": agent_data.get("progress", 0),
                            "tasks_completed": agent_data.get("tasks_completed", 0),
                            "tasks_total": agent_data.get("tasks_total", 0),
                            "estimated_effort": agent_data.get("estimated_effort", "unknown"),
                            "minutes_since_update": int(time_diff / 60),
                            "is_stuck": time_diff > self.stuck_threshold,
                            "blocking_issue": agent_data.get("blocking_issue", False)
                        }
                        
                        # Flag stuck agents
                        if time_diff > self.stuck_threshold:
                            agent_progress["stuck_agents"].append(agent_name)
                            
                        # Flag critical issues
                        if agent_data.get("priority", "").startswith("P0"):
                            agent_progress["critical_issues"].append({
                                "agent": agent_name,
                                "priority": agent_data.get("priority"),
                                "blocking": agent_data.get("blocking_issue", False)
                            })
                            
                    except Exception as e:
                        logger.error(f"Error parsing time for {agent_name}: {e}")
        
        # Determine overall health
        if len(agent_progress["stuck_agents"]) > 0:
            agent_progress["overall_health"] = "degraded"
        elif len(agent_progress["critical_issues"]) > 2:
            agent_progress["overall_health"] = "warning"
        else:
            agent_progress["overall_health"] = "healthy"
            
        return agent_progress
    
    def check_dashboard_health(self) -> Dict[str, Any]:
        """Check if dashboard is responding properly"""
        dashboard_status = {
            "running": False,
            "responding": False,
            "tabs_working": False,
            "websocket_active": False,
            "url": "http://localhost:5003"
        }
        
        try:
            # Check if dashboard is running
            response = requests.get("http://localhost:5003", timeout=5)
            if response.status_code == 200:
                dashboard_status["running"] = True
                dashboard_status["responding"] = True
                
                # Check if it contains expected content
                content = response.text
                if "GitHub Integration" in content and "Work Queue" in content:
                    dashboard_status["tabs_working"] = True
                    
        except Exception as e:
            logger.warning(f"Dashboard health check failed: {e}")
            
        return dashboard_status
    
    def check_work_queues(self) -> Dict[str, Any]:
        """Check work queue status"""
        queue_status = {
            "total_items": 0,
            "critical_items": 0,
            "assigned_items": 0,
            "stuck_items": 0,
            "items": []
        }
        
        if self.work_queue_dir.exists():
            for queue_file in self.work_queue_dir.glob("*.json"):
                try:
                    with open(queue_file, 'r') as f:
                        item = json.load(f)
                        
                    queue_status["total_items"] += 1
                    
                    if item.get("priority", "").startswith("P0"):
                        queue_status["critical_items"] += 1
                        
                    if item.get("assigned_to"):
                        queue_status["assigned_items"] += 1
                        
                    queue_status["items"].append({
                        "file": queue_file.name,
                        "title": item.get("title", "Unknown"),
                        "priority": item.get("priority", "Unknown"),
                        "assigned_to": item.get("assigned_to", "Unassigned"),
                        "status": item.get("status", "Unknown")
                    })
                    
                except Exception as e:
                    logger.error(f"Error reading queue file {queue_file}: {e}")
                    
        return queue_status
    
    def check_github_integration_readiness(self) -> Dict[str, Any]:
        """Check if system is ready for GitHub Issues transition"""
        readiness = {
            "github_agent_exists": False,
            "github_agent_functional": False,
            "api_service_ready": False,
            "webhook_configured": False,
            "work_queue_supports_github": False,
            "dashboard_github_tab": False,
            "ready_for_transition": False,
            "recommendations": []
        }
        
        # Check if GitHub agent exists
        github_agent_file = Path("github-issues-agent.py")
        if github_agent_file.exists():
            readiness["github_agent_exists"] = True
            
            # Basic functionality check
            try:
                with open(github_agent_file, 'r') as f:
                    content = f.read()
                    if "GitHubIssuesAgent" in content and "monitor_issues" in content:
                        readiness["github_agent_functional"] = True
            except Exception as e:
                logger.error(f"Error checking GitHub agent: {e}")
        
        # Check work queue manager
        work_queue_file = Path("work-queue-manager.py")
        if work_queue_file.exists():
            try:
                with open(work_queue_file, 'r') as f:
                    content = f.read()
                    if "GITHUB_ISSUE" in content and "github_issue_id" in content:
                        readiness["work_queue_supports_github"] = True
            except Exception as e:
                logger.error(f"Error checking work queue: {e}")
        
        # Check dashboard
        dashboard_file = Path("comprehensive-tabbed-dashboard.py")
        if dashboard_file.exists():
            try:
                with open(dashboard_file, 'r') as f:
                    content = f.read()
                    if "GitHub Integration" in content:
                        readiness["dashboard_github_tab"] = True
            except Exception as e:
                logger.error(f"Error checking dashboard: {e}")
        
        # Determine overall readiness
        if (readiness["github_agent_exists"] and 
            readiness["work_queue_supports_github"] and 
            readiness["dashboard_github_tab"]):
            readiness["ready_for_transition"] = True
        
        # Generate recommendations
        if not readiness["github_agent_functional"]:
            readiness["recommendations"].append("Complete GitHub agent implementation")
        if not readiness["api_service_ready"]:
            readiness["recommendations"].append("Configure GitHub API authentication")
        if not readiness["webhook_configured"]:
            readiness["recommendations"].append("Setup GitHub webhooks for real-time monitoring")
            
        return readiness
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        logger.info("Generating comprehensive agent status report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "agent_progress": self.check_agent_progress(),
            "dashboard_health": self.check_dashboard_health(),
            "work_queue_status": self.check_work_queues(),
            "github_readiness": self.check_github_integration_readiness(),
            "recommendations": [],
            "next_actions": []
        }
        
        # Generate recommendations based on status
        agent_progress = report["agent_progress"]
        dashboard_health = report["dashboard_health"]
        github_readiness = report["github_readiness"]
        
        if len(agent_progress["stuck_agents"]) > 0:
            report["recommendations"].append(f"URGENT: Check stuck agents: {', '.join(agent_progress['stuck_agents'])}")
            
        if not dashboard_health["responding"]:
            report["recommendations"].append("CRITICAL: Dashboard is not responding - restart comprehensive-tabbed-dashboard.py")
            
        if not dashboard_health["tabs_working"]:
            report["recommendations"].append("HIGH: Dashboard tabs may not be working - check JavaScript errors")
            
        if github_readiness["ready_for_transition"]:
            report["recommendations"].append("READY: System ready for GitHub Issues transition")
            report["next_actions"].append("Create GitHub Issues agent assignment")
            report["next_actions"].append("Configure GitHub API authentication")
            report["next_actions"].append("Migrate current tasks to GitHub Issues")
        
        return report
    
    def save_report(self, report: Dict[str, Any]):
        """Save status report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"agent_status_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Status report saved to {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    def print_summary(self, report: Dict[str, Any]):
        """Print human-readable summary"""
        print("\n" + "="*80)
        print("🔍 AGENT STATUS MONITOR - COMPREHENSIVE REPORT")
        print("="*80)
        
        # Agent Progress
        agent_progress = report["agent_progress"]
        print(f"\n📊 AGENT PROGRESS:")
        print(f"   • Total Agents: {agent_progress['total_agents']}")
        print(f"   • Overall Health: {agent_progress['overall_health'].upper()}")
        print(f"   • Stuck Agents: {len(agent_progress['stuck_agents'])}")
        print(f"   • Critical Issues: {len(agent_progress['critical_issues'])}")
        
        if agent_progress["stuck_agents"]:
            print(f"   • ⚠️  STUCK: {', '.join(agent_progress['stuck_agents'])}")
        
        # Dashboard Health
        dashboard = report["dashboard_health"]
        print(f"\n🖥️  DASHBOARD HEALTH:")
        print(f"   • Running: {'✅' if dashboard['running'] else '❌'}")
        print(f"   • Responding: {'✅' if dashboard['responding'] else '❌'}")
        print(f"   • Tabs Working: {'✅' if dashboard['tabs_working'] else '❌'}")
        print(f"   • URL: {dashboard['url']}")
        
        # Work Queue
        queue = report["work_queue_status"]
        print(f"\n📋 WORK QUEUE:")
        print(f"   • Total Items: {queue['total_items']}")
        print(f"   • Critical Items: {queue['critical_items']}")
        print(f"   • Assigned Items: {queue['assigned_items']}")
        
        # GitHub Readiness
        github = report["github_readiness"]
        print(f"\n🐙 GITHUB INTEGRATION READINESS:")
        print(f"   • Agent Exists: {'✅' if github['github_agent_exists'] else '❌'}")
        print(f"   • Agent Functional: {'✅' if github['github_agent_functional'] else '❌'}")
        print(f"   • Work Queue Ready: {'✅' if github['work_queue_supports_github'] else '❌'}")
        print(f"   • Dashboard Ready: {'✅' if github['dashboard_github_tab'] else '❌'}")
        print(f"   • Overall Ready: {'✅' if github['ready_for_transition'] else '❌'}")
        
        # Recommendations
        if report["recommendations"]:
            print(f"\n⚡ RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        # Next Actions
        if report["next_actions"]:
            print(f"\n🎯 NEXT ACTIONS:")
            for i, action in enumerate(report["next_actions"], 1):
                print(f"   {i}. {action}")
        
        print("\n" + "="*80)

def main():
    """Main monitoring function"""
    monitor = AgentStatusMonitor()
    
    # Generate comprehensive report
    report = monitor.generate_status_report()
    
    # Save report
    monitor.save_report(report)
    
    # Print summary
    monitor.print_summary(report)
    
    # Check if we should recommend GitHub transition
    if report["github_readiness"]["ready_for_transition"]:
        print("\n🚀 GITHUB TRANSITION RECOMMENDATION:")
        print("   System is ready to transition from file-based to GitHub Issues task management!")
        print("   Next steps:")
        print("   1. Complete current critical tasks (dashboard fix)")
        print("   2. Assign GitHub integration agent")
        print("   3. Configure GitHub API authentication")
        print("   4. Migrate existing tasks to GitHub Issues")
        print("   5. Setup real-time GitHub webhooks")

if __name__ == "__main__":
    main()
