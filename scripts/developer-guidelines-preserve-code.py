#!/usr/bin/env python3
"""
Developer Guidelines - Preserve Existing Code
==============================================
Creates guidelines for developers to ensure they don't break
or recreate functionality that already exists (75% complete).
"""

import subprocess
import json
from datetime import datetime

def create_developer_preservation_guidelines():
    """Create guidelines for developers to preserve existing code"""
    
    body_content = """## CRITICAL DEVELOPER GUIDELINES

### ⚠️ IMPORTANT: Services are Already 75% Complete!

Most functionality already exists and works. Your job is to:
1. **FIX** bugs found by QA
2. **COMPLETE** the remaining 25%
3. **PRESERVE** all working code
4. **ENHANCE** without breaking

### 🚫 DO NOT:
- Rewrite existing working code
- Change architecture without architect approval
- Delete functionality you don't understand
- Refactor working code without reason
- Change API contracts
- Modify database schemas without migration

### ✅ DO:
- Read and understand existing code first
- Run tests before making changes
- Keep backward compatibility
- Add to existing code, don't replace
- Document your changes
- Test thoroughly before committing

## Pre-Development Checklist

### 1. Before You Start Coding
```bash
# MANDATORY: Run this checklist before any development

# 1. Pull latest code
git pull origin main

# 2. Check what already exists
ls -la services/
grep -r "function_name" .
git log --oneline -10

# 3. Run existing tests
pytest tests/
npm test

# 4. Check current functionality
python service_health_check.py

# 5. Read existing documentation
cat README.md
cat ARCHITECTURE.md

# 6. Review QA bug reports
gh issue list --label bug
```

### 2. Understanding What Exists

#### Service Inventory (75% Complete):
```yaml
NiroSubsV2:
  ns-auth:
    complete:
      - User registration
      - Basic login
      - JWT tokens
      - Password hashing
    missing:
      - MFA (25%)
      - Session management (25%)
      - Rate limiting (25%)
      
  ns-payments:
    complete:
      - Payment processing
      - Basic subscriptions
      - Stripe integration
    missing:
      - Webhook handling (25%)
      - Refund processing (25%)
      - Invoice generation (25%)
      
  ns-dashboard:
    complete:
      - Basic UI layout
      - Agent cards
      - Activity feed
    missing:
      - Tab system fix
      - Cost monitoring
      - Kill switch

VisualForgeV2:
  vf-audio:
    complete:
      - File upload
      - Format detection
      - Basic processing
    missing:
      - Advanced filters (25%)
      - Batch processing (25%)
      
  vf-video:
    complete:
      - Video upload
      - Thumbnail generation
      - Basic encoding
    missing:
      - Streaming support (25%)
      - Subtitle processing (25%)
```

### 3. Safe Development Practices

#### A. Always Check First
```python
# BEFORE creating a new function
def create_new_feature():
    # WRONG - might already exist!
    pass

# RIGHT - Check first
import os
import ast

def check_if_exists(function_name):
    for root, dirs, files in os.walk('services'):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file)) as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if node.name == function_name:
                                print(f"Found {function_name} in {file}")
                                return True
    return False

# Use before creating
if not check_if_exists('process_payment'):
    def process_payment():
        pass
```

#### B. Extend, Don't Replace
```python
# WRONG - Replacing existing code
class AuthService:  # This might already exist!
    def login(self, email, password):
        # New implementation
        pass

# RIGHT - Extend existing code
from services.auth import AuthService as BaseAuthService

class EnhancedAuthService(BaseAuthService):
    def login(self, email, password):
        # Call existing implementation
        result = super().login(email, password)
        
        # Add new functionality
        self.add_mfa_check(result)
        return result
    
    def add_mfa_check(self, login_result):
        # New MFA functionality
        pass
```

#### C. Fix, Don't Rewrite
```javascript
// WRONG - Complete rewrite
function switchTab(tabId) {
    // Completely new implementation
}

// RIGHT - Fix the specific issue
function switchTab(tabId) {
    // Keep working parts
    const existingLogic = getCurrentTabLogic();
    
    // Fix only the broken part
    if (!tabId) {
        console.error('Tab ID required');
        return;
    }
    
    // Preserve rest of functionality
    existingLogic.apply(this, arguments);
}
```

### 4. Bug Fix Protocol

When QA reports a bug:

#### Step 1: Reproduce
```bash
# Get bug details
gh issue view <issue-number>

# Reproduce locally
python reproduce_bug.py --issue <number>
```

#### Step 2: Locate
```bash
# Find the problematic code
grep -r "error_message" .
git blame file.py | grep "function_name"
git log -p --grep="related_feature"
```

#### Step 3: Fix Minimally
```python
# WRONG - Rewrite entire function
def process_data(data):
    # 100 lines of new code
    pass

# RIGHT - Surgical fix
def process_data(data):
    # Keep existing code
    result = existing_processing(data)
    
    # Fix only the bug
    if result is None:  # Bug was here
        result = default_value  # Fix
    
    return result
```

#### Step 4: Test Everything
```bash
# Test your fix
pytest tests/test_specific_bug.py

# Test nothing else broke
pytest tests/  # ALL tests must pass

# Integration test
python integration_test.py
```

### 5. Completing the Remaining 25%

For missing features:

#### A. Check Requirements
```python
# Read original requirements
with open('requirements/service_name.md') as f:
    requirements = f.read()
    
# Identify what's missing
missing_features = identify_gaps(requirements, current_implementation)
```

#### B. Add Without Breaking
```python
class PaymentService:
    # Existing methods (DO NOT MODIFY)
    def process_payment(self): 
        pass
    
    def create_subscription(self):
        pass
    
    # ADD new methods for missing 25%
    def process_webhook(self, event):
        '''New functionality - webhook handling'''
        # Implementation
        pass
    
    def generate_invoice(self, payment_id):
        '''New functionality - invoice generation'''
        # Implementation
        pass
```

### 6. Communication Requirements

#### Before Making Changes:
1. Comment on the issue: "Starting work on bug #123"
2. Check with architect for structural changes
3. Coordinate with other developers
4. Review QA test cases

#### After Making Changes:
1. Update issue with fix details
2. Document what was changed
3. Add tests for new code
4. Request QA retest

### 7. Git Workflow

```bash
# ALWAYS use feature branches
git checkout -b fix/issue-123-tab-system

# Make minimal commits
git add -p  # Add selectively
git commit -m "Fix: Tab switching in dashboard (issue #123)"

# Before merging
git checkout main
git pull origin main
git checkout fix/issue-123-tab-system
git rebase main

# Test after rebase
pytest tests/
npm test

# Create PR with details
gh pr create --title "Fix #123: Dashboard tab switching" \\
             --body "Fixed specific issue without breaking existing functionality"
```

### 8. Code Review Checklist

Before submitting PR:
- [ ] Existing tests still pass
- [ ] New tests added for changes
- [ ] No unnecessary refactoring
- [ ] API contracts unchanged
- [ ] Database schemas unchanged
- [ ] Documentation updated
- [ ] QA bug verified fixed
- [ ] No new bugs introduced

### 9. Emergency Procedures

If you accidentally break something:

```bash
# Immediate rollback
git revert HEAD
git push origin main

# Notify team
gh issue create --title "URGENT: Reverted breaking change" \\
                --body "Reverted commit <hash> due to <issue>"

# Fix properly
git checkout -b fix/emergency-repair
# Make proper fix
# Test thoroughly
# Re-submit PR
```

### 10. Architect Approval Required For:

- Database schema changes
- API breaking changes
- Architecture modifications
- Service communication changes
- Security-related changes
- Performance optimizations affecting structure
- Third-party service integrations
- Major refactoring

## Summary

### The Golden Rules:
1. **READ** before you write
2. **TEST** before you commit
3. **EXTEND** don't replace
4. **FIX** don't rewrite
5. **PRESERVE** working code
6. **COMPLETE** missing features
7. **COMMUNICATE** with team

### Remember:
- 75% is already done and working
- Your job is the final 25% + bug fixes
- Breaking existing code = more work for everyone
- Small, targeted changes > large rewrites

### Consequences of Breaking Code:
- QA has to retest everything
- Other services might fail
- Delays in delivery
- Angry users
- Rollback and rework

## Your Commitment

By working on this project, you commit to:
- [ ] Preserving existing functionality
- [ ] Testing before committing
- [ ] Communicating with team
- [ ] Following these guidelines
- [ ] Asking when unsure

**Priority: P0 - MANDATORY FOR ALL DEVELOPERS**
**Effective: IMMEDIATELY**"""
    
    issue = {
        "title": "[Developer Guidelines] DO NOT Break or Recreate Existing Code - Services are 75% Complete",
        "body": body_content,
        "labels": ["guidelines", "developer", "critical", "priority/P0", "preserve-code"],
        "assignee": "all-developers"
    }
    
    # Create the issue
    repo = "NiroAgentV2/business-operations"
    
    print("\n" + "="*80)
    print("CREATING DEVELOPER PRESERVATION GUIDELINES")
    print("="*80)
    
    print(f"\nCreating: {issue['title']}")
    
    cmd = [
        "gh", "issue", "create",
        "--repo", repo,
        "--title", issue["title"],
        "--body", issue["body"]
    ]
    
    for label in issue.get("labels", []):
        cmd.extend(["--label", label])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"  [OK] Created: {url}")
            return url
        else:
            print(f"  [INFO] Issue may already exist")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    return None

def main():
    """Main entry point"""
    
    url = create_developer_preservation_guidelines()
    
    print("\n" + "="*80)
    print("DEVELOPER GUIDELINES CREATED")
    print("="*80)
    
    print("\n[GUIDELINES ESTABLISHED]:")
    print("1. Don't break existing code (75% complete)")
    print("2. Fix bugs, don't rewrite")
    print("3. Complete missing 25%")
    print("4. Test everything before committing")
    print("5. Get architect approval for structural changes")
    
    print("\n[WORKFLOW]:")
    print("QA Tests → Finds Bugs → Developers Fix (not rewrite) → QA Retests")
    
    print("\n[SUCCESS!]")
    print("Developers now have clear guidelines to preserve existing work!")

if __name__ == "__main__":
    main()