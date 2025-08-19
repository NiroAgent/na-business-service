#!/usr/bin/env python3
"""
Create VS Code Workspace files for each service with embedded agent instructions
This allows running separate Copilot agents in parallel through VS Code
"""

import json
import os
from pathlib import Path

def create_workspace_for_service(repo_name, service_name, repo_path, environment="dev"):
    """Create a VS Code workspace file for a specific service"""
    
    workspace_name = f"{service_name}-{environment}-agent"
    workspace_file = Path(repo_path) / service_name / f"{workspace_name}.code-workspace"
    
    # Read the agent instructions
    instruction_file = Path(repo_path) / service_name / f"AGENT_INSTRUCTIONS_{environment.upper()}.md"
    
    workspace_config = {
        "folders": [
            {
                "path": ".",
                "name": f"{service_name} ({environment})"
            },
            {
                "path": "../../..",
                "name": "Projects (Full Context)"
            },
            {
                "path": "../..",
                "name": f"{repo_name} (Repository)"
            }
        ],
        "settings": {
            # VS Code settings for the workspace
            "terminal.integrated.defaultProfile.windows": "PowerShell",
            "terminal.integrated.defaultProfile.linux": "bash",
            
            # Copilot settings
            "github.copilot.enable": {
                "*": True
            },
            "github.copilot.advanced": {
                "authProvider": "github",
                "debug.showScores": True
            },
            
            # Custom agent settings
            "agentTesting.service": service_name,
            "agentTesting.environment": environment,
            "agentTesting.repository": repo_name,
            "agentTesting.instructionFile": f"AGENT_INSTRUCTIONS_{environment.upper()}.md",
            
            # Auto-save to prevent losing fixes
            "files.autoSave": "afterDelay",
            "files.autoSaveDelay": 1000,
            
            # Terminal commands for quick testing
            "terminal.integrated.env.windows": {
                "SERVICE_NAME": service_name,
                "ENVIRONMENT": environment,
                "AWS_REGION": "us-east-1"
            }
        },
        "tasks": {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Run Health Check",
                    "type": "shell",
                    "command": f"curl https://api-endpoint/{service_name}/health",
                    "group": "test",
                    "presentation": {
                        "reveal": "always",
                        "panel": "new"
                    }
                },
                {
                    "label": "Run Unit Tests",
                    "type": "shell",
                    "command": "npm test",
                    "group": {
                        "kind": "test",
                        "isDefault": True
                    }
                },
                {
                    "label": "Deploy to Environment",
                    "type": "shell",
                    "command": f"aws lambda update-function-code --function-name {environment}-{service_name}-lambda --zip-file fileb://deployment.zip",
                    "group": "build"
                },
                {
                    "label": "Check CloudWatch Logs",
                    "type": "shell",
                    "command": f"aws logs tail /aws/lambda/{environment}-{service_name}-lambda --follow",
                    "presentation": {
                        "reveal": "always",
                        "panel": "dedicated"
                    }
                },
                {
                    "label": "Fix and Redeploy",
                    "type": "shell",
                    "command": "npm run build && npm run deploy",
                    "dependsOn": ["Run Unit Tests"],
                    "group": "build"
                }
            ]
        },
        "launch": {
            "version": "0.2.0",
            "configurations": [
                {
                    "type": "node",
                    "request": "launch",
                    "name": "Debug Lambda Function",
                    "program": "${workspaceFolder}/index.js",
                    "env": {
                        "ENVIRONMENT": environment,
                        "SERVICE_NAME": service_name
                    }
                }
            ]
        },
        "extensions": {
            "recommendations": [
                "GitHub.copilot",
                "GitHub.copilot-chat",
                "amazonwebservices.aws-toolkit-vscode",
                "ms-vscode.PowerShell",
                "dbaeumer.vscode-eslint",
                "esbenp.prettier-vscode"
            ]
        }
    }
    
    # Add agent-specific instructions as comments in settings
    if instruction_file.exists():
        workspace_config["settings"]["agentTesting.instructions"] = f"See {instruction_file.name} for detailed testing instructions"
    
    # Write workspace file
    with open(workspace_file, 'w', encoding='utf-8') as f:
        json.dump(workspace_config, f, indent=2)
    
    print(f"Created workspace: {workspace_file}")
    return workspace_file

