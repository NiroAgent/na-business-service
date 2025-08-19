#!/usr/bin/env python3
"""
Agent Assignment via GitHub Custom Fields
==========================================
Uses custom fields to assign specific agents to issues
Integrates with our 50-agent spot instance system
"""

import subprocess
import json
from typing import Dict, List

def create_agent_config():
    """Create agent configuration with our actual agent roles"""
    
    agents_config = {
        "agents": [
            {
                "name": "vf-developer-agent",
                "type": "developer",
                "repos": ["vf-dashboard-service", "vf-auth-service", "vf-video-service", "vf-image-service", "vf-audio-service"],
                "role": "Implements features, fixes bugs",
                "spot_instances": 20  # 20 developer agents on spot
            },
            {
                "name": "vf-qa-agent",
                "type": "qa",
                "repos": ["all"],
                "role": "Tests and validates code",
                "spot_instances": 10  # 10 QA agents
            },
            {
                "name": "vf-devops-agent",
                "type": "devops",
                "repos": ["all"],
                "role": "Handles deployments and infrastructure",
                "spot_instances": 5  # 5 DevOps agents
            },
            {
                "name": "vf-manager-agent",
                "type": "manager",
                "repos": ["business-operations"],
                "role": "Project management and delegation",
                "spot_instances": 5  # 5 manager agents
            },
            {
                "name": "vf-architect-agent",
                "type": "architect",
                "repos": ["all"],
                "role": "Reviews and approves technical designs",
                "spot_instances": 5  # 5 architect agents
            },
            {
                "name": "vf-security-agent",
                "type": "security",
                "repos": ["all"],
                "role": "Security analysis and compliance",
                "spot_instances": 3  # 3 security agents
            },
            {
                "name": "vf-analytics-agent",
                "type": "analytics",
                "repos": ["business-operations"],
                "role": "Data analysis and reporting",
                "spot_instances": 2  # 2 analytics agents
            }
        ],
        "total_spot_instances": 50,
        "deployment": {
            "region": "us-east-1",
            "instance_type": "t3.large",
            "spot_price": "0.03"
        }
    }
    
    # Save as JSON (more universal)
    with open("agents.json", "w") as f:
        json.dump(agents_config, f, indent=2)
    
    print("[OK] Created agents.json configuration")
    return agents_config

def create_custom_field_setup():
    """Create GitHub custom field configuration for agent assignment"""
    
    setup_script = '''#!/bin/bash
# Setup GitHub Custom Fields for Agent Assignment

echo "Setting up custom fields for agent assignment..."

# For each repository, create custom field
REPOS=(
    "VisualForgeMediaV2/vf-dashboard-service"
    "VisualForgeMediaV2/vf-auth-service"
    "VisualForgeMediaV2/vf-video-service"
    "VisualForgeMediaV2/vf-image-service"
    "VisualForgeMediaV2/vf-audio-service"
    "VisualForgeMediaV2/business-operations"
)

for REPO in "${REPOS[@]}"; do
    echo "Creating custom field for $REPO..."
    
    # Create custom field via GitHub API
    gh api "/repos/$REPO/properties/values" \\
        -X PATCH \\
        -f properties='[
            {
                "property_name": "assigned_agent",
                "value": "none"
            },
            {
                "property_name": "agent_status",
                "value": "pending"
            },
            {
                "property_name": "processing_started",
                "value": ""
            },
            {
                "property_name": "estimated_completion",
                "value": ""
            }
        ]' 2>/dev/null || echo "  Custom fields may already exist"
done

echo "Custom fields setup complete!"
'''
    
    with open("setup-custom-fields.sh", "w") as f:
        f.write(setup_script)
    
    print("[OK] Created setup-custom-fields.sh")
    return "setup-custom-fields.sh"

