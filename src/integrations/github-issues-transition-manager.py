#!/usr/bin/env python3
"""
GitHub Issues Transition Manager
Implements the transition from file-based to GitHub Issues task management
"""

import json
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('GitHubTransition')

class GitHubIssuesTransitionManager:
    def __init__(self):
        self.work_queue_dir = Path("work_queue")
        self.github_agent_file = Path("github-issues-agent.py")
        self.transition_config = {
            "repository": "stevesurles/NiroSubs-V2",  # From repo context
            "labels": {
                "ai_agent_task": "ai-agent-task",
                "critical": "P0-Critical",
                "high": "P1-High", 
                "medium": "P2-Medium",
                "low": "P3-Low",
                "backend": "backend",
                "frontend": "frontend", 
                "testing": "testing",
                "devops": "devops",
                "security": "security",
                "documentation": "documentation"
            },
            "agent_assignments": {
                "GPT4-Completion-Agent": "@completion-agent",
                "GPT4-Testing-Agent": "@testing-agent",
                "GPT4-Documentation-Agent": "@documentation-agent",
                "GPT4-DevOps-Agent": "@devops-agent", 
                "GPT4-Security-Agent": "@security-agent",
                "GPT4-Dashboard-Agent": "@dashboard-agent"
            }
        }
    
    def analyze_current_tasks(self) -> Dict[str, Any]:
        """Analyze current file-based tasks for migration"""
        analysis = {
            "total_tasks": 0,
            "critical_tasks": 0,
            "assigned_tasks": 0,
            "ready_for_migration": [],
            "requires_completion": [],
            "migration_summary": {}
        }
        
        if not self.work_queue_dir.exists():
            logger.warning("Work queue directory not found")
            return analysis
        
        for task_file in self.work_queue_dir.glob("*.json"):
            try:
                with open(task_file, 'r') as f:
                    task = json.load(f)
                
                analysis["total_tasks"] += 1
                
                if task.get("priority", "").startswith("P0"):
                    analysis["critical_tasks"] += 1
                
                if task.get("assigned_to"):
                    analysis["assigned_tasks"] += 1
                
                # Determine migration readiness
                task_info = {
                    "file": task_file.name,
                    "title": task.get("title", "Unknown"),
                    "priority": task.get("priority", "P2-MEDIUM"),
                    "assigned_to": task.get("assigned_to", ""),
                    "status": task.get("status", "unknown"),
                    "estimated_effort": task.get("estimated_total_effort", "unknown")
                }
                
                # Check if task is ready for migration or needs completion first
                if task.get("status") == "assigned" and task.get("priority", "").startswith("P0"):
                    analysis["requires_completion"].append(task_info)
                else:
                    analysis["ready_for_migration"].append(task_info)
                
            except Exception as e:
                logger.error(f"Error analyzing {task_file}: {e}")
        
        analysis["migration_summary"] = {
            "immediate_migration": len(analysis["ready_for_migration"]),
            "complete_first": len(analysis["requires_completion"]),
            "total": analysis["total_tasks"]
        }
        
        return analysis
    
    def create_github_issue_templates(self) -> Dict[str, str]:
        """Create GitHub issue templates for different task types"""
        templates = {
            "agent_task": """## 🤖 AI Agent Task

**Agent Assignment**: {assigned_agent}
**Priority**: {priority}
**Estimated Effort**: {estimated_effort}

## 📋 Task Description
{description}

## ✅ Sub-tasks
{subtasks}

## 🎯 Deliverables
{deliverables}

## ✨ Success Criteria
{success_criteria}

## 🔗 Dependencies
{dependencies}

---
**Automation**: This issue will be automatically assigned to the appropriate AI agent based on labels.
**Progress Tracking**: Update progress using GitHub's built-in project boards and milestones.
**Integration**: Connected to agent coordination system via GitHub Issues Agent.

/label {labels}
/assign {assignee}""",

            "bug_fix": """## 🐛 Bug Report

**Priority**: {priority}
**Affected Component**: {component}

## 🔍 Problem Description
{description}

## 🔧 Expected Solution
{solution}

## 🧪 Testing Requirements
{testing}

/label bug,{priority_label},{component_label}""",

            "feature_request": """## ✨ Feature Request

**Priority**: {priority}
**Component**: {component}

## 📝 Feature Description
{description}

## 🎯 Acceptance Criteria
{criteria}

## 🛠️ Implementation Notes
{implementation}

/label enhancement,{priority_label},{component_label}"""
        }
        
        return templates
    
    def generate_migration_issues(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate GitHub issues from current tasks"""
        issues = []
        templates = self.create_github_issue_templates()
        
        # Migrate ready tasks
        for task_info in analysis["ready_for_migration"]:
            try:
                # Load full task details
                task_file = self.work_queue_dir / task_info["file"]
                with open(task_file, 'r') as f:
                    full_task = json.load(f)
                
                # Create GitHub issue
                issue = self._convert_task_to_issue(full_task, templates)
                issues.append(issue)
                
            except Exception as e:
                logger.error(f"Error converting {task_info['file']}: {e}")
        
        return issues
    
    def _convert_task_to_issue(self, task: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        """Convert a task to GitHub issue format"""
        # Determine issue type
        issue_type = "agent_task"  # Default
        
        # Format sub-tasks
        subtasks = ""
        if task.get("tasks"):
            for i, subtask in enumerate(task["tasks"], 1):
                subtasks += f"{i}. **{subtask.get('task', 'Unknown')}**\n"
                subtasks += f"   - File: `{subtask.get('file', 'N/A')}`\n"
                subtasks += f"   - Effort: {subtask.get('estimated_effort', 'Unknown')}\n"
                subtasks += f"   - Details: {subtask.get('details', 'No details')}\n\n"
        
        # Format deliverables
        deliverables = ""
        if task.get("deliverables"):
            for deliverable in task["deliverables"]:
                deliverables += f"- {deliverable}\n"
        
        # Format success criteria
        success_criteria = ""
        if task.get("success_criteria"):
            for criteria in task["success_criteria"]:
                success_criteria += f"- {criteria}\n"
        
        # Format dependencies
        dependencies = ""
        if task.get("dependencies"):
            dependencies = ", ".join(task["dependencies"])
        
        # Determine labels
        labels = ["ai-agent-task"]
        
        priority = task.get("priority", "P2-MEDIUM")
        if priority.startswith("P0"):
            labels.append("critical")
        elif priority.startswith("P1"):
            labels.append("high-priority")
        
        # Add component labels based on content
        title_desc = (task.get("title", "") + " " + task.get("description", "")).lower()
        if "dashboard" in title_desc or "ui" in title_desc:
            labels.append("frontend")
        if "test" in title_desc:
            labels.append("testing")
        if "docker" in title_desc or "deploy" in title_desc:
            labels.append("devops")
        if "security" in title_desc:
            labels.append("security")
        if "doc" in title_desc:
            labels.append("documentation")
        
        # Create issue body
        body = templates[issue_type].format(
            assigned_agent=task.get("assigned_to", "Unassigned"),
            priority=priority,
            estimated_effort=task.get("estimated_total_effort", "Unknown"),
            description=task.get("description", "No description"),
            subtasks=subtasks,
            deliverables=deliverables,
            success_criteria=success_criteria,
            dependencies=dependencies,
            labels=" ".join(labels),
            assignee=self.transition_config["agent_assignments"].get(
                task.get("assigned_to", ""), ""
            )
        )
        
        return {
            "title": task.get("title", "Untitled Task"),
            "body": body,
            "labels": labels,
            "assignees": [],  # Will be set by GitHub agent
            "milestone": None,
            "original_file": task.get("created_at", "unknown"),
            "priority": priority,
            "agent": task.get("assigned_to", "")
        }
    
    def create_transition_plan(self, analysis: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive transition plan"""
        plan = {
            "transition_id": f"github_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "current_state": {
                "file_based_tasks": analysis["total_tasks"],
                "critical_tasks": analysis["critical_tasks"],
                "completion_required": len(analysis["requires_completion"])
            },
            "migration_plan": {
                "phase_1": "Complete Critical Tasks (Dashboard, AI Developer Agent)",
                "phase_2": "Setup GitHub Integration", 
                "phase_3": "Migrate Tasks to GitHub Issues",
                "phase_4": "Enable Real-time GitHub Monitoring"
            },
            "github_issues_to_create": len(issues),
            "implementation_steps": [
                {
                    "step": 1,
                    "action": "Complete dashboard tab functionality",
                    "status": "in_progress",
                    "estimated_time": "30 minutes"
                },
                {
                    "step": 2, 
                    "action": "Complete AI Developer Agent (TypeScript, Docker generators)",
                    "status": "pending",
                    "estimated_time": "2-3 hours"
                },
                {
                    "step": 3,
                    "action": "Setup GitHub API authentication",
                    "status": "pending", 
                    "estimated_time": "30 minutes"
                },
                {
                    "step": 4,
                    "action": "Create GitHub Issues from current tasks",
                    "status": "ready",
                    "estimated_time": "1 hour"
                },
                {
                    "step": 5,
                    "action": "Configure GitHub Issues Agent monitoring",
                    "status": "ready",
                    "estimated_time": "1 hour"
                },
                {
                    "step": 6,
                    "action": "Setup real-time webhooks",
                    "status": "pending",
                    "estimated_time": "1 hour"
                }
            ],
            "success_criteria": [
                "All critical tasks completed",
                "GitHub Issues created for remaining tasks",
                "GitHub Issues Agent monitoring active",
                "Real-time task updates via GitHub webhooks",
                "Dashboard showing GitHub integration status"
            ],
            "rollback_plan": "File-based system remains as backup during transition"
        }
        
        return plan
    
    def save_transition_artifacts(self, analysis: Dict[str, Any], issues: List[Dict[str, Any]], plan: Dict[str, Any]):
        """Save all transition artifacts"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save analysis
        with open(f"github_transition_analysis_{timestamp}.json", 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save generated issues
        with open(f"github_issues_to_create_{timestamp}.json", 'w') as f:
            json.dump(issues, f, indent=2)
        
        # Save transition plan
        with open(f"github_transition_plan_{timestamp}.json", 'w') as f:
            json.dump(plan, f, indent=2)
        
        # Create transition script
        script_content = self._generate_transition_script(issues)
        with open(f"github_transition_script_{timestamp}.py", 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"Transition artifacts saved with timestamp {timestamp}")
    
    def _generate_transition_script(self, issues: List[Dict[str, Any]]) -> str:
        """Generate script to create GitHub issues"""
        script = '''#!/usr/bin/env python3
"""
GitHub Issues Creation Script
Automatically created by GitHub Transition Manager
"""

import requests
import json
import os
from typing import List, Dict, Any

def create_github_issues(issues: List[Dict[str, Any]], token: str, repo: str):
    """Create GitHub issues from task list"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    created_issues = []
    
    for issue in issues:
        try:
            response = requests.post(
                f"https://api.github.com/repos/{repo}/issues",
                headers=headers,
                json={
                    "title": issue["title"],
                    "body": issue["body"], 
                    "labels": issue["labels"]
                }
            )
            
            if response.status_code == 201:
                created_issue = response.json()
                print(f"✅ Created issue #{created_issue['number']}: {issue['title']}")
                created_issues.append(created_issue)
            else:
                print(f"❌ Failed to create issue: {issue['title']} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating issue {issue['title']}: {e}")
    
    return created_issues

