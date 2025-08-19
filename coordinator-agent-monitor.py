#!/usr/bin/env python3
"""
Coordinator Agent Monitor
Monitors all AI agents across all services and organizations
As the coordinator, I oversee all agent operations
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import os

class CoordinatorAgentMonitor:
    """Master coordinator monitoring all agents"""
    
    def __init__(self):
        self.organizations = [
            "VisualForgeMediaV2",
            "NiroSubs-V2", 
            "BulkMediaGenerator",
            "VisualForgeAI-Archive",
            "NeroLabsLLC",
            "NiroAgentV1"
        ]
        
        self.services = {
            "VisualForgeMediaV2": [
                "vf-agent-service",
                "vf-text-service",
                "business-operations",
                "vf-audio", "vf-video", "vf-image", "vf-bulk"
            ],
            "NiroSubs-V2": [
                "ns-auth", "ns-dashboard", "ns-payments", "ns-user", "ns-shell"
            ]
        }
        
        self.ai_agents = [
            # Development Pipeline (5 agents)
            "ai-architect-agent",
            "ai-developer-agent", 
            "ai-qa-agent",
            "ai-devops-agent",
            "ai-manager-agent",
            
            # Business Operations (9 agents)
            "ai-project-manager-agent",
            "ai-marketing-agent",
            "ai-sales-agent",
            "ai-support-agent",
            "ai-customer-success-agent",
            "ai-analytics-agent",
            "ai-finance-agent",
            "ai-operations-agent",
            "ai-security-agent"
        ]
        
        self.agent_status = {}
        self.service_health = {}
        self.issue_queue = {}
        
    def check_github_issues(self, org, repo=None):
        """Check GitHub issues for agent tasks"""
        issues = []
        
        if repo:
            repos = [f"{org}/{repo}"]
        else:
            repos = [f"{org}/{service}" for service in self.services.get(org, [])]
            if org == "VisualForgeMediaV2":
                repos.append(f"{org}/business-operations")
        
        for repo_path in repos:
            try:
                cmd = [
                    "gh", "issue", "list",
                    "--repo", repo_path,
                    "--state", "open",
                    "--json", "number,title,labels,assignees,createdAt",
                    "--limit", "50"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout:
                    repo_issues = json.loads(result.stdout)
                    for issue in repo_issues:
                        issue['repository'] = repo_path
                    issues.extend(repo_issues)
            except Exception as e:
                print(f"[WARNING] Could not check {repo_path}: {e}")
        
        return issues
    
    def analyze_agent_workload(self, issues):
        """Analyze workload distribution across agents"""
        workload = {}
        
        for issue in issues:
            labels = [label['name'] for label in issue.get('labels', [])]
            
            # Determine assigned agent based on labels
            assigned_agent = None
            for label in labels:
                if "operations/monitoring" in label:
                    assigned_agent = "ai-operations-agent"
                elif "security/" in label:
                    assigned_agent = "ai-security-agent"
                elif "analytics/" in label:
                    assigned_agent = "ai-analytics-agent"
                elif "support/" in label:
                    assigned_agent = "ai-support-agent"
                elif "marketing/" in label:
                    assigned_agent = "ai-marketing-agent"
                elif "sales/" in label:
                    assigned_agent = "ai-sales-agent"
                elif "finance/" in label:
                    assigned_agent = "ai-finance-agent"
                elif "agent-task" in label:
                    assigned_agent = "ai-developer-agent"
            
            if assigned_agent:
                if assigned_agent not in workload:
                    workload[assigned_agent] = []
                workload[assigned_agent].append({
                    'issue': issue['number'],
                    'title': issue['title'],
                    'repo': issue['repository'],
                    'created': issue['createdAt']
                })
        
        return workload
    
    def check_service_health(self):
        """Check health of all services"""
        health_status = {}
        
        # Check local services
        local_services = [
            ("Emergency Dashboard", "http://localhost:5003/health"),
            ("Claude Service", "http://localhost:3003/health"),
            ("VF Agent Service", "http://localhost:3001/health"),
            ("VF Text Service", "http://localhost:4004/health"),
            ("Visual Forge AI", "http://localhost:5006/health"),
            ("PM Workflow", "http://localhost:5005/health")
        ]
        
        for service_name, url in local_services:
            try:
                import urllib.request
                response = urllib.request.urlopen(url, timeout=2)
                if response.status == 200:
                    health_status[service_name] = "HEALTHY"
                else:
                    health_status[service_name] = "UNHEALTHY"
            except:
                health_status[service_name] = "OFFLINE"
        
        return health_status
    
    def generate_coordinator_report(self):
        """Generate comprehensive coordinator report"""
        print("\n" + "="*80)
        print("COORDINATOR AGENT MONITORING REPORT")
        print("="*80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Role: Master Coordinator")
        print(f"Monitoring: {len(self.ai_agents)} AI Agents across {len(self.organizations)} Organizations")
        
        # Check service health
        print("\n[SERVICE HEALTH STATUS]")
        health = self.check_service_health()
        for service, status in health.items():
            status_icon = "[OK]" if status == "HEALTHY" else "[X]" if status == "OFFLINE" else "[!]"
            print(f"  {status_icon} {service}: {status}")
        
        # Check GitHub issues across all organizations
        print("\n[GITHUB ISSUE ANALYSIS]")
        total_issues = 0
        all_issues = []
        
        for org in self.organizations:
            org_issues = self.check_github_issues(org)
            if org_issues:
                print(f"\n  {org}:")
                print(f"    Open Issues: {len(org_issues)}")
                total_issues += len(org_issues)
                all_issues.extend(org_issues)
        
        # Analyze agent workload
        print("\n[AGENT WORKLOAD DISTRIBUTION]")
        workload = self.analyze_agent_workload(all_issues)
        
        for agent in self.ai_agents:
            tasks = workload.get(agent, [])
            status = "IDLE" if not tasks else f"ACTIVE ({len(tasks)} tasks)"
            print(f"  {agent}: {status}")
            if tasks:
                for task in tasks[:3]:  # Show first 3 tasks
                    print(f"    - Issue #{task['issue']}: {task['title'][:50]}...")
        
        # Priority analysis
        print("\n[PRIORITY ANALYSIS]")
        priority_count = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
        for issue in all_issues:
            labels = [label['name'] for label in issue.get('labels', [])]
            for label in labels:
                for priority in priority_count.keys():
                    if f"priority/{priority}" in label:
                        priority_count[priority] += 1
                        break
        
        for priority, count in priority_count.items():
            if count > 0:
                print(f"  {priority}: {count} issues")
        
        # SLA warnings
        print("\n[SLA WARNINGS]")
        now = datetime.now()
        sla_violations = []
        
        for issue in all_issues:
            created = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00'))
            age_hours = (now - created.replace(tzinfo=None)).total_seconds() / 3600
            
            labels = [label['name'] for label in issue.get('labels', [])]
            for label in labels:
                if "priority/P0" in label and age_hours > 1:
                    sla_violations.append(f"P0 Issue #{issue['number']} - {age_hours:.1f}h old (SLA: 1h)")
                elif "priority/P1" in label and age_hours > 4:
                    sla_violations.append(f"P1 Issue #{issue['number']} - {age_hours:.1f}h old (SLA: 4h)")
        
        if sla_violations:
            for violation in sla_violations[:5]:  # Show first 5
                print(f"  [ALERT] {violation}")
        else:
            print("  No SLA violations detected")
        
        # Recommendations
        print("\n[COORDINATOR RECOMMENDATIONS]")
        if total_issues > 50:
            print("  - High issue volume detected. Consider scaling up agents.")
        if any(status != "HEALTHY" for status in health.values()):
            print("  - Service health issues detected. Investigate offline services.")
        if priority_count["P0"] > 0:
            print("  - Critical P0 issues require immediate attention.")
        if not workload:
            print("  - No agent assignments detected. Check label configuration.")
        
        print("\n" + "="*80)
        print("END OF COORDINATOR REPORT")
        print("="*80)
        
        # Save report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": total_issues,
            "service_health": health,
            "agent_workload": {k: len(v) for k, v in workload.items()},
            "priority_distribution": priority_count,
            "sla_violations": len(sla_violations)
        }
        
        report_path = Path("coordinator_report.json")
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return report_data

if __name__ == "__main__":
    monitor = CoordinatorAgentMonitor()
    
    print("[COORDINATOR] Starting comprehensive agent monitoring...")
    print("[COORDINATOR] As the master coordinator, I oversee all agent operations")
    
    # Generate report
    report = monitor.generate_coordinator_report()
    
    print(f"\n[COORDINATOR] Report saved to coordinator_report.json")
    print("[COORDINATOR] Monitoring complete. All agents under supervision.")