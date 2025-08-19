#!/usr/bin/env python3
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
    issues = [
  {
    "title": "CRITICAL: Dashboard Tab Switching & Data Loading Fix",
    "body": "## \ud83e\udd16 AI Agent Task\n\n**Agent Assignment**: GPT4-Dashboard-Agent\n**Priority**: P0-CRITICAL-URGENT\n**Estimated Effort**: 5-8 hours\n\n## \ud83d\udccb Task Description\nDashboard completely broken - tabs not clickable, no data loading\n\n## \u2705 Sub-tasks\n1. **Fix Dashboard Tab Switching**\n   - File: `comprehensive-tabbed-dashboard.py`\n   - Effort: 1-2 hours\n   - Details: Debug and fix tab navigation - tabs not clickable, investigate JavaScript issues\n\n2. **Fix Data Loading Issues**\n   - File: `comprehensive-tabbed-dashboard.py`\n   - Effort: 1-2 hours\n   - Details: Debug data not loading in dashboard, check WebSocket connections and API endpoints\n\n3. **Implement Playwright Test Suite**\n   - File: `tests/dashboard_playwright_tests.py`\n   - Effort: 2-3 hours\n   - Details: Create comprehensive Playwright tests for tab switching, data loading, and UI interactions\n\n4. **Dashboard Health Monitoring**\n   - File: `dashboard_health_checker.py`\n   - Effort: 1 hour\n   - Details: Create automated health checks for dashboard functionality\n\n\n\n## \ud83c\udfaf Deliverables\n\n\n## \u2728 Success Criteria\n\n\n## \ud83d\udd17 Dependencies\n\n\n---\n**Automation**: This issue will be automatically assigned to the appropriate AI agent based on labels.\n**Progress Tracking**: Update progress using GitHub's built-in project boards and milestones.\n**Integration**: Connected to agent coordination system via GitHub Issues Agent.\n\n/label ai-agent-task critical frontend\n/assign @dashboard-agent",
    "labels": [
      "ai-agent-task",
      "critical",
      "frontend"
    ],
    "assignees": [],
    "milestone": null,
    "original_file": "2025-08-18T14:24:12.419366",
    "priority": "P0-CRITICAL-URGENT",
    "agent": "GPT4-Dashboard-Agent"
  },
  {
    "title": "Production Deployment Infrastructure",
    "body": "## \ud83e\udd16 AI Agent Task\n\n**Agent Assignment**: GPT4-DevOps-Agent\n**Priority**: P1-HIGH\n**Estimated Effort**: 6.5 hours\n\n## \ud83d\udccb Task Description\nCreate production-ready deployment infrastructure\n\n## \u2705 Sub-tasks\n1. **Docker Configuration**\n   - File: `Dockerfile`\n   - Effort: 1 hour\n   - Details: Production Dockerfile for AI Developer Agent\n\n2. **Kubernetes Manifests**\n   - File: `k8s/`\n   - Effort: 2 hours\n   - Details: Kubernetes deployment, service, and ingress manifests\n\n3. **CI/CD Pipeline**\n   - File: `.github/workflows/`\n   - Effort: 2 hours\n   - Details: GitHub Actions for automated testing and deployment\n\n4. **Monitoring Setup**\n   - File: `monitoring/`\n   - Effort: 1.5 hours\n   - Details: Prometheus, Grafana, and logging configuration\n\n\n\n## \ud83c\udfaf Deliverables\n- Production Docker image\n- Kubernetes deployment manifests\n- CI/CD pipeline operational\n- Monitoring and alerting setup\n\n\n## \u2728 Success Criteria\n- One-click deployment to production\n- Automated testing in CI/CD\n- Health monitoring operational\n- Scalable and resilient infrastructure\n\n\n## \ud83d\udd17 Dependencies\nClaude Opus AI Developer Agent (75% complete)\n\n---\n**Automation**: This issue will be automatically assigned to the appropriate AI agent based on labels.\n**Progress Tracking**: Update progress using GitHub's built-in project boards and milestones.\n**Integration**: Connected to agent coordination system via GitHub Issues Agent.\n\n/label ai-agent-task high-priority devops\n/assign @devops-agent",
    "labels": [
      "ai-agent-task",
      "high-priority",
      "devops"
    ],
    "assignees": [],
    "milestone": null,
    "original_file": "2025-08-18T14:12:45.943566",
    "priority": "P1-HIGH",
    "agent": "GPT4-DevOps-Agent"
  },
  {
    "title": "Complete Documentation Suite",
    "body": "## \ud83e\udd16 AI Agent Task\n\n**Agent Assignment**: GPT4-Documentation-Agent\n**Priority**: P1-HIGH\n**Estimated Effort**: 7.0 hours\n\n## \ud83d\udccb Task Description\nCreate comprehensive documentation for AI Developer Agent\n\n## \u2705 Sub-tasks\n1. **API Documentation**\n   - File: `docs/API_REFERENCE.md`\n   - Effort: 2 hours\n   - Details: Complete API reference for AI Developer Agent\n\n2. **User Guide**\n   - File: `docs/USER_GUIDE.md`\n   - Effort: 2 hours\n   - Details: Step-by-step guide for using the AI Developer Agent\n\n3. **Architecture Documentation**\n   - File: `docs/ARCHITECTURE.md`\n   - Effort: 1.5 hours\n   - Details: Technical architecture and design decisions\n\n4. **Integration Examples**\n   - File: `docs/EXAMPLES.md`\n   - Effort: 1.5 hours\n   - Details: Real-world integration examples and use cases\n\n\n\n## \ud83c\udfaf Deliverables\n- Complete API documentation\n- User guide with examples\n- Architecture documentation\n- Integration examples and tutorials\n\n\n## \u2728 Success Criteria\n- Documentation covers all features\n- Examples are functional and tested\n- Clear setup and usage instructions\n- Architecture decisions documented\n\n\n## \ud83d\udd17 Dependencies\nClaude Opus AI Developer Agent (75% complete)\n\n---\n**Automation**: This issue will be automatically assigned to the appropriate AI agent based on labels.\n**Progress Tracking**: Update progress using GitHub's built-in project boards and milestones.\n**Integration**: Connected to agent coordination system via GitHub Issues Agent.\n\n/label ai-agent-task high-priority frontend documentation\n/assign @documentation-agent",
    "labels": [
      "ai-agent-task",
      "high-priority",
      "frontend",
      "documentation"
    ],
    "assignees": [],
    "milestone": null,
    "original_file": "2025-08-18T14:12:45.935265",
    "priority": "P1-HIGH",
    "agent": "GPT4-Documentation-Agent"
  },
  {
    "title": "Security Analysis and Hardening",
    "body": "## \ud83e\udd16 AI Agent Task\n\n**Agent Assignment**: GPT4-Security-Agent\n**Priority**: P1-HIGH\n**Estimated Effort**: 6.5 hours\n\n## \ud83d\udccb Task Description\nComprehensive security analysis and hardening\n\n## \u2705 Sub-tasks\n1. **Security Scanning**\n   - File: `security_scan.py`\n   - Effort: 2 hours\n   - Details: Automated security scanning of generated code\n\n2. **Authentication/Authorization**\n   - File: `ai-developer-agent.py`\n   - Effort: 2 hours\n   - Details: Add security features to generated projects\n\n3. **Vulnerability Assessment**\n   - File: `security_assessment.md`\n   - Effort: 1.5 hours\n   - Details: Security assessment report and recommendations\n\n4. **Security Best Practices**\n   - File: `docs/SECURITY.md`\n   - Effort: 1 hour\n   - Details: Security guidelines and best practices\n\n\n\n## \ud83c\udfaf Deliverables\n- Automated security scanning\n- Security hardening implementation\n- Vulnerability assessment report\n- Security documentation and guidelines\n\n\n## \u2728 Success Criteria\n- No critical security vulnerabilities\n- Authentication/authorization implemented\n- Security scanning automated\n- Security best practices documented\n\n\n## \ud83d\udd17 Dependencies\nClaude Opus AI Developer Agent (75% complete)\n\n---\n**Automation**: This issue will be automatically assigned to the appropriate AI agent based on labels.\n**Progress Tracking**: Update progress using GitHub's built-in project boards and milestones.\n**Integration**: Connected to agent coordination system via GitHub Issues Agent.\n\n/label ai-agent-task high-priority security\n/assign @security-agent",
    "labels": [
      "ai-agent-task",
      "high-priority",
      "security"
    ],
    "assignees": [],
    "milestone": null,
    "original_file": "2025-08-18T14:12:45.953043",
    "priority": "P1-HIGH",
    "agent": "GPT4-Security-Agent"
  },
  {
    "title": "Untitled Task",
    "body": "## \ud83e\udd16 AI Agent Task\n\n**Agent Assignment**: Unassigned\n**Priority**: HIGH\n**Estimated Effort**: Unknown\n\n## \ud83d\udccb Task Description\nNo description\n\n## \u2705 Sub-tasks\n\n\n## \ud83c\udfaf Deliverables\n\n\n## \u2728 Success Criteria\n\n\n## \ud83d\udd17 Dependencies\n\n\n---\n**Automation**: This issue will be automatically assigned to the appropriate AI agent based on labels.\n**Progress Tracking**: Update progress using GitHub's built-in project boards and milestones.\n**Integration**: Connected to agent coordination system via GitHub Issues Agent.\n\n/label ai-agent-task\n/assign ",
    "labels": [
      "ai-agent-task"
    ],
    "assignees": [],
    "milestone": null,
    "original_file": "unknown",
    "priority": "HIGH",
    "agent": ""
  },
  {
    "title": "Untitled Task",
    "body": "## \ud83e\udd16 AI Agent Task\n\n**Agent Assignment**: Unassigned\n**Priority**: HIGH\n**Estimated Effort**: Unknown\n\n## \ud83d\udccb Task Description\nNo description\n\n## \u2705 Sub-tasks\n\n\n## \ud83c\udfaf Deliverables\n\n\n## \u2728 Success Criteria\n\n\n## \ud83d\udd17 Dependencies\n\n\n---\n**Automation**: This issue will be automatically assigned to the appropriate AI agent based on labels.\n**Progress Tracking**: Update progress using GitHub's built-in project boards and milestones.\n**Integration**: Connected to agent coordination system via GitHub Issues Agent.\n\n/label ai-agent-task\n/assign ",
    "labels": [
      "ai-agent-task"
    ],
    "assignees": [],
    "milestone": null,
    "original_file": "unknown",
    "priority": "HIGH",
    "agent": ""
  }
]
    
    print(f"🚀 Creating {len(issues)} GitHub issues...")
    created = create_github_issues(issues, GITHUB_TOKEN, REPOSITORY)
    print(f"✅ Successfully created {len(created)} issues")

if __name__ == "__main__":
    main()
