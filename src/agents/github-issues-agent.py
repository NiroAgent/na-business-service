#!/usr/bin/env python3
"""
GitHub Issues Monitor Agent
Monitors GitHub issues and intelligently distributes work to specialized agents
Part of the AI Software Development Team
"""

import json
import os
import time
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re
import threading
from pathlib import Path
import hashlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_issues_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GitHubIssuesAgent')

@dataclass
class Issue:
    """GitHub Issue data structure"""
    number: int
    title: str
    body: str
    state: str
    labels: List[str]
    assignees: List[str]
    created_at: str
    updated_at: str
    repository: str
    author: str
    milestone: Optional[str] = None
    project: Optional[str] = None
    priority: Optional[str] = None
    complexity: Optional[str] = None
    estimated_hours: Optional[float] = None

@dataclass
class WorkTicket:
    """Internal work ticket for agent assignment"""
    ticket_id: str
    issue_number: int
    repository: str
    title: str
    description: str
    issue_type: str
    priority: str
    complexity: str
    assigned_agent: Optional[str]
    status: str
    created_at: str
    deadline: Optional[str] = None
    dependencies: List[str] = None
    subtasks: List[str] = None

class GitHubIssuesAgent:
    """Main agent for monitoring and distributing GitHub issues"""
    
    def __init__(self, owner: str = "stevesurles", repositories: List[str] = None):
        self.owner = owner
        self.repositories = repositories or [
            "NiroSubs-V2",
            "VisualForgeMediaV2",
            "NiroProjects"
        ]
        
        # Work queue management
        self.work_queue = []
        self.processed_issues = set()
        self.agent_assignments = defaultdict(list)
        
        # Agent specializations
        self.agent_specializations = {
            'backend-dev-agent': ['backend', 'api', 'database', 'server', 'microservice'],
            'frontend-dev-agent': ['frontend', 'ui', 'ux', 'react', 'vue', 'css'],
            'devops-agent': ['deployment', 'ci/cd', 'docker', 'kubernetes', 'aws'],
            'qa-agent': ['test', 'qa', 'quality', 'bug', 'regression'],
            'security-agent': ['security', 'vulnerability', 'auth', 'encryption'],
            'docs-agent': ['documentation', 'docs', 'readme', 'api-docs'],
            'performance-agent': ['performance', 'optimization', 'speed', 'memory'],
            'data-agent': ['data', 'analytics', 'ml', 'ai', 'pipeline']
        }
        
        # Priority mapping
        self.priority_map = {
            'P0': 'critical',
            'P1': 'high',
            'P2': 'medium',
            'P3': 'low',
            'P4': 'trivial'
        }
        
        # Issue type patterns
        self.issue_patterns = {
            'bug': r'(bug|error|issue|problem|broken|fix|crash|failure)',
            'feature': r'(feature|enhancement|new|add|implement|create)',
            'documentation': r'(doc|documentation|readme|guide|tutorial)',
            'refactor': r'(refactor|cleanup|reorganize|restructure|improve)',
            'test': r'(test|testing|coverage|qa|quality)',
            'performance': r'(performance|slow|optimize|speed|memory|cpu)',
            'security': r'(security|vulnerability|cve|auth|permission)',
            'deployment': r'(deploy|deployment|ci/cd|pipeline|release)'
        }
        
        # Complexity estimation patterns
        self.complexity_patterns = {
            'trivial': ['typo', 'text change', 'comment', 'rename'],
            'small': ['simple', 'minor', 'quick', 'easy'],
            'medium': ['moderate', 'standard', 'normal'],
            'large': ['complex', 'major', 'significant', 'substantial'],
            'epic': ['epic', 'massive', 'complete rewrite', 'architecture']
        }
        
        # Monitoring state
        self.monitoring = True
        self.poll_interval = 30  # seconds
        self.monitor_thread = None
        
        # Communication hub integration
        self.hub_enabled = False
        self.hub_client = None
        
        # Metrics
        self.metrics = {
            'total_issues_processed': 0,
            'issues_by_type': defaultdict(int),
            'issues_by_priority': defaultdict(int),
            'assignments_by_agent': defaultdict(int),
            'avg_assignment_time': 0,
            'assignment_times': []
        }
    
    def fetch_issues(self, repo: str, state: str = "open") -> List[Issue]:
        """Fetch issues from a GitHub repository"""
        try:
            cmd = [
                'gh', 'issue', 'list',
                '--repo', f'{self.owner}/{repo}',
                '--state', state,
                '--json', 'number,title,body,state,labels,assignees,createdAt,updatedAt,author,milestone',
                '--limit', '100'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to fetch issues from {repo}: {result.stderr}")
                return []
            
            issues_data = json.loads(result.stdout or '[]')
            issues = []
            
            for issue_data in issues_data:
                issue = Issue(
                    number=issue_data['number'],
                    title=issue_data['title'],
                    body=issue_data.get('body', ''),
                    state=issue_data['state'],
                    labels=[label['name'] for label in issue_data.get('labels', [])],
                    assignees=[a['login'] for a in issue_data.get('assignees', [])],
                    created_at=issue_data['createdAt'],
                    updated_at=issue_data['updatedAt'],
                    repository=repo,
                    author=issue_data.get('author', {}).get('login', 'unknown'),
                    milestone=issue_data.get('milestone', {}).get('title') if issue_data.get('milestone') else None
                )
                
                # Extract priority and complexity
                issue.priority = self._extract_priority(issue)
                issue.complexity = self._estimate_complexity(issue)
                issue.estimated_hours = self._estimate_hours(issue.complexity)
                
                issues.append(issue)
            
            logger.info(f"Fetched {len(issues)} issues from {repo}")
            return issues
            
        except Exception as e:
            logger.error(f"Error fetching issues from {repo}: {e}")
            return []
    
    def _extract_priority(self, issue: Issue) -> str:
        """Extract priority from issue labels or title"""
        # Check labels first
        for label in issue.labels:
            label_upper = label.upper()
            if label_upper in self.priority_map:
                return self.priority_map[label_upper]
            if 'critical' in label.lower():
                return 'critical'
            if 'high' in label.lower():
                return 'high'
            if 'medium' in label.lower():
                return 'medium'
            if 'low' in label.lower():
                return 'low'
        
        # Check title for priority indicators
        title_lower = issue.title.lower()
        if any(word in title_lower for word in ['urgent', 'critical', 'asap', 'blocker']):
            return 'critical'
        if any(word in title_lower for word in ['important', 'high priority']):
            return 'high'
        
        # Default priority based on issue type
        if 'bug' in [l.lower() for l in issue.labels]:
            return 'high'
        if 'security' in [l.lower() for l in issue.labels]:
            return 'critical'
        
        return 'medium'
    
    def _estimate_complexity(self, issue: Issue) -> str:
        """Estimate issue complexity based on content analysis"""
        combined_text = f"{issue.title} {issue.body}".lower()
        
        # Check for explicit complexity indicators
        for complexity, patterns in self.complexity_patterns.items():
            if any(pattern in combined_text for pattern in patterns):
                return complexity
        
        # Estimate based on description length and content
        body_lines = issue.body.count('\n')
        body_words = len(issue.body.split())
        
        # Check for technical indicators
        has_code = '```' in issue.body
        has_multiple_components = len(re.findall(r'- \[.\]', issue.body)) > 3
        mentions_architecture = any(word in combined_text for word in ['architecture', 'design', 'refactor', 'migration'])
        
        if mentions_architecture or body_lines > 50 or has_multiple_components:
            return 'large'
        elif has_code or body_lines > 20 or body_words > 200:
            return 'medium'
        elif body_lines > 5 or body_words > 50:
            return 'small'
        else:
            return 'trivial'
    
    def _estimate_hours(self, complexity: str) -> float:
        """Estimate hours based on complexity"""
        estimates = {
            'trivial': 0.5,
            'small': 2.0,
            'medium': 8.0,
            'large': 24.0,
            'epic': 80.0
        }
        return estimates.get(complexity, 8.0)
    
    def process_issue_templates(self, issue: Issue) -> Dict[str, Any]:
        """Process and parse issue templates"""
        template_data = {
            'type': None,
            'requirements': [],
            'acceptance_criteria': [],
            'technical_details': {},
            'dependencies': []
        }
        
        # Detect issue type
        combined_text = f"{issue.title} {issue.body}".lower()
        for issue_type, pattern in self.issue_patterns.items():
            if re.search(pattern, combined_text):
                template_data['type'] = issue_type
                break
        
        if not template_data['type']:
            template_data['type'] = 'task'  # Default type
        
        # Parse common template sections
        body_lines = issue.body.split('\n')
        current_section = None
        
        for line in body_lines:
            line = line.strip()
            
            # Detect section headers
            if line.startswith('## ') or line.startswith('### '):
                section_title = line.lstrip('#').strip().lower()
                if 'requirement' in section_title:
                    current_section = 'requirements'
                elif 'acceptance' in section_title or 'criteria' in section_title:
                    current_section = 'acceptance'
                elif 'technical' in section_title or 'implementation' in section_title:
                    current_section = 'technical'
                elif 'depend' in section_title:
                    current_section = 'dependencies'
                else:
                    current_section = None
            
            # Parse section content
            elif current_section and line:
                if line.startswith('- ') or line.startswith('* '):
                    content = line[2:].strip()
                    if current_section == 'requirements':
                        template_data['requirements'].append(content)
                    elif current_section == 'acceptance':
                        template_data['acceptance_criteria'].append(content)
                    elif current_section == 'dependencies':
                        template_data['dependencies'].append(content)
                elif current_section == 'technical':
                    # Parse key-value pairs for technical details
                    if ':' in line:
                        key, value = line.split(':', 1)
                        template_data['technical_details'][key.strip()] = value.strip()
        
        return template_data
    
    def create_work_ticket(self, issue: Issue, template_data: Dict[str, Any]) -> WorkTicket:
        """Create internal work ticket from issue"""
        ticket_id = hashlib.md5(f"{issue.repository}#{issue.number}".encode()).hexdigest()[:8]
        
        # Prepare description with parsed data
        description = issue.body
        if template_data['requirements']:
            description += "\n\n**Requirements:**\n" + "\n".join(f"- {r}" for r in template_data['requirements'])
        if template_data['acceptance_criteria']:
            description += "\n\n**Acceptance Criteria:**\n" + "\n".join(f"- {a}" for a in template_data['acceptance_criteria'])
        
        # Calculate deadline based on priority
        deadline = None
        if issue.priority == 'critical':
            deadline = (datetime.now() + timedelta(hours=4)).isoformat()
        elif issue.priority == 'high':
            deadline = (datetime.now() + timedelta(days=1)).isoformat()
        elif issue.priority == 'medium':
            deadline = (datetime.now() + timedelta(days=3)).isoformat()
        
        ticket = WorkTicket(
            ticket_id=ticket_id,
            issue_number=issue.number,
            repository=issue.repository,
            title=issue.title,
            description=description,
            issue_type=template_data['type'],
            priority=issue.priority,
            complexity=issue.complexity,
            assigned_agent=None,
            status='pending',
            created_at=datetime.now().isoformat(),
            deadline=deadline,
            dependencies=template_data['dependencies'],
            subtasks=[]
        )
        
        return ticket
    
    def assign_to_agent(self, ticket: WorkTicket) -> str:
        """Assign work ticket to appropriate specialized agent"""
        start_time = datetime.now()
        
        # Analyze ticket content for agent selection
        combined_text = f"{ticket.title} {ticket.description}".lower()
        
        # Score each agent based on keyword matches
        agent_scores = {}
        for agent, keywords in self.agent_specializations.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                agent_scores[agent] = score
        
        # Add specific rules based on issue type and labels
        if ticket.issue_type == 'bug':
            agent_scores['qa-agent'] = agent_scores.get('qa-agent', 0) + 3
        elif ticket.issue_type == 'feature':
            # Determine if frontend or backend
            if any(word in combined_text for word in ['ui', 'frontend', 'react', 'component', 'css']):
                agent_scores['frontend-dev-agent'] = agent_scores.get('frontend-dev-agent', 0) + 3
            else:
                agent_scores['backend-dev-agent'] = agent_scores.get('backend-dev-agent', 0) + 3
        elif ticket.issue_type == 'documentation':
            agent_scores['docs-agent'] = agent_scores.get('docs-agent', 0) + 5
        elif ticket.issue_type == 'security':
            agent_scores['security-agent'] = agent_scores.get('security-agent', 0) + 5
        elif ticket.issue_type == 'performance':
            agent_scores['performance-agent'] = agent_scores.get('performance-agent', 0) + 5
        elif ticket.issue_type == 'deployment':
            agent_scores['devops-agent'] = agent_scores.get('devops-agent', 0) + 5
        
        # Select agent with highest score
        if agent_scores:
            assigned_agent = max(agent_scores, key=agent_scores.get)
        else:
            # Default assignment based on type
            default_assignments = {
                'bug': 'qa-agent',
                'feature': 'backend-dev-agent',
                'documentation': 'docs-agent',
                'refactor': 'backend-dev-agent',
                'test': 'qa-agent',
                'performance': 'performance-agent',
                'security': 'security-agent',
                'deployment': 'devops-agent'
            }
            assigned_agent = default_assignments.get(ticket.issue_type, 'backend-dev-agent')
        
        ticket.assigned_agent = assigned_agent
        ticket.status = 'assigned'
        
        # Update metrics
        assignment_time = (datetime.now() - start_time).total_seconds()
        self.metrics['assignment_times'].append(assignment_time)
        self.metrics['avg_assignment_time'] = sum(self.metrics['assignment_times']) / len(self.metrics['assignment_times'])
        self.metrics['assignments_by_agent'][assigned_agent] += 1
        
        logger.info(f"Assigned ticket {ticket.ticket_id} to {assigned_agent} (Priority: {ticket.priority}, Complexity: {ticket.complexity})")
        
        return assigned_agent
    
    def distribute_work(self, ticket: WorkTicket):
        """Distribute work ticket to assigned agent"""
        if not ticket.assigned_agent:
            logger.error(f"Cannot distribute ticket {ticket.ticket_id} - no agent assigned")
            return
        
        # Create work package for agent
        work_package = {
            'ticket_id': ticket.ticket_id,
            'issue_number': ticket.issue_number,
            'repository': ticket.repository,
            'title': ticket.title,
            'description': ticket.description,
            'type': ticket.issue_type,
            'priority': ticket.priority,
            'complexity': ticket.complexity,
            'deadline': ticket.deadline,
            'dependencies': ticket.dependencies,
            'assigned_at': datetime.now().isoformat()
        }
        
        # Save work package to agent's queue
        agent_queue_file = f"work_queues/{ticket.assigned_agent}_queue.json"
        Path("work_queues").mkdir(exist_ok=True)
        
        # Load existing queue
        existing_queue = []
        if os.path.exists(agent_queue_file):
            try:
                with open(agent_queue_file, 'r') as f:
                    existing_queue = json.load(f)
            except:
                existing_queue = []
        
        # Add new work package
        existing_queue.append(work_package)
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'trivial': 4}
        existing_queue.sort(key=lambda x: priority_order.get(x['priority'], 5))
        
        # Save updated queue
        with open(agent_queue_file, 'w') as f:
            json.dump(existing_queue, f, indent=2)
        
        # Track assignment
        self.agent_assignments[ticket.assigned_agent].append(ticket.ticket_id)
        
        # If communication hub is enabled, send message
        if self.hub_enabled and self.hub_client:
            self.hub_client.send(
                ticket.assigned_agent,
                'task_assignment',
                work_package,
                priority=priority_order.get(ticket.priority, 5)
            )
        
        logger.info(f"Distributed work package to {ticket.assigned_agent}: {ticket.title}")
    
    def monitor_issues(self):
        """Main monitoring loop"""
        logger.info("Starting issue monitoring...")
        
        while self.monitoring:
            try:
                all_issues = []
                
                # Fetch issues from all repositories
                for repo in self.repositories:
                    issues = self.fetch_issues(repo)
                    all_issues.extend(issues)
                
                # Process new issues
                for issue in all_issues:
                    issue_key = f"{issue.repository}#{issue.number}"
                    
                    if issue_key not in self.processed_issues:
                        logger.info(f"Processing new issue: {issue_key} - {issue.title}")
                        
                        # Process issue template
                        template_data = self.process_issue_templates(issue)
                        
                        # Create work ticket
                        ticket = self.create_work_ticket(issue, template_data)
                        
                        # Assign to agent
                        self.assign_to_agent(ticket)
                        
                        # Add to work queue
                        self.work_queue.append(ticket)
                        
                        # Distribute work
                        self.distribute_work(ticket)
                        
                        # Mark as processed
                        self.processed_issues.add(issue_key)
                        
                        # Update metrics
                        self.metrics['total_issues_processed'] += 1
                        self.metrics['issues_by_type'][template_data['type']] += 1
                        self.metrics['issues_by_priority'][issue.priority] += 1
                
                # Log status
                logger.info(f"Monitoring cycle complete. Processed: {self.metrics['total_issues_processed']} total issues")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.poll_interval)
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_issues, daemon=True)
            self.monitor_thread.start()
            logger.info("Issue monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            logger.info("Issue monitoring stopped")
    
    def get_work_queue_status(self) -> Dict[str, Any]:
        """Get current work queue status"""
        status = {
            'total_tickets': len(self.work_queue),
            'pending': len([t for t in self.work_queue if t.status == 'pending']),
            'assigned': len([t for t in self.work_queue if t.status == 'assigned']),
            'by_priority': {},
            'by_agent': dict(self.agent_assignments),
            'metrics': self.metrics
        }
        
        for priority in ['critical', 'high', 'medium', 'low', 'trivial']:
            status['by_priority'][priority] = len([t for t in self.work_queue if t.priority == priority])
        
        return status
    
    def handle_issue_update(self, repo: str, issue_number: int, update_type: str, data: Dict[str, Any]):
        """Handle issue update events (for webhook integration)"""
        logger.info(f"Handling {update_type} for {repo}#{issue_number}")
        
        # Find corresponding work ticket
        ticket = None
        for t in self.work_queue:
            if t.repository == repo and t.issue_number == issue_number:
                ticket = t
                break
        
        if not ticket:
            logger.warning(f"No ticket found for {repo}#{issue_number}")
            return
        
        # Handle different update types
        if update_type == 'closed':
            ticket.status = 'completed'
            logger.info(f"Issue {repo}#{issue_number} closed - marking ticket as completed")
        
        elif update_type == 'reopened':
            ticket.status = 'pending'
            # Re-assign if needed
            self.assign_to_agent(ticket)
            self.distribute_work(ticket)
            logger.info(f"Issue {repo}#{issue_number} reopened - reassigning")
        
        elif update_type == 'labeled':
            # Update priority if priority label changed
            new_priority = self._extract_priority_from_labels(data.get('labels', []))
            if new_priority != ticket.priority:
                ticket.priority = new_priority
                logger.info(f"Updated priority for {repo}#{issue_number} to {new_priority}")
        
        elif update_type == 'assigned':
            # Track manual assignments
            assignees = data.get('assignees', [])
            if assignees:
                logger.info(f"Issue {repo}#{issue_number} manually assigned to {assignees}")
    
    def _extract_priority_from_labels(self, labels: List[str]) -> str:
        """Extract priority from label list"""
        for label in labels:
            label_upper = label.upper()
            if label_upper in self.priority_map:
                return self.priority_map[label_upper]
        return 'medium'
    
    def save_state(self):
        """Save agent state to file"""
        state = {
            'processed_issues': list(self.processed_issues),
            'work_queue': [asdict(t) for t in self.work_queue],
            'agent_assignments': dict(self.agent_assignments),
            'metrics': self.metrics
        }
        
        with open('github_issues_agent_state.json', 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info("Agent state saved")
    
    def load_state(self):
        """Load agent state from file"""
        if os.path.exists('github_issues_agent_state.json'):
            try:
                with open('github_issues_agent_state.json', 'r') as f:
                    state = json.load(f)
                
                self.processed_issues = set(state.get('processed_issues', []))
                self.metrics = state.get('metrics', self.metrics)
                
                # Reconstruct work queue
                self.work_queue = []
                for ticket_data in state.get('work_queue', []):
                    ticket = WorkTicket(**ticket_data)
                    self.work_queue.append(ticket)
                
                self.agent_assignments = defaultdict(list, state.get('agent_assignments', {}))
                
                logger.info(f"Agent state loaded: {len(self.processed_issues)} processed issues")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")


def main():
    """Main execution function"""
    logger.info("Starting GitHub Issues Monitor Agent...")
    
    # Initialize agent
    agent = GitHubIssuesAgent()
    
    # Load previous state if exists
    agent.load_state()
    
    # Create work queues directory
    Path("work_queues").mkdir(exist_ok=True)
    
    # Start monitoring
    agent.start_monitoring()
    
    try:
        # Keep running and periodically save state
        while True:
            time.sleep(60)  # Save state every minute
            agent.save_state()
            
            # Log status
            status = agent.get_work_queue_status()
            logger.info(f"Queue status: {status['total_tickets']} tickets, "
                       f"{status['assigned']} assigned, {status['pending']} pending")
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        agent.stop_monitoring()
        agent.save_state()


if __name__ == "__main__":
    main()