#!/usr/bin/env python3
"""
Update CLAUDE.md with Delegation Policy
========================================
Add delegation rules to CLAUDE.md so I remember to delegate everything
"""

import os

def update_claude_md():
    """Add delegation policy to CLAUDE.md"""
    
    delegation_section = """

## CRITICAL: DELEGATION POLICY

### MY #1 RULE: DELEGATE EVERYTHING THROUGH THE SYSTEM

I must ONLY:
1. Create ONE issue to a manager
2. Monitor progress
3. Nothing else

### Delegation Pattern:
```bash
# CORRECT - One delegation to manager
gh issue create --repo business-operations --title "[Manager] Fix X"

# WRONG - Never do these:
- Don't create developer tasks
- Don't create QA tasks  
- Don't write implementation details
- Don't make technical decisions
```

### The System:
- GitHub Issues = Delegation mechanism
- Always delegate to managers
- Managers create all sub-tasks
- I only monitor

### Anti-Patterns to Avoid:
- Creating multiple issues = Micromanaging
- Writing code examples = Doing developer's job
- Creating test cases = Doing QA's job
- Technical decisions = Architect's job

### My Mantras:
- "One delegation, then monitor"
- "Through the system, not around it"
- "If I'm writing code, I'm doing it wrong"
- "Managers manage, I delegate"

### Issue Repository Rules:
- I create issues ONLY in: `business-operations`
- Managers create issues in service repos
- RULE #1: Issues belong in their own repos

"""
    
    # Check if CLAUDE.md exists
    claude_path = "CLAUDE.md"
    
    if os.path.exists(claude_path):
        print(f"Updating existing {claude_path}...")
        with open(claude_path, 'r') as f:
            content = f.read()
        
        # Add delegation section if not already there
        if "DELEGATION POLICY" not in content:
            content = delegation_section + "\n" + content
            with open(claude_path, 'w') as f:
                f.write(content)
            print("[OK] Added delegation policy to CLAUDE.md")
        else:
            print("[INFO] Delegation policy already in CLAUDE.md")
    else:
        print(f"Creating new {claude_path}...")
        
        full_content = f"""# CLAUDE.md - AI Agent Instructions

{delegation_section}

## System Overview
This is an autonomous business system using GitHub Issues as the operational database.

## Agent Hierarchy
1. Managers - Receive delegations, create tasks
2. Architects - Review and approve
3. Developers - Implement
4. QA - Test
5. DevOps - Deploy

## Key Workflows
1. User requests something
2. I delegate to manager
3. Manager creates tasks in proper repos
4. Teams execute
5. I monitor progress

## Remember
- ALWAYS delegate to managers
- NEVER create implementation details
- ONE issue only
- Monitor, don't manage
"""
        
        with open(claude_path, 'w') as f:
            f.write(full_content)
        print("[OK] Created CLAUDE.md with delegation policy")
    
    # Also create a reminder file
    with open("REMEMBER_TO_DELEGATE.md", 'w') as f:
        f.write("""# REMEMBER: DELEGATE EVERYTHING!

## Before creating ANY issue, ask yourself:
1. Am I delegating to a manager? (If no, STOP)
2. Am I creating only ONE issue? (If no, STOP)
3. Am I avoiding implementation details? (If no, STOP)

## The ONLY correct pattern:
```bash
gh issue create \
  --repo business-operations \
  --title "[Manager] Do something" \
  --body "Brief description. You own this."
```

## That's it. Nothing more.
""")
    print("[OK] Created REMEMBER_TO_DELEGATE.md")

def main():
    print("\n" + "="*80)
    print("UPDATING DELEGATION POLICY")
    print("="*80)
    
    update_claude_md()
    
    print("\n" + "="*80)
    print("POLICY UPDATED")
    print("="*80)
    
    print("\n[FILES CREATED/UPDATED]:")
    print("- CLAUDE.md - Main instructions with delegation policy")
    print("- DELEGATION_POLICY.md - Detailed delegation rules")
    print("- REMEMBER_TO_DELEGATE.md - Quick reminder")
    
    print("\n[KEY RULES NOW DOCUMENTED]:")
    print("1. ONLY delegate to managers")
    print("2. ONE issue only")
    print("3. NO implementation details")
    print("4. Through the system")
    print("5. Monitor, don't manage")
    
    print("\n[SUCCESS!]")
    print("Delegation policy is now part of my persistent instructions!")

if __name__ == "__main__":
    main()