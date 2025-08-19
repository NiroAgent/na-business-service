#!/usr/bin/env python3
"""
GitHub Project Board Agent
Manages GitHub Projects for sprint planning and task tracking
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
from enum import Enum
import threading
from pathlib import Path
import hashlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('project_board_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ProjectBoardAgent')

class ColumnType(Enum):
    """Project column types"""
    BACKLOG = "Backlog"
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    TESTING = "Testing"
    DONE = "Done"
    BLOCKED = "Blocked"
    CANCELLED = "Cancelled"

class CardType(Enum):
    """Project card types"""
    ISSUE = "Issue"
    PULL_REQUEST = "PullRequest"
    NOTE = "Note"

@dataclass
class ProjectBoard:
    """GitHub Project board structure"""
    id: str
    name: str
    description: str
    state: str  # open, closed
    created_at: str
    updated_at: str
    columns: Dict[str, str]  # column_name -> column_id
    cards_count: int
    repository: Optional[str]

@dataclass
class ProjectCard:
    """Project card structure"""
    card_id: str
    column_id: str
    column_name: str
    content_type: CardType
    content_url: Optional[str]
    issue_number: Optional[int]
    pr_number: Optional[int]
    note: Optional[str]
    created_at: str
    updated_at: str
    position: int
    creator: str
    labels: List[str]
    assignees: List[str]

@dataclass
class Sprint:
    """Sprint structure for Agile workflow"""
    sprint_id: str
    name: str
    goal: str
    start_date: str
    end_date: str
    project_id: str
    status: str  # planning, active, review, completed
    velocity: int
    planned_points: int
    completed_points: int
    issues: List[int]
    burndown_data: List[Dict[str, Any]]

class ProjectBoardAgent:
    """Main agent for GitHub Projects management"""
    
    def __init__(self, owner: str = "stevesurles"):
        self.owner = owner
        self.projects = {}
        self.cards = {}
        self.sprints = {}
        self.active_sprint = None
        
        # Column workflow mapping
        self.workflow_transitions = {
            ColumnType.BACKLOG: [ColumnType.TODO],
            ColumnType.TODO: [ColumnType.IN_PROGRESS],
            ColumnType.IN_PROGRESS: [ColumnType.IN_REVIEW, ColumnType.BLOCKED],
            ColumnType.IN_REVIEW: [ColumnType.TESTING, ColumnType.IN_PROGRESS],
            ColumnType.TESTING: [ColumnType.DONE, ColumnType.IN_PROGRESS],
            ColumnType.BLOCKED: [ColumnType.IN_PROGRESS, ColumnType.TODO],
            ColumnType.DONE: [],
            ColumnType.CANCELLED: []
        }
        
        # Automation rules
        self.automation_rules = {
            'new_issue': self._handle_new_issue,
            'pr_created': self._handle_pr_created,
            'pr_merged': self._handle_pr_merged,
            'issue_closed': self._handle_issue_closed,
            'review_requested': self._handle_review_requested,
            'review_completed': self._handle_review_completed
        }
        
        # Sprint settings
        self.sprint_duration = 14  # days
        self.velocity_history = []
        self.story_point_field = 'story_points'
        
        # Card priorities
        self.priority_weights = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'trivial': 1
        }
        
        # Monitoring
        self.monitor_interval = 30
        self.monitoring = True
        self.monitor_thread = None
        
        # Metrics
        self.metrics = {
            'total_projects': 0,
            'total_cards': 0,
            'cards_moved': 0,
            'sprints_completed': 0,
            'avg_cycle_time': 0,
            'throughput': [],
            'cycle_times': [],
            'velocity_trend': []
        }
    
    def create_project(self, name: str, description: str, 
                      repository: str = None,
                      columns: List[str] = None) -> Optional[ProjectBoard]:
        """Create a new GitHub Project"""
        try:
            # Default columns if not specified
            if not columns:
                columns = [col.value for col in ColumnType]
            
            # Create project using gh CLI
            cmd = ['gh', 'project', 'create',
                   '--owner', self.owner,
                   '--title', name]
            
            if description:
                cmd.extend(['--body', description])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract project ID from output
                project_url = result.stdout.strip()
                project_id = project_url.split('/')[-1]
                
                # Create columns
                column_ids = {}
                for column_name in columns:
                    column_id = self._create_column(project_id, column_name)
                    if column_id:
                        column_ids[column_name] = column_id
                
                # Create project object
                project = ProjectBoard(
                    id=project_id,
                    name=name,
                    description=description,
                    state='open',
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    columns=column_ids,
                    cards_count=0,
                    repository=repository
                )
                
                self.projects[project_id] = project
                self.metrics['total_projects'] += 1
                
                logger.info(f"Created project: {name} (ID: {project_id})")
                return project
                
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
        
        return None
    
    def _create_column(self, project_id: str, column_name: str) -> Optional[str]:
        """Create a project column"""
        try:
            result = subprocess.run(
                ['gh', 'api', f'projects/{project_id}/columns',
                 '--method', 'POST',
                 '--field', f'name={column_name}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                logger.info(f"Created column '{column_name}' in project {project_id}")
                return data['id']
                
        except Exception as e:
            logger.error(f"Failed to create column: {e}")
        
        return None
    
    def add_issue_to_board(self, project_id: str, repo: str, 
                          issue_number: int, column: str = None) -> Optional[ProjectCard]:
        """Add an issue to a project board"""
        if project_id not in self.projects:
            logger.error(f"Project {project_id} not found")
            return None
        
        project = self.projects[project_id]
        target_column = column or ColumnType.BACKLOG.value
        
        if target_column not in project.columns:
            logger.error(f"Column '{target_column}' not found in project")
            return None
        
        try:
            # Get issue details first
            issue_data = self._get_issue_details(repo, issue_number)
            if not issue_data:
                return None
            
            # Create card in project
            column_id = project.columns[target_column]
            
            result = subprocess.run(
                ['gh', 'api', f'projects/columns/{column_id}/cards',
                 '--method', 'POST',
                 '--field', f'content_id={issue_data["id"]}',
                 '--field', 'content_type=Issue'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                card_data = json.loads(result.stdout)
                
                # Create card object
                card = ProjectCard(
                    card_id=str(card_data['id']),
                    column_id=column_id,
                    column_name=target_column,
                    content_type=CardType.ISSUE,
                    content_url=card_data.get('content_url'),
                    issue_number=issue_number,
                    pr_number=None,
                    note=None,
                    created_at=card_data['created_at'],
                    updated_at=card_data['updated_at'],
                    position=0,
                    creator=card_data.get('creator', {}).get('login', 'unknown'),
                    labels=issue_data.get('labels', []),
                    assignees=issue_data.get('assignees', [])
                )
                
                self.cards[card.card_id] = card
                project.cards_count += 1
                self.metrics['total_cards'] += 1
                
                logger.info(f"Added issue #{issue_number} to {target_column} column")
                return card
                
        except Exception as e:
            logger.error(f"Failed to add issue to board: {e}")
        
        return None
    
    def _get_issue_details(self, repo: str, issue_number: int) -> Optional[Dict]:
        """Get issue details from GitHub"""
        try:
            result = subprocess.run(
                ['gh', 'issue', 'view', str(issue_number),
                 '--repo', f'{self.owner}/{repo}',
                 '--json', 'id,title,labels,assignees,state'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    'id': data['id'],
                    'title': data['title'],
                    'labels': [l['name'] for l in data.get('labels', [])],
                    'assignees': [a['login'] for a in data.get('assignees', [])],
                    'state': data['state']
                }
                
        except Exception as e:
            logger.error(f"Failed to get issue details: {e}")
        
        return None
    
    def move_card(self, card_id: str, target_column: str, 
                 position: str = "top") -> bool:
        """Move a card to a different column"""
        if card_id not in self.cards:
            logger.error(f"Card {card_id} not found")
            return False
        
        card = self.cards[card_id]
        
        # Find target column ID
        target_column_id = None
        for project in self.projects.values():
            if target_column in project.columns:
                target_column_id = project.columns[target_column]
                break
        
        if not target_column_id:
            logger.error(f"Target column '{target_column}' not found")
            return False
        
        # Check workflow transition validity
        current_col = ColumnType(card.column_name)
        target_col = ColumnType(target_column)
        
        if target_col not in self.workflow_transitions.get(current_col, []) and \
           current_col != target_col:
            logger.warning(f"Invalid transition from {current_col.value} to {target_col.value}")
            # Allow the move anyway for flexibility
        
        try:
            result = subprocess.run(
                ['gh', 'api', f'projects/columns/cards/{card_id}/moves',
                 '--method', 'POST',
                 '--field', f'column_id={target_column_id}',
                 '--field', f'position={position}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Update card
                old_column = card.column_name
                card.column_id = target_column_id
                card.column_name = target_column
                card.updated_at = datetime.now().isoformat()
                
                # Track cycle time
                if target_column == ColumnType.DONE.value:
                    created = datetime.fromisoformat(card.created_at.replace('Z', '+00:00'))
                    cycle_time = (datetime.now() - created).total_seconds() / 3600  # hours
                    self.metrics['cycle_times'].append(cycle_time)
                    self.metrics['avg_cycle_time'] = sum(self.metrics['cycle_times']) / len(self.metrics['cycle_times'])
                
                self.metrics['cards_moved'] += 1
                
                logger.info(f"Moved card {card_id} from {old_column} to {target_column}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to move card: {e}")
        
        return False
    
    def create_sprint(self, name: str, goal: str, 
                     project_id: str, duration_days: int = None) -> Optional[Sprint]:
        """Create a new sprint"""
        if project_id not in self.projects:
            logger.error(f"Project {project_id} not found")
            return None
        
        duration = duration_days or self.sprint_duration
        
        sprint = Sprint(
            sprint_id=hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:8],
            name=name,
            goal=goal,
            start_date=datetime.now().isoformat(),
            end_date=(datetime.now() + timedelta(days=duration)).isoformat(),
            project_id=project_id,
            status='planning',
            velocity=self._calculate_velocity(),
            planned_points=0,
            completed_points=0,
            issues=[],
            burndown_data=[]
        )
        
        self.sprints[sprint.sprint_id] = sprint
        
        logger.info(f"Created sprint: {name} (ID: {sprint.sprint_id})")
        return sprint
    
    def _calculate_velocity(self) -> int:
        """Calculate team velocity based on history"""
        if not self.velocity_history:
            return 20  # Default velocity
        
        # Average of last 3 sprints
        recent = self.velocity_history[-3:]
        return int(sum(recent) / len(recent))
    
    def plan_sprint(self, sprint_id: str, issue_numbers: List[int], 
                    story_points: Dict[int, int]) -> bool:
        """Plan sprint with selected issues"""
        if sprint_id not in self.sprints:
            logger.error(f"Sprint {sprint_id} not found")
            return False
        
        sprint = self.sprints[sprint_id]
        
        # Calculate total points
        total_points = sum(story_points.values())
        
        # Check against velocity
        if total_points > sprint.velocity * 1.2:  # Allow 20% over velocity
            logger.warning(f"Sprint overcommitted: {total_points} points vs {sprint.velocity} velocity")
        
        sprint.issues = issue_numbers
        sprint.planned_points = total_points
        sprint.status = 'planning'
        
        # Move issues to TODO column
        project = self.projects[sprint.project_id]
        for issue_num in issue_numbers:
            # Find card for issue
            for card in self.cards.values():
                if card.issue_number == issue_num:
                    self.move_card(card.card_id, ColumnType.TODO.value)
                    break
        
        logger.info(f"Planned sprint {sprint_id} with {len(issue_numbers)} issues, {total_points} points")
        return True
    
    def start_sprint(self, sprint_id: str) -> bool:
        """Start a sprint"""
        if sprint_id not in self.sprints:
            return False
        
        sprint = self.sprints[sprint_id]
        
        if sprint.status != 'planning':
            logger.warning(f"Sprint {sprint_id} is not in planning status")
            return False
        
        sprint.status = 'active'
        sprint.start_date = datetime.now().isoformat()
        self.active_sprint = sprint_id
        
        # Initialize burndown data
        sprint.burndown_data = [{
            'date': sprint.start_date,
            'remaining_points': sprint.planned_points,
            'ideal_points': sprint.planned_points
        }]
        
        logger.info(f"Started sprint: {sprint.name}")
        return True
    
    def update_burndown(self, sprint_id: str):
        """Update sprint burndown chart data"""
        if sprint_id not in self.sprints:
            return
        
        sprint = self.sprints[sprint_id]
        
        # Calculate remaining points
        remaining_points = sprint.planned_points
        
        # Check completed issues
        for issue_num in sprint.issues:
            for card in self.cards.values():
                if card.issue_number == issue_num and \
                   card.column_name == ColumnType.DONE.value:
                    # Subtract points for completed issue
                    # (Would need story points from issue labels or custom field)
                    remaining_points -= 3  # Default 3 points
        
        # Calculate ideal burndown
        days_elapsed = (datetime.now() - datetime.fromisoformat(sprint.start_date)).days
        days_total = (datetime.fromisoformat(sprint.end_date) - 
                     datetime.fromisoformat(sprint.start_date)).days
        ideal_points = sprint.planned_points * (1 - days_elapsed / days_total)
        
        # Add data point
        sprint.burndown_data.append({
            'date': datetime.now().isoformat(),
            'remaining_points': remaining_points,
            'ideal_points': max(0, ideal_points)
        })
        
        sprint.completed_points = sprint.planned_points - remaining_points
    
    def complete_sprint(self, sprint_id: str) -> Dict[str, Any]:
        """Complete a sprint and generate retrospective data"""
        if sprint_id not in self.sprints:
            return {}
        
        sprint = self.sprints[sprint_id]
        sprint.status = 'completed'
        sprint.end_date = datetime.now().isoformat()
        
        # Calculate sprint metrics
        completed_issues = []
        incomplete_issues = []
        
        for issue_num in sprint.issues:
            completed = False
            for card in self.cards.values():
                if card.issue_number == issue_num:
                    if card.column_name == ColumnType.DONE.value:
                        completed_issues.append(issue_num)
                        completed = True
                    break
            
            if not completed:
                incomplete_issues.append(issue_num)
        
        # Update velocity history
        self.velocity_history.append(sprint.completed_points)
        self.metrics['sprints_completed'] += 1
        
        # Generate retrospective
        retrospective = {
            'sprint_name': sprint.name,
            'sprint_goal': sprint.goal,
            'duration': (datetime.fromisoformat(sprint.end_date) - 
                        datetime.fromisoformat(sprint.start_date)).days,
            'planned_points': sprint.planned_points,
            'completed_points': sprint.completed_points,
            'velocity': sprint.completed_points,
            'completion_rate': sprint.completed_points / sprint.planned_points * 100 if sprint.planned_points > 0 else 0,
            'completed_issues': completed_issues,
            'incomplete_issues': incomplete_issues,
            'burndown_data': sprint.burndown_data
        }
        
        # Clear active sprint
        if self.active_sprint == sprint_id:
            self.active_sprint = None
        
        logger.info(f"Completed sprint {sprint.name}: {sprint.completed_points}/{sprint.planned_points} points")
        
        return retrospective
    
    def _handle_new_issue(self, repo: str, issue_number: int):
        """Handle new issue automation"""
        # Find active project
        for project in self.projects.values():
            if project.repository == repo and project.state == 'open':
                # Add to backlog
                self.add_issue_to_board(project.id, repo, issue_number, 
                                       ColumnType.BACKLOG.value)
                break
    
    def _handle_pr_created(self, repo: str, pr_number: int):
        """Handle PR created automation"""
        # Add PR card to In Review column
        for project in self.projects.values():
            if project.repository == repo and project.state == 'open':
                # Create PR card
                column_id = project.columns.get(ColumnType.IN_REVIEW.value)
                if column_id:
                    # Would create PR card here
                    logger.info(f"Added PR #{pr_number} to review column")
                break
    
    def _handle_pr_merged(self, repo: str, pr_number: int):
        """Handle PR merged automation"""
        # Move related issue to Testing
        # Find card for PR
        for card in self.cards.values():
            if card.pr_number == pr_number:
                self.move_card(card.card_id, ColumnType.TESTING.value)
                break
    
    def _handle_issue_closed(self, repo: str, issue_number: int):
        """Handle issue closed automation"""
        # Move to Done column
        for card in self.cards.values():
            if card.issue_number == issue_number:
                self.move_card(card.card_id, ColumnType.DONE.value)
                
                # Update sprint if active
                if self.active_sprint:
                    self.update_burndown(self.active_sprint)
                break
    
    def _handle_review_requested(self, repo: str, pr_number: int):
        """Handle review requested automation"""
        # Move to In Review column
        for card in self.cards.values():
            if card.pr_number == pr_number:
                self.move_card(card.card_id, ColumnType.IN_REVIEW.value)
                break
    
    def _handle_review_completed(self, repo: str, pr_number: int, approved: bool):
        """Handle review completed automation"""
        for card in self.cards.values():
            if card.pr_number == pr_number:
                if approved:
                    self.move_card(card.card_id, ColumnType.TESTING.value)
                else:
                    self.move_card(card.card_id, ColumnType.IN_PROGRESS.value)
                break
    
    def get_board_overview(self, project_id: str) -> Dict[str, Any]:
        """Get project board overview"""
        if project_id not in self.projects:
            return {}
        
        project = self.projects[project_id]
        
        # Count cards by column
        column_counts = defaultdict(int)
        for card in self.cards.values():
            if card.column_name in project.columns:
                column_counts[card.column_name] += 1
        
        # Calculate throughput
        done_cards = [c for c in self.cards.values() 
                     if c.column_name == ColumnType.DONE.value]
        
        # Weekly throughput
        week_ago = datetime.now() - timedelta(days=7)
        recent_done = [c for c in done_cards 
                      if datetime.fromisoformat(c.updated_at.replace('Z', '+00:00')) > week_ago]
        
        return {
            'project_name': project.name,
            'total_cards': project.cards_count,
            'column_distribution': dict(column_counts),
            'weekly_throughput': len(recent_done),
            'avg_cycle_time': self.metrics['avg_cycle_time'],
            'active_sprint': self.active_sprint,
            'state': project.state
        }
    
    def generate_reports(self) -> Dict[str, Any]:
        """Generate project management reports"""
        reports = {
            'projects': [],
            'sprints': [],
            'metrics': self.metrics,
            'velocity_trend': self.velocity_history[-10:],  # Last 10 sprints
            'throughput_trend': [],
            'cycle_time_distribution': {}
        }
        
        # Project summaries
        for project in self.projects.values():
            reports['projects'].append({
                'name': project.name,
                'cards': project.cards_count,
                'state': project.state,
                'overview': self.get_board_overview(project.id)
            })
        
        # Sprint summaries
        for sprint in self.sprints.values():
            reports['sprints'].append({
                'name': sprint.name,
                'status': sprint.status,
                'velocity': sprint.velocity,
                'completion': sprint.completed_points / sprint.planned_points * 100 
                            if sprint.planned_points > 0 else 0
            })
        
        # Cycle time distribution
        if self.metrics['cycle_times']:
            reports['cycle_time_distribution'] = {
                'min': min(self.metrics['cycle_times']),
                'max': max(self.metrics['cycle_times']),
                'avg': self.metrics['avg_cycle_time'],
                'median': sorted(self.metrics['cycle_times'])[len(self.metrics['cycle_times'])//2]
            }
        
        return reports
    
    def monitor_boards(self):
        """Monitor project boards for updates"""
        logger.info("Starting project board monitoring...")
        
        while self.monitoring:
            try:
                # Update active sprint burndown
                if self.active_sprint:
                    self.update_burndown(self.active_sprint)
                
                # Check for stale cards
                for card in self.cards.values():
                    if card.column_name == ColumnType.IN_PROGRESS.value:
                        updated = datetime.fromisoformat(card.updated_at.replace('Z', '+00:00'))
                        if datetime.now() - updated > timedelta(days=3):
                            logger.warning(f"Card {card.card_id} has been in progress for >3 days")
                
                # Calculate throughput
                done_today = 0
                today = datetime.now().date()
                for card in self.cards.values():
                    if card.column_name == ColumnType.DONE.value:
                        updated = datetime.fromisoformat(card.updated_at.replace('Z', '+00:00'))
                        if updated.date() == today:
                            done_today += 1
                
                if done_today > 0:
                    self.metrics['throughput'].append({
                        'date': today.isoformat(),
                        'count': done_today
                    })
                
                # Log status
                active_cards = len([c for c in self.cards.values() 
                                  if c.column_name in [ColumnType.IN_PROGRESS.value, 
                                                       ColumnType.IN_REVIEW.value]])
                logger.info(f"Monitoring: {len(self.projects)} projects, "
                          f"{active_cards} active cards")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.monitor_interval)
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_boards, daemon=True)
            self.monitor_thread.start()
            logger.info("Board monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            logger.info("Board monitoring stopped")
    
    def save_state(self):
        """Save agent state"""
        state = {
            'projects': {pid: asdict(p) for pid, p in self.projects.items()},
            'cards': {cid: asdict(c) for cid, c in self.cards.items()},
            'sprints': {sid: asdict(s) for sid, s in self.sprints.items()},
            'active_sprint': self.active_sprint,
            'velocity_history': self.velocity_history,
            'metrics': self.metrics
        }
        
        # Convert enums to strings for JSON serialization
        for card_data in state['cards'].values():
            card_data['content_type'] = card_data['content_type'].value if isinstance(card_data['content_type'], Enum) else card_data['content_type']
        
        with open('project_board_agent_state.json', 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        logger.info("Agent state saved")
    
    def load_state(self):
        """Load agent state"""
        if os.path.exists('project_board_agent_state.json'):
            try:
                with open('project_board_agent_state.json', 'r') as f:
                    state = json.load(f)
                
                # Restore projects
                self.projects = {}
                for pid, pdata in state.get('projects', {}).items():
                    self.projects[pid] = ProjectBoard(**pdata)
                
                # Restore cards
                self.cards = {}
                for cid, cdata in state.get('cards', {}).items():
                    # Convert string back to enum
                    cdata['content_type'] = CardType(cdata['content_type'])
                    self.cards[cid] = ProjectCard(**cdata)
                
                # Restore sprints
                self.sprints = {}
                for sid, sdata in state.get('sprints', {}).items():
                    self.sprints[sid] = Sprint(**sdata)
                
                self.active_sprint = state.get('active_sprint')
                self.velocity_history = state.get('velocity_history', [])
                self.metrics = state.get('metrics', self.metrics)
                
                logger.info(f"Agent state loaded: {len(self.projects)} projects, "
                          f"{len(self.cards)} cards, {len(self.sprints)} sprints")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")


def main():
    """Main execution function"""
    logger.info("Starting Project Board Agent...")
    
    # Initialize agent
    agent = ProjectBoardAgent()
    
    # Load previous state if exists
    agent.load_state()
    
    # Start monitoring
    agent.start_monitoring()
    
    print("\n" + "="*80)
    print("Project Board Agent Initialized Successfully!")
    print("="*80)
    print(f"Projects: {len(agent.projects)}")
    print(f"Cards: {len(agent.cards)}")
    print(f"Sprints: {len(agent.sprints)}")
    print(f"Active Sprint: {agent.active_sprint or 'None'}")
    print(f"Sprints Completed: {agent.metrics['sprints_completed']}")
    print("="*80)
    
    try:
        # Keep running and periodically save state
        while True:
            time.sleep(60)  # Save state every minute
            agent.save_state()
            
            # Generate and log reports
            reports = agent.generate_reports()
            logger.info(f"Status: {len(agent.projects)} projects, "
                       f"{len(agent.cards)} cards, "
                       f"Avg cycle time: {agent.metrics['avg_cycle_time']:.1f} hours")
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        agent.stop_monitoring()
        agent.save_state()


if __name__ == "__main__":
    main()