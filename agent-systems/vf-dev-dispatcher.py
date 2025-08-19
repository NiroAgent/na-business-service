#!/usr/bin/env python3
"""
VF-Dev Agent Dispatcher
=======================
Receives webhooks from GitHub and dispatches work to agents on spot instances
Runs on vf-dev server
"""

from flask import Flask, request, jsonify
import boto3
import json
import requests
import logging
from datetime import datetime
import random
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS clients
ec2 = boto3.client('ec2', region_name='us-east-1')
ssm = boto3.client('ssm', region_name='us-east-1')

# Track agent assignments
agent_assignments = {}
agent_workload = {}

# Agent configuration
AGENT_CONFIG = {
    "vf-developer-agent": {
        "count": 20,
        "skills": ["code", "debug", "implement", "feature"],
        "repos": ["vf-dashboard-service", "vf-auth-service", "vf-video-service", 
                  "vf-image-service", "vf-audio-service", "vf-text-service"]
    },
    "vf-qa-agent": {
        "count": 10,
        "skills": ["test", "validate", "qa", "quality"],
        "repos": ["all"]
    },
    "vf-devops-agent": {
        "count": 5,
        "skills": ["deploy", "infrastructure", "ci/cd", "aws"],
        "repos": ["all"]
    },
    "vf-architect-agent": {
        "count": 5,
        "skills": ["design", "architecture", "review", "standards"],
        "repos": ["all"]
    },
    "vf-manager-agent": {
        "count": 5,
        "skills": ["manage", "coordinate", "plan", "delegate"],
        "repos": ["business-operations"]
    },
    "vf-security-agent": {
        "count": 3,
        "skills": ["security", "audit", "compliance", "vulnerability"],
        "repos": ["all"]
    },
    "vf-analytics-agent": {
        "count": 2,
        "skills": ["analyze", "report", "metrics", "data"],
        "repos": ["business-operations"]
    }
}

@app.route('/agent-dispatch', methods=['POST'])
def dispatch_agent():
    """Main webhook endpoint for GitHub"""
    
    data = request.json
    logger.info(f"Received dispatch request: {data}")
    
    repository = data.get('repository')
    issue_number = data.get('issue_number')
    agent_type = data.get('agent', 'vf-developer-agent')
    action = data.get('action', 'process')
    
    # Find available agent instance
    instance = find_available_agent(agent_type)
    
    if not instance:
        logger.warning(f"No available {agent_type} instances")
        return jsonify({
            'status': 'error',
            'message': 'No available agents'
        }), 503
    
    # Dispatch work to agent
    result = dispatch_to_instance(instance, {
        'type': action,
        'repository': repository,
        'issue_number': issue_number,
        'agent_type': agent_type,
        'timestamp': datetime.now().isoformat()
    })
    
    if result:
        # Track assignment
        assignment_key = f"{repository}#{issue_number}"
        agent_assignments[assignment_key] = {
            'agent': agent_type,
            'instance_id': instance['InstanceId'],
            'started': datetime.now().isoformat(),
            'status': 'processing'
        }
        
        # Update GitHub issue
        update_github_issue(repository, issue_number, agent_type, 'processing')
        
        return jsonify({
            'status': 'success',
            'agent': agent_type,
            'instance': instance['InstanceId'],
            'message': f'Dispatched to {agent_type}'
        }), 200
    
    return jsonify({
        'status': 'error',
        'message': 'Failed to dispatch to agent'
    }), 500

def find_available_agent(agent_type):
    """Find an available spot instance running the specified agent type"""
    
    try:
        # Get running spot instances
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running']},
                {'Name': 'instance-lifecycle', 'Values': ['spot']},
                {'Name': 'tag:AgentType', 'Values': [agent_type]}
            ]
        )
        
        available_instances = []
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                
                # Check workload
                current_load = agent_workload.get(instance_id, 0)
                if current_load < 3:  # Max 3 concurrent issues per instance
                    available_instances.append(instance)
        
        if available_instances:
            # Select instance with lowest load
            selected = min(available_instances, 
                          key=lambda x: agent_workload.get(x['InstanceId'], 0))
            
            # Update workload
            agent_workload[selected['InstanceId']] = \
                agent_workload.get(selected['InstanceId'], 0) + 1
            
            return selected
            
    except Exception as e:
        logger.error(f"Error finding agent: {e}")
    
    return None

def dispatch_to_instance(instance, work_item):
    """Send work to specific EC2 instance via SSM"""
    
    try:
        instance_id = instance['InstanceId']
        
        # Create command to run on instance
        command = f"""
        cd /home/ec2-user/agents
        python3 process_issue.py \\
            --repo '{work_item['repository']}' \\
            --issue {work_item['issue_number']} \\
            --agent-type '{work_item['agent_type']}'
        """
        
        # Send command via SSM
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': [command],
                'workingDirectory': ['/home/ec2-user/agents']
            },
            TimeoutSeconds=3600
        )
        
        logger.info(f"Dispatched to {instance_id}: {response['Command']['CommandId']}")
        return True
        
    except Exception as e:
        logger.error(f"Error dispatching to instance: {e}")
        return False

def update_github_issue(repository, issue_number, agent_type, status):
    """Update GitHub issue with agent assignment"""
    
    try:
        # Use GitHub API to add comment
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            logger.warning("No GitHub token available")
            return
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Add comment
        comment_body = f"""🤖 **Agent Assignment Update**

- **Assigned Agent**: `{agent_type}`
- **Status**: `{status}`
- **Timestamp**: {datetime.now().isoformat()}

The agent is now processing this issue on our spot instance infrastructure.
"""
        
        url = f"https://api.github.com/repos/{repository}/issues/{issue_number}/comments"
        
        response = requests.post(url, 
                                 json={'body': comment_body},
                                 headers=headers)
        
        if response.status_code == 201:
            logger.info(f"Updated issue {repository}#{issue_number}")
        else:
            logger.warning(f"Failed to update issue: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error updating GitHub issue: {e}")

@app.route('/status', methods=['GET'])
def get_status():
    """Get dispatcher status and agent workload"""
    
    total_agents = sum(config['count'] for config in AGENT_CONFIG.values())
    
    # Get current spot instance status
    running_instances = 0
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running']},
                {'Name': 'instance-lifecycle', 'Values': ['spot']}
            ]
        )
        
        for reservation in response['Reservations']:
            running_instances += len(reservation['Instances'])
            
    except Exception as e:
        logger.error(f"Error getting instance status: {e}")
    
    return jsonify({
        'status': 'running',
        'total_agents': total_agents,
        'running_instances': running_instances,
        'active_assignments': len(agent_assignments),
        'workload': agent_workload,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Load GitHub token from environment or file
    if not os.environ.get('GITHUB_TOKEN'):
        try:
            with open('/etc/agents/github-token', 'r') as f:
                os.environ['GITHUB_TOKEN'] = f.read().strip()
        except:
            logger.warning("No GitHub token found")
    
    # Start Flask app
    logger.info("Starting VF-Dev Agent Dispatcher...")
    logger.info(f"Total agents configured: {sum(c['count'] for c in AGENT_CONFIG.values())}")
    
    app.run(host='0.0.0.0', port=8080, debug=False)