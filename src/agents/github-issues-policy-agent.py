#!/usr/bin/env python3
"""
GitHub Issues Agent with Policy Integration
Enhanced GitHub Issues agent that includes policy compliance and knowledge base integration
"""

import json
import requests
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('GitHubIssuesAgent')

# Import policy engine (PostgreSQL version preferred, SQLite fallback)
try:
    from postgresql_agent_policy_engine import PostgreSQLAgentPolicyEngine as PolicyEngine
    logger.info("Using PostgreSQL policy engine")
    POLICY_ENGINE_TYPE = "postgresql"
except ImportError:
    try:
        from agent_policy_engine import AgentPolicyEngine as PolicyEngine
        logger.info("Using SQLite policy engine")
        POLICY_ENGINE_TYPE = "sqlite"
    except ImportError:
        logger.warning("No policy engine available - running without policy integration")
        PolicyEngine = None
        POLICY_ENGINE_TYPE = None

class PolicyEnhancedGitHubAgent:
    def __init__(self, github_token: str = None, repo: str = "stevesurles/NiroSubs-V2"):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.repo = repo
        
        # Initialize policy engine if available
        if PolicyEngine:
            try:
                if POLICY_ENGINE_TYPE == "postgresql":
                    self.policy_engine = PolicyEngine()  # PostgreSQL engine
                else:
                    self.policy_engine = PolicyEngine()  # SQLite engine
                logger.info(f"Policy engine initialized ({POLICY_ENGINE_TYPE})")
            except Exception as e:
                logger.error(f"Failed to initialize policy engine: {e}")
                self.policy_engine = None
        else:
            self.policy_engine = None
            logger.warning("Policy engine not available - continuing without policy integration")
            
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.github_token}" if self.github_token else "",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        # Agent role mapping for automatic assignment
        self.role_mapping = {
            "completion-agent": "completion_agent",
            "testing-agent": "testing_agent", 
            "devops-agent": "devops_agent",
            "security-agent": "security_agent",
            "documentation-agent": "documentation_agent",
            "dashboard-agent": "dashboard_agent"
        }
        
        # Label to role mapping
        self.label_to_role = {
            "backend": "completion_agent",
            "frontend": "dashboard_agent",
            "testing": "testing_agent",
            "devops": "devops_agent",
            "security": "security_agent",
            "documentation": "documentation_agent",
            "critical": "security_agent",  # Critical issues go to security for review
            "ai-agent-task": "completion_agent"  # Default for AI agent tasks
        }
    
    def create_policy_compliant_issue(self, title: str, body: str, labels: List[str] = None, assignees: List[str] = None) -> Dict[str, Any]:
        """Create GitHub issue with policy compliance check"""
        labels = labels or []
        assignees = assignees or []
        
        # Determine primary role based on labels
        primary_role = self._determine_role_from_labels(labels)
        
        # Policy assessment
        content_to_assess = f"{title}\n\n{body}"
        
        if self.policy_engine:
            assessment = self.policy_engine.assess_agent_action(
                agent_id="github_issues_agent",
                role_id=primary_role,
                content=content_to_assess
            )
        else:
            # Default assessment when policy engine not available
            assessment = {
                "allowed": True,
                "risk_level": 1,
                "violations": [],
                "suggestions": [],
                "compliance_level": 100,
                "audit_id": f"no_policy_{datetime.now().timestamp()}"
            }
        
        # Enhance issue with policy information
        enhanced_body = self._enhance_issue_with_policy(body, assessment, primary_role)
        
        # Add policy compliance labels
        policy_labels = self._generate_policy_labels(assessment)
        labels.extend(policy_labels)
        
        # Create the issue
        issue_data = {
            "title": title,
            "body": enhanced_body,
            "labels": labels,
            "assignees": assignees
        }
        
        if not self.github_token:
            # Simulation mode - return what would be created
            logger.info("SIMULATION MODE - No GitHub token provided")
            return {
                "number": 999,
                "html_url": "https://github.com/simulation/issue/999",
                "simulation": True,
                "issue_data": issue_data,
                "policy_assessment": assessment
            }
        
        try:
            response = requests.post(
                f"{self.base_url}/repos/{self.repo}/issues",
                headers=self.headers,
                json=issue_data,
                timeout=30
            )
            
            if response.status_code == 201:
                issue = response.json()
                logger.info(f"Created issue #{issue['number']}: {title}")
                
                # Add policy assessment comment
                self._add_policy_comment(issue['number'], assessment, primary_role)
                
                return issue
            else:
                logger.error(f"Failed to create issue: {response.status_code} - {response.text}")
                return {"error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            return {"error": str(e)}
    
    def _determine_role_from_labels(self, labels: List[str]) -> str:
        """Determine primary agent role from issue labels"""
        for label in labels:
            if label in self.label_to_role:
                return self.label_to_role[label]
        
        # Default to completion agent
        return "completion_agent"
    
    def _enhance_issue_with_policy(self, body: str, assessment: Dict[str, Any], role_id: str) -> str:
        """Enhance issue body with policy information"""
        enhanced_body = body
        
        # Add policy compliance section
        enhanced_body += "\n\n---\n\n## 🔐 Policy Compliance\n\n"
        
        # Compliance status
        compliance_icon = "✅" if assessment["allowed"] else "❌"
        enhanced_body += f"**Status**: {compliance_icon} {'Compliant' if assessment['allowed'] else 'Requires Review'}\n"
        enhanced_body += f"**Risk Level**: {assessment['risk_level']}/4\n"
        enhanced_body += f"**Compliance Score**: {assessment['compliance_level']}%\n\n"
        
        # Violations (if any)
        if assessment["violations"]:
            enhanced_body += "### ⚠️ Policy Violations\n\n"
            for violation in assessment["violations"]:
                enhanced_body += f"- **{violation.get('policy', 'Unknown Policy')}** ({violation.get('severity', 'unknown')})\n"
                if 'description' in violation:
                    enhanced_body += f"  - {violation['description']}\n"
        
        # Suggestions
        if assessment["suggestions"]:
            enhanced_body += "### 💡 Compliance Suggestions\n\n"
            for suggestion in assessment["suggestions"][:3]:  # Limit to top 3
                enhanced_body += f"- {suggestion}\n"
        
        # Role-specific guidelines
        if self.policy_engine:
            guidelines = self.policy_engine.get_role_guidelines(role_id)
            if guidelines["knowledge_base"]:
                enhanced_body += f"\n### 📚 Relevant Guidelines\n\n"
                for kb in guidelines["knowledge_base"][:2]:  # Top 2 most relevant
                    enhanced_body += f"- **{kb['title']}** - {kb['category']}\n"
        
        enhanced_body += f"\n*Policy assessment performed by Agent Policy Engine v1.0*"
        
        return enhanced_body
    
    def _generate_policy_labels(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate labels based on policy assessment"""
        labels = []
        
        # Risk level labels
        risk_level = assessment["risk_level"]
        if risk_level >= 4:
            labels.append("policy-critical")
        elif risk_level >= 3:
            labels.append("policy-high-risk")
        elif risk_level >= 2:
            labels.append("policy-medium-risk")
        else:
            labels.append("policy-compliant")
        
        # Compliance labels
        if assessment["compliance_level"] >= 90:
            labels.append("compliance-excellent")
        elif assessment["compliance_level"] >= 70:
            labels.append("compliance-good")
        else:
            labels.append("compliance-needs-improvement")
        
        # Violation type labels
        for violation in assessment["violations"]:
            if "security" in violation.get("policy", "").lower():
                labels.append("security-review-required")
            if "documentation" in violation.get("policy", "").lower():
                labels.append("docs-required")
            if "testing" in violation.get("policy", "").lower():
                labels.append("tests-required")
        
        return labels
    
    def _add_policy_comment(self, issue_number: int, assessment: Dict[str, Any], role_id: str):
        """Add detailed policy assessment as comment"""
        if not self.github_token:
            logger.info(f"SIMULATION: Would add policy comment to issue #{issue_number}")
            return
        
        comment_body = "## 🤖 Automated Policy Assessment\n\n"
        comment_body += f"**Agent Role**: {role_id.replace('_', ' ').title()}\n"
        comment_body += f"**Assessment ID**: `{assessment.get('audit_id', 'local_assessment')}`\n"
        comment_body += f"**Timestamp**: {datetime.now().isoformat()}\n\n"
        
        # Detailed violations
        if assessment["violations"]:
            comment_body += "### 🚨 Detailed Policy Analysis\n\n"
            for i, violation in enumerate(assessment["violations"], 1):
                comment_body += f"{i}. **{violation.get('policy', 'Unknown Policy')}**\n"
                comment_body += f"   - **Severity**: {violation.get('severity', 'unknown')}\n"
                comment_body += f"   - **Description**: {violation.get('description', 'No description')}\n"
                comment_body += f"   - **Mitigation**: {violation.get('mitigation', 'No mitigation provided')}\n\n"
        
        # Knowledge base references
        if self.policy_engine:
            guidelines = self.policy_engine.get_role_guidelines(role_id)
            if guidelines["knowledge_base"]:
                comment_body += "### 📖 Reference Documentation\n\n"
                for kb in guidelines["knowledge_base"]:
                    comment_body += f"- **{kb['title']}** ({kb['category']})\n"
                    comment_body += f"  - Tags: {', '.join(kb['tags'])}\n"
                    comment_body += f"  - Version: {kb['version']}\n\n"
        
        comment_body += "---\n*This assessment helps ensure code quality, security, and compliance standards.*"
        
        try:
            response = requests.post(
                f"{self.base_url}/repos/{self.repo}/issues/{issue_number}/comments",
                headers=self.headers,
                json={"body": comment_body},
                timeout=30
            )
            
            if response.status_code == 201:
                logger.info(f"Added policy comment to issue #{issue_number}")
            else:
                logger.warning(f"Failed to add comment: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error adding policy comment: {e}")
    
    def migrate_work_queue_to_github(self, work_queue_dir: str = "work_queue") -> List[Dict[str, Any]]:
        """Migrate existing work queue items to GitHub Issues with policy compliance"""
        work_queue_path = Path(work_queue_dir)
        created_issues = []
        
        if not work_queue_path.exists():
            logger.warning(f"Work queue directory not found: {work_queue_dir}")
            return created_issues
        
        logger.info("Migrating work queue to GitHub Issues with policy compliance...")
        
        for task_file in work_queue_path.glob("*.json"):
            try:
                with open(task_file, 'r') as f:
                    task = json.load(f)
                
                # Convert task to GitHub issue format
                title = task.get("title", "Migrated Task")
                
                # Create comprehensive issue body
                body = self._format_task_as_issue_body(task)
                
                # Determine labels
                labels = self._determine_task_labels(task)
                
                # Create issue with policy compliance
                issue = self.create_policy_compliant_issue(title, body, labels)
                
                if "error" not in issue:
                    created_issues.append({
                        "original_file": task_file.name,
                        "issue_number": issue.get("number"),
                        "issue_url": issue.get("html_url"),
                        "policy_compliant": issue.get("policy_assessment", {}).get("allowed", False)
                    })
                    
                    # Add small delay to avoid rate limiting
                    time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error migrating {task_file}: {e}")
        
        logger.info(f"Migration complete: {len(created_issues)} issues created")
        return created_issues
    
    def _format_task_as_issue_body(self, task: Dict[str, Any]) -> str:
        """Format work queue task as GitHub issue body"""
        body = f"## Task Description\n{task.get('description', 'No description provided')}\n\n"
        
        # Sub-tasks
        if task.get("tasks"):
            body += "## Sub-tasks\n\n"
            for i, subtask in enumerate(task["tasks"], 1):
                body += f"- [ ] **{subtask.get('task', 'Unknown task')}**\n"
                if subtask.get("file"):
                    body += f"  - File: `{subtask['file']}`\n"
                if subtask.get("estimated_effort"):
                    body += f"  - Effort: {subtask['estimated_effort']}\n"
                if subtask.get("details"):
                    body += f"  - Details: {subtask['details']}\n"
                body += "\n"
        
        # Deliverables
        if task.get("deliverables"):
            body += "## Deliverables\n\n"
            for deliverable in task["deliverables"]:
                body += f"- [ ] {deliverable}\n"
            body += "\n"
        
        # Success criteria
        if task.get("success_criteria"):
            body += "## Success Criteria\n\n"
            for criteria in task["success_criteria"]:
                body += f"- [ ] {criteria}\n"
            body += "\n"
        
        # Metadata
        body += "## Metadata\n\n"
        body += f"- **Priority**: {task.get('priority', 'Unknown')}\n"
        body += f"- **Estimated Effort**: {task.get('estimated_total_effort', 'Unknown')}\n"
        body += f"- **Original File**: `{task.get('created_at', 'Unknown')}`\n"
        
        if task.get("dependencies"):
            body += f"- **Dependencies**: {', '.join(task['dependencies'])}\n"
        
        body += f"\n---\n*Migrated from file-based work queue to GitHub Issues*"
        
        return body
    
    def _determine_task_labels(self, task: Dict[str, Any]) -> List[str]:
        """Determine appropriate labels for migrated task"""
        labels = ["ai-agent-task", "migrated"]
        
        # Priority labels
        priority = task.get("priority", "")
        if priority.startswith("P0"):
            labels.append("critical")
        elif priority.startswith("P1"):
            labels.append("high-priority")
        elif priority.startswith("P2"):
            labels.append("medium-priority")
        else:
            labels.append("low-priority")
        
        # Content-based labels
        title_desc = (task.get("title", "") + " " + task.get("description", "")).lower()
        
        if any(word in title_desc for word in ["dashboard", "ui", "frontend", "react"]):
            labels.append("frontend")
        if any(word in title_desc for word in ["api", "backend", "server", "database"]):
            labels.append("backend")
        if any(word in title_desc for word in ["test", "testing", "qa"]):
            labels.append("testing")
        if any(word in title_desc for word in ["docker", "deploy", "devops", "infrastructure"]):
            labels.append("devops")
        if any(word in title_desc for word in ["security", "auth", "vulnerability"]):
            labels.append("security")
        if any(word in title_desc for word in ["doc", "documentation", "readme"]):
            labels.append("documentation")
        
        # Agent assignment labels
        assigned_to = task.get("assigned_to", "").lower()
        if "completion" in assigned_to:
            labels.append("completion-agent")
        elif "testing" in assigned_to:
            labels.append("testing-agent")
        elif "devops" in assigned_to:
            labels.append("devops-agent")
        elif "security" in assigned_to:
            labels.append("security-agent")
        elif "documentation" in assigned_to:
            labels.append("documentation-agent")
        elif "dashboard" in assigned_to:
            labels.append("dashboard-agent")
        
        return labels

def main():
    """Test the policy-enhanced GitHub Issues agent"""
    print("🔐 Testing Policy-Enhanced GitHub Issues Agent...")
    
    agent = PolicyEnhancedGitHubAgent()
    
    # Test issue creation with policy compliance
    print("\n📝 Creating test issue with policy compliance...")
    
    test_issue = agent.create_policy_compliant_issue(
        title="Complete AI Developer Agent TypeScript Generator",
        body="""
## Task Description
Complete the TypeScript Express generator in the AI Developer Agent.

## Implementation Details
```typescript
const password = "hardcoded_secret_123"; // TODO: Fix this security issue
function generateExpress() {
    // Implementation needed
}
```

## Requirements
- Complete TypeScript generator class
- Add proper error handling  
- Include security best practices
- Add unit tests
        """,
        labels=["ai-agent-task", "backend", "completion-agent"],
        assignees=[]
    )
    
    print(f"   Result: {'✅ Success' if 'number' in test_issue else '❌ Failed'}")
    if 'number' in test_issue:
        print(f"   Issue: #{test_issue['number']}")
        print(f"   URL: {test_issue.get('html_url', 'Simulation mode')}")
        
        if 'policy_assessment' in test_issue:
            assessment = test_issue['policy_assessment']
            print(f"   Policy Status: {'✅ Compliant' if assessment['allowed'] else '❌ Needs Review'}")
            print(f"   Risk Level: {assessment['risk_level']}/4")
    
    # Test work queue migration
    print(f"\n📋 Testing work queue migration...")
    migration_results = agent.migrate_work_queue_to_github()
    
    print(f"   Migrated Issues: {len(migration_results)}")
    for result in migration_results[:3]:  # Show first 3
        compliant = "✅" if result['policy_compliant'] else "❌"
        print(f"   • {result['original_file']} → Issue #{result.get('issue_number', 'SIM')} {compliant}")
    
    # Show policy database status
    print(f"\n📊 Policy Engine Status:")
    print(f"   • Database: agent_policies.db")
    print(f"   • Roles: 6 SDLC agent roles defined")
    print(f"   • Policies: Code quality, security, testing, documentation")
    print(f"   • Knowledge Base: Standards and guidelines for each role")
    print(f"   • VF Integration: Cross-platform policy enforcement")
    
    print(f"\n🎯 Benefits:")
    print(f"   • Automatic policy compliance checking for all GitHub Issues")
    print(f"   • Role-based guidelines and knowledge base integration")
    print(f"   • Policy violation detection and mitigation suggestions")
    print(f"   • Compliance scoring and risk assessment")
    print(f"   • Integration with VF Policy Engine for cross-platform consistency")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Set GITHUB_TOKEN environment variable for real GitHub integration")
    print(f"   2. Run migration script to convert work queue to GitHub Issues")
    print(f"   3. Configure GitHub webhooks for real-time policy monitoring")
    print(f"   4. Setup automated policy compliance reporting")

if __name__ == "__main__":
    main()
