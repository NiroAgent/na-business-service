#!/usr/bin/env python3
"""
Agent Accountability Tracker
Verifies agents are ACTUALLY doing their assigned work
"""

import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

class AgentAccountabilityTracker:
    """Track and verify agent work completion"""
    
    def __init__(self):
        self.evidence = {
            "test_execution": [],
            "bug_issues_created": [],
            "fix_commits": [],
            "agent_activity": []
        }
        
    def check_test_execution_evidence(self):
        """Look for proof tests were actually run"""
        print("\n[CHECKING TEST EXECUTION EVIDENCE]")
        print("-" * 50)
        
        # Check for recent playwright reports
        test_reports = [
            "VisualForgeMediaV2/*/mfe/playwright-report/index.html",
            "VisualForgeMediaV2/*/mfe/test-results/*.json",
            "NiroSubs-V2/*/test-results/*.json",
            "NiroSubs-V2/*/playwright-report/index.html"
        ]
        
        recent_tests = []
        for pattern in test_reports:
            reports = Path(".").glob(pattern)
            for report in reports:
                stat = report.stat()
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                age = datetime.now() - mod_time
                
                if age < timedelta(hours=24):
                    recent_tests.append({
                        "file": str(report),
                        "modified": mod_time.isoformat(),
                        "age_hours": age.total_seconds() / 3600
                    })
        
        if recent_tests:
            print(f"[OK] Found {len(recent_tests)} recent test executions")
            for test in recent_tests:
                print(f"  - {test['file']}: {test['age_hours']:.1f} hours ago")
        else:
            print("[FAIL] NO RECENT TEST EXECUTIONS FOUND!")
            print("  Agents are NOT running tests as instructed!")
        
        return recent_tests
    
    def check_bug_issues_created(self):
        """Check if bugs from tests are being logged as GitHub issues"""
        print("\n[CHECKING BUG ISSUES CREATED]")
        print("-" * 50)
        
        repos = [
            "VisualForgeMediaV2/vf-dashboard-service",
            "VisualForgeMediaV2/vf-audio-service",
            "VisualForgeMediaV2/vf-video-service",
            "VisualForgeMediaV2/business-operations",
            "NiroSubs-V2/nirosubs-v2-platform"
        ]
        
        bug_issues = []
        for repo in repos:
            cmd = [
                "gh", "issue", "list",
                "--repo", repo,
                "--label", "bug",
                "--json", "number,title,createdAt",
                "--limit", "20"
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout:
                    issues = json.loads(result.stdout)
                    for issue in issues:
                        created = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00'))
                        age = datetime.now(created.tzinfo) - created
                        if age < timedelta(hours=24):
                            bug_issues.append({
                                "repo": repo,
                                "number": issue['number'],
                                "title": issue['title'],
                                "age_hours": age.total_seconds() / 3600
                            })
            except:
                pass
        
        if bug_issues:
            print(f"[OK] Found {len(bug_issues)} bug issues created in last 24h")
            for bug in bug_issues:
                print(f"  - {bug['repo']}#{bug['number']}: {bug['title'][:50]}...")
        else:
            print("[FAIL] NO BUG ISSUES CREATED FROM TESTS!")
            print("  Agents are NOT logging bugs they find!")
        
        return bug_issues
    
    def check_fix_commits(self):
        """Check for commits that fix bugs"""
        print("\n[CHECKING BUG FIX COMMITS]")
        print("-" * 50)
        
        repos = [
            "VisualForgeMediaV2",
            "NiroSubs-V2"
        ]
        
        fix_commits = []
        for repo in repos:
            try:
                cmd = ["git", "log", "--oneline", "--since=24 hours ago", "--grep=fix", "-i"]
                result = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
                
                if result.stdout:
                    commits = result.stdout.strip().split('\n')
                    fix_commits.extend([f"{repo}: {c}" for c in commits if c])
            except:
                pass
        
        if fix_commits:
            print(f"[OK] Found {len(fix_commits)} fix commits in last 24h")
            for commit in fix_commits[:5]:
                print(f"  - {commit}")
        else:
            print("[FAIL] NO BUG FIX COMMITS FOUND!")
            print("  Developers are NOT fixing bugs!")
        
        return fix_commits
    
    def check_agent_activity(self):
        """Check if agent processes are actually running"""
        print("\n[CHECKING AGENT PROCESS ACTIVITY]")
        print("-" * 50)
        
        cmd = ["ps", "aux"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        agent_processes = []
        agent_names = ["qa", "developer", "devops", "operations", "test", "agent"]
        
        for line in result.stdout.split('\n'):
            for agent in agent_names:
                if agent in line.lower() and "python" in line.lower():
                    agent_processes.append(line[:100])
        
        if agent_processes:
            print(f"[OK] Found {len(agent_processes)} agent processes running")
            for proc in agent_processes[:3]:
                print(f"  - {proc}")
        else:
            print("[FAIL] NO AGENT PROCESSES RUNNING!")
            print("  Agents are NOT active!")
        
        return agent_processes
    
    def generate_accountability_report(self):
        """Generate comprehensive accountability report"""
        print("\n" + "=" * 80)
        print("AGENT ACCOUNTABILITY REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().isoformat()}")
        print("Purpose: Verify agents are ACTUALLY doing their assigned work\n")
        
        # Gather evidence
        test_evidence = self.check_test_execution_evidence()
        bug_evidence = self.check_bug_issues_created()
        fix_evidence = self.check_fix_commits()
        process_evidence = self.check_agent_activity()
        
        # Summary
        print("\n[ACCOUNTABILITY SUMMARY]")
        print("-" * 50)
        
        accountability_score = 0
        max_score = 4
        
        if test_evidence:
            accountability_score += 1
            print("[OK] Test Execution: VERIFIED")
        else:
            print("[FAIL] Test Execution: NOT HAPPENING")
        
        if bug_evidence:
            accountability_score += 1
            print("[OK] Bug Logging: VERIFIED")
        else:
            print("[FAIL] Bug Logging: NOT HAPPENING")
        
        if fix_evidence:
            accountability_score += 1
            print("[OK] Bug Fixes: VERIFIED")
        else:
            print("[FAIL] Bug Fixes: NOT HAPPENING")
        
        if process_evidence:
            accountability_score += 1
            print("[OK] Agent Processes: RUNNING")
        else:
            print("[FAIL] Agent Processes: NOT RUNNING")
        
        print(f"\nAccountability Score: {accountability_score}/{max_score}")
        
        # Enforcement Actions
        print("\n[ENFORCEMENT ACTIONS REQUIRED]")
        print("-" * 50)
        
        if accountability_score < max_score:
            print("CRITICAL: Agents are NOT following directives!")
            print("\nImmediate Actions:")
            print("1. Start agent processes NOW")
            print("2. Run Playwright tests IMMEDIATELY")
            print("3. Create GitHub issues for EVERY bug found")
            print("4. Commit fixes with clear messages")
            print("5. Generate test reports as evidence")
            
            print("\nCoordinator Must:")
            print("- Escalate to management")
            print("- Reassign work to active agents")
            print("- Implement hourly check-ins")
            print("- Require evidence of work completed")
        else:
            print("All agents working as directed. Continue monitoring.")
        
        print("\n" + "=" * 80)
        print("END OF ACCOUNTABILITY REPORT")
        print("=" * 80)
        
        # Save report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "accountability_score": accountability_score,
            "max_score": max_score,
            "evidence": {
                "test_executions": len(test_evidence),
                "bug_issues": len(bug_evidence),
                "fix_commits": len(fix_evidence),
                "agent_processes": len(process_evidence)
            },
            "compliance": accountability_score == max_score
        }
        
        with open("accountability_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        return report_data

if __name__ == "__main__":
    tracker = AgentAccountabilityTracker()
    
    print("[COORDINATOR] Running Agent Accountability Check")
    print("[COORDINATOR] Verifying agents are ACTUALLY working\n")
    
    report = tracker.generate_accountability_report()
    
    if report["accountability_score"] < report["max_score"]:
        print("\n[ALERT] AGENTS ARE NOT COMPLYING WITH DIRECTIVES!")
        print("[ACTION] Immediate intervention required!")
    else:
        print("\n[OK] Agents are working as directed")
    
    print("\nReport saved to accountability_report.json")