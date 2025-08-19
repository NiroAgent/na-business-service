#!/usr/bin/env python3
"""
Manager Documentation Cleanup Delegation
=========================================
Delegates documentation organization and cleanup to management team
to establish clear documentation standards and archive excess files.
"""

import subprocess
import json
from datetime import datetime

def create_documentation_cleanup_delegation():
    """Create manager delegation for documentation cleanup"""
    
    issue = {
        "title": "[Manager] Organize and Standardize All Documentation - Archive Excess Files",
        "body": """## Management Directive: Documentation Cleanup and Standardization

### Executive Summary
Our documentation is scattered and excessive. As Documentation Manager, you will lead a complete reorganization, establishing strict documentation standards and archiving all excess files.

### Current Problem
- Too many random documents everywhere
- No clear documentation structure
- Duplicate and outdated content
- Difficult to find relevant information
- Maintenance overhead too high

### Documentation Standards to Implement

#### 1. Standard Document Set Per Service
Each service MUST have exactly these documents (no more, no less):

```
service-name/
├── README.md           # Overview and quick start
├── API.md              # API documentation
├── ARCHITECTURE.md     # Technical architecture
├── DEPLOYMENT.md       # Deployment instructions
├── TESTING.md          # Testing guide
├── TROUBLESHOOTING.md  # Common issues and solutions
└── CHANGELOG.md        # Version history
```

**Total: 7 documents per service**

#### 2. Standard Document Set Per Organization/Repository
Each repository root MUST have exactly:

```
repository-root/
├── README.md           # Project overview
├── CONTRIBUTING.md     # Contribution guidelines
├── ARCHITECTURE.md     # System architecture
├── SETUP.md           # Development setup
├── DEPLOYMENT.md      # Production deployment
├── SECURITY.md        # Security policies
├── LICENSE.md         # License information
├── CLAUDE.md          # AI agent instructions
└── docs/
    ├── api/           # API references
    ├── guides/        # User guides
    └── archive/       # Old documentation
```

**Total: 8 root documents + organized subdirectories**

#### 3. Documentation Cleanup Tasks

##### Phase 1: Audit (Day 1)
**Assign to: ai-documentation-agent**

Create comprehensive audit report:
```python
class DocumentationAudit:
    def audit_all_repos(self):
        findings = {
            "total_documents": 0,
            "duplicate_content": [],
            "outdated_files": [],
            "missing_standards": [],
            "excess_files": [],
            "to_archive": []
        }
        return findings
```

Document categories to identify:
- Current and relevant (keep)
- Outdated but historical (archive)
- Duplicate content (merge and delete)
- Random notes/drafts (delete)
- Missing required docs (create)

##### Phase 2: Standardization (Day 2)
**Assign to: ai-technical-writer-agent**

For each service and repository:
1. Create missing standard documents
2. Merge duplicate content
3. Update outdated information
4. Ensure consistent formatting
5. Apply templates

**Document Templates:**

```markdown
# README.md Template
# [Service/Project Name]

## Overview
Brief description (2-3 sentences)

## Quick Start
1. Installation
2. Basic usage
3. Example

## Documentation
- [API Documentation](./API.md)
- [Architecture](./ARCHITECTURE.md)
- [Deployment](./DEPLOYMENT.md)

## Support
- Issues: [GitHub Issues](link)
- Contact: [team/email]
```

```markdown
# API.md Template
# API Documentation

## Endpoints
### GET /endpoint
- Description:
- Parameters:
- Response:
- Example:

## Authentication
## Rate Limiting
## Error Codes
```

##### Phase 3: Archival (Day 3)
**Assign to: ai-devops-agent**

Archive strategy:
```
archive/
├── 2024/
│   ├── old-readme-v1.md
│   ├── deprecated-setup.md
│   └── legacy-docs.zip
├── migration/
│   ├── windows-setup.md
│   └── old-scripts.md
└── drafts/
    ├── random-notes.md
    └── temp-docs.md
```

Rules for archiving:
- Compress files older than 6 months
- Keep for 1 year then delete
- Tag with date and reason
- Create index file

##### Phase 4: Cleanup Execution (Day 4)
**Assign to: ai-it-infrastructure-agent**

```bash
#!/bin/bash
# Documentation cleanup script

# Find all markdown files
find . -name "*.md" > all-docs.txt

# Identify non-standard docs
grep -v -E "(README|API|ARCHITECTURE|DEPLOYMENT|TESTING|TROUBLESHOOTING|CHANGELOG|CONTRIBUTING|SETUP|SECURITY|LICENSE|CLAUDE)" all-docs.txt > excess-docs.txt

# Archive excess files
mkdir -p docs/archive/$(date +%Y%m%d)
while read file; do
    mv "$file" docs/archive/$(date +%Y%m%d)/
done < excess-docs.txt

# Generate report
echo "Archived $(wc -l < excess-docs.txt) excess documents"
```

#### 4. Service-Specific Documentation

##### NiroSubsV2 Services
Standard docs for each:
- ns-auth
- ns-dashboard
- ns-payments
- ns-user
- ns-shell

**Total: 5 services × 7 docs = 35 documents**

##### VisualForgeV2 Services
Standard docs for each:
- vf-audio
- vf-video
- vf-image
- vf-text
- vf-bulk
- vf-dashboard

**Total: 6 services × 7 docs = 42 documents**

##### Agent Documentation
One doc per agent type:
- developer-agent.md
- devops-agent.md
- qa-agent.md
- architect-agent.md
- pm-agent.md
- etc.

**Total: 14 agent docs**

#### 5. Documentation Governance

##### Ownership Matrix
| Document | Owner | Reviewer | Approver |
|----------|-------|----------|----------|
| README | Developer | Architect | PM |
| API | Developer | QA | Architect |
| ARCHITECTURE | Architect | Tech Lead | CTO |
| DEPLOYMENT | DevOps | QA | PM |
| TESTING | QA | Developer | Lead |
| TROUBLESHOOTING | Support | DevOps | PM |
| CHANGELOG | PM | Developer | Lead |

##### Update Frequency
- README: Monthly
- API: On change
- ARCHITECTURE: Quarterly
- DEPLOYMENT: On change
- TESTING: Sprint
- TROUBLESHOOTING: As needed
- CHANGELOG: Per release

##### Quality Standards
- Maximum 500 lines per document
- Clear sections and headers
- Code examples where relevant
- Diagrams for architecture
- Version controlled
- Reviewed before merge

#### 6. Implementation Plan

##### Week 1: Audit & Planning
- Day 1-2: Complete audit of all documentation
- Day 3: Create cleanup plan
- Day 4: Get approval from stakeholders
- Day 5: Prepare templates and tools

##### Week 2: Execution
- Day 1-2: Archive excess documents
- Day 3-4: Create missing standard docs
- Day 5: Merge and consolidate

##### Week 3: Validation
- Day 1-2: Review all documentation
- Day 3: Test documentation accuracy
- Day 4: Update CI/CD to enforce standards
- Day 5: Training and handover

#### 7. Enforcement Mechanisms

##### Pre-commit Hooks
```python
def check_documentation():
    required_docs = [
        "README.md",
        "API.md",
        "ARCHITECTURE.md",
        "DEPLOYMENT.md",
        "TESTING.md",
        "TROUBLESHOOTING.md",
        "CHANGELOG.md"
    ]
    
    for doc in required_docs:
        if not os.path.exists(doc):
            raise Exception(f"Missing required doc: {doc}")
    
    # Check for excess docs
    all_docs = glob.glob("*.md")
    excess = set(all_docs) - set(required_docs)
    if excess:
        raise Exception(f"Excess docs found: {excess}")
```

##### GitHub Actions
```yaml
name: Documentation Standards Check
on: [push, pull_request]
jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check documentation standards
        run: |
          python check_documentation.py
          markdown-lint *.md
```

#### 8. Success Metrics

##### Quantitative Metrics
- Document count reduced by 70%
- Standard compliance: 100%
- Search time reduced by 80%
- Maintenance time reduced by 60%
- Documentation coverage: 100%

##### Qualitative Metrics
- Developer satisfaction survey
- Time to find information
- Documentation accuracy
- Onboarding efficiency
- Support ticket reduction

#### 9. Delegation to Agents

Create issues for each agent:

**Documentation Agent:**
- Title: "Audit all documentation and create report"
- Deadline: 2 days

**Technical Writer Agent:**
- Title: "Standardize documentation using templates"
- Deadline: 3 days

**DevOps Agent:**
- Title: "Implement archival system and automation"
- Deadline: 2 days

**QA Agent:**
- Title: "Validate documentation accuracy"
- Deadline: 2 days

#### 10. Communication Plan

Daily standup topics:
- Documents processed
- Issues encountered
- Help needed
- Progress percentage

Weekly report:
- Total docs audited
- Docs archived
- Docs created
- Compliance rate

### Your Immediate Actions

1. **Today:**
   - Assign documentation audit to agents
   - Create documentation templates
   - Set up archive structure

2. **Tomorrow:**
   - Review audit results
   - Approve cleanup plan
   - Begin archival process

3. **This Week:**
   - Complete all archival
   - Standardize all services
   - Implement enforcement

### Final Documentation Structure

```
autonomous-business-system/
├── README.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── SETUP.md
├── DEPLOYMENT.md
├── SECURITY.md
├── LICENSE.md
├── CLAUDE.md
├── services/
│   ├── ns-auth/
│   │   └── [7 standard docs]
│   ├── ns-dashboard/
│   │   └── [7 standard docs]
│   └── ...
├── agents/
│   ├── developer-agent.md
│   ├── devops-agent.md
│   └── ...
└── docs/
    ├── archive/
    │   └── 2024/
    └── guides/
```

**Total Documentation Count:**
- Root: 8 documents
- Services: 11 × 7 = 77 documents
- Agents: 14 documents
- **TOTAL: 99 documents** (down from current 300+)

### Authority

You have full authority to:
- Delete redundant documentation
- Archive outdated files
- Enforce standards
- Reject non-compliant PRs
- Mandate documentation updates

### Deadline
**Complete cleanup: 2 weeks**
**Quick wins: 3 days**

### Priority: P0 (CRITICAL)
Documentation chaos is blocking productivity. Fix it now!

**BEGIN IMMEDIATELY**""",
        "labels": ["documentation", "cleanup", "management", "priority/P0", "standardization"],
        "assignee": "ai-project-manager-agent"
    }
    
    # Create the issue
    repo = "NiroAgentV2/business-operations"
    
    print("\n" + "="*80)
    print("CREATING DOCUMENTATION CLEANUP DELEGATION")
    print("="*80)
    
    print(f"\nDelegating to Manager: {issue['title']}")
    
    cmd = [
        "gh", "issue", "create",
        "--repo", repo,
        "--title", issue["title"],
        "--body", issue["body"]
    ]
    
    # Add labels
    for label in issue.get("labels", []):
        cmd.extend(["--label", label])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"  [OK] Delegated to Manager: {url}")
            return url
        else:
            print(f"  [INFO] Issue may already exist or error occurred")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    return None

def main():
    """Main entry point"""
    
    url = create_documentation_cleanup_delegation()
    
    print("\n" + "="*80)
    print("DOCUMENTATION CLEANUP DELEGATION COMPLETE")
    print("="*80)
    
    print("\n[MANAGER WILL NOW:]")
    print("1. Audit all existing documentation")
    print("2. Create standard document templates")
    print("3. Archive excess documents")
    print("4. Enforce 7 docs per service rule")
    print("5. Implement automated compliance checks")
    
    print("\n[EXPECTED OUTCOME:]")
    print("- From 300+ random docs to 99 organized docs")
    print("- Clear structure for every service")
    print("- Automated enforcement via CI/CD")
    print("- Easy to find information")
    print("- Reduced maintenance overhead")
    
    print("\n[DOCUMENTATION STANDARDS:]")
    print("Per Service: 7 documents")
    print("Per Repository: 8 root documents")
    print("Per Agent: 1 document")
    print("Total System: ~99 documents")
    
    print("\n[SUCCESS!]")
    print("Manager will coordinate the entire cleanup operation!")

if __name__ == "__main__":
    main()