def create_agent_launcher_script(repo_name, service_name, environments=["dev", "staging"]):
    """Create a script to launch VS Code with agent workspace"""
    
    launcher_content = f"""#!/bin/bash
# Launch VS Code workspaces for {service_name} agent testing

echo "🚀 Launching VS Code Agent Workspaces for {service_name}"
echo "================================================"

# Function to launch VS Code with a specific workspace
launch_workspace() {{
    local workspace_file=$1
    local env=$2
    
    echo "Opening $env environment workspace..."
    code "$workspace_file" --new-window
    
    # Wait a bit between launches to avoid overwhelming the system
    sleep 2
}}

# Launch workspaces for each environment
"""
    
    for env in environments:
        workspace_name = f"{service_name}-{env}-agent.code-workspace"
        launcher_content += f'launch_workspace "{workspace_name}" "{env}"\n'
    
    launcher_content += """
echo "✅ All workspaces launched!"
echo ""
echo "Instructions:"
echo "1. In each VS Code window, open the integrated terminal"
echo "2. Use GitHub Copilot Chat to execute the agent instructions"
echo "3. Ask Copilot: 'Please read AGENT_INSTRUCTIONS_[ENV].md and execute all tests'"
echo "4. Monitor the Tasks output for test results"
echo "5. Let Copilot fix any issues it finds"
"""
    
    # Windows version
    launcher_ps1 = launcher_content.replace("#!/bin/bash", "# PowerShell script").replace("sleep", "Start-Sleep")
    launcher_ps1 = launcher_ps1.replace("echo", "Write-Host").replace("code", "code.cmd")
    
    # Save launcher scripts
    service_path = Path(f"E:/Projects/{repo_name}/{service_name}")
    
    bash_file = service_path / "launch-agent-workspaces.sh"
    with open(bash_file, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    ps1_file = service_path / "launch-agent-workspaces.ps1"
    with open(ps1_file, 'w', encoding='utf-8') as f:
        f.write(launcher_ps1)
    
    print(f"Created launchers: {bash_file} and {ps1_file}")

def create_copilot_agent_prompt(service_name, environment):
    """Create a prompt file for Copilot to use as agent"""
    
    prompt = f"""# GitHub Copilot Agent Prompt for {service_name} ({environment})

You are an autonomous testing and remediation agent for {service_name} in the {environment} environment.

## Your Mission

1. Read the file AGENT_INSTRUCTIONS_{environment.upper()}.md in this workspace
2. Execute all tests described in those instructions
3. Fix any issues you find
4. Deploy the fixes
5. Verify the fixes work

## How to Execute

1. **Start Testing**:
   - Run the task "Run Health Check" from the Command Palette (Ctrl+Shift+P > Tasks: Run Task)
   - Run the task "Run Unit Tests"
   - Check the output for any failures

2. **If Tests Fail**:
   - Analyze the error messages
   - Look at the relevant code files
   - Propose and implement fixes
   - Re-run the tests to verify

3. **Deploy Fixes**:
   - If all tests pass after fixes, run "Deploy to Environment" task
   - Monitor CloudWatch logs with "Check CloudWatch Logs" task

4. **Report Results**:
   Create a file called TEST_RESULTS_{environment.upper()}.json with:
   {{
       "service": "{service_name}",
       "environment": "{environment}",
       "timestamp": "current-time",
       "tests_run": number,
       "tests_passed": number,
       "tests_failed": number,
       "issues_fixed": ["list of fixes"],
       "deployment_status": "success|failed"
   }}

## Available Commands

You can run these in the integrated terminal:
- `npm test` - Run unit tests
- `npm run lint` - Check code quality
- `npm run build` - Build the service
- `npm run deploy` - Deploy to AWS
- `aws logs tail /aws/lambda/{environment}-{service_name}-lambda --follow` - View logs

## Important Notes

- DO NOT modify production without explicit approval
- Always run tests before deploying
- Create descriptive commit messages for any fixes
- If you encounter permissions issues, note them in the results

Start by reading AGENT_INSTRUCTIONS_{environment.upper()}.md and then begin testing!
"""
    
    return prompt

def create_all_workspaces():
    """Create workspaces for all services"""
    
    repos = {
        'NiroSubs-V2': {
            'path': 'E:/Projects/NiroSubs-V2',
            'services': ['ns-auth', 'ns-dashboard', 'ns-payments', 'ns-user', 'ns-shell']
        },
        'VisualForgeMediaV2': {
            'path': 'E:/Projects/VisualForgeMediaV2',
            'services': ['vf-audio-service', 'vf-video-service', 'vf-image-service', 
                        'vf-text-service', 'vf-bulk-service', 'vf-dashboard-service']
        }
    }
    
    environments = ['dev', 'staging']
    
    for repo_name, config in repos.items():
        for service in config['services']:
            for env in environments:
                # Create workspace file
                create_workspace_for_service(repo_name, service, config['path'], env)
                
                # Create Copilot prompt file
                prompt = create_copilot_agent_prompt(service, env)
                prompt_file = Path(config['path']) / service / f"COPILOT_AGENT_PROMPT_{env.upper()}.md"
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(prompt)
                print(f"Created Copilot prompt: {prompt_file}")
            
            # Create launcher script for this service
            create_agent_launcher_script(repo_name, service, environments)
    
    # Create master launcher script
    create_master_launcher()

def create_master_launcher():
    """Create a master script to launch all agents at once"""
    
    master_script = """#!/bin/bash
# Master launcher for all VS Code agent workspaces

echo "🚀 Launching ALL Agent Workspaces"
echo "=================================="

# Function to launch a service's workspaces
launch_service() {
    local repo=$1
    local service=$2
    
    echo "Launching $service agents..."
    cd "E:/Projects/$repo/$service"
    
    # Launch dev workspace
    code "$service-dev-agent.code-workspace" --new-window &
    sleep 1
    
    # Launch staging workspace
    code "$service-staging-agent.code-workspace" --new-window &
    sleep 1
}

# Launch NiroSubs services
echo "Starting NiroSubs agents..."
launch_service "NiroSubs-V2" "ns-auth"
launch_service "NiroSubs-V2" "ns-dashboard"
launch_service "NiroSubs-V2" "ns-payments"
launch_service "NiroSubs-V2" "ns-user"
launch_service "NiroSubs-V2" "ns-shell"

# Launch VisualForgeMedia services
echo "Starting VisualForgeMedia agents..."
launch_service "VisualForgeMediaV2" "vf-audio-service"
launch_service "VisualForgeMediaV2" "vf-video-service"
launch_service "VisualForgeMediaV2" "vf-image-service"
launch_service "VisualForgeMediaV2" "vf-text-service"
launch_service "VisualForgeMediaV2" "vf-bulk-service"
launch_service "VisualForgeMediaV2" "vf-dashboard-service"

echo "✅ All agent workspaces launched!"
echo ""
echo "You now have 22 VS Code windows open (11 services × 2 environments)"
echo "Each window has GitHub Copilot ready to act as an autonomous agent"
echo ""
echo "In each window:"
echo "1. Open GitHub Copilot Chat (Ctrl+Shift+I)"
echo "2. Ask: 'Please read COPILOT_AGENT_PROMPT_[ENV].md and start testing'"
echo "3. Copilot will execute the tests and fix issues autonomously"
"""
    
    with open('E:/Projects/launch-all-vscode-agents.sh', 'w', encoding='utf-8') as f:
        f.write(master_script)
    
    # Windows version
    ps1_script = master_script.replace("#!/bin/bash", "# PowerShell")
    ps1_script = ps1_script.replace("echo", "Write-Host")
    ps1_script = ps1_script.replace("code", "code.cmd")
    ps1_script = ps1_script.replace("sleep", "Start-Sleep")
    ps1_script = ps1_script.replace("&\n", "\n")
    
    with open('E:/Projects/launch-all-vscode-agents.ps1', 'w', encoding='utf-8') as f:
        f.write(ps1_script)
    
    print("Created master launchers: launch-all-vscode-agents.sh and .ps1")

if __name__ == "__main__":
    print("Creating VS Code workspaces for all services...")
    print("=" * 60)
    create_all_workspaces()
    print("=" * 60)
    print("✅ All workspaces created!")
    print("")
    print("To launch agents:")
    print("1. For individual service: cd to service dir and run ./launch-agent-workspaces.ps1")
    print("2. For all services: Run ./launch-all-vscode-agents.ps1 from E:/Projects")
    print("")
    print("Each workspace will open in a separate VS Code window with:")
    print("- Agent instructions loaded")
    print("- Tasks configured for testing")
    print("- GitHub Copilot ready to execute")
    print("- Debugging configured")
    print("- AWS integration ready")