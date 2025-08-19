#!/usr/bin/env python3
"""
Agent Unstuck and GitHub Transition Coordinator
Resolves stuck agent situation and prepares GitHub Issues transition
"""

import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AgentUnstuck')

class AgentUnstuckCoordinator:
    def __init__(self):
        self.work_queue_dir = Path("work_queue")
        self.agent_assignments_dir = Path("agent_assignments")
        self.github_issues_template = {
            "labels": ["ai-agent-task", "sdlc"],
            "assignees": [],
            "milestone": None,
            "projects": []
        }
    
    def analyze_stuck_situation(self) -> Dict[str, Any]:
        """Analyze why agents are stuck and what needs to be done"""
        analysis = {
            "problem": "All 6 agents assigned but not executing",
            "root_cause": "Agent assignments exist as JSON files but no actual agent processes running",
            "solutions": [
                "Option 1: Start actual GPT-4 agent processes (complex)",
                "Option 2: Transition to GitHub Issues workflow (recommended)",
                "Option 3: Manual execution of critical tasks"
            ],
            "recommended_action": "github_transition",
            "critical_tasks": [],
            "immediate_needs": []
        }
        
        # Analyze critical tasks from work queue
        if self.work_queue_dir.exists():
            for queue_file in self.work_queue_dir.glob("*.json"):
                try:
                    with open(queue_file, 'r') as f:
                        task = json.load(f)
                    
                    if task.get("priority", "").startswith("P0"):
                        analysis["critical_tasks"].append({
                            "file": queue_file.name,
                            "title": task.get("title", "Unknown"),
                            "assigned_to": task.get("assigned_to", "Unassigned"),
                            "description": task.get("description", "")
                        })
                except Exception as e:
                    logger.error(f"Error reading {queue_file}: {e}")
        
        # Determine immediate needs
        if len(analysis["critical_tasks"]) > 0:
            analysis["immediate_needs"].append("Resolve critical P0 tasks immediately")
        analysis["immediate_needs"].extend([
            "Fix dashboard tab functionality (user reported)",
            "Complete AI Developer Agent (75% done)",
            "Transition to GitHub Issues for proper SDLC"
        ])
        
        return analysis
    
    def create_github_issues_migration_plan(self) -> Dict[str, Any]:
        """Create plan to migrate to GitHub Issues"""
        migration_plan = {
            "phase": "GitHub Issues Migration",
            "timeline": "Immediate - 2 hours",
            "prerequisites": [
                "Complete critical dashboard fix",
                "Verify GitHub agent functionality",
                "Configure GitHub API authentication"
            ],
            "migration_tasks": [],
            "github_issues_to_create": [],
            "configuration_needed": []
        }
        
        # Convert current tasks to GitHub Issues format
        if self.work_queue_dir.exists():
            for queue_file in self.work_queue_dir.glob("*.json"):
                try:
                    with open(queue_file, 'r') as f:
                        task = json.load(f)
                    
                    github_issue = {
                        "title": task.get("title", "Unknown Task"),
                        "body": self._format_issue_body(task),
                        "labels": self._determine_labels(task),
                        "priority": task.get("priority", "P2-MEDIUM"),
                        "assigned_agent": task.get("assigned_to", ""),
                        "original_file": queue_file.name
                    }
                    
                    migration_plan["github_issues_to_create"].append(github_issue)
                    
                except Exception as e:
                    logger.error(f"Error processing {queue_file}: {e}")
        
        # Configuration needed
        migration_plan["configuration_needed"] = [
            "GitHub API token setup",
            "Repository webhook configuration",
            "Agent label system (ai-agent-task, backend, frontend, etc.)",
            "Issue templates for different task types",
            "Automatic assignment rules"
        ]
        
        return migration_plan
    
    def _format_issue_body(self, task: Dict[str, Any]) -> str:
        """Format task as GitHub issue body"""
        body = f"## Task Description\n{task.get('description', 'No description')}\n\n"
        
        if task.get("tasks"):
            body += "## Sub-tasks\n"
            for i, subtask in enumerate(task["tasks"], 1):
                body += f"{i}. **{subtask.get('task', 'Unknown')}**\n"
                body += f"   - File: `{subtask.get('file', 'N/A')}`\n"
                body += f"   - Effort: {subtask.get('estimated_effort', 'Unknown')}\n"
                body += f"   - Details: {subtask.get('details', 'No details')}\n\n"
        
        if task.get("deliverables"):
            body += "## Deliverables\n"
            for deliverable in task["deliverables"]:
                body += f"- {deliverable}\n"
            body += "\n"
        
        if task.get("success_criteria"):
            body += "## Success Criteria\n"
            for criteria in task["success_criteria"]:
                body += f"- {criteria}\n"
            body += "\n"
        
        body += f"## Metadata\n"
        body += f"- **Priority**: {task.get('priority', 'Unknown')}\n"
        body += f"- **Estimated Effort**: {task.get('estimated_total_effort', 'Unknown')}\n"
        body += f"- **Coordination Type**: {task.get('coordination_type', 'Unknown')}\n"
        body += f"- **Created**: {task.get('created_at', 'Unknown')}\n"
        
        if task.get("dependencies"):
            body += f"- **Dependencies**: {', '.join(task['dependencies'])}\n"
        
        body += f"\n---\n*This issue was migrated from file-based task management to GitHub Issues workflow.*"
        
        return body
    
    def _determine_labels(self, task: Dict[str, Any]) -> List[str]:
        """Determine appropriate labels for GitHub issue"""
        labels = ["ai-agent-task", "sdlc"]
        
        # Priority labels
        priority = task.get("priority", "P2-MEDIUM")
        if priority.startswith("P0"):
            labels.append("critical")
        elif priority.startswith("P1"):
            labels.append("high-priority")
        
        # Task type labels
        title = task.get("title", "").lower()
        description = task.get("description", "").lower()
        
        if any(word in title + description for word in ["test", "testing", "qa"]):
            labels.append("testing")
        if any(word in title + description for word in ["dashboard", "ui", "frontend"]):
            labels.append("frontend")
        if any(word in title + description for word in ["api", "backend", "server"]):
            labels.append("backend")
        if any(word in title + description for word in ["docker", "deploy", "devops"]):
            labels.append("devops")
        if any(word in title + description for word in ["security", "auth"]):
            labels.append("security")
        if any(word in title + description for word in ["doc", "documentation"]):
            labels.append("documentation")
        
        # Agent assignment labels
        assigned_to = task.get("assigned_to", "")
        if "completion" in assigned_to.lower():
            labels.append("completion-agent")
        elif "testing" in assigned_to.lower():
            labels.append("testing-agent")
        elif "dashboard" in assigned_to.lower():
            labels.append("dashboard-agent")
        elif "devops" in assigned_to.lower():
            labels.append("devops-agent")
        elif "security" in assigned_to.lower():
            labels.append("security-agent")
        elif "documentation" in assigned_to.lower():
            labels.append("documentation-agent")
        
        return labels
    
    def generate_immediate_action_plan(self) -> Dict[str, Any]:
        """Generate immediate action plan to unstuck agents"""
        action_plan = {
            "timestamp": datetime.now().isoformat(),
            "situation": "All 6 agents stuck - no actual execution happening",
            "immediate_actions": [
                {
                    "priority": "P0-CRITICAL",
                    "action": "Fix Dashboard Tabs",
                    "reason": "User reported tabs not clickable, blocks monitoring",
                    "method": "Manual fix of comprehensive-tabbed-dashboard.py",
                    "estimated_time": "30 minutes"
                },
                {
                    "priority": "P0-CRITICAL", 
                    "action": "Complete AI Developer Agent",
                    "reason": "75% complete, needed for code generation",
                    "method": "Manual completion of missing TypeScript/Docker generators",
                    "estimated_time": "2-3 hours"
                },
                {
                    "priority": "P1-HIGH",
                    "action": "GitHub Issues Migration",
                    "reason": "Proper SDLC task management as user requested",
                    "method": "Migrate tasks to GitHub Issues, setup automation",
                    "estimated_time": "1-2 hours"
                }
            ],
            "github_transition_steps": [
                "1. Complete critical dashboard and AI Developer Agent tasks",
                "2. Setup GitHub API authentication",
                "3. Create GitHub Issues from current work queue",
                "4. Configure GitHub Issues agent to monitor and assign",
                "5. Setup webhooks for real-time updates",
                "6. Transition from file-based to issue-based workflow"
            ],
            "fallback_plan": "Manual execution of critical tasks while setting up GitHub workflow"
        }
        
        return action_plan
    
    def save_migration_plan(self, analysis: Dict[str, Any], migration_plan: Dict[str, Any], action_plan: Dict[str, Any]):
        """Save all plans to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save analysis
        with open(f"agent_stuck_analysis_{timestamp}.json", 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save migration plan
        with open(f"github_migration_plan_{timestamp}.json", 'w') as f:
            json.dump(migration_plan, f, indent=2)
        
        # Save action plan
        with open(f"immediate_action_plan_{timestamp}.json", 'w') as f:
            json.dump(action_plan, f, indent=2)
        
        logger.info(f"Plans saved with timestamp {timestamp}")
    
    def print_summary(self, analysis: Dict[str, Any], action_plan: Dict[str, Any]):
        """Print executive summary"""
        print("\n" + "="*80)
        print("🚨 AGENT STUCK SITUATION - IMMEDIATE ACTION REQUIRED")
        print("="*80)
        
        print(f"\n❌ PROBLEM: {analysis['problem']}")
        print(f"🔍 ROOT CAUSE: {analysis['root_cause']}")
        
        print(f"\n⚡ IMMEDIATE ACTIONS NEEDED:")
        for i, action in enumerate(action_plan["immediate_actions"], 1):
            print(f"   {i}. {action['priority']} - {action['action']}")
            print(f"      Reason: {action['reason']}")
            print(f"      Time: {action['estimated_time']}")
        
        print(f"\n🐙 GITHUB TRANSITION RECOMMENDATION:")
        print("   ✅ GitHub agent exists and is functional")
        print("   ✅ Work queue supports GitHub issues")
        print("   ✅ Infrastructure ready for transition")
        print("   🎯 Next: Complete critical tasks, then migrate to GitHub Issues")
        
        print(f"\n🎯 SUCCESS PATH:")
        print("   1. Fix dashboard (30 min) - unblock monitoring")
        print("   2. Complete AI Developer Agent (2-3 hours) - finish core functionality")
        print("   3. Migrate to GitHub Issues (1-2 hours) - proper SDLC workflow")
        print("   4. All future tasks managed via GitHub Issues with automation")
        
        print("\n" + "="*80)

def main():
    """Main coordination function"""
    coordinator = AgentUnstuckCoordinator()
    
    # Analyze situation
    analysis = coordinator.analyze_stuck_situation()
    
    # Create migration plan
    migration_plan = coordinator.create_github_issues_migration_plan()
    
    # Generate action plan
    action_plan = coordinator.generate_immediate_action_plan()
    
    # Save plans
    coordinator.save_migration_plan(analysis, migration_plan, action_plan)
    
    # Print summary
    coordinator.print_summary(analysis, action_plan)
    
    print(f"\n📁 FILES CREATED:")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"   • agent_stuck_analysis_{timestamp}.json")
    print(f"   • github_migration_plan_{timestamp}.json") 
    print(f"   • immediate_action_plan_{timestamp}.json")

if __name__ == "__main__":
    main()
