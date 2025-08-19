#!/usr/bin/env python3
"""
Delegate Issue Reorganization
==============================
Delegate the task of moving issues to proper repositories
"""

import subprocess
from datetime import datetime

def create_reorganization_delegation():
    """Delegate issue reorganization to appropriate agent"""
    
    # DevOps would handle infrastructure/repo organization
    # Manager would handle project organization
    # Let's use DevOps for technical repo management
    
    issue = {
        "title": "[DevOps] Reorganize All Issues to Proper Repositories - RULE #1",
        "body": """## Issue Reorganization Task

### RULE #1: Every project's issues belong in their own repository!

### Current Problem
- Issues are scattered in wrong repos
- Some in business-operations that belong in service repos
- No clear organization

### Your Task
1. **Audit** all existing issues across all repos
2. **Move** issues to their correct repositories:
   - vf-audio-service → Audio-related issues
   - vf-video-service → Video-related issues  
   - vf-image-service → Image-related issues
   - vf-dashboard-service → Dashboard/UI issues
   - vf-auth-service → Authentication issues
   - business-operations → ONLY management/coordination issues

3. **Close** duplicate issues
4. **Create** missing issues in proper repos
5. **Report** completion status

### Migration Rules
- QA test issues → Service repo being tested
- Dev bug fixes → Service repo with the bug
- Feature requests → Service repo getting the feature
- Architecture reviews → business-operations
- Management tasks → business-operations

### Process
```bash
# For each misplaced issue:
1. Create new issue in correct repo
2. Copy all relevant information
3. Add comment: "Moved to [correct-repo]#[issue-number]"
4. Close old issue with reason: "Moved to correct repository"
```

### Expected Outcome
- Each service repo has its own issues
- business-operations only has cross-cutting issues
- Clear ownership and tracking
- No duplicate issues

### Priority: P0 - Do this immediately
### Deadline: Today

### Report back with:
- Number of issues moved
- Final issue count per repo
- Any issues that couldn't be categorized""",
        "repo": "VisualForgeMediaV2/business-operations"
    }
    
    # Alternative: Delegate to Manager instead
    manager_issue = {
        "title": "[Manager] Enforce RULE #1 - Move All Issues to Proper Repositories",
        "body": """## Management Task: Issue Organization

### RULE #1: Issues must be in their proper repositories!

### Your Responsibility
As Project Manager, ensure all issues are in the correct repositories.

### Action Required
1. **Review** all repositories and their issues
2. **Coordinate** with service owners to move issues
3. **Delegate** the actual moving to:
   - DevOps for technical reorganization
   - QA leads for test issues
   - Dev leads for development issues

4. **Enforce** this going forward:
   - Review new issues daily
   - Move misplaced issues immediately
   - Train team on proper issue creation

### Repository Mapping
- Service-specific work → Service repository
- Cross-cutting concerns → business-operations
- Infrastructure → devops-infrastructure repo
- Documentation → docs repo (if exists)

### Success Metrics
- 100% of issues in correct repos
- No new misplaced issues
- Team trained on Rule #1

### Priority: P0
### This is now a permanent responsibility""",
        "repo": "VisualForgeMediaV2/business-operations"
    }
    
    print("\n" + "="*80)
    print("DELEGATING ISSUE REORGANIZATION")
    print("="*80)
    
    # Create the manager delegation (manager coordinates, delegates to DevOps)
    print("\nCreating delegation to Manager (who will coordinate with DevOps)...")
    
    cmd = [
        "gh", "issue", "create",
        "--repo", manager_issue["repo"],
        "--title", manager_issue["title"],
        "--body", manager_issue["body"]
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"[OK] Created: {url}")
            print("\nManager will now:")
            print("1. Review all misplaced issues")
            print("2. Coordinate with DevOps to move them")
            print("3. Enforce Rule #1 going forward")
            return url
        else:
            print(f"[ERROR] {result.stderr}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    return None

def main():
    url = create_reorganization_delegation()
    
    print("\n" + "="*80)
    print("DELEGATION COMPLETE")
    print("="*80)
    
    print("\n[DELEGATION CHAIN]:")
    print("You → Manager: 'Enforce Rule #1'")
    print("Manager → DevOps: 'Move these issues'")
    print("Manager → Team: 'Follow Rule #1'")
    
    print("\n[EXPECTED OUTCOME]:")
    print("- All issues moved to proper repos")
    print("- Rule #1 enforced permanently")
    print("- Manager owns this responsibility")
    
    print("\n[YOUR ROLE]:")
    print("✓ Delegated to manager")
    print("✓ Monitor progress")
    print("✓ Hold manager accountable")
    print("✗ Don't do it yourself!")

if __name__ == "__main__":
    main()