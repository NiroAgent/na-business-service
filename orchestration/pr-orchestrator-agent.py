#!/usr/bin/env python3
"""
Pull Request Orchestrator Agent
Manages the complete PR lifecycle from creation to merge
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
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pr_orchestrator_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PROrchestrator')

class PRState(Enum):
    """Pull Request states"""
    DRAFT = "draft"
    READY = "ready"
    IN_REVIEW = "in_review"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    MERGING = "merging"
    MERGED = "merged"
    CLOSED = "closed"
    CONFLICT = "conflict"

@dataclass
class PullRequest:
    """Pull Request data structure"""
    pr_id: str
    number: int
    repository: str
    title: str
    description: str
    branch: str
    base_branch: str
    state: PRState
    author: str
    created_at: str
    updated_at: str
    reviewers: List[str]
    approvals: List[str]
    requested_changes: List[Dict[str, str]]
    labels: List[str]
    checks_status: Dict[str, str]
    conflicts: bool
    mergeable: bool
    comments: List[Dict[str, Any]]
    commits: List[str]
    files_changed: int
    additions: int
    deletions: int

@dataclass
class ReviewRequest:
    """Review request tracking"""
    pr_id: str
    reviewer: str
    requested_at: str
    reviewed_at: Optional[str]
    status: str  # pending, approved, changes_requested
    comments: List[str]

@dataclass
class MergeStrategy:
    """Merge strategy configuration"""
    method: str  # merge, squash, rebase
    delete_branch: bool
    require_approvals: int
    require_checks: List[str]
    auto_merge: bool

class PROrchestrator:
    """Main orchestrator for PR lifecycle management"""
    
    def __init__(self, owner: str = "stevesurles"):
        self.owner = owner
        self.active_prs = {}
        self.review_queue = []
        self.merge_queue = []
        
        # PR templates
        self.pr_templates = {
            'feature': {
                'prefix': '[FEATURE]',
                'template': """## Description
{description}

## Type of Change
- [ ] New feature (non-breaking change which adds functionality)

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Code comments updated
- [ ] README updated if needed
- [ ] API documentation updated"""
            },
            'bugfix': {
                'prefix': '[FIX]',
                'template': """## Description
{description}

## Root Cause
{root_cause}

## Solution
{solution}

## Testing
- [ ] Bug reproduction test added
- [ ] Fix verified
- [ ] Regression tests pass"""
            },
            'refactor': {
                'prefix': '[REFACTOR]',
                'template': """## Description
{description}

## Motivation
{motivation}

## Changes
{changes}

