#!/usr/bin/env python3
"""
Agent Compliance Monitoring System
===================================
Monitors PM story creation and agent processing to ensure
architectural standards compliance.
"""

import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class AgentComplianceMonitor:
    """Monitor agent compliance with architectural standards"""
    
    def __init__(self):
        self.repo = "NiroAgentV2/business-operations"
        self.monitoring_data = {
            "pm_stories": [],
            "architect_reviews": [],
            "agent_processing": [],
            "violations": []
        }
        
    def check_story_quality(self, issue: Dict) -> Dict:
        """Check if PM created story has all required elements"""
        
        required_elements = {
            "description": False,
            "tasks": False,
            "acceptance_criteria": False,
            "test_cases": False,
            "assigned_agents": False
        }
        
        body = issue.get("body", "").lower()
        
        # Check for required sections
        if "description" in body or "objective" in body:
            required_elements["description"] = True
        if "tasks" in body or "implementation" in body:
            required_elements["tasks"] = True
        if "acceptance criteria" in body or "given" in body and "when" in body and "then" in body:
            required_elements["acceptance_criteria"] = True
        if "test" in body or "testing" in body:
            required_elements["test_cases"] = True
        if "agent" in body or "assigned" in body:
            required_elements["assigned_agents"] = True
        
        completeness = sum(required_elements.values()) / len(required_elements) * 100
        
        return {
            "issue_number": issue["number"],
            "title": issue["title"],
            "completeness": completeness,
            "missing_elements": [k for k, v in required_elements.items() if not v],
            "has_architect_review": self.check_architect_review(issue),
            "status": "complete" if completeness >= 80 else "incomplete"
        }
    
    def check_architect_review(self, issue: Dict) -> bool:
        """Check if story has architect approval"""
        
        comments = self.get_issue_comments(issue["number"])
        
        for comment in comments:
            if "architect" in comment.get("author", {}).get("login", "").lower():
                if any(word in comment.get("body", "").lower() 
                      for word in ["approved", "lgtm", "looks good", "+1"]):
                    return True
        
        # Check labels
        labels = [label.get("name", "") for label in issue.get("labels", [])]
        return "architect-approved" in labels
    
    def get_issue_comments(self, issue_number: int) -> List[Dict]:
        """Get comments for an issue"""
        
        try:
            cmd = [
                "gh", "api",
                f"repos/{self.repo}/issues/{issue_number}/comments",
                "--jq", "."
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        
        return []
    
    def check_agent_processing(self) -> Dict:
        """Check if agents are processing stories correctly"""
        
        agent_status = {
            "developer": {"processing": 0, "completed": 0, "compliant": 0},
            "devops": {"processing": 0, "completed": 0, "compliant": 0},
            "qa": {"processing": 0, "completed": 0, "compliant": 0}
        }
        
        try:
            # Get all issues
            cmd = [
                "gh", "issue", "list",
                "--repo", self.repo,
                "--limit", "100",
                "--json", "number,title,body,labels,assignees,state"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                
                for issue in issues:
                    # Check assignees
                    assignees = [a.get("login", "") for a in issue.get("assignees", [])]
                    
                    for assignee in assignees:
                        if "developer" in assignee:
                            agent_status["developer"]["processing"] += 1
                            if issue["state"] == "CLOSED":
                                agent_status["developer"]["completed"] += 1
                            if self.check_architect_review(issue):
                                agent_status["developer"]["compliant"] += 1
                                
                        elif "devops" in assignee:
                            agent_status["devops"]["processing"] += 1
                            if issue["state"] == "CLOSED":
                                agent_status["devops"]["completed"] += 1
                            if self.check_architect_review(issue):
                                agent_status["devops"]["compliant"] += 1
                                
                        elif "qa" in assignee or "test" in assignee:
                            agent_status["qa"]["processing"] += 1
                            if issue["state"] == "CLOSED":
                                agent_status["qa"]["completed"] += 1
                            if self.check_architect_review(issue):
                                agent_status["qa"]["compliant"] += 1
        except Exception as e:
            print(f"Error checking agent processing: {e}")
        
        return agent_status
    
    def generate_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_stories": 0,
                "complete_stories": 0,
                "architect_approved": 0,
                "violations_found": 0
            },
            "pm_compliance": {
                "stories_created": 0,
                "average_completeness": 0,
                "common_missing_elements": []
            },
            "architect_compliance": {
                "stories_reviewed": 0,
                "approval_rate": 0,
                "average_review_time": "N/A"
            },
            "agent_compliance": {},
            "violations": [],
            "recommendations": []
        }
        
        try:
            # Get all issues
            cmd = [
                "gh", "issue", "list",
                "--repo", self.repo,
                "--limit", "100",
                "--json", "number,title,body,labels,assignees,state,createdAt"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                
                # Analyze PM stories
                pm_stories = [i for i in issues if any(
                    keyword in i.get("title", "").lower() 
                    for keyword in ["story", "feature", "implement", "build", "create"]
                )]
                
                report["summary"]["total_stories"] = len(pm_stories)
                
                completeness_scores = []
                missing_elements_count = {}
                
                for story in pm_stories:
                    quality = self.check_story_quality(story)
                    completeness_scores.append(quality["completeness"])
                    
                    if quality["completeness"] >= 80:
                        report["summary"]["complete_stories"] += 1
                    
                    if quality["has_architect_review"]:
                        report["summary"]["architect_approved"] += 1
                    else:
                        report["violations"].append({
                            "type": "missing_architect_review",
                            "issue": story["number"],
                            "title": story["title"]
                        })
                    
                    for element in quality["missing_elements"]:
                        missing_elements_count[element] = missing_elements_count.get(element, 0) + 1
                
                # Calculate PM compliance
                if completeness_scores:
                    report["pm_compliance"]["average_completeness"] = sum(completeness_scores) / len(completeness_scores)
                
                report["pm_compliance"]["stories_created"] = len(pm_stories)
                report["pm_compliance"]["common_missing_elements"] = sorted(
                    missing_elements_count.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3]
                
                # Check architect compliance
                report["architect_compliance"]["stories_reviewed"] = report["summary"]["architect_approved"]
                if report["summary"]["total_stories"] > 0:
                    report["architect_compliance"]["approval_rate"] = (
                        report["summary"]["architect_approved"] / report["summary"]["total_stories"] * 100
                    )
                
                # Get agent compliance
                report["agent_compliance"] = self.check_agent_processing()
                
                # Count violations
                report["summary"]["violations_found"] = len(report["violations"])
                
                # Generate recommendations
                if report["pm_compliance"]["average_completeness"] < 80:
                    report["recommendations"].append(
                        "PMs need to include all required elements in stories"
                    )
                
                if report["architect_compliance"]["approval_rate"] < 100:
                    report["recommendations"].append(
                        "Ensure all stories get architect review before implementation"
                    )
                
                for agent, stats in report["agent_compliance"].items():
                    if stats["processing"] > 0:
                        compliance_rate = stats["compliant"] / stats["processing"] * 100
                        if compliance_rate < 100:
                            report["recommendations"].append(
                                f"{agent.capitalize()} agents should wait for architect approval"
                            )
                
        except Exception as e:
            report["error"] = str(e)
        
        return report
    
    def display_report(self, report: Dict):
        """Display compliance report"""
        
        print("\n" + "="*80)
        print("AGENT COMPLIANCE MONITORING REPORT")
        print("="*80)
        print(f"Generated: {report['timestamp']}")
        
        print("\n[SUMMARY]")
        print(f"Total Stories: {report['summary']['total_stories']}")
        print(f"Complete Stories: {report['summary']['complete_stories']}")
        print(f"Architect Approved: {report['summary']['architect_approved']}")
        print(f"Violations Found: {report['summary']['violations_found']}")
        
        print("\n[PM COMPLIANCE]")
        print(f"Stories Created: {report['pm_compliance']['stories_created']}")
        print(f"Average Completeness: {report['pm_compliance']['average_completeness']:.1f}%")
        if report['pm_compliance']['common_missing_elements']:
            print("Common Missing Elements:")
            for element, count in report['pm_compliance']['common_missing_elements']:
                print(f"  - {element}: {count} stories")
        
        print("\n[ARCHITECT COMPLIANCE]")
        print(f"Stories Reviewed: {report['architect_compliance']['stories_reviewed']}")
        print(f"Approval Rate: {report['architect_compliance']['approval_rate']:.1f}%")
        
        print("\n[AGENT COMPLIANCE]")
        for agent, stats in report['agent_compliance'].items():
            if stats['processing'] > 0:
                compliance_rate = stats['compliant'] / stats['processing'] * 100
                print(f"{agent.capitalize()} Agent:")
                print(f"  Processing: {stats['processing']}")
                print(f"  Completed: {stats['completed']}")
                print(f"  Compliant: {stats['compliant']} ({compliance_rate:.1f}%)")
        
        if report['violations']:
            print("\n[VIOLATIONS]")
            for violation in report['violations'][:5]:  # Show first 5
                print(f"  - {violation['type']}: Issue #{violation['issue']}")
        
        if report['recommendations']:
            print("\n[RECOMMENDATIONS]")
            for rec in report['recommendations']:
                print(f"  - {rec}")
    
    def continuous_monitoring(self, interval: int = 300):
        """Run continuous monitoring"""
        
        print("\n" + "="*80)
        print("STARTING CONTINUOUS COMPLIANCE MONITORING")
        print("="*80)
        print(f"Checking every {interval} seconds...")
        
        while True:
            try:
                report = self.generate_compliance_report()
                self.display_report(report)
                
                # Save report
                with open("compliance-report.json", "w") as f:
                    json.dump(report, f, indent=2)
                
                print(f"\n[SAVED] Report saved to compliance-report.json")
                print(f"[NEXT] Next check in {interval} seconds...")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n[STOPPED] Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")
                time.sleep(interval)

def main():
    """Main entry point"""
    monitor = AgentComplianceMonitor()
    
    # Generate initial report
    report = monitor.generate_compliance_report()
    monitor.display_report(report)
    
    # Ask if should continue monitoring
    print("\n" + "="*80)
    print("OPTIONS:")
    print("1. Start continuous monitoring (checks every 5 minutes)")
    print("2. Exit after single report")
    
    # For automated execution, just run single report
    print("\n[INFO] Running single compliance check...")
    
    # Save report
    with open("compliance-report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("[SAVED] Report saved to compliance-report.json")
    print("\n[COMPLETE] Compliance monitoring system ready for continuous operation")

if __name__ == "__main__":
    main()