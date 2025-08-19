#!/usr/bin/env python3
"""Create all GitHub issues for delegation"""

import subprocess
import json
from datetime import datetime

def create_issues():
    repo = "NiroAgentV2/business-operations"
    issues = []
    
    # Simplified issue list
    issue_list = [
        ("Build Monitoring Dashboard", "Create real-time dashboard for agent monitoring", ["priority/P0", "dashboard"]),
        ("Deploy to AWS", "Deploy all agents to AWS Lambda/Fargate", ["priority/P0", "aws"]),
        ("Setup Monitoring", "Implement 24/7 monitoring system", ["priority/P0", "monitoring"]),
        ("GitHub Actions", "Configure CI/CD automation", ["priority/P1", "automation"]),
        ("Agent Self-Improvement", "Implement learning system", ["priority/P1", "improvement"]),
        ("Integration Testing", "Complete system testing", ["priority/P1", "testing"]),
        ("Security Audit", "Security hardening", ["priority/P1", "security"]),
        ("Documentation", "Create complete docs", ["priority/P2", "docs"]),
        ("Cost Optimization", "Reduce operational costs", ["priority/P2", "finance"]),
        ("Success Metrics", "Implement KPI tracking", ["priority/P2", "metrics"])
    ]
    
    print("Creating GitHub Issues...")
    print("="*60)
    
    for title, body, labels in issue_list:
        print(f"\nCreating: {title}")
        
        cmd = [
            "gh", "issue", "create",
            "--repo", repo,
            "--title", title,
            "--body", body
        ]
        
        for label in labels:
            cmd.extend(["--label", label])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                url = result.stdout.strip()
                issues.append(url)
                print(f"  [OK] {url}")
            else:
                print(f"  [SKIP] May already exist")
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    print(f"\n[DONE] Created/checked {len(issue_list)} issues")
    return issues

if __name__ == "__main__":
    create_issues()