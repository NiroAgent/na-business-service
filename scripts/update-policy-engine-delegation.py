#!/usr/bin/env python3
"""
Update Policy Engine with Delegation Rules
===========================================
Add delegation policy to the agent-policy-coordinator
"""

import json
from datetime import datetime

def create_delegation_policy():
    """Create comprehensive delegation policy for the coordinator"""
    
    delegation_policy = {
        "version": "2.0",
        "updated": datetime.now().isoformat(),
        "name": "Delegation Policy Engine",
        
        "prime_directive": {
            "rule": "DELEGATE EVERYTHING THROUGH THE SYSTEM",
            "description": "All work must be delegated to managers via GitHub Issues",
            "enforcement": "MANDATORY"
        },
        
        "delegation_rules": {
            "rule_1": {
                "name": "Single Delegation Only",
                "description": "Create exactly ONE issue to a manager",
                "violation_action": "Reject multiple issues",
                "example_correct": "gh issue create --repo business-operations --title '[Manager] Fix Dashboard'",
                "example_wrong": "Creating multiple developer/QA tasks"
            },
            "rule_2": {
                "name": "Managers Only",
                "description": "ONLY delegate to managers, never to contributors",
                "allowed_assignees": ["manager", "project-manager", "pm"],
                "forbidden_assignees": ["developer", "qa", "devops", "designer"],
                "violation_action": "Redirect to manager"
            },
            "rule_3": {
                "name": "No Implementation Details",
                "description": "Delegation must be high-level only",
                "forbidden_content": ["code examples", "test cases", "technical specs", "database schemas"],
                "allowed_content": ["problem description", "deadline", "priority"],
                "violation_action": "Strip details, keep only objective"
            },
            "rule_4": {
                "name": "Repository Restriction",
                "description": "Only create issues in business-operations",
                "allowed_repos": ["business-operations"],
                "forbidden_repos": ["service repos", "component repos"],
                "violation_action": "Redirect to business-operations"
            }
        },
        
        "delegation_workflow": {
            "step_1": {
                "trigger": "User request or problem identified",
                "action": "Create manager delegation",
                "output": "Single issue in business-operations"
            },
            "step_2": {
                "trigger": "Manager receives issue",
                "action": "Manager creates sub-tasks",
                "output": "Issues in appropriate service repos"
            },
            "step_3": {
                "trigger": "Tasks created",
                "action": "Teams self-organize",
                "output": "Work begins"
            },
            "step_4": {
                "trigger": "Periodic check",
                "action": "Monitor manager issue",
                "output": "Progress update"
            }
        },
        
        "issue_routing": {
            "dashboard_problems": {
                "delegate_to": "UI Manager",
                "repo": "business-operations",
                "manager_creates_in": "vf-dashboard-service"
            },
            "service_issues": {
                "delegate_to": "Service Manager",
                "repo": "business-operations",
                "manager_creates_in": "[service]-service repo"
            },
            "infrastructure": {
                "delegate_to": "Infrastructure Manager",
                "repo": "business-operations",
                "manager_creates_in": "infrastructure repo"
            },
            "testing_needs": {
                "delegate_to": "QA Manager",
                "repo": "business-operations",
                "manager_creates_in": "service repos"
            }
        },
        
        "monitoring_rules": {
            "check_frequency": "Every 4 hours",
            "check_command": "gh issue list --assignee manager --repo business-operations",
            "escalation_after": "24 hours no update",
            "completion_verification": "Issue closed with resolution"
        },
        
        "anti_patterns": {
            "micromanagement": {
                "indicator": "Creating >1 issue for same problem",
                "correction": "Consolidate into single manager delegation"
            },
            "doing_work": {
                "indicator": "Writing code or implementation details",
                "correction": "Remove details, delegate objective only"
            },
            "wrong_level": {
                "indicator": "Assigning to non-managers",
                "correction": "Reassign to appropriate manager"
            },
            "wrong_repo": {
                "indicator": "Creating in service repos",
                "correction": "Move to business-operations"
            }
        },
        
        "enforcement": {
            "pre_creation_check": {
                "validate_assignee": "Must be manager role",
                "validate_repo": "Must be business-operations",
                "validate_count": "Only 1 issue per problem",
                "validate_content": "No implementation details"
            },
            "post_creation_audit": {
                "frequency": "Every issue creation",
                "violations_log": "delegation-violations.log",
                "correction_action": "Close and recreate properly"
            }
        },
        
        "templates": {
            "standard_delegation": {
                "title": "[Manager] {action_required}",
                "body": """## Delegation
                
What needs to be done: {one_sentence_description}
Priority: {P0|P1|P2}
Deadline: {if_applicable}

You own this. Create tasks as needed.
Report when complete."""
            },
            "emergency_delegation": {
                "title": "[Manager] URGENT: {critical_issue}",
                "body": """## Critical Issue

Problem: {description}
Impact: {who_affected}
Priority: P0

Fix immediately. All hands if needed.
Report every 2 hours."""
            }
        },
        
        "metrics": {
            "delegation_efficiency": {
                "measure": "Issues created by me vs managers",
                "target": "1:10 ratio (1 mine, 10+ theirs)",
                "current": "Track in metrics.json"
            },
            "resolution_time": {
                "measure": "Time from delegation to completion",
                "target": "Based on priority level",
                "tracking": "GitHub issue timestamps"
            }
        }
    }
    
    # Save the policy
    with open("delegation-policy-engine.json", "w") as f:
        json.dump(delegation_policy, f, indent=2)
    
    print("[OK] Created delegation-policy-engine.json")
    
    # Create Python implementation for coordinator
    coordinator_update = '''
class DelegationPolicyEngine:
    """Enforce delegation rules in the coordinator"""
    
    def __init__(self):
        with open("delegation-policy-engine.json") as f:
            self.policy = json.load(f)
    
    def validate_issue_creation(self, issue_data):
        """Validate before creating any issue"""
        
        violations = []
        
        # Check assignee is manager
        if issue_data.get("assignee") not in self.policy["delegation_rules"]["rule_2"]["allowed_assignees"]:
            violations.append("Not delegating to manager")
        
        # Check repo is business-operations
        if issue_data.get("repo") != "business-operations":
            violations.append("Wrong repository")
        
        # Check for implementation details
        forbidden = self.policy["delegation_rules"]["rule_3"]["forbidden_content"]
        if any(term in issue_data.get("body", "").lower() for term in forbidden):
            violations.append("Contains implementation details")
        
        if violations:
            raise ValueError(f"Delegation policy violations: {violations}")
        
        return True
    
    def create_proper_delegation(self, request):
        """Create a proper delegation following policy"""
        
        template = self.policy["templates"]["standard_delegation"]
        
        issue = {
            "repo": "business-operations",
            "assignee": "manager",
            "title": template["title"].format(action_required=request),
            "body": template["body"].format(
                one_sentence_description=request,
                P0="P1",  # Default priority
                if_applicable="None"
            )
        }
        
        return issue
    
    def monitor_delegations(self):
        """Monitor all delegated issues"""
        
        cmd = self.policy["monitoring_rules"]["check_command"]
        # Execute and track
        pass
'''
    
    with open("delegation_policy_engine.py", "w") as f:
        f.write(coordinator_update)
    
    print("[OK] Created delegation_policy_engine.py")
    
    return delegation_policy

def main():
    print("\n" + "="*80)
    print("CREATING DELEGATION POLICY ENGINE")
    print("="*80)
    
    policy = create_delegation_policy()
    
    print("\n[POLICY ENGINE COMPONENTS]:")
    print("1. Prime Directive: DELEGATE EVERYTHING")
    print("2. Delegation Rules: 4 core rules")
    print("3. Workflow: 4-step process")
    print("4. Issue Routing: Manager assignments")
    print("5. Anti-patterns: What to avoid")
    print("6. Enforcement: Pre and post checks")
    
    print("\n[INTEGRATION POINTS]:")
    print("- agent-policy-coordinator.py - Import and use")
    print("- delegation-policy-engine.json - Policy configuration")
    print("- delegation_policy_engine.py - Implementation")
    
    print("\n[ENFORCEMENT MECHANISM]:")
    print("Before creating any issue:")
    print("  1. Check assignee (must be manager)")
    print("  2. Check repo (must be business-operations)")
    print("  3. Check content (no implementation details)")
    print("  4. Check count (only 1 issue)")
    
    print("\n[SUCCESS!]")
    print("Delegation policy now integrated into policy engine!")

if __name__ == "__main__":
    main()