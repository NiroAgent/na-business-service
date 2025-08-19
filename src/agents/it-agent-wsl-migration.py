#!/usr/bin/env python3
"""
IT Agent WSL Migration Delegation
==================================
Delegates the entire WSL/Linux migration to an IT infrastructure agent
who will handle the technical migration autonomously.
"""

import subprocess
import json
from datetime import datetime

def create_it_agent_delegation():
    """Create comprehensive IT agent delegation for WSL migration"""
    
    issue = {
        "title": "[IT-Agent] Migrate Autonomous Business System from Windows to WSL/Linux",
        "body": """## IT Infrastructure Agent - WSL Migration Task

### Priority: P0 (Critical)
### Assigned: ai-it-infrastructure-agent

### Objective
Complete migration of the entire autonomous business system from Windows (E:\\Projects) to WSL/Linux environment to resolve Unicode encoding issues and improve system performance.

### Current Situation
- **Problem**: Windows cp1252 encoding causing Unicode/emoji failures
- **Location**: E:\\Projects\\ on Windows
- **Solution**: Migrate to WSL (Windows Subsystem for Linux)
- **Urgency**: Blocking agent operations due to encoding errors

### Migration Requirements

#### Phase 1: Environment Setup
1. **Verify WSL Installation**
   - Check if WSL2 is installed
   - If not, install WSL2 with Ubuntu 22.04
   - Configure WSL2 as default

2. **Create Linux Environment**
   ```bash
   # Target directory
   ~/autonomous-business-system/
   
   # Required tools
   - Python 3.10+
   - GitHub CLI (gh)
   - Git
   - Docker (optional)
   - tmux/screen for session management
   ```

3. **File Migration**
   - Copy all *.py files from E:\\Projects
   - Copy all *.json configuration files
   - Copy all *.md documentation
   - Copy all *.html dashboard files
   - Copy all *.sh scripts
   - Convert line endings (dos2unix)
   - Set proper permissions (chmod +x)

#### Phase 2: Dependency Installation
1. **System Packages**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv
   sudo apt install -y gh git curl wget
   sudo apt install -y dos2unix tmux htop
   ```

2. **Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **GitHub CLI Authentication**
   - Configure gh auth
   - Test repository access
   - Verify issue creation capability

#### Phase 3: Service Configuration
1. **Create Startup Scripts**
   - run-linux.sh (main runner)
   - start-all-agents.sh (batch startup)
   - monitor-agents.sh (monitoring)

2. **Background Services**
   - Configure tmux sessions for each agent
   - Setup systemd services (optional)
   - Implement auto-restart on failure

3. **Logging Configuration**
   - Centralized log directory
   - Log rotation setup
   - Real-time log monitoring

#### Phase 4: Testing & Validation
1. **Unicode Testing**
   ```python
   # Must pass without errors
   print("🚀 🤖 ✅ 📊 💻 🎯")
   ```

2. **Agent Testing**
   - Test each agent individually
   - Verify GitHub API access
   - Test inter-agent communication
   - Validate file operations

3. **Performance Testing**
   - Measure startup times
   - Check memory usage
   - Monitor CPU utilization
   - Verify network connectivity

#### Phase 5: Migration Execution
1. **Pre-Migration Checklist**
   - [ ] Backup Windows project
   - [ ] Document current agent states
   - [ ] Save all configuration
   - [ ] Note any running processes

2. **Migration Steps**
   - [ ] Setup WSL environment
   - [ ] Copy all files
   - [ ] Install dependencies
   - [ ] Configure services
   - [ ] Test all components
   - [ ] Start monitoring

3. **Post-Migration Validation**
   - [ ] All agents responding
   - [ ] Unicode working
   - [ ] Logs generating
   - [ ] Dashboard accessible
   - [ ] GitHub integration working

### Automation Script
Create and execute: `auto-migrate-to-wsl.sh`

```bash
#!/bin/bash
# Automated WSL Migration Script
# TO BE CREATED BY IT AGENT

set -e  # Exit on error

echo "Starting automated WSL migration..."

# Step 1: Environment detection
detect_environment() {
    if grep -qi microsoft /proc/version; then
        echo "WSL detected"
        return 0
    else
        echo "Not in WSL"
        return 1
    fi
}

# Step 2: File migration
migrate_files() {
    SOURCE="/mnt/e/Projects"
    DEST="$HOME/autonomous-business-system"
    
    mkdir -p "$DEST"
    cp -r "$SOURCE"/* "$DEST/"
    
    # Fix permissions and line endings
    find "$DEST" -name "*.py" -exec chmod +x {} \\;
    find "$DEST" -name "*.sh" -exec chmod +x {} \\;
    find "$DEST" -type f -exec dos2unix {} \\; 2>/dev/null
}

# Step 3: Install dependencies
install_dependencies() {
    sudo apt update
    sudo apt install -y python3-venv gh git tmux
    
    cd "$HOME/autonomous-business-system"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

# Step 4: Start services
start_services() {
    tmux new-session -d -s coordinator 'python3 agent-policy-coordinator.py'
    tmux new-session -d -s monitor 'python3 continuous-monitor.py'
    tmux new-session -d -s compliance 'python3 agent-compliance-monitor.py'
}

# Execute migration
main() {
    detect_environment || exit 1
    migrate_files
    install_dependencies
    start_services
    
    echo "Migration complete!"
    echo "Check status: tmux ls"
}

main "$@"
```

### Success Criteria
1. **Functional Requirements**
   - [ ] All Python scripts run without encoding errors
   - [ ] Emojis display correctly (🚀 ✅ 🤖)
   - [ ] All agents operational
   - [ ] GitHub integration working
   - [ ] Dashboard accessible

2. **Performance Requirements**
   - [ ] Agent startup < 5 seconds
   - [ ] Memory usage < 500MB per agent
   - [ ] No Unicode-related errors in logs
   - [ ] File operations 2x faster than Windows

3. **Operational Requirements**
   - [ ] Auto-restart on failure
   - [ ] Log rotation configured
   - [ ] Monitoring active
   - [ ] Remote access configured
   - [ ] Backup strategy implemented

### Deliverables
1. **Migration Report**
   - Pre-migration state
   - Migration steps taken
   - Issues encountered
   - Resolution actions
   - Post-migration validation

2. **Documentation**
   - WSL setup guide
   - Linux operation manual
   - Troubleshooting guide
   - Emergency rollback procedure

3. **Monitoring Dashboard**
   - Real-time agent status
   - System resource usage
   - Log aggregation view
   - Alert notifications

### Timeline
- **Hour 1**: Environment setup
- **Hour 2**: File migration
- **Hour 3**: Dependency installation
- **Hour 4**: Service configuration
- **Hour 5**: Testing & validation
- **Hour 6**: Documentation & handover

### Risk Mitigation
1. **Backup Strategy**
   - Keep Windows copy intact
   - Create WSL snapshot
   - Document rollback steps

2. **Failure Recovery**
   - Automated retry logic
   - Manual intervention procedures
   - Escalation path defined

3. **Testing Protocol**
   - Unit tests for each component
   - Integration testing
   - Load testing
   - Failover testing

### Support Requirements
- **From DevOps Agent**: Infrastructure setup assistance
- **From Developer Agent**: Code adaptation for Linux
- **From QA Agent**: Testing and validation
- **From PM Agent**: Progress tracking and reporting

### Notes
- Windows project remains as backup
- WSL2 required for best performance
- Consider Docker containers for future
- May need VPN configuration for corporate networks

### Command Reference
```bash
# Check WSL version
wsl --version

# Access from Windows
\\\\wsl$\\Ubuntu\\home\\username\\autonomous-business-system

# Access Windows from WSL
/mnt/c/Users/
/mnt/e/Projects/

# Monitor agents
tmux attach -t coordinator
tmux attach -t monitor

# Check logs
tail -f ~/autonomous-business-system/*.log

# Service status
ps aux | grep python
```

### Emergency Contacts
- **Escalation**: ai-tech-lead-agent
- **Architecture**: ai-architect-agent  
- **Operations**: ai-devops-agent

### Priority: P0 (URGENT - System Blocked)
### Estimated Time: 6 hours
### Start: IMMEDIATELY

**IMPORTANT**: The entire system is currently impaired due to Windows encoding issues. This migration is critical for resuming full autonomous operations.""",
        "labels": ["infrastructure", "migration", "priority/P0", "wsl", "linux"],
        "assignee": "ai-it-infrastructure-agent"
    }
    
    # Create the issue
    repo = "NiroAgentV2/business-operations"
    
    print("\n" + "="*80)
    print("CREATING IT AGENT WSL MIGRATION DELEGATION")
    print("="*80)
    
    print(f"\nDelegating to IT Agent: {issue['title']}")
    
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
            print(f"  [OK] Delegated to IT Agent: {url}")
            return url
        else:
            print(f"  [INFO] Issue may already exist or error occurred")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    return None