def main():
    # Configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set this environment variable
    REPOSITORY = "stevesurles/NiroSubs-V2"
    
    if not GITHUB_TOKEN:
        print("❌ Please set GITHUB_TOKEN environment variable")
        return
    
    # Issues to create
    issues = ''' + json.dumps(issues, indent=2) + '''
    
    print(f"🚀 Creating {len(issues)} GitHub issues...")
    created = create_github_issues(issues, GITHUB_TOKEN, REPOSITORY)
    print(f"✅ Successfully created {len(created)} issues")

if __name__ == "__main__":
    main()
'''
        return script
    
    def print_transition_summary(self, analysis: Dict[str, Any], plan: Dict[str, Any]):
        """Print transition summary"""
        print("\n" + "="*80)
        print("🔄 GITHUB ISSUES TRANSITION PLAN")
        print("="*80)
        
        print(f"\n📊 CURRENT STATE:")
        print(f"   • Total File-based Tasks: {analysis['total_tasks']}")
        print(f"   • Critical Tasks: {analysis['critical_tasks']}")
        print(f"   • Tasks Requiring Completion: {len(analysis['requires_completion'])}")
        print(f"   • Ready for Migration: {len(analysis['ready_for_migration'])}")
        
        print(f"\n🎯 MIGRATION PHASES:")
        for i, (phase, description) in enumerate(plan["migration_plan"].items(), 1):
            print(f"   {i}. {description}")
        
        print(f"\n⚡ IMPLEMENTATION STEPS:")
        for step in plan["implementation_steps"]:
            status_icon = "✅" if step["status"] == "in_progress" else "⏳" if step["status"] == "ready" else "⏸️"
            print(f"   {step['step']}. {status_icon} {step['action']} ({step['estimated_time']})")
        
        print(f"\n🐙 GITHUB INTEGRATION BENEFITS:")
        print("   • Real-time task tracking and updates")
        print("   • Automatic agent assignment via labels")
        print("   • Built-in progress tracking and milestones")
        print("   • Integration with CI/CD workflows")
        print("   • Better collaboration and transparency")
        print("   • Automatic issue creation from new requirements")
        
        print("\n" + "="*80)

def main():
    """Main transition coordination"""
    manager = GitHubIssuesTransitionManager()
    
    print("🔄 Analyzing current task state for GitHub Issues transition...")
    analysis = manager.analyze_current_tasks()
    
    print("📝 Generating GitHub Issues from current tasks...")
    issues = manager.generate_migration_issues(analysis)
    
    print("📋 Creating comprehensive transition plan...")
    plan = manager.create_transition_plan(analysis, issues)
    
    print("💾 Saving transition artifacts...")
    manager.save_transition_artifacts(analysis, issues, plan)
    
    print("📊 Transition plan complete!")
    manager.print_transition_summary(analysis, plan)
    
    print(f"\n📁 ARTIFACTS CREATED:")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"   • github_transition_analysis_{timestamp}.json")
    print(f"   • github_issues_to_create_{timestamp}.json") 
    print(f"   • github_transition_plan_{timestamp}.json")
    print(f"   • github_transition_script_{timestamp}.py")
    
    print(f"\n🚀 NEXT STEPS:")
    print("   1. Complete critical dashboard and AI Developer Agent tasks")
    print("   2. Set GITHUB_TOKEN environment variable")
    print(f"   3. Run: python github_transition_script_{timestamp}.py")
    print("   4. Configure GitHub Issues Agent monitoring")
    print("   5. Verify all tasks are properly tracked in GitHub Issues")

if __name__ == "__main__":
    main()