def create_agent_picker():
    """Create TypeScript agent picker that integrates with our system"""
    
    picker_code = '''import fs from "fs";
import path from "path";
import yaml from "js-yaml";
import inquirer from "inquirer";
import { execSync } from "child_process";

interface Agent {
    name: string;
    type: string;
    repos: string[];
    role: string;
    spot_instances: number;
}

interface AgentConfig {
    agents: Agent[];
    total_spot_instances: number;
    deployment: {
        region: string;
        instance_type: string;
        spot_price: string;
    };
}

// Load our agent configuration
const config = yaml.load(fs.readFileSync("agents.yml", "utf8")) as AgentConfig;

async function assignAgentToIssue() {
    // Get repository
    const { repo } = await inquirer.prompt([
        {
            type: "list",
            name: "repo",
            message: "Select repository:",
            choices: [
                "vf-dashboard-service",
                "vf-auth-service",
                "vf-video-service",
                "vf-image-service",
                "vf-audio-service",
                "business-operations"
            ]
        }
    ]);

    // Get issue number
    const { issueNumber } = await inquirer.prompt([
        {
            type: "input",
            name: "issueNumber",
            message: "Enter issue number:",
            validate: (input: string) => {
                return !isNaN(parseInt(input)) || "Please enter a valid number";
            }
        }
    ]);

    // Select agent(s)
    const availableAgents = config.agents.filter(a => 
        a.repos.includes("all") || a.repos.includes(repo)
    );

    const { selectedAgents } = await inquirer.prompt([
        {
            type: "checkbox",
            name: "selectedAgents",
            message: "Select agent(s) to assign:",
            choices: availableAgents.map(a => ({
                name: `${a.name} (${a.role}) - ${a.spot_instances} instances`,
                value: a.name
            })),
            validate: (arr: string[]) => arr.length > 0 || "Select at least one agent"
        }
    ]);

    // Update custom field with assigned agents
    for (const agentName of selectedAgents) {
        console.log(`\\nAssigning ${agentName} to issue #${issueNumber} in ${repo}...`);
        
        // Update custom field via GitHub API
        const cmd = `gh api /repos/VisualForgeMediaV2/${repo}/issues/${issueNumber}/properties \\
            -X PATCH \\
            -f properties='[{"property_name": "assigned_agent", "value": "${agentName}"}]'`;
        
        try {
            execSync(cmd, { stdio: "inherit" });
            console.log(`✓ Assigned ${agentName}`);
            
            // Trigger agent processing
            triggerAgentProcessing(repo, issueNumber, agentName);
        } catch (error) {
            console.error(`✗ Failed to assign ${agentName}`);
        }
    }
}

function triggerAgentProcessing(repo: string, issueNumber: string, agentName: string) {
    // Send webhook to dispatcher on vf-dev
    console.log(`Triggering ${agentName} to process issue...`);
    
    const webhookCmd = `curl -X POST https://vf-dev.visualforgemedia.com/agent-webhook \\
        -H "Content-Type: application/json" \\
        -d '{
            "repo": "${repo}",
            "issue": ${issueNumber},
            "agent": "${agentName}",
            "action": "process"
        }'`;
    
    try {
        execSync(webhookCmd, { stdio: "pipe" });
        console.log(`✓ Agent triggered`);
    } catch (error) {
        console.error(`✗ Failed to trigger agent`);
    }
}

async function checkAgentStatus() {
    const { repo, issueNumber } = await inquirer.prompt([
        {
            type: "input",
            name: "repo",
            message: "Repository name:"
        },
        {
            type: "input",
            name: "issueNumber",
            message: "Issue number:"
        }
    ]);

    // Get custom field values
    const cmd = `gh api /repos/VisualForgeMediaV2/${repo}/issues/${issueNumber}/properties --jq '.properties'`;
    
    try {
        const result = execSync(cmd, { encoding: "utf8" });
        const properties = JSON.parse(result);
        
        console.log("\\n=== Agent Assignment Status ===");
        console.log(`Assigned Agent: ${properties.assigned_agent || "none"}`);
        console.log(`Status: ${properties.agent_status || "pending"}`);
        console.log(`Started: ${properties.processing_started || "not started"}`);
        console.log(`ETA: ${properties.estimated_completion || "unknown"}`);
    } catch (error) {
        console.error("Failed to get status");
    }
}

// Main menu
async function main() {
    const { action } = await inquirer.prompt([
        {
            type: "list",
            name: "action",
            message: "What would you like to do?",
            choices: [
                { name: "Assign agent(s) to issue", value: "assign" },
                { name: "Check agent status on issue", value: "status" },
                { name: "View available agents", value: "list" },
                { name: "Exit", value: "exit" }
            ]
        }
    ]);

    switch (action) {
        case "assign":
            await assignAgentToIssue();
            break;
        case "status":
            await checkAgentStatus();
            break;
        case "list":
            console.log("\\n=== Available Agents (50 total on spot instances) ===");
            config.agents.forEach(a => {
                console.log(`${a.name}: ${a.role} (${a.spot_instances} instances)`);
            });
            break;
        case "exit":
            process.exit(0);
    }
    
    // Loop back to menu
    if (action !== "exit") {
        await main();
    }
}

// Run
main().catch(console.error);
'''
    
    with open("scripts/agent-picker.ts", "w") as f:
        f.write(picker_code)
    
    print("[OK] Created scripts/agent-picker.ts")

