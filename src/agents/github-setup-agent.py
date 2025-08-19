#!/usr/bin/env python3
"""
GitHub Token Setup Agent
Helps set up GitHub integration and provides token management
"""

import os
import logging
import subprocess
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('GitHubSetupAgent')

class GitHubSetupAgent:
    """Agent for setting up GitHub integration"""
    
    def __init__(self):
        self.name = "github-setup-agent"
        
    def check_github_status(self):
        """Check current GitHub setup status"""
        status = {
            "github_token": os.getenv("GITHUB_TOKEN") is not None,
            "github_token_length": len(os.getenv("GITHUB_TOKEN", "")),
            "git_available": self._check_git_available(),
            "github_api_test": False
        }
        
        if status["github_token"]:
            status["github_api_test"] = self._test_github_api()
        
        return status
    
    def _check_git_available(self):
        """Check if git is available"""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _test_github_api(self):
        """Test GitHub API connection"""
        try:
            import requests
            
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                return False
            
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"GitHub API test failed: {e}")
            return False
    
    def create_env_file(self, github_token: str = None):
        """Create or update .env file with GitHub token"""
        env_content = []
        
        # Read existing .env if it exists
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if not line.strip().startswith("GITHUB_TOKEN="):
                        env_content.append(line.strip())
        
        # Add GitHub token
        if github_token:
            env_content.append(f"GITHUB_TOKEN={github_token}")
        else:
            env_content.append("GITHUB_TOKEN=your_token_here")
        
        # Add other common variables if not present
        common_vars = [
            "VF_AGENT_SERVICE_URL=http://localhost:3000",
            "DATABASE_URL=postgresql://niro_user:niro_password@localhost:5432/niro_policies"
        ]
        
        for var in common_vars:
            var_name = var.split("=")[0]
            if not any(line.startswith(f"{var_name}=") for line in env_content):
                env_content.append(var)
        
        # Write .env file
        with open(".env", "w") as f:
            for line in env_content:
                f.write(line + "\n")
        
        logger.info("Created/updated .env file")
    
    def setup_github_integration(self):
        """Set up GitHub integration"""
        logger.info("🔧 Setting up GitHub integration...")
        
        status = self.check_github_status()
        
        if not status["git_available"]:
            logger.warning("Git not available - install Git first")
            return {"success": False, "error": "Git not installed"}
        
        if not status["github_token"]:
            logger.info("🔑 GitHub token not found")
            self._create_token_instructions()
            self.create_env_file()
            return {"success": True, "setup_required": True, "instructions": "GITHUB_TOKEN_SETUP.md"}
        
        if not status["github_api_test"]:
            logger.warning("GitHub token invalid or API not accessible")
            return {"success": False, "error": "Invalid GitHub token"}
        
        logger.info("✅ GitHub integration ready")
        return {"success": True, "ready": True}
    
    def _create_token_instructions(self):
        """Create detailed token setup instructions"""
        instructions = '''# GitHub Token Setup Instructions

## Step 1: Create Personal Access Token

1. Go to GitHub: https://github.com/settings/tokens
2. Click "Generate new token" -> "Generate new token (classic)"
3. Give it a descriptive name: "SDLC Agent Integration"
4. Set expiration (recommend 90 days or No expiration for development)
5. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `write:packages` (Upload packages to GitHub Package Registry)
   - `read:org` (Read org and team membership)

## Step 2: Copy and Set Token

1. Copy the generated token (starts with `ghp_` or `github_pat_`)
2. Set environment variable:

### Windows (Command Prompt):
```cmd
set GITHUB_TOKEN=your_token_here
```

### Windows (PowerShell):
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

### Linux/Mac:
```bash
export GITHUB_TOKEN=your_token_here
```

### Or use .env file:
Add this line to `.env` file:
```
GITHUB_TOKEN=your_token_here
```

## Step 3: Test Integration

Run the test command:
```bash
python github-setup-agent.py
```

## Step 4: Verify Policy Integration

Test the GitHub Issues agent:
```bash
python github-issues-policy-agent.py
```

## Security Notes

- Never commit tokens to version control
- Use environment variables or secure vaults
- Rotate tokens regularly
- Use minimal required permissions

## Troubleshooting

- If token is invalid: regenerate on GitHub
- If API fails: check network/firewall
- If permissions fail: verify token scopes
'''
        
        with open("GITHUB_TOKEN_SETUP.md", "w", encoding='utf-8') as f:
            f.write(instructions)
        
        logger.info("Created GITHUB_TOKEN_SETUP.md")
    
    def test_policy_integration(self):
        """Test GitHub Issues agent with policy integration"""
        try:
            # Dynamic import for GitHub agent
            import importlib.util
            
            spec = importlib.util.spec_from_file_location("github_issues_policy_agent", "github-issues-policy-agent.py")
            github_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(github_module)
            
            # Test agent initialization
            agent = github_module.PolicyEnhancedGitHubAgent()
            
            test_results = {
                "agent_initialized": True,
                "policy_engine_available": agent.policy_engine is not None,
                "github_token_set": os.getenv("GITHUB_TOKEN") is not None
            }
            
            if agent.policy_engine:
                # Test policy assessment
                try:
                    test_assessment = agent.policy_engine.assess_agent_action(
                        agent_id="github-test",
                        role_id="github-issues-agent",
                        content="# Test Issue\n\nThis is a test GitHub issue for policy compliance."
                    )
                    test_results["policy_assessment_working"] = test_assessment.get("success", False)
                except Exception as e:
                    test_results["policy_assessment_error"] = str(e)
            
            return test_results
            
        except Exception as e:
            logger.error(f"Policy integration test failed: {e}")
            return {"error": str(e)}
    
    def run_migration_tasks(self):
        """Run the migration tasks mentioned in the requirements"""
        logger.info("🚀 Running migration tasks...")
        
        tasks = {
            "set_github_token": self.setup_github_integration(),
            "test_policy_integration": self.test_policy_integration()
        }
        
        # Check if migration script exists and run it
        if os.path.exists("policy-migration-tool.py"):
            try:
                logger.info("Running policy migration script...")
                result = subprocess.run([sys.executable, "policy-migration-tool.py"], 
                                      capture_output=True, text=True, timeout=60)
                tasks["migration_script"] = {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr
                }
            except Exception as e:
                tasks["migration_script"] = {"error": str(e)}
        
        return tasks