def create_it_agent_role():
    """Create IT infrastructure agent if it doesn't exist"""
    
    agent_definition = {
        "name": "ai-it-infrastructure-agent",
        "role": "IT Infrastructure and Operations Specialist",
        "responsibilities": [
            "System migrations and upgrades",
            "Environment setup and configuration",
            "Infrastructure automation",
            "System monitoring and maintenance",
            "Security hardening",
            "Backup and disaster recovery",
            "Performance optimization",
            "Troubleshooting and support"
        ],
        "skills": [
            "Linux administration",
            "Windows administration", 
            "WSL configuration",
            "Docker/Kubernetes",
            "Shell scripting",
            "Python automation",
            "Network configuration",
            "Security best practices"
        ],
        "tools": [
            "Bash/PowerShell",
            "Ansible/Terraform",
            "Docker/Kubernetes",
            "Git/GitHub",
            "Monitoring tools",
            "Log management"
        ]
    }
    
    # Save agent definition
    with open("ai-it-infrastructure-agent.json", "w") as f:
        json.dump(agent_definition, f, indent=2)
    
    print("\n[OK] IT Infrastructure Agent role defined")
    return agent_definition

def main():
    """Main entry point"""
    
    # Create IT agent role
    create_it_agent_role()
    
    # Create delegation issue
    url = create_it_agent_delegation()
    
    print("\n" + "="*80)
    print("IT AGENT DELEGATION COMPLETE")
    print("="*80)
    
    print("\n[DELEGATED SUCCESSFULLY]")
    print("The IT Infrastructure Agent will now:")
    print("1. Setup WSL/Linux environment")
    print("2. Migrate all project files")
    print("3. Install dependencies")
    print("4. Configure services")
    print("5. Test and validate")
    print("6. Start all agents in Linux")
    
    print("\n[EXPECTED OUTCOME]")
    print("- Full Unicode support")
    print("- Better performance")
    print("- Production-like environment")
    print("- Automated service management")
    print("- No more encoding errors!")
    
    print("\n[MONITORING]")
    print("The IT agent will provide progress updates in the GitHub issue")
    print("Migration should complete within 6 hours")
    
    print("\n[IMPORTANT]")
    print("This is proper delegation - letting the IT specialist handle infrastructure!")

if __name__ == "__main__":
    main()