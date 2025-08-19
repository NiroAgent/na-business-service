#!/usr/bin/env python3
"""
GitHub Webhook Handler for PM and Agent System Integration
Handles real-time GitHub events and coordinates with agent system
"""

from flask import Flask, request, jsonify
import hashlib
import hmac
import json
import os
import requests
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubWebhookHandler:
    def __init__(self):
        self.webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET')
        self.agent_api_url = os.getenv('AGENT_API_URL', 'http://localhost:5003/api')
        self.pm_notification_url = os.getenv('PM_NOTIFICATION_URL')
        
        # Agent skill mapping for intelligent assignment
        self.agent_skills = {
            'pm-agent': ['epic', 'planning', 'coordination', 'management', 'oversight'],
            'frontend-agent': ['ui', 'ux', 'react', 'dashboard', 'frontend', 'javascript'],
            'backend-agent': ['api', 'database', 'server', 'backend', 'python', 'flask'],
            'devops-agent': ['deployment', 'infrastructure', 'aws', 'docker', 'kubernetes', 'ci/cd'],
            'qa-agent': ['testing', 'qa', 'quality', 'validation', 'bug', 'test'],
            'security-agent': ['security', 'auth', 'encryption', 'vulnerability', 'compliance'],
            'integration-agent': ['webhook', 'api', 'integration', 'third-party', 'automation'],
            'analytics-agent': ['metrics', 'monitoring', 'analytics', 'reporting', 'data']
        }
        
        # Current agent workload (in production, this would be from database)
        self.agent_workload = {
            'pm-agent': 3,
            'frontend-agent': 2,
            'backend-agent': 4,
            'devops-agent': 1,
            'qa-agent': 2,
            'security-agent': 1,
            'integration-agent': 2,
            'analytics-agent': 1
        }

    def verify_signature(self, payload_body, signature_header):
        """Verify GitHub webhook signature"""
        if not self.webhook_secret:
            logger.warning("No webhook secret configured - skipping verification")
            return True
            
        if not signature_header:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature_header)

    def get_best_agent_for_issue(self, issue_data):
        """Intelligent agent assignment based on issue content and current workload"""
        title = issue_data.get('title', '').lower()
        body = issue_data.get('body', '').lower() if issue_data.get('body') else ''
        labels = [label['name'].lower() for label in issue_data.get('labels', [])]
        
        content = f"{title} {body} {' '.join(labels)}"
        
        # Score each agent based on skill match
        agent_scores = {}
        for agent, skills in self.agent_skills.items():
            score = 0
            for skill in skills:
                if skill in content:
                    score += 1
            
            # Adjust score based on current workload (prefer less busy agents)
            workload_penalty = self.agent_workload.get(agent, 0) * 0.1
            final_score = score - workload_penalty
            
            agent_scores[agent] = final_score
        
        # Get best agent
        best_agent = max(agent_scores.items(), key=lambda x: x[1])
        
        # If no specific match, assign to PM for triage
        if best_agent[1] <= 0:
            return 'pm-agent', 'Default assignment for triage'
        
        return best_agent[0], f"Skill match score: {best_agent[1]:.1f}"

    def calculate_priority(self, issue_data):
        """Calculate issue priority based on content and labels"""
        title = issue_data.get('title', '').lower()
        labels = [label['name'].lower() for label in issue_data.get('labels', [])]
        
        # Priority keywords
        if any(keyword in title for keyword in ['critical', 'urgent', 'emergency']):
            return 'P0-Critical'
        elif any(keyword in title for keyword in ['high', 'important']) or 'high-priority' in labels:
            return 'P1-High'
        elif any(keyword in title for keyword in ['low', 'minor']) or 'low-priority' in labels:
            return 'P3-Low'
        elif 'backlog' in labels:
            return 'P4-Backlog'
        else:
            return 'P2-Medium'

    def estimate_completion_days(self, issue_data, assigned_agent):
        """Estimate completion time based on issue type and assigned agent"""
        title = issue_data.get('title', '').lower()
        
        # Base estimates by issue type
        if 'epic' in title:
            base_days = 14
        elif 'feature' in title:
            base_days = 5
        elif 'bug' in title or 'fix' in title:
            base_days = 2
        elif 'enhancement' in title:
            base_days = 3
        else:
            base_days = 3
        
        # Adjust based on agent expertise
        agent_multiplier = {
            'pm-agent': 1.2,  # PM needs coordination time
            'frontend-agent': 1.0,
            'backend-agent': 1.0,
            'devops-agent': 0.8,  # DevOps is efficient
            'qa-agent': 0.9,
            'security-agent': 1.1,
            'integration-agent': 1.0,
            'analytics-agent': 0.9
        }
        
        multiplier = agent_multiplier.get(assigned_agent, 1.0)
        return max(1, int(base_days * multiplier))

    def notify_agent_system(self, event_type, data):
        """Notify the agent system about GitHub events"""
        try:
            payload = {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            response = requests.post(
                f"{self.agent_api_url}/webhook/github",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Successfully notified agent system: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to notify agent system: {e}")

    def notify_pm(self, event_type, data):
        """Notify PM about important events"""
        if not self.pm_notification_url:
            return
            
        try:
            payload = {
                'event': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            requests.post(self.pm_notification_url, json=payload, timeout=5)
            logger.info(f"PM notified: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to notify PM: {e}")

    def process_issue_opened(self, issue_data):
        """Process new issue creation"""
        logger.info(f"Processing new issue: #{issue_data['number']} - {issue_data['title']}")
        
        # Get best agent assignment
        assigned_agent, assignment_reason = self.get_best_agent_for_issue(issue_data)
        priority = self.calculate_priority(issue_data)
        estimated_days = self.estimate_completion_days(issue_data, assigned_agent)
        
        # Update agent workload
        self.agent_workload[assigned_agent] = self.agent_workload.get(assigned_agent, 0) + 1
        
        assignment_data = {
            'issue_number': issue_data['number'],
            'issue_title': issue_data['title'],
            'assigned_agent': assigned_agent,
            'assignment_reason': assignment_reason,
            'priority': priority,
            'estimated_completion_days': estimated_days,
            'repository': issue_data['html_url'].split('/')[-3:-1]
        }
        
        # Notify agent system
        self.notify_agent_system('issue_assigned', assignment_data)
        
        # Notify PM for high priority issues
        if priority in ['P0-Critical', 'P1-High']:
            self.notify_pm('high_priority_assignment', assignment_data)
        
        return assignment_data

    def process_issue_closed(self, issue_data):
        """Process issue completion"""
        logger.info(f"Processing issue closure: #{issue_data['number']}")
        
        # Extract agent from labels (in production, use custom fields)
        assigned_agent = None
        for label in issue_data.get('labels', []):
            if label['name'].startswith('assigned:'):
                assigned_agent = label['name'].split(':')[1]
                break
        
        if assigned_agent:
            # Update agent workload
            self.agent_workload[assigned_agent] = max(0, self.agent_workload.get(assigned_agent, 0) - 1)
            
            completion_data = {
                'issue_number': issue_data['number'],
                'issue_title': issue_data['title'],
                'completed_by': assigned_agent,
                'completion_time': datetime.now().isoformat()
            }
            
            # Notify agent system
            self.notify_agent_system('issue_completed', completion_data)
            
            return completion_data
        
        return None

# Initialize webhook handler
webhook_handler = GitHubWebhookHandler()

@app.route('/webhook/github', methods=['POST'])
def handle_github_webhook():
    """Main webhook endpoint for GitHub events"""
    
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not webhook_handler.verify_signature(request.data, signature):
        logger.warning("Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Parse event
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json
    
    logger.info(f"Received GitHub event: {event_type}")
    
    try:
        if event_type == 'issues':
            action = payload.get('action')
            issue_data = payload.get('issue')
            
            if action == 'opened':
                result = webhook_handler.process_issue_opened(issue_data)
                return jsonify({
                    'status': 'success',
                    'action': 'issue_assigned',
                    'assignment': result
                })
                
            elif action == 'closed':
                result = webhook_handler.process_issue_closed(issue_data)
                return jsonify({
                    'status': 'success',
                    'action': 'issue_completed',
                    'completion': result
                })
        
        elif event_type == 'issue_comment':
            # Handle issue comments for agent communication
            comment_data = payload.get('comment')
            issue_data = payload.get('issue')
            
            webhook_handler.notify_agent_system('issue_comment', {
                'issue_number': issue_data['number'],
                'comment_author': comment_data['user']['login'],
                'comment_body': comment_data['body']
            })
        
        return jsonify({'status': 'success', 'message': 'Event processed'})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/api/agents/workload', methods=['GET'])
def get_agent_workload():
    """Get current agent workload status"""
    return jsonify({
        'workload': webhook_handler.agent_workload,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agents/skills', methods=['GET'])
def get_agent_skills():
    """Get agent skills mapping"""
    return jsonify({
        'skills': webhook_handler.agent_skills,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agent_count': len(webhook_handler.agent_workload),
        'total_workload': sum(webhook_handler.agent_workload.values())
    })

if __name__ == '__main__':
    print("🔗 GitHub Webhook Handler for PM and Agent System")
    print("=" * 50)
    print(f"🎯 Webhook endpoint: /webhook/github")
    print(f"📊 Agent workload API: /api/agents/workload")
    print(f"🛠️ Agent skills API: /api/agents/skills")
    print(f"❤️ Health check: /health")
    print(f"🤖 Managing {len(webhook_handler.agent_skills)} specialized agents")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5004, debug=False)
