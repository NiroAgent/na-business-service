#!/usr/bin/env python3
"""
GitHub Issues Business Operations Integration
Converts GitHub Issues into work items for our autonomous business agents
"""

import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GitHubIssuesIntegration')

@dataclass
class GitHubIssue:
    """GitHub Issue data structure"""
    id: int
    number: int
    title: str
    body: str
    state: str
    labels: List[str]
    assignee: Optional[str]
    created_at: str
    updated_at: str
    url: str
    
    def to_work_item(self) -> Dict[str, Any]:
        """Convert GitHub issue to work item format"""
        # Determine priority from labels
        priority = "P2"  # Default
        for label in self.labels:
            if "priority/" in label:
                priority = label.split("/")[1].split("-")[0]
                break
        
        # Determine agent assignment from labels
        assigned_agent = None
        for label in self.labels:
            if "assigned/" in label:
                assigned_agent = label.split("/")[1]
                break
        
        # Determine item type from labels
        item_type = "general"
        for label in self.labels:
            if "/" in label and not label.startswith(("priority/", "assigned/", "status/")):
                item_type = label.split("/")[0]
                break
        
        return {
            "item_id": f"github-{self.number}",
            "title": self.title,
            "description": self.body or "",
            "item_type": item_type,
            "priority": priority,
            "assigned_agent": assigned_agent,
            "status": "pending",
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": {
                "github_issue_id": self.id,
                "github_issue_number": self.number,
                "github_url": self.url,
                "github_labels": self.labels,
                "github_state": self.state
            }
        }