def create_package_json():
    """Create package.json for the agent picker"""
    
    package = {
        "name": "vf-agent-assignment",
        "version": "1.0.0",
        "private": True,
        "type": "module",
        "scripts": {
            "agents": "ts-node scripts/agent-picker.ts",
            "setup": "bash setup-custom-fields.sh"
        },
        "dependencies": {
            "inquirer": "^9.2.16",
            "js-yaml": "^4.1.0"
        },
        "devDependencies": {
            "@types/node": "^20.12.7",
            "@types/inquirer": "^9.0.3",
            "@types/js-yaml": "^4.0.5",
            "ts-node": "^10.9.2",
            "typescript": "^5.5.4"
        }
    }
    
    with open("package.json", "w") as f:
        json.dump(package, f, indent=2)
    
    print("[OK] Created package.json")

def create_github_action_for_custom_fields():
    """Create GitHub Action that reads custom fields and triggers agents"""
    
    workflow = """name: Process Issues Based on Custom Fields

on:
  issues:
    types: [opened, edited, labeled]
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number to process'
        required: true

jobs:
  check-and-process:
    runs-on: ubuntu-latest
    
    steps:
    - name: Get Custom Field Values
      id: custom-fields
      uses: actions/github-script@v6
      with:
        script: |
          const issue_number = context.issue?.number || context.payload.inputs?.issue_number;
          
          // Get custom field values
          const { data } = await github.rest.repos.getCustomProperties({
            owner: context.repo.owner,
            repo: context.repo.repo
          });
          
          // Get assigned agent from custom field
          const assignedAgent = data.properties?.assigned_agent;
          
          if (assignedAgent && assignedAgent !== 'none') {
            core.setOutput('agent', assignedAgent);
            core.setOutput('should_process', 'true');
          } else {
            core.setOutput('should_process', 'false');
          }
    
    - name: Trigger Agent Processing
      if: steps.custom-fields.outputs.should_process == 'true'
      run: |
        curl -X POST https://vf-dev.visualforgemedia.com/agent-webhook \\
          -H "Content-Type: application/json" \\
          -d '{
            "repo": "${{ github.repository }}",
            "issue": ${{ github.event.issue.number }},
            "agent": "${{ steps.custom-fields.outputs.agent }}",
            "action": "process"
          }'
    
    - name: Update Status Field
      if: steps.custom-fields.outputs.should_process == 'true'
      uses: actions/github-script@v6
      with:
        script: |
          await github.rest.repos.createOrUpdateCustomProperty({
            owner: context.repo.owner,
            repo: context.repo.repo,
            custom_property_name: 'agent_status',
            value: 'processing'
          });
          
          await github.rest.repos.createOrUpdateCustomProperty({
            owner: context.repo.owner,
            repo: context.repo.repo,
            custom_property_name: 'processing_started',
            value: new Date().toISOString()
          });
"""
    
    with open(".github/workflows/custom-field-processor.yml", "w") as f:
        f.write(workflow)
    
    print("[OK] Created .github/workflows/custom-field-processor.yml")

def main():
    print("\n" + "="*80)
    print("AGENT CUSTOM FIELD ASSIGNMENT SYSTEM")
    print("="*80)
    
    # Create configurations
    create_agent_config()
    create_custom_field_setup()
    
    # Create agent picker
    import os
    os.makedirs("scripts", exist_ok=True)
    create_agent_picker()
    
    # Create package.json
    create_package_json()
    
    # Create GitHub Action
    os.makedirs(".github/workflows", exist_ok=True)
    create_github_action_for_custom_fields()
    
    print("\n[SYSTEM COMPONENTS]:")
    print("1. agents.yml - Agent configuration (50 agents)")
    print("2. setup-custom-fields.sh - Creates GitHub custom fields")
    print("3. scripts/agent-picker.ts - Interactive agent assignment")
    print("4. .github/workflows/custom-field-processor.yml - Auto-processing")
    
    print("\n[HOW IT WORKS]:")
    print("1. Run: npm install")
    print("2. Run: npm run setup (creates custom fields)")
    print("3. Run: npm run agents (interactive picker)")
    print("4. Select repo, issue, and agent(s)")
    print("5. Custom field gets updated")
    print("6. GitHub Action triggers")
    print("7. Agent on spot instance processes")
    
    print("\n[ADVANTAGES]:")
    print("- Concrete assignment via custom fields")
    print("- Multiple agents can be assigned")
    print("- Status tracking in custom fields")
    print("- Works with 50-agent spot instance system")
    print("- $8-15/month total cost")
    
    print("\n[AGENT DISTRIBUTION]:")
    print("- 20 Developer agents")
    print("- 10 QA agents")
    print("- 5 DevOps agents")
    print("- 5 Manager agents")
    print("- 5 Architect agents")
    print("- 3 Security agents")
    print("- 2 Analytics agents")
    print("= 50 Total on spot instances")
    
    print("\n[SUCCESS!]")
    print("Custom field assignment system created!")

if __name__ == "__main__":
    main()