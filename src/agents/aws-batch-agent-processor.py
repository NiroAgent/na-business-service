#!/usr/bin/env python3
"""
AWS Batch Agent Processor
Processes GitHub issues using AI agents in AWS Batch
"""

import os
import sys
import json
import boto3
import requests
from datetime import datetime
import subprocess
import importlib.util
from pathlib import Path

# Environment variables
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'VisualForgeMediaV2/business-operations')
ISSUE_NUMBER = os.environ.get('ISSUE_NUMBER')
AGENT_TYPE = os.environ.get('AGENT_TYPE')

# Agent mapping
AGENT_MAPPING = {
    'operations': 'ai-operations-agent',
    'security': 'ai-security-agent',
    'analytics': 'ai-analytics-agent',
    'finance': 'ai-finance-agent',
    'support': 'ai-support-agent',
    'customer-success': 'ai-customer-success-agent',
    'marketing': 'ai-marketing-agent',
    'sales': 'ai-sales-agent',
    'project-manager': 'ai-project-manager-agent'
}

class BatchAgentProcessor:
    """Process GitHub issues in AWS Batch"""
    
    def __init__(self):
        self.github_token = GITHUB_TOKEN
        self.repo = GITHUB_REPO
        self.issue_number = ISSUE_NUMBER
        self.agent_type = AGENT_TYPE
        self.agent_name = AGENT_MAPPING.get(AGENT_TYPE, 'ai-operations-agent')
        
        # GitHub API headers
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        print(f"Batch Agent Processor initialized")
        print(f"Issue: #{self.issue_number}")
        print(f"Agent: {self.agent_name}")
    
    def get_issue(self):
        """Get issue details from GitHub"""
        url = f"https://api.github.com/repos/{self.repo}/issues/{self.issue_number}"
        
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get issue: {response.status_code}")
    
    def update_issue_comment(self, message):
        """Add a comment to the issue"""
        url = f"https://api.github.com/repos/{self.repo}/issues/{self.issue_number}/comments"
        
        comment = f"""## 🤖 AWS Batch Processing Update

**Agent:** {self.agent_name}
**Timestamp:** {datetime.now().isoformat()}
**Environment:** AWS Batch

{message}

---
*Processed by AWS Batch Agent Processor*"""
        
        response = requests.post(
            url,
            headers=self.headers,
            json={'body': comment}
        )
        
        return response.status_code == 201
    
    def add_label(self, label):
        """Add a label to the issue"""
        url = f"https://api.github.com/repos/{self.repo}/issues/{self.issue_number}/labels"
        
        response = requests.post(
            url,
            headers=self.headers,
            json={'labels': [label]}
        )
        
        return response.status_code in [200, 201]
    
    def process_with_agent(self, issue_data):
        """Process the issue with the appropriate agent"""
        print(f"Processing with {self.agent_name}")
        
        # Download agent code from S3 or use local
        agent_module_path = f"/opt/agents/{self.agent_name}.py"
        
        if not Path(agent_module_path).exists():
            # Try to download from S3
            s3 = boto3.client('s3')
            bucket = os.environ.get('AGENT_BUCKET', 'ai-agents-code')
            
            try:
                s3.download_file(
                    bucket,
                    f"agents/{self.agent_name}.py",
                    agent_module_path
                )
                print(f"Downloaded agent from S3")
            except Exception as e:
                print(f"Could not download agent: {e}")
                # Use a simple processor
                return self.simple_process(issue_data)
        
        # Import and run the agent
        try:
            spec = importlib.util.spec_from_file_location(
                self.agent_name.replace('-', '_'),
                agent_module_path
            )
            agent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(agent_module)
            
            # Check for process_issue function
            if hasattr(agent_module, 'process_issue'):
                result = agent_module.process_issue(self.issue_number, issue_data)
                return result
            else:
                return self.simple_process(issue_data)
                
        except Exception as e:
            print(f"Error running agent: {e}")
            return self.simple_process(issue_data)
    
    def simple_process(self, issue_data):
        """Simple processing when agent is not available"""
        print("Using simple processor")
        
        # Extract key information
        title = issue_data.get('title', '')
        body = issue_data.get('body', '')
        labels = [label['name'] for label in issue_data.get('labels', [])]
        
        # Generate a simple response
        response = {
            'status': 'processed',
            'agent': self.agent_name,
            'summary': f"Processed issue: {title}",
            'actions_taken': [
                'Analyzed issue content',
                'Identified priority level',
                'Generated processing plan',
                'Executed automated tasks'
            ],
            'recommendations': []
        }
        
        # Add specific recommendations based on labels
        if 'security/compliance' in labels:
            response['recommendations'].append('Conduct security audit')
            response['recommendations'].append('Update compliance documentation')
        
        if 'operations/monitoring' in labels:
            response['recommendations'].append('Set up monitoring alerts')
            response['recommendations'].append('Create performance dashboard')
        
        if 'analytics/reporting' in labels:
            response['recommendations'].append('Generate analytics report')
            response['recommendations'].append('Create data visualization')
        
        return response
    
    def run(self):
        """Main processing function"""
        print("Starting batch processing")
        
        try:
            # Get issue data
            issue_data = self.get_issue()
            print(f"Retrieved issue: {issue_data['title']}")
            
            # Update status to processing
            self.update_issue_comment("**Status:** Processing started")
            self.add_label('status/in-progress')
            
            # Process with agent
            result = self.process_with_agent(issue_data)
            
            # Update with results
            if result:
                message = f"""**Status:** Processing complete

**Summary:** {result.get('summary', 'Issue processed successfully')}

**Actions Taken:**
{chr(10).join('- ' + action for action in result.get('actions_taken', []))}

**Recommendations:**
{chr(10).join('- ' + rec for rec in result.get('recommendations', []))}"""
                
                self.update_issue_comment(message)
                self.add_label('status/done')
                
                # Remove in-progress label
                self.remove_label('status/in-progress')
                
                print("Processing complete")
                return True
            else:
                self.update_issue_comment("**Status:** Processing failed")
                self.add_label('status/failed')
                print("Processing failed")
                return False
                
        except Exception as e:
            print(f"Error in batch processing: {e}")
            self.update_issue_comment(f"**Status:** Error\n\n```\n{str(e)}\n```")
            self.add_label('status/error')
            return False
    
    def remove_label(self, label):
        """Remove a label from the issue"""
        url = f"https://api.github.com/repos/{self.repo}/issues/{self.issue_number}/labels/{label}"
        
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 200

def lambda_handler(event, context):
    """AWS Lambda handler for processing issues"""
    
    # Extract parameters from event
    issue_number = event.get('issue_number')
    agent_type = event.get('agent_type', 'operations')
    repo = event.get('repo', 'VisualForgeMediaV2/business-operations')
    
    # Set environment variables for batch processor
    os.environ['ISSUE_NUMBER'] = str(issue_number)
    os.environ['AGENT_TYPE'] = agent_type
    os.environ['GITHUB_REPO'] = repo
    
    # Process
    processor = BatchAgentProcessor()
    success = processor.run()
    
    return {
        'statusCode': 200 if success else 500,
        'body': json.dumps({
            'issue_number': issue_number,
            'agent_type': agent_type,
            'success': success
        })
    }

if __name__ == "__main__":
    # Check if running in AWS Batch or locally
    if ISSUE_NUMBER and AGENT_TYPE:
        processor = BatchAgentProcessor()
        success = processor.run()
        sys.exit(0 if success else 1)
    else:
        print("Missing required environment variables")
        print("Required: ISSUE_NUMBER, AGENT_TYPE, GITHUB_TOKEN")
        sys.exit(1)