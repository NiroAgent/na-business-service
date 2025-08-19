
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