## Testing
- [ ] All existing tests pass
- [ ] No functionality changes verified"""
            }
        }
        
        # Review criteria
        self.review_criteria = {
            'code_quality': [
                'No code smells',
                'Follows coding standards',
                'Proper error handling',
                'No security vulnerabilities'
            ],
            'testing': [
                'Adequate test coverage',
                'Tests are meaningful',
                'Edge cases covered'
            ],
            'documentation': [
                'Code is well-commented',
                'API changes documented',
                'README updated if needed'
            ],
            'performance': [
                'No performance regressions',
                'Efficient algorithms used',
                'Resource usage acceptable'
            ]
        }
        
        # Merge strategies by PR type
        self.merge_strategies = {
            'feature': MergeStrategy('squash', True, 2, ['continuous-integration'], True),
            'bugfix': MergeStrategy('squash', True, 1, ['continuous-integration'], True),
            'hotfix': MergeStrategy('merge', False, 1, [], True),
            'refactor': MergeStrategy('squash', True, 2, ['continuous-integration'], False),
            'release': MergeStrategy('merge', False, 3, ['continuous-integration', 'security-scan'], False)
        }
        
        # Conflict resolution strategies
        self.conflict_strategies = {
            'ours': 'Accept current branch changes',
            'theirs': 'Accept incoming changes',
            'manual': 'Manual resolution required',
            'rebase': 'Rebase and resolve'
        }
        
        # Auto-review patterns
        self.auto_review_patterns = {
            'documentation': r'(\.md$|\.rst$|\.txt$)',
            'configuration': r'(\.json$|\.yaml$|\.yml$|\.toml$)',
            'minor_changes': {'additions': 10, 'deletions': 10}
        }
        
        # Monitoring
        self.monitor_interval = 30
        self.monitoring = True
        self.monitor_thread = None
        
        # Metrics
        self.metrics = {
            'total_prs_created': 0,
            'total_prs_merged': 0,
            'total_prs_closed': 0,
            'avg_review_time': 0,
            'avg_merge_time': 0,
            'conflict_resolutions': 0,
            'auto_merges': 0,
            'review_times': [],
            'merge_times': []
        }
    
    def create_pr(self, repo: str, branch: str, base: str, 
                  title: str, description: str, 
                  pr_type: str = 'feature',
                  reviewers: List[str] = None,
                  labels: List[str] = None,
                  draft: bool = False) -> Optional[PullRequest]:
        """Create a new pull request"""
        try:
            # Prepare PR body using template
            template = self.pr_templates.get(pr_type, self.pr_templates['feature'])
            body = template['template'].format(
                description=description,
                root_cause=description,  # Placeholder
                solution=description,     # Placeholder
                motivation=description,   # Placeholder
                changes=description      # Placeholder
            )
            
            # Add prefix to title
            full_title = f"{template['prefix']} {title}"
            
            # Create PR using gh CLI
            cmd = [
                'gh', 'pr', 'create',
                '--repo', f'{self.owner}/{repo}',
                '--base', base,
                '--head', branch,
                '--title', full_title,
                '--body', body
            ]
            
            if draft:
                cmd.append('--draft')
            
            if reviewers:
                cmd.extend(['--reviewer', ','.join(reviewers)])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract PR URL and number
                pr_url = result.stdout.strip()
                pr_number = int(pr_url.split('/')[-1])
                
                # Add labels if specified
                if labels:
                    self._add_labels(repo, pr_number, labels)
                
                # Create PR object
                pr = self._get_pr_details(repo, pr_number)
                if pr:
                    pr.state = PRState.DRAFT if draft else PRState.READY
                    
                    # Generate unique ID
                    pr.pr_id = hashlib.md5(f"{repo}#{pr_number}".encode()).hexdigest()[:8]
                    
                    # Track PR
                    self.active_prs[pr.pr_id] = pr
                    
                    # Add to review queue if not draft
                    if not draft:
                        self._queue_for_review(pr)
                    
                    # Update metrics
                    self.metrics['total_prs_created'] += 1
                    
                    logger.info(f"Created PR #{pr_number} in {repo}: {full_title}")
                    return pr
                    
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
        
        return None
    
    def _get_pr_details(self, repo: str, pr_number: int) -> Optional[PullRequest]:
        """Get detailed PR information"""
        try:
            # Get PR details
            result = subprocess.run(
                ['gh', 'pr', 'view', str(pr_number),
                 '--repo', f'{self.owner}/{repo}',
                 '--json', 'number,title,body,headRefName,baseRefName,state,author,createdAt,updatedAt,labels,reviewRequests,reviews,statusCheckRollup,files,additions,deletions,commits'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Process review data
                reviewers = [r['login'] for r in data.get('reviewRequests', [])]
                approvals = []
                requested_changes = []
                
                for review in data.get('reviews', []):
                    if review['state'] == 'APPROVED':
                        approvals.append(review['author']['login'])
                    elif review['state'] == 'CHANGES_REQUESTED':
                        requested_changes.append({
                            'author': review['author']['login'],
                            'body': review.get('body', '')
                        })
                
                # Process status checks
                checks_status = {}
                for check in data.get('statusCheckRollup', []):
                    checks_status[check.get('context', 'unknown')] = check.get('state', 'pending')
                
                # Create PR object
                pr = PullRequest(
                    pr_id="",  # Will be set by caller
                    number=data['number'],
                    repository=repo,
                    title=data['title'],
                    description=data.get('body', ''),
                    branch=data['headRefName'],
                    base_branch=data['baseRefName'],
                    state=PRState.READY,  # Will be updated based on status
                    author=data.get('author', {}).get('login', 'unknown'),
                    created_at=data['createdAt'],
                    updated_at=data['updatedAt'],
                    reviewers=reviewers,
                    approvals=approvals,
                    requested_changes=requested_changes,
                    labels=[l['name'] for l in data.get('labels', [])],
                    checks_status=checks_status,
                    conflicts=False,  # Will be checked separately
                    mergeable=True,   # Will be checked separately
                    comments=[],      # Will be fetched if needed
                    commits=[c['oid'] for c in data.get('commits', [])],
                    files_changed=len(data.get('files', [])),
                    additions=data.get('additions', 0),
                    deletions=data.get('deletions', 0)
                )
                
                return pr
                
        except Exception as e:
            logger.error(f"Failed to get PR details: {e}")
        
        return None
    
    def _add_labels(self, repo: str, pr_number: int, labels: List[str]):
        """Add labels to a PR"""
        try:
            for label in labels:
                subprocess.run(
                    ['gh', 'pr', 'edit', str(pr_number),
                     '--repo', f'{self.owner}/{repo}',
                     '--add-label', label],
                    capture_output=True
                )
            logger.info(f"Added labels to PR #{pr_number}: {labels}")
        except Exception as e:
            logger.error(f"Failed to add labels: {e}")
    
    def _queue_for_review(self, pr: PullRequest):
        """Add PR to review queue"""
        # Check if auto-reviewable
        if self._is_auto_reviewable(pr):
            self._perform_auto_review(pr)
        else:
            # Add to manual review queue
            review_request = ReviewRequest(
                pr_id=pr.pr_id,
                reviewer="pending",
                requested_at=datetime.now().isoformat(),
                reviewed_at=None,
                status="pending",
                comments=[]
            )
            self.review_queue.append(review_request)
            logger.info(f"PR {pr.pr_id} queued for review")
    
    def _is_auto_reviewable(self, pr: PullRequest) -> bool:
        """Check if PR can be auto-reviewed"""
        # Check for documentation only changes
        if pr.files_changed > 0:
            # Would need to fetch file list and check patterns
            pass
        
        # Check for minor changes
        minor = self.auto_review_patterns['minor_changes']
        if pr.additions <= minor['additions'] and pr.deletions <= minor['deletions']:
            return True
        
        # Check labels
        if 'auto-review' in pr.labels:
            return True
        
        return False
    
    def _perform_auto_review(self, pr: PullRequest):
        """Perform automated review"""
        logger.info(f"Performing auto-review for PR {pr.pr_id}")
        
        try:
            # Run automated checks
            checks_passed = self._run_automated_checks(pr)
            
            if checks_passed:
                # Approve PR
                subprocess.run(
                    ['gh', 'pr', 'review', str(pr.number),
                     '--repo', f'{self.owner}/{pr.repository}',
                     '--approve',
                     '--body', 'Auto-approved: All automated checks passed'],
                    capture_output=True
                )
                
                pr.approvals.append('auto-reviewer')
                pr.state = PRState.APPROVED
                
                # Queue for merge if auto-merge enabled
                strategy = self._get_merge_strategy(pr)
                if strategy.auto_merge:
                    self._queue_for_merge(pr)
                
                logger.info(f"Auto-approved PR {pr.pr_id}")
            else:
                # Request changes
                subprocess.run(
                    ['gh', 'pr', 'review', str(pr.number),
                     '--repo', f'{self.owner}/{pr.repository}',
                     '--request-changes',
                     '--body', 'Automated checks failed. Please review the feedback.'],
                    capture_output=True
                )
                
                pr.state = PRState.CHANGES_REQUESTED
                logger.info(f"Changes requested for PR {pr.pr_id}")
                
        except Exception as e:
            logger.error(f"Auto-review failed: {e}")
    
    def _run_automated_checks(self, pr: PullRequest) -> bool:
        """Run automated quality checks"""
        checks_passed = True
        
        # Check CI status
        for check, status in pr.checks_status.items():
            if 'continuous-integration' in check and status != 'success':
                checks_passed = False
                logger.warning(f"CI check failed for PR {pr.pr_id}: {check}")
        
        # Check for conflicts
        if pr.conflicts:
            checks_passed = False
            logger.warning(f"PR {pr.pr_id} has conflicts")
        
        # Additional checks could be added here
        # - Code quality metrics
        # - Security scanning
        # - Test coverage
        
        return checks_passed
    
    def request_review(self, pr_id: str, reviewers: List[str]) -> bool:
        """Request review from specific reviewers"""
        if pr_id not in self.active_prs:
            logger.error(f"PR {pr_id} not found")
            return False
        
        pr = self.active_prs[pr_id]
        
        try:
            result = subprocess.run(
                ['gh', 'pr', 'edit', str(pr.number),
                 '--repo', f'{self.owner}/{pr.repository}',
                 '--add-reviewer', ','.join(reviewers)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pr.reviewers.extend(reviewers)
                pr.state = PRState.IN_REVIEW
                
                # Create review requests
                for reviewer in reviewers:
                    review_request = ReviewRequest(
                        pr_id=pr_id,
                        reviewer=reviewer,
                        requested_at=datetime.now().isoformat(),
                        reviewed_at=None,
                        status="pending",
                        comments=[]
                    )
                    self.review_queue.append(review_request)
                
                logger.info(f"Requested review from {reviewers} for PR {pr_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to request review: {e}")
        
        return False
    
    def handle_review_feedback(self, pr_id: str, reviewer: str, 
                              status: str, comments: List[str]):
        """Handle review feedback"""
        if pr_id not in self.active_prs:
            return
        
        pr = self.active_prs[pr_id]
        
        # Update review status
        for review in self.review_queue:
            if review.pr_id == pr_id and review.reviewer == reviewer:
                review.status = status
                review.reviewed_at = datetime.now().isoformat()
                review.comments = comments
                break
        
        # Update PR state
        if status == 'approved':
            pr.approvals.append(reviewer)
            
            # Check if enough approvals
            strategy = self._get_merge_strategy(pr)
            if len(pr.approvals) >= strategy.require_approvals:
                pr.state = PRState.APPROVED
                
                # Queue for merge if auto-merge enabled
                if strategy.auto_merge:
                    self._queue_for_merge(pr)
        
        elif status == 'changes_requested':
            pr.requested_changes.append({
                'author': reviewer,
                'comments': comments
            })
            pr.state = PRState.CHANGES_REQUESTED
        
        # Calculate review time
        created = datetime.fromisoformat(pr.created_at.replace('Z', '+00:00'))
        review_time = (datetime.now() - created).total_seconds() / 3600  # hours
        self.metrics['review_times'].append(review_time)
        self.metrics['avg_review_time'] = sum(self.metrics['review_times']) / len(self.metrics['review_times'])
        
        logger.info(f"Processed review from {reviewer} for PR {pr_id}: {status}")
    
    def _get_merge_strategy(self, pr: PullRequest) -> MergeStrategy:
        """Get merge strategy for PR"""
        # Determine PR type from labels or title
        pr_type = 'feature'  # Default
        
        for label in pr.labels:
            if label.lower() in self.merge_strategies:
                pr_type = label.lower()
                break
        
        return self.merge_strategies.get(pr_type, self.merge_strategies['feature'])
    
    def _queue_for_merge(self, pr: PullRequest):
        """Add PR to merge queue"""
        if pr.pr_id not in self.merge_queue:
            self.merge_queue.append(pr.pr_id)
            pr.state = PRState.MERGING
            logger.info(f"PR {pr.pr_id} queued for merge")
    
    def merge_pr(self, pr_id: str, method: str = None) -> bool:
        """Merge a pull request"""
        if pr_id not in self.active_prs:
            logger.error(f"PR {pr_id} not found")
            return False
        
        pr = self.active_prs[pr_id]
        
        # Check merge requirements
        if not self._check_merge_requirements(pr):
            logger.warning(f"PR {pr_id} does not meet merge requirements")
            return False
        
        # Get merge strategy
        strategy = self._get_merge_strategy(pr)
        merge_method = method or strategy.method
        
        try:
            cmd = ['gh', 'pr', 'merge', str(pr.number),
                   '--repo', f'{self.owner}/{pr.repository}']
            
            # Add merge method
            if merge_method == 'squash':
                cmd.append('--squash')
            elif merge_method == 'rebase':
                cmd.append('--rebase')
            else:
                cmd.append('--merge')
            
            # Add delete branch flag
            if strategy.delete_branch:
                cmd.append('--delete-branch')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                pr.state = PRState.MERGED
                
                # Update metrics
                self.metrics['total_prs_merged'] += 1
                if strategy.auto_merge:
                    self.metrics['auto_merges'] += 1
                
                # Calculate merge time
                created = datetime.fromisoformat(pr.created_at.replace('Z', '+00:00'))
                merge_time = (datetime.now() - created).total_seconds() / 3600  # hours
                self.metrics['merge_times'].append(merge_time)
                self.metrics['avg_merge_time'] = sum(self.metrics['merge_times']) / len(self.metrics['merge_times'])
                
                # Remove from queues
                if pr_id in self.merge_queue:
                    self.merge_queue.remove(pr_id)
                
                logger.info(f"Merged PR {pr_id} using {merge_method} method")
                return True
                
        except Exception as e:
            logger.error(f"Failed to merge PR: {e}")
        
        return False
    
    def _check_merge_requirements(self, pr: PullRequest) -> bool:
        """Check if PR meets merge requirements"""
        strategy = self._get_merge_strategy(pr)
        
        # Check approvals
        if len(pr.approvals) < strategy.require_approvals:
            logger.warning(f"PR {pr.pr_id} needs {strategy.require_approvals} approvals, has {len(pr.approvals)}")
            return False
        
        # Check required checks
        for required_check in strategy.require_checks:
            check_passed = False
            for check, status in pr.checks_status.items():
                if required_check in check and status == 'success':
                    check_passed = True
                    break
            
            if not check_passed:
                logger.warning(f"PR {pr.pr_id} missing required check: {required_check}")
                return False
        
        # Check for conflicts
        if pr.conflicts:
            logger.warning(f"PR {pr.pr_id} has conflicts")
            return False
        
        # Check for requested changes
        if pr.requested_changes and pr.state == PRState.CHANGES_REQUESTED:
            logger.warning(f"PR {pr.pr_id} has unresolved change requests")
            return False
        
        return True
    
    def handle_conflicts(self, pr_id: str, strategy: str = 'manual') -> bool:
        """Handle merge conflicts"""
        if pr_id not in self.active_prs:
            return False
        
        pr = self.active_prs[pr_id]
        pr.state = PRState.CONFLICT
        
        logger.info(f"Handling conflicts for PR {pr_id} using {strategy} strategy")
        
        if strategy == 'rebase':
            try:
                # Attempt to rebase
                result = subprocess.run(
                    ['gh', 'pr', 'checkout', str(pr.number),
                     '--repo', f'{self.owner}/{pr.repository}'],
                    capture_output=True
                )
                
                if result.returncode == 0:
                    # Perform rebase
                    subprocess.run(['git', 'rebase', pr.base_branch], capture_output=True)
                    subprocess.run(['git', 'push', '--force-with-lease'], capture_output=True)
                    
                    pr.conflicts = False
                    pr.state = PRState.READY
                    
                    self.metrics['conflict_resolutions'] += 1
                    logger.info(f"Successfully rebased PR {pr_id}")
                    return True
                    
            except Exception as e:
                logger.error(f"Failed to rebase: {e}")
        
        elif strategy == 'ours' or strategy == 'theirs':
            # These would require more complex git operations
            logger.warning(f"Strategy {strategy} not fully implemented")
        
        # Default to manual resolution
        logger.info(f"Manual conflict resolution required for PR {pr_id}")
        return False
    
    def update_pr(self, pr_id: str, title: str = None, 
                  description: str = None, labels: List[str] = None) -> bool:
        """Update PR details"""
        if pr_id not in self.active_prs:
            return False
        
        pr = self.active_prs[pr_id]
        
        try:
            cmd = ['gh', 'pr', 'edit', str(pr.number),
                   '--repo', f'{self.owner}/{pr.repository}']
            
            if title:
                cmd.extend(['--title', title])
                pr.title = title
            
            if description:
                cmd.extend(['--body', description])
                pr.description = description
            
            if labels:
                for label in labels:
                    cmd.extend(['--add-label', label])
                pr.labels.extend(labels)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                pr.updated_at = datetime.now().isoformat()
                logger.info(f"Updated PR {pr_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update PR: {e}")
        
        return False
    
    def close_pr(self, pr_id: str, comment: str = None) -> bool:
        """Close a pull request without merging"""
        if pr_id not in self.active_prs:
            return False
        
        pr = self.active_prs[pr_id]
        
        try:
            # Add closing comment if provided
            if comment:
                subprocess.run(
                    ['gh', 'pr', 'comment', str(pr.number),
                     '--repo', f'{self.owner}/{pr.repository}',
                     '--body', comment],
                    capture_output=True
                )
            
            # Close PR
            result = subprocess.run(
                ['gh', 'pr', 'close', str(pr.number),
                 '--repo', f'{self.owner}/{pr.repository}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pr.state = PRState.CLOSED
                self.metrics['total_prs_closed'] += 1
                
                # Remove from queues
                if pr_id in self.merge_queue:
                    self.merge_queue.remove(pr_id)
                
                logger.info(f"Closed PR {pr_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to close PR: {e}")
        
        return False
    
    def monitor_prs(self):
        """Monitor PRs for updates"""
        logger.info("Starting PR monitoring...")
        
        while self.monitoring:
            try:
                # Process merge queue
                for pr_id in list(self.merge_queue):
                    pr = self.active_prs.get(pr_id)
                    if pr and pr.state == PRState.APPROVED:
                        if self._check_merge_requirements(pr):
                            self.merge_pr(pr_id)
                
                # Check for PR updates
                for pr_id, pr in list(self.active_prs.items()):
                    if pr.state not in [PRState.MERGED, PRState.CLOSED]:
                        # Refresh PR details
                        updated_pr = self._get_pr_details(pr.repository, pr.number)
                        if updated_pr:
                            # Update tracked PR
                            updated_pr.pr_id = pr_id
                            self.active_prs[pr_id] = updated_pr
                            
                            # Check for state changes
                            if len(updated_pr.approvals) >= self._get_merge_strategy(updated_pr).require_approvals:
                                if updated_pr.state != PRState.APPROVED:
                                    updated_pr.state = PRState.APPROVED
                                    if self._get_merge_strategy(updated_pr).auto_merge:
                                        self._queue_for_merge(updated_pr)
                
                # Log status
                active_count = len([pr for pr in self.active_prs.values() 
                                  if pr.state not in [PRState.MERGED, PRState.CLOSED]])
                logger.info(f"Monitoring: {active_count} active PRs, "
                          f"{len(self.merge_queue)} in merge queue")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.monitor_interval)
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_prs, daemon=True)
            self.monitor_thread.start()
            logger.info("PR monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            logger.info("PR monitoring stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'active_prs': len(self.active_prs),
            'review_queue': len(self.review_queue),
            'merge_queue': len(self.merge_queue),
            'prs_by_state': self._count_by_state(),
            'metrics': self.metrics
        }
    
    def _count_by_state(self) -> Dict[str, int]:
        """Count PRs by state"""
        counts = defaultdict(int)
        for pr in self.active_prs.values():
            counts[pr.state.value] += 1
        return dict(counts)
    
    def save_state(self):
        """Save orchestrator state"""
        state = {
            'active_prs': {pr_id: asdict(pr) for pr_id, pr in self.active_prs.items()},
            'review_queue': [asdict(r) for r in self.review_queue],
            'merge_queue': self.merge_queue,
            'metrics': self.metrics
        }
        
        with open('pr_orchestrator_state.json', 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        logger.info("Orchestrator state saved")
    
    def load_state(self):
        """Load orchestrator state"""
        if os.path.exists('pr_orchestrator_state.json'):
            try:
                with open('pr_orchestrator_state.json', 'r') as f:
                    state = json.load(f)
                
                # Restore active PRs
                self.active_prs = {}
                for pr_id, pr_data in state.get('active_prs', {}).items():
                    pr_data['state'] = PRState(pr_data['state'])
                    self.active_prs[pr_id] = PullRequest(**pr_data)
                
                # Restore queues
                self.review_queue = [ReviewRequest(**r) for r in state.get('review_queue', [])]
                self.merge_queue = state.get('merge_queue', [])
                
                # Restore metrics
                self.metrics = state.get('metrics', self.metrics)
                
                logger.info(f"Orchestrator state loaded: {len(self.active_prs)} active PRs")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")


def main():
    """Main execution function"""
    logger.info("Starting PR Orchestrator Agent...")
    
    # Initialize orchestrator
    orchestrator = PROrchestrator()
    
    # Load previous state if exists
    orchestrator.load_state()
    
    # Start monitoring
    orchestrator.start_monitoring()
    
    print("\n" + "="*80)
    print("PR Orchestrator Agent Initialized Successfully!")
    print("="*80)
    print(f"Active PRs: {len(orchestrator.active_prs)}")
    print(f"Review Queue: {len(orchestrator.review_queue)}")
    print(f"Merge Queue: {len(orchestrator.merge_queue)}")
    print(f"Total PRs Created: {orchestrator.metrics['total_prs_created']}")
    print(f"Total PRs Merged: {orchestrator.metrics['total_prs_merged']}")
    print("="*80)
    
    try:
        # Keep running and periodically save state
        while True:
            time.sleep(60)  # Save state every minute
            orchestrator.save_state()
            
            # Log status
            status = orchestrator.get_status()
            logger.info(f"Status: {status['active_prs']} active, "
                       f"{status['review_queue']} in review, "
                       f"{status['merge_queue']} pending merge")
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        orchestrator.stop_monitoring()
        orchestrator.save_state()


if __name__ == "__main__":
    main()