def main():
    """Main function for GitHub setup agent"""
    logger.info("🔧 GitHub Setup Agent - Setting up GitHub Integration")
    
    agent = GitHubSetupAgent()
    
    # Check current status
    status = agent.check_github_status()
    logger.info(f"Current GitHub status: {status}")
    
    # Set up GitHub integration
    setup_result = agent.setup_github_integration()
    logger.info(f"Setup result: {setup_result}")
    
    # Test policy integration
    if setup_result.get("ready") or os.getenv("GITHUB_TOKEN"):
        test_result = agent.test_policy_integration()
        logger.info(f"Policy integration test: {test_result}")
    
    # Run migration tasks
    migration_result = agent.run_migration_tasks()
    logger.info(f"Migration tasks: {migration_result}")
    
    # Create summary report
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "github_status": status,
        "setup_result": setup_result,
        "policy_test": test_result if 'test_result' in locals() else None,
        "migration_tasks": migration_result,
        "next_steps": [
            "Set GITHUB_TOKEN environment variable if not already set",
            "Run github-issues-policy-agent.py to test full integration",
            "Start creating policy-compliant GitHub Issues",
            "Monitor policy compliance metrics"
        ]
    }
    
    # Save summary
    import json
    with open("GITHUB_SETUP_SUMMARY.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info("✅ GitHub setup completed - see GITHUB_SETUP_SUMMARY.json")
    
    if not status["github_token"]:
        logger.info("🔑 NEXT: Set your GitHub token using instructions in GITHUB_TOKEN_SETUP.md")
    elif setup_result.get("ready"):
        logger.info("🚀 READY: GitHub integration is ready for use!")
    
    return summary


if __name__ == "__main__":
    main()