class GitHubIssuesIntegration:
    """Integration with GitHub Issues for business operations"""
    
    def __init__(self, repo_owner: str, repo_name: str, github_token: str = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        
        # Business operation labels mapping
        self.business_labels = {
            # Management
            "management/strategic-planning": {"agent": "ai-manager", "priority": "P1"},
            "management/resource-allocation": {"agent": "ai-manager", "priority": "P1"},
            "management/escalation": {"agent": "ai-manager", "priority": "P0"},
            "management/kpi-review": {"agent": "ai-manager", "priority": "P2"},
            
            # Marketing
            "marketing/content-creation": {"agent": "ai-marketing", "priority": "P2"},
            "marketing/campaign-management": {"agent": "ai-marketing", "priority": "P1"},
            "marketing/seo-optimization": {"agent": "ai-marketing", "priority": "P2"},
            "marketing/brand-monitoring": {"agent": "ai-marketing", "priority": "P2"},
            "marketing/lead-generation": {"agent": "ai-marketing", "priority": "P1"},
            
            # Sales
            "sales/lead-qualification": {"agent": "ai-sales", "priority": "P1"},
            "sales/opportunity-management": {"agent": "ai-sales", "priority": "P1"},
            "sales/crm-updates": {"agent": "ai-sales", "priority": "P2"},
            "sales/revenue-tracking": {"agent": "ai-sales", "priority": "P1"},
            
            # Support
            "support/customer-inquiry": {"agent": "ai-support", "priority": "P1"},
            "support/knowledge-base": {"agent": "ai-support", "priority": "P3"},
            "support/bug-reports": {"agent": "ai-support", "priority": "P1"},
            "support/feature-requests": {"agent": "ai-support", "priority": "P2"},
            "support/escalations": {"agent": "ai-support", "priority": "P0"},
            
            # Customer Success
            "success/onboarding": {"agent": "ai-customer-success", "priority": "P1"},
            "success/retention": {"agent": "ai-customer-success", "priority": "P1"},
            "success/expansion": {"agent": "ai-customer-success", "priority": "P2"},
            "success/health-check": {"agent": "ai-customer-success", "priority": "P2"},
            
            # Analytics & Finance
            "analytics/reporting": {"agent": "ai-analytics", "priority": "P2"},
            "analytics/data-analysis": {"agent": "ai-analytics", "priority": "P2"},
            "finance/budgeting": {"agent": "ai-finance", "priority": "P1"},
            "finance/compliance": {"agent": "ai-finance", "priority": "P1"},
            
            # Operations & Security
            "operations/monitoring": {"agent": "ai-operations", "priority": "P1"},
            "operations/optimization": {"agent": "ai-operations", "priority": "P2"},
            "security/threat-detection": {"agent": "ai-security", "priority": "P0"},
            "security/compliance": {"agent": "ai-security", "priority": "P1"}
        }
        
        # Initialize GitHub API client
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Business-Automation/1.0"
        }
        
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
        
        logger.info(f"🐙 GitHub Issues integration initialized for {repo_owner}/{repo_name}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        return self.headers.copy()
    
    def fetch_issues(self, state: str = "open", labels: str = None) -> List[GitHubIssue]:
        """Fetch issues from GitHub repository"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues"
        
        params = {
            "state": state,
            "per_page": 100  # Maximum per page
        }
        
        if labels:
            params["labels"] = labels
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            
            issues_data = response.json()
            issues = []
            
            for issue_data in issues_data:
                # Skip pull requests (they appear as issues in GitHub API)
                if "pull_request" in issue_data:
                    continue
                
                labels = [label["name"] for label in issue_data.get("labels", [])]
                assignee = issue_data.get("assignee", {}).get("login") if issue_data.get("assignee") else None
                
                issue = GitHubIssue(
                    id=issue_data["id"],
                    number=issue_data["number"],
                    title=issue_data["title"],
                    body=issue_data.get("body", ""),
                    state=issue_data["state"],
                    labels=labels,
                    assignee=assignee,
                    created_at=issue_data["created_at"],
                    updated_at=issue_data["updated_at"],
                    url=issue_data["html_url"]
                )
                
                issues.append(issue)
            
            logger.info(f"📋 Fetched {len(issues)} issues from GitHub")
            return issues
            
        except Exception as e:
            logger.error(f"Error fetching GitHub issues: {e}")
            return []
    
    def fetch_business_operations(self) -> List[Dict[str, Any]]:
        """Fetch business operation issues and convert to work items"""
        # Get all open issues with business operation labels
        business_label_names = list(self.business_labels.keys())
        work_items = []
        
        # GitHub API doesn't support OR queries for labels, so we fetch all and filter
        all_issues = self.fetch_issues(state="open")
        
        for issue in all_issues:
            # Check if issue has any business operation labels
            has_business_label = any(label in business_label_names for label in issue.labels)
            
            if has_business_label:
                work_item = issue.to_work_item()
                
                # Auto-assign agent based on business labels
                for label in issue.labels:
                    if label in self.business_labels:
                        config = self.business_labels[label]
                        if not work_item["assigned_agent"]:
                            work_item["assigned_agent"] = config["agent"]
                        # Update priority if not explicitly set
                        if work_item["priority"] == "P2" and config["priority"]:
                            work_item["priority"] = config["priority"]
                        break
                
                work_items.append(work_item)
                logger.info(f"📋 Business operation: {work_item['title']} -> {work_item['assigned_agent']}")
        
        logger.info(f"🎯 Converted {len(work_items)} GitHub issues to business operations")
        return work_items
    
    def update_issue_status(self, issue_number: int, status: str, comment: str = None) -> bool:
        """Update GitHub issue status and add comment"""
        try:
            # Add comment if provided
            if comment:
                self.add_comment(issue_number, comment)
            
            # Update labels based on status
            status_label = f"status/{status}"
            self.add_label_to_issue(issue_number, status_label)
            
            # Close issue if status is 'done'
            if status == "done":
                self.close_issue(issue_number)
            
            logger.info(f"✅ Updated issue #{issue_number} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating issue #{issue_number}: {e}")
            return False
    
    def add_comment(self, issue_number: int, comment: str) -> bool:
        """Add comment to GitHub issue"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}/comments"
        
        data = {
            "body": comment
        }
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=data)
            response.raise_for_status()
            logger.info(f"💬 Added comment to issue #{issue_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding comment to issue #{issue_number}: {e}")
            return False
    
    def add_label_to_issue(self, issue_number: int, label: str) -> bool:
        """Add label to GitHub issue"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}/labels"
        
        data = {
            "labels": [label]
        }
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=data)
            response.raise_for_status()
            logger.info(f"🏷️ Added label '{label}' to issue #{issue_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding label to issue #{issue_number}: {e}")
            return False
    
    def close_issue(self, issue_number: int) -> bool:
        """Close GitHub issue"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}"
        
        data = {
            "state": "closed"
        }
        
        try:
            response = requests.patch(url, headers=self.get_headers(), json=data)
            response.raise_for_status()
            logger.info(f"🔒 Closed issue #{issue_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing issue #{issue_number}: {e}")
            return False
    
    def create_business_operation_issue(self, title: str, description: str, 
                                      operation_type: str, priority: str = "P2") -> int:
        """Create a new business operation issue"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues"
        
        # Determine labels based on operation type
        labels = [
            f"{operation_type}",
            f"priority/{priority}",
            "status/todo"
        ]
        
        # Add agent assignment if known
        if operation_type in self.business_labels:
            agent = self.business_labels[operation_type]["agent"]
            labels.append(f"assigned/{agent}")
        
        data = {
            "title": title,
            "body": description,
            "labels": labels
        }
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=data)
            response.raise_for_status()
            
            issue_data = response.json()
            issue_number = issue_data["number"]
            
            logger.info(f"📝 Created business operation issue #{issue_number}: {title}")
            return issue_number
            
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return None
    
    def setup_repository_labels(self) -> bool:
        """Set up business operation labels in the repository"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/labels"
        
        # Define label colors
        label_colors = {
            "management": "0052CC",
            "marketing": "1F8B4C", 
            "sales": "F4C430",
            "support": "FF6B6B",
            "success": "4ECDC4",
            "analytics": "9013FE",
            "finance": "795548",
            "operations": "607D8B",
            "security": "F44336",
            "priority": "E91E63",
            "assigned": "2196F3",
            "status": "4CAF50"
        }
        
        labels_to_create = []
        
        # Business operation labels
        for label_name in self.business_labels.keys():
            category = label_name.split("/")[0]
            labels_to_create.append({
                "name": label_name,
                "color": label_colors.get(category, "CCCCCC"),
                "description": f"Business operation: {label_name}"
            })
        
        # Priority labels
        for priority in ["P0-critical", "P1-high", "P2-medium", "P3-low", "P4-backlog"]:
            labels_to_create.append({
                "name": f"priority/{priority}",
                "color": label_colors["priority"],
                "description": f"Priority level: {priority}"
            })
        
        # Status labels
        for status in ["todo", "in-progress", "review", "done", "blocked"]:
            labels_to_create.append({
                "name": f"status/{status}",
                "color": label_colors["status"],
                "description": f"Work status: {status}"
            })
        
        # Agent assignment labels
        agents = ["ai-manager", "ai-marketing", "ai-sales", "ai-support", 
                 "ai-customer-success", "ai-analytics", "ai-finance", 
                 "ai-operations", "ai-security"]
        
        for agent in agents:
            labels_to_create.append({
                "name": f"assigned/{agent}",
                "color": label_colors["assigned"],
                "description": f"Assigned to: {agent}"
            })
        
        # Create labels
        created_count = 0
        for label_data in labels_to_create:
            try:
                response = requests.post(url, headers=self.get_headers(), json=label_data)
                if response.status_code == 201:
                    created_count += 1
                elif response.status_code == 422:
                    # Label already exists
                    pass
                else:
                    response.raise_for_status()
                    
            except Exception as e:
                logger.warning(f"Could not create label {label_data['name']}: {e}")
        
        logger.info(f"🏷️ Set up {created_count} business operation labels in repository")
        return True
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status and metrics"""
        try:
            # Fetch recent issues
            recent_issues = self.fetch_issues(state="all")
            
            # Count by category
            categories = {}
            priorities = {}
            statuses = {}
            
            for issue in recent_issues:
                for label in issue.labels:
                    if "/" in label:
                        category, value = label.split("/", 1)
                        if category == "priority":
                            priorities[value] = priorities.get(value, 0) + 1
                        elif category == "status":
                            statuses[value] = statuses.get(value, 0) + 1
                        elif category in ["management", "marketing", "sales", "support", 
                                        "success", "analytics", "finance", "operations", "security"]:
                            categories[category] = categories.get(category, 0) + 1
            
            return {
                "timestamp": datetime.now().isoformat(),
                "repository": f"{self.repo_owner}/{self.repo_name}",
                "total_issues": len(recent_issues),
                "business_operations": sum(categories.values()),
                "categories": categories,
                "priorities": priorities,
                "statuses": statuses,
                "integration_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error getting integration status: {e}")
            return {"integration_status": "error", "error": str(e)}


# Integration with agent orchestrator
def integrate_github_with_orchestrator(github_integration: GitHubIssuesIntegration):
    """Integrate GitHub Issues with agent orchestrator"""
    try:
        # Import orchestrator
        sys.path.append(str(Path(__file__).parent))
        from agent_orchestration_system import get_orchestrator, Priority
        
        orchestrator = get_orchestrator()
        
        # Fetch business operations from GitHub
        work_items = github_integration.fetch_business_operations()
        
        # Add to orchestrator work queue
        for work_item in work_items:
            # Map priority
            priority_map = {
                "P0": Priority.CRITICAL,
                "P1": Priority.HIGH,
                "P2": Priority.MEDIUM,
                "P3": Priority.LOW,
                "P4": Priority.BACKLOG
            }
            
            priority = priority_map.get(work_item["priority"], Priority.MEDIUM)
            
            # Add to work queue
            orchestrator.add_work_item(
                title=work_item["title"],
                description=work_item["description"],
                item_type=work_item["item_type"],
                priority=priority,
                metadata=work_item["metadata"]
            )
        
        logger.info(f"🔄 Integrated {len(work_items)} GitHub issues with orchestrator")
        return True
        
    except Exception as e:
        logger.error(f"Error integrating with orchestrator: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🐙 GITHUB ISSUES BUSINESS OPERATIONS INTEGRATION")
    print("="*80)
    print("Converting GitHub Issues into autonomous business operations")
    print("AWS Serverless-First Architecture")
    print("="*80 + "\n")
    
    # Example usage
    repo_owner = "stevesurles"  # Change to your repo
    repo_name = "business-operations"  # Change to your business operations repo
    
    # Initialize integration
    github_integration = GitHubIssuesIntegration(repo_owner, repo_name)
    
    # Set up repository labels
    github_integration.setup_repository_labels()
    
    # Fetch and display current business operations
    work_items = github_integration.fetch_business_operations()
    
    print(f"📊 GitHub Issues Integration Status:")
    print(f"   Repository: {repo_owner}/{repo_name}")
    print(f"   Business Operations: {len(work_items)}")
    
    if work_items:
        print(f"\n🎯 Current Operations:")
        for item in work_items[:5]:  # Show first 5
            print(f"   - {item['title']} ({item['item_type']}) -> {item['assigned_agent']}")
    
    # Get integration status
    status = github_integration.get_integration_status()
    print(f"\n📈 Integration Metrics:")
    print(f"   Total Issues: {status.get('total_issues', 0)}")
    print(f"   Business Operations: {status.get('business_operations', 0)}")
    print(f"   Categories: {list(status.get('categories', {}).keys())}")
    
    # Integrate with orchestrator
    print(f"\n🔄 Integrating with Agent Orchestrator...")
    success = integrate_github_with_orchestrator(github_integration)
    
    if success:
        print("✅ GitHub Issues successfully integrated with agent orchestrator!")
    else:
        print("⚠️ Integration with orchestrator not available - run in standalone mode")
    
    print(f"\n🚀 GitHub Issues Business Operations Integration Ready!")
    print(f"Create issues with business operation labels to trigger agent automation.")
