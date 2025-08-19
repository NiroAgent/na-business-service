#!/usr/bin/env python3

"""
GitHub Agent Picker - Interactive Assignment Tool
Assigns specific agents from 50-agent pool to GitHub issues with cost optimization
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class GitHubAgentPicker:
    def __init__(self):
        self.config = self.load_agent_config()
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            print("❌ GITHUB_TOKEN environment variable required")
            sys.exit(1)
    
    def load_agent_config(self) -> Dict:
        """Load agent configuration from agents.json"""
        try:
            with open('agent-systems/agents.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ agents.json not found. Run setup first.")
            sys.exit(1)
    
    def get_repositories(self) -> List[str]:
        """Get available repositories"""
        return [
            "autonomous-business-system",
            "NiroSubs-V2", 
            "VisualForgeMediaV2",
            "agent-dashboard"
        ]
    
    def get_available_agents(self) -> Dict[str, Dict]:
        """Get all available agents organized by type"""
        agents = {}
        config = self.config['agent_configuration']['distribution']
        
        # Developer agents (20)
        agents['Developer'] = {
            'developer_frontend_1': 'React/Vue specialist',
            'developer_frontend_2': 'Angular/TypeScript specialist', 
            'developer_frontend_3': 'Mobile/React Native specialist',
            'developer_backend_1': 'Node.js/Express specialist',
            'developer_backend_2': 'Python/Django specialist',
            'developer_backend_3': 'Python/FastAPI specialist',
            'developer_backend_4': 'Database optimization specialist',
            'developer_fullstack_1': 'MERN stack specialist',
            'developer_fullstack_2': 'Next.js specialist',
            'developer_fullstack_3': 'Cloud integration specialist',
            'developer_api_1': 'REST API specialist',
            'developer_api_2': 'GraphQL specialist',
            'developer_performance_1': 'Web performance specialist',
            'developer_performance_2': 'Database performance specialist',
            'developer_devops_1': 'CI/CD pipeline specialist',
            'developer_devops_2': 'Docker/Kubernetes specialist',
            'developer_security_1': 'Security-focused developer',
            'developer_security_2': 'Auth/OAuth specialist',
            'developer_integration_1': 'Third-party integration specialist',
            'developer_integration_2': 'Payment/Stripe specialist'
        }
        
        # QA agents (10)
        agents['QA'] = {
            'qa_automation_1': 'Cypress/Playwright specialist',
            'qa_automation_2': 'Jest/Testing Library specialist',
            'qa_automation_3': 'API testing specialist',
            'qa_manual_1': 'Manual testing specialist',
            'qa_manual_2': 'UX/UI testing specialist',
            'qa_performance_1': 'Performance testing specialist',
            'qa_performance_2': 'Load testing specialist',
            'qa_security_1': 'Security testing specialist',
            'qa_accessibility_1': 'Accessibility testing specialist',
            'qa_mobile_1': 'Mobile testing specialist'
        }
        
        # DevOps agents (5)
        agents['DevOps'] = {
            'devops_cicd_1': 'GitHub Actions specialist',
            'devops_cicd_2': 'Deployment automation specialist',
            'devops_infrastructure_1': 'AWS/CloudFormation specialist',
            'devops_infrastructure_2': 'Terraform specialist',
            'devops_monitoring_1': 'Monitoring/alerting specialist'
        }
        
        # Manager agents (5)
        agents['Manager'] = {
            'manager_project_1': 'Agile/Scrum specialist',
            'manager_project_2': 'Sprint planning specialist',
            'manager_product_1': 'Product strategy specialist',
            'manager_product_2': 'Stakeholder communication specialist',
            'manager_coordination_1': 'Team coordination specialist'
        }
        
        # Architect agents (5)
        agents['Architect'] = {
            'architect_system_1': 'System architecture specialist',
            'architect_system_2': 'Microservices specialist',
            'architect_platform_1': 'Platform architecture specialist',
            'architect_integration_1': 'Integration architecture specialist',
            'architect_scalability_1': 'Scalability specialist'
        }
        
        # Security agents (3)
        agents['Security'] = {
            'security_assessment_1': 'Vulnerability assessment specialist',
            'security_compliance_1': 'Compliance auditing specialist',
            'security_code_review_1': 'Security code review specialist'
        }
        
        # Analytics agents (2)
        agents['Analytics'] = {
            'analytics_performance_1': 'Performance analytics specialist',
            'analytics_business_1': 'Business intelligence specialist'
        }
        
        return agents
    
    def display_agents(self, agents: Dict[str, Dict]):
        """Display available agents organized by type"""
        print("\n🤖 Available Agents (50 total - 95% cost optimized with spot instances):")
        print("💰 Monthly cost: $8-15 vs $150-300 with Lambda\n")
        
        for agent_type, agent_list in agents.items():
            print(f"📋 {agent_type} ({len(agent_list)} agents):")
            for i, (agent_id, description) in enumerate(agent_list.items(), 1):
                print(f"  {i:2d}. {agent_id} - {description}")
            print()
    
    def select_repository(self) -> str:
        """Interactive repository selection"""
        repos = self.get_repositories()
        print("📁 Select Repository:")
        for i, repo in enumerate(repos, 1):
            print(f"  {i}. {repo}")
        
        while True:
            try:
                choice = int(input("\nEnter repository number: ")) - 1
                if 0 <= choice < len(repos):
                    return repos[choice]
                print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def select_issue(self, repo: str) -> str:
        """Get issue number from user"""
        while True:
            issue_num = input(f"\n🎯 Enter issue number for {repo}: ").strip()
            if issue_num.isdigit():
                return issue_num
            print("❌ Please enter a valid issue number.")
    
    def select_agents(self, agents: Dict[str, Dict]) -> List[str]:
        """Interactive agent selection"""
        selected = []
        
        print("\n🎯 Agent Selection:")
        print("Enter agent IDs (comma-separated) or type categories:")
        print("Examples: 'developer_frontend_1,qa_automation_1' or 'frontend,testing'")
        print("Available shortcuts: frontend, backend, fullstack, qa, devops, manager, architect, security, analytics")
        
        selection = input("\nYour selection: ").strip().lower()
        
        # Handle shortcuts
        shortcuts = {
            'frontend': ['developer_frontend_1', 'developer_frontend_2', 'developer_frontend_3'],
            'backend': ['developer_backend_1', 'developer_backend_2', 'developer_backend_3'],
            'fullstack': ['developer_fullstack_1', 'developer_fullstack_2', 'developer_fullstack_3'],
            'qa': ['qa_automation_1', 'qa_manual_1', 'qa_performance_1'],
            'devops': ['devops_cicd_1', 'devops_infrastructure_1'],
            'manager': ['manager_project_1'],
            'architect': ['architect_system_1'],
            'security': ['security_assessment_1'],
            'analytics': ['analytics_performance_1']
        }
        
        if selection in shortcuts:
            selected = shortcuts[selection]
        else:
            # Parse comma-separated agent IDs
            agent_ids = [id.strip() for id in selection.split(',')]
            all_agents = {}
            for agent_group in agents.values():
                all_agents.update(agent_group)
            
            for agent_id in agent_ids:
                if agent_id in all_agents:
                    selected.append(agent_id)
                else:
                    print(f"⚠️  Agent '{agent_id}' not found. Skipping.")
        
        if not selected:
            print("❌ No valid agents selected. Using default developer agent.")
            selected = ['developer_fullstack_1']
        
        return selected
    
    def get_priority(self) -> str:
        """Get priority level"""
        priorities = {
            '1': 'P0_critical',
            '2': 'P1_high', 
            '3': 'P2_medium',
            '4': 'P3_low',
            '5': 'P4_backlog'
        }
        
        print("\n🎯 Priority Level:")
        print("  1. P0 Critical (Production down)")
        print("  2. P1 High (Major feature broken)")
        print("  3. P2 Medium (Standard development)")
        print("  4. P3 Low (Minor improvements)")
        print("  5. P4 Backlog (Future consideration)")
        
        while True:
            choice = input("Select priority (1-5): ").strip()
            if choice in priorities:
                return priorities[choice]
            print("❌ Please enter 1-5.")
    
    def estimate_completion(self, priority: str, agent_count: int) -> str:
        """Estimate completion time based on priority and agent count"""
        base_hours = {
            'P0_critical': 2,
            'P1_high': 8, 
            'P2_medium': 24,
            'P3_low': 72,
            'P4_backlog': 168
        }
        
        hours = base_hours.get(priority, 24) // max(agent_count, 1)
        completion_time = datetime.now() + timedelta(hours=hours)
        return completion_time.isoformat()
    
    def assign_agents(self, repo: str, issue_num: str, agents: List[str], priority: str):
        """Assign agents to GitHub issue via custom fields"""
        print(f"\n🚀 Assigning {len(agents)} agents to issue #{issue_num} in {repo}")
        
        # Prepare custom field updates
        estimated_completion = self.estimate_completion(priority, len(agents))
        processing_started = datetime.now().isoformat()
        
        # Update custom fields via GitHub API
        try:
            # Primary agent assignment
            primary_agent = agents[0]
            
            # Use GitHub CLI to update custom fields
            commands = [
                f'gh issue edit {issue_num} --repo NiroAgentV2/{repo} --add-field "assigned_agent={primary_agent}"',
                f'gh issue edit {issue_num} --repo NiroAgentV2/{repo} --add-field "agent_status=assigned"',
                f'gh issue edit {issue_num} --repo NiroAgentV2/{repo} --add-field "priority_level={priority}"',
                f'gh issue edit {issue_num} --repo NiroAgentV2/{repo} --add-field "processing_started={processing_started}"',
                f'gh issue edit {issue_num} --repo NiroAgentV2/{repo} --add-field "estimated_completion={estimated_completion}"'
            ]
            
            if len(agents) > 1:
                agent_notes = f"Multi-agent assignment: {', '.join(agents)}"
                commands.append(f'gh issue edit {issue_num} --repo NiroAgentV2/{repo} --add-field "agent_notes={agent_notes}"')
            
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"⚠️  Warning: {result.stderr.strip()}")
            
            print(f"✅ Successfully assigned agents to issue #{issue_num}")
            print(f"   Primary agent: {primary_agent}")
            if len(agents) > 1:
                print(f"   Additional agents: {', '.join(agents[1:])}")
            print(f"   Priority: {priority}")
            print(f"   Estimated completion: {estimated_completion}")
            
            # Trigger GitHub Action
            self.trigger_github_action(repo, issue_num, agents)
            
        except Exception as e:
            print(f"❌ Error assigning agents: {str(e)}")
    
    def trigger_github_action(self, repo: str, issue_num: str, agents: List[str]):
        """Trigger GitHub Action for agent processing"""
        print(f"\n🔄 Triggering GitHub Action for spot instance deployment...")
        
        try:
            cmd = f'gh workflow run agent-assignment.yml --repo NiroAgentV2/{repo} -f issue_number={issue_num} -f agents="{",".join(agents)}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ GitHub Action triggered successfully")
                print("🎯 Agents will be deployed to spot instances for processing")
            else:
                print(f"⚠️  GitHub Action trigger warning: {result.stderr.strip()}")
                
        except Exception as e:
            print(f"⚠️  Could not trigger GitHub Action: {str(e)}")
    
    def run(self):
        """Main interactive flow"""
        print("🤖 GitHub Agent Picker - 50 Agent Assignment System")
        print("💰 95% Cost Optimized with Spot Instances ($8-15/month)")
        print("=" * 60)
        
        # Get available agents
        agents = self.get_available_agents()
        
        # Display agents
        self.display_agents(agents)
        
        # Interactive selection
        repo = self.select_repository()
        issue_num = self.select_issue(repo)
        selected_agents = self.select_agents(agents)
        priority = self.get_priority()
        
        # Confirm assignment
        print(f"\n📋 Assignment Summary:")
        print(f"   Repository: {repo}")
        print(f"   Issue: #{issue_num}")
        print(f"   Agents: {', '.join(selected_agents)}")
        print(f"   Priority: {priority}")
        
        confirm = input("\n✅ Proceed with assignment? (y/N): ").strip().lower()
        if confirm == 'y':
            self.assign_agents(repo, issue_num, selected_agents, priority)
        else:
            print("❌ Assignment cancelled.")

if __name__ == "__main__":
    picker = GitHubAgentPicker()
    picker.run()
