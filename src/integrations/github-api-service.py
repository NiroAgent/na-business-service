#!/usr/bin/env python3
"""
GitHub API Service Layer
Centralized GitHub operations management with rate limiting and optimization
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
from collections import deque
import threading
import hashlib
import base64
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_api_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GitHubAPIService')

@dataclass
class APIQuota:
    """API rate limit tracking"""
    limit: int
    remaining: int
    reset_time: datetime
    used: int

@dataclass
class PullRequest:
    """Pull Request data structure"""
    number: int
    title: str
    description: str
    branch: str
    base_branch: str
    state: str
    draft: bool
    assignees: List[str]
    reviewers: List[str]
    labels: List[str]
    created_at: str
    updated_at: str
    repository: str

@dataclass
class ProjectCard:
    """GitHub Project card"""
    id: str
    content_type: str
    content_url: str
    column: str
    note: Optional[str] = None

class APIRateLimiter:
    """Intelligent rate limiting for GitHub API"""
    
    def __init__(self):
        self.quotas = {}
        self.request_queue = deque()
        self.request_history = deque(maxlen=1000)
        self.lock = threading.Lock()
        
        # Rate limit thresholds
        self.warning_threshold = 0.2  # Warn when 20% remaining
        self.throttle_threshold = 0.1  # Throttle when 10% remaining
    
    def check_quota(self) -> APIQuota:
        """Check current API quota"""
        try:
            result = subprocess.run(
                ['gh', 'api', 'rate_limit'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                core_limit = data['resources']['core']
                
                quota = APIQuota(
                    limit=core_limit['limit'],
                    remaining=core_limit['remaining'],
                    reset_time=datetime.fromtimestamp(core_limit['reset']),
                    used=core_limit['used']
                )
                
                self.quotas['core'] = quota
                return quota
            
        except Exception as e:
            logger.error(f"Failed to check API quota: {e}")
        
        # Return default quota if check fails
        return APIQuota(limit=5000, remaining=5000, reset_time=datetime.now() + timedelta(hours=1), used=0)
    
    def should_throttle(self) -> bool:
        """Determine if requests should be throttled"""
        quota = self.check_quota()
        remaining_percent = quota.remaining / quota.limit if quota.limit > 0 else 1
        
        if remaining_percent < self.throttle_threshold:
            logger.warning(f"API quota low: {quota.remaining}/{quota.limit} remaining")
            return True
        
        return False
    
    def wait_if_needed(self):
        """Wait if rate limit is approaching"""
        if self.should_throttle():
            quota = self.quotas.get('core')
            if quota:
                wait_time = (quota.reset_time - datetime.now()).total_seconds()
                if wait_time > 0:
                    logger.info(f"Rate limit throttling - waiting {wait_time:.0f} seconds")
                    time.sleep(min(wait_time, 60))  # Max wait 60 seconds

class GitHubAuthManager:
    """Manage GitHub authentication and tokens"""
    
    def __init__(self):
        self.tokens = []
        self.current_token_index = 0
        self.app_id = os.getenv('GITHUB_APP_ID')
        self.installation_id = os.getenv('GITHUB_INSTALLATION_ID')
    
    def verify_auth(self) -> bool:
        """Verify GitHub CLI authentication"""
        try:
            result = subprocess.run(
                ['gh', 'auth', 'status'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def refresh_auth(self) -> bool:
        """Refresh GitHub authentication"""
        try:
            result = subprocess.run(
                ['gh', 'auth', 'refresh'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def rotate_token(self):
        """Rotate to next available token (if multiple configured)"""
        if len(self.tokens) > 1:
            self.current_token_index = (self.current_token_index + 1) % len(self.tokens)
            logger.info(f"Rotated to token {self.current_token_index}")

class WebhookManager:
    """Manage GitHub webhooks"""
    
    def __init__(self):
        self.webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET', 'default_secret')
        self.registered_webhooks = {}
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        import hmac
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)
    
    def register_webhook(self, repo: str, events: List[str], url: str) -> bool:
        """Register a new webhook"""
        try:
            config = {
                'url': url,
                'content_type': 'json',
                'secret': self.webhook_secret
            }
            
            result = subprocess.run(
                ['gh', 'api', f'repos/{repo}/hooks', '--method', 'POST',
                 '--field', f'config={json.dumps(config)}',
                 '--field', f'events={json.dumps(events)}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                webhook_data = json.loads(result.stdout)
                self.registered_webhooks[repo] = webhook_data['id']
                logger.info(f"Webhook registered for {repo}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register webhook: {e}")
        
        return False

class GitHubAPIService:
    """Main GitHub API service"""
    
    def __init__(self, owner: str = "stevesurles"):
        self.owner = owner
        self.auth_manager = GitHubAuthManager()
        self.rate_limiter = APIRateLimiter()
        self.webhook_manager = WebhookManager()
        
        # Verify authentication
        if not self.auth_manager.verify_auth():
            logger.warning("GitHub authentication not verified")
            self.auth_manager.refresh_auth()
        
        # Cache for optimization
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Batch operation queue
        self.batch_queue = []
        self.batch_size = 10
        
    def create_pull_request(self, repo: str, branch: str, base: str, 
                          title: str, body: str, 
                          assignees: List[str] = None,
                          reviewers: List[str] = None,
                          labels: List[str] = None,
                          draft: bool = False) -> Optional[PullRequest]:
        """Create a new pull request"""
        self.rate_limiter.wait_if_needed()
        
        try:
            # Build command
            cmd = [
                'gh', 'pr', 'create',
                '--repo', f'{self.owner}/{repo}',
                '--base', base,
                '--head', branch,
                '--title', title,
                '--body', body
            ]
            
            if draft:
                cmd.append('--draft')
            
            if assignees:
                cmd.extend(['--assignee', ','.join(assignees)])
            
            if reviewers:
                cmd.extend(['--reviewer', ','.join(reviewers)])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract PR number from output
                pr_url = result.stdout.strip()
                pr_number = int(pr_url.split('/')[-1])
                
                # Add labels if specified
                if labels:
                    self.add_labels_to_pr(repo, pr_number, labels)
                
                # Get PR details
                pr_data = self.get_pull_request(repo, pr_number)
                
                logger.info(f"Created PR #{pr_number} in {repo}")
                return pr_data
                
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
        
        return None
    
    def get_pull_request(self, repo: str, pr_number: int) -> Optional[PullRequest]:
        """Get pull request details"""
        self.rate_limiter.wait_if_needed()
        
        try:
            result = subprocess.run(
                ['gh', 'pr', 'view', str(pr_number),
                 '--repo', f'{self.owner}/{repo}',
                 '--json', 'number,title,body,headRefName,baseRefName,state,isDraft,assignees,reviewRequests,labels,createdAt,updatedAt'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                pr = PullRequest(
                    number=data['number'],
                    title=data['title'],
                    description=data.get('body', ''),
                    branch=data['headRefName'],
                    base_branch=data['baseRefName'],
                    state=data['state'],
                    draft=data.get('isDraft', False),
                    assignees=[a['login'] for a in data.get('assignees', [])],
                    reviewers=[r['login'] for r in data.get('reviewRequests', [])],
                    labels=[l['name'] for l in data.get('labels', [])],
                    created_at=data['createdAt'],
                    updated_at=data['updatedAt'],
                    repository=repo
                )
                
                return pr
                
        except Exception as e:
            logger.error(f"Failed to get PR #{pr_number}: {e}")
        
        return None
    
    def add_labels_to_pr(self, repo: str, pr_number: int, labels: List[str]):
        """Add labels to a pull request"""
        self.rate_limiter.wait_if_needed()
        
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
    
    def request_review(self, repo: str, pr_number: int, reviewers: List[str]):
        """Request review for a pull request"""
        self.rate_limiter.wait_if_needed()
        
        try:
            result = subprocess.run(
                ['gh', 'pr', 'edit', str(pr_number),
                 '--repo', f'{self.owner}/{repo}',
                 '--add-reviewer', ','.join(reviewers)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Requested review from {reviewers} for PR #{pr_number}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to request review: {e}")
        
        return False
    
    def approve_pr(self, repo: str, pr_number: int, comment: str = ""):
        """Approve a pull request"""
        self.rate_limiter.wait_if_needed()
        
        try:
            cmd = ['gh', 'pr', 'review', str(pr_number),
                   '--repo', f'{self.owner}/{repo}',
                   '--approve']
            
            if comment:
                cmd.extend(['--body', comment])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Approved PR #{pr_number}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to approve PR: {e}")
        
        return False
    
    def merge_pr(self, repo: str, pr_number: int, 
                 merge_method: str = "squash",
                 delete_branch: bool = True) -> bool:
        """Merge a pull request"""
        self.rate_limiter.wait_if_needed()
        
        try:
            cmd = ['gh', 'pr', 'merge', str(pr_number),
                   '--repo', f'{self.owner}/{repo}']
            
            # Add merge method
            if merge_method == "squash":
                cmd.append('--squash')
            elif merge_method == "rebase":
                cmd.append('--rebase')
            else:
                cmd.append('--merge')
            
            if delete_branch:
                cmd.append('--delete-branch')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Merged PR #{pr_number} using {merge_method}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to merge PR: {e}")
        
        return False
    
    def create_branch(self, repo: str, branch_name: str, base_branch: str = "main") -> bool:
        """Create a new branch"""
        self.rate_limiter.wait_if_needed()
        
        try:
            # Use git commands through gh
            result = subprocess.run(
                ['gh', 'api', f'repos/{self.owner}/{repo}/git/refs',
                 '--method', 'POST',
                 '--field', f'ref=refs/heads/{branch_name}',
                 '--field', f'sha={{{{ (gh api repos/{self.owner}/{repo}/git/refs/heads/{base_branch} --jq .object.sha) }}}}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Created branch {branch_name} from {base_branch}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create branch: {e}")
        
        return False
    
    def protect_branch(self, repo: str, branch: str, 
                      require_reviews: int = 1,
                      dismiss_stale_reviews: bool = True,
                      require_code_owner_reviews: bool = False) -> bool:
        """Set branch protection rules"""
        self.rate_limiter.wait_if_needed()
        
        try:
            protection_rules = {
                "required_status_checks": {
                    "strict": True,
                    "contexts": ["continuous-integration"]
                },
                "enforce_admins": False,
                "required_pull_request_reviews": {
                    "required_approving_review_count": require_reviews,
                    "dismiss_stale_reviews": dismiss_stale_reviews,
                    "require_code_owner_reviews": require_code_owner_reviews
                },
                "restrictions": None
            }
            
            result = subprocess.run(
                ['gh', 'api', f'repos/{self.owner}/{repo}/branches/{branch}/protection',
                 '--method', 'PUT',
                 '--input', '-'],
                input=json.dumps(protection_rules),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Protected branch {branch} in {repo}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to protect branch: {e}")
        
        return False
    
    def manage_project_boards(self, repo: str, project_name: str, 
                            columns: List[str] = None) -> Optional[Dict]:
        """Create or update project board"""
        self.rate_limiter.wait_if_needed()
        
        try:
            # Create project
            result = subprocess.run(
                ['gh', 'project', 'create',
                 '--owner', self.owner,
                 '--title', project_name,
                 '--format', 'json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                project_data = json.loads(result.stdout)
                project_id = project_data['id']
                
                # Add columns if specified
                if columns:
                    for column in columns:
                        self.add_project_column(project_id, column)
                
                logger.info(f"Created project board: {project_name}")
                return project_data
                
        except Exception as e:
            logger.error(f"Failed to manage project board: {e}")
        
        return None
    
    def add_project_column(self, project_id: str, column_name: str) -> bool:
        """Add column to project board"""
        self.rate_limiter.wait_if_needed()
        
        try:
            result = subprocess.run(
                ['gh', 'api', f'projects/{project_id}/columns',
                 '--method', 'POST',
                 '--field', f'name={column_name}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Added column {column_name} to project {project_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add project column: {e}")
        
        return False
    
    def move_project_card(self, card_id: str, column_id: str, position: str = "top") -> bool:
        """Move project card to different column"""
        self.rate_limiter.wait_if_needed()
        
        try:
            result = subprocess.run(
                ['gh', 'api', f'projects/columns/cards/{card_id}/moves',
                 '--method', 'POST',
                 '--field', f'column_id={column_id}',
                 '--field', f'position={position}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Moved card {card_id} to column {column_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to move project card: {e}")
        
        return False
    
    def create_issue(self, repo: str, title: str, body: str,
                    labels: List[str] = None,
                    assignees: List[str] = None,
                    milestone: str = None) -> Optional[int]:
        """Create a new issue"""
        self.rate_limiter.wait_if_needed()
        
        try:
            cmd = ['gh', 'issue', 'create',
                   '--repo', f'{self.owner}/{repo}',
                   '--title', title,
                   '--body', body]
            
            if labels:
                cmd.extend(['--label', ','.join(labels)])
            
            if assignees:
                cmd.extend(['--assignee', ','.join(assignees)])
            
            if milestone:
                cmd.extend(['--milestone', milestone])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract issue number from URL
                issue_url = result.stdout.strip()
                issue_number = int(issue_url.split('/')[-1])
                
                logger.info(f"Created issue #{issue_number} in {repo}")
                return issue_number
                
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
        
        return None
    
    def close_issue(self, repo: str, issue_number: int, comment: str = None) -> bool:
        """Close an issue"""
        self.rate_limiter.wait_if_needed()
        
        try:
            # Add comment if provided
            if comment:
                subprocess.run(
                    ['gh', 'issue', 'comment', str(issue_number),
                     '--repo', f'{self.owner}/{repo}',
                     '--body', comment],
                    capture_output=True
                )
            
            # Close issue
            result = subprocess.run(
                ['gh', 'issue', 'close', str(issue_number),
                 '--repo', f'{self.owner}/{repo}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Closed issue #{issue_number}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to close issue: {e}")
        
        return False
    
    def batch_operations(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute batch operations for efficiency"""
        results = []
        
        # Group operations by type
        grouped_ops = {}
        for op in operations:
            op_type = op['type']
            if op_type not in grouped_ops:
                grouped_ops[op_type] = []
            grouped_ops[op_type].append(op)
        
        # Execute grouped operations
        for op_type, ops in grouped_ops.items():
            if op_type == 'add_labels':
                # Batch label additions
                for op in ops:
                    self.add_labels_to_pr(op['repo'], op['pr_number'], op['labels'])
                    results.append({'success': True, 'operation': op})
            
            elif op_type == 'close_issues':
                # Batch issue closures
                for op in ops:
                    success = self.close_issue(op['repo'], op['issue_number'], op.get('comment'))
                    results.append({'success': success, 'operation': op})
            
            # Add more batch operation types as needed
        
        logger.info(f"Executed {len(operations)} batch operations")
        return results
    
    def get_workflow_runs(self, repo: str, workflow_name: str = None, 
                         status: str = None, limit: int = 10) -> List[Dict]:
        """Get workflow run information"""
        self.rate_limiter.wait_if_needed()
        
        try:
            cmd = ['gh', 'run', 'list',
                   '--repo', f'{self.owner}/{repo}',
                   '--limit', str(limit),
                   '--json', 'databaseId,name,status,conclusion,createdAt']
            
            if workflow_name:
                cmd.extend(['--workflow', workflow_name])
            
            if status:
                cmd.extend(['--status', status])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
                
        except Exception as e:
            logger.error(f"Failed to get workflow runs: {e}")
        
        return []
    
    def trigger_workflow(self, repo: str, workflow_file: str, 
                        ref: str = "main", inputs: Dict[str, Any] = None) -> bool:
        """Trigger a workflow dispatch event"""
        self.rate_limiter.wait_if_needed()
        
        try:
            cmd = ['gh', 'workflow', 'run', workflow_file,
                   '--repo', f'{self.owner}/{repo}',
                   '--ref', ref]
            
            if inputs:
                for key, value in inputs.items():
                    cmd.extend(['--field', f'{key}={value}'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Triggered workflow {workflow_file} in {repo}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to trigger workflow: {e}")
        
        return False
    
    def get_file_content(self, repo: str, path: str, ref: str = "main") -> Optional[str]:
        """Get file content from repository"""
        cache_key = f"{repo}:{path}:{ref}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_data['content']
        
        self.rate_limiter.wait_if_needed()
        
        try:
            result = subprocess.run(
                ['gh', 'api', f'repos/{self.owner}/{repo}/contents/{path}',
                 '--jq', '.content'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Decode base64 content
                content = base64.b64decode(result.stdout.strip()).decode('utf-8')
                
                # Cache result
                self.cache[cache_key] = {
                    'content': content,
                    'timestamp': datetime.now()
                }
                
                return content
                
        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
        
        return None
    
    def update_file(self, repo: str, path: str, content: str, 
                   message: str, branch: str = "main") -> bool:
        """Update file in repository"""
        self.rate_limiter.wait_if_needed()
        
        try:
            # Get current file SHA
            result = subprocess.run(
                ['gh', 'api', f'repos/{self.owner}/{repo}/contents/{path}',
                 '--jq', '.sha'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                sha = result.stdout.strip()
                
                # Update file
                update_data = {
                    'message': message,
                    'content': base64.b64encode(content.encode()).decode(),
                    'sha': sha,
                    'branch': branch
                }
                
                result = subprocess.run(
                    ['gh', 'api', f'repos/{self.owner}/{repo}/contents/{path}',
                     '--method', 'PUT',
                     '--input', '-'],
                    input=json.dumps(update_data),
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info(f"Updated file {path} in {repo}")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to update file: {e}")
        
        return False
    
    def get_commit_diff(self, repo: str, commit_sha: str) -> Optional[str]:
        """Get diff for a specific commit"""
        self.rate_limiter.wait_if_needed()
        
        try:
            result = subprocess.run(
                ['gh', 'api', f'repos/{self.owner}/{repo}/commits/{commit_sha}',
                 '--jq', '.files'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
                
        except Exception as e:
            logger.error(f"Failed to get commit diff: {e}")
        
        return None
    
    def search_code(self, query: str, repo: str = None, 
                   language: str = None, limit: int = 10) -> List[Dict]:
        """Search code in repositories"""
        self.rate_limiter.wait_if_needed()
        
        try:
            search_query = query
            if repo:
                search_query += f" repo:{self.owner}/{repo}"
            if language:
                search_query += f" language:{language}"
            
            result = subprocess.run(
                ['gh', 'search', 'code', search_query,
                 '--limit', str(limit),
                 '--json', 'repository,path,textMatches'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
                
        except Exception as e:
            logger.error(f"Failed to search code: {e}")
        
        return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get API service metrics"""
        quota = self.rate_limiter.check_quota()
        
        return {
            'api_quota': {
                'limit': quota.limit,
                'remaining': quota.remaining,
                'used': quota.used,
                'reset_time': quota.reset_time.isoformat()
            },
            'cache_size': len(self.cache),
            'batch_queue_size': len(self.batch_queue),
            'webhooks_registered': len(self.webhook_manager.registered_webhooks)
        }


def main():
    """Main execution for testing"""
    logger.info("Initializing GitHub API Service...")
    
    # Initialize service
    service = GitHubAPIService()
    
    # Check API quota
    quota = service.rate_limiter.check_quota()
    logger.info(f"API Quota: {quota.remaining}/{quota.limit} remaining")
    
    # Test operations
    # Example: Create a test issue
    # issue_number = service.create_issue(
    #     "test-repo",
    #     "Test Issue from API Service",
    #     "This is a test issue created by the GitHub API Service",
    #     labels=["test", "automated"]
    # )
    
    # Get metrics
    metrics = service.get_metrics()
    logger.info(f"Service metrics: {json.dumps(metrics, indent=2)}")
    
    print("\n" + "="*80)
    print("GitHub API Service Initialized Successfully!")
    print("="*80)
    print(f"Authentication: {'✓' if service.auth_manager.verify_auth() else '✗'}")
    print(f"API Quota: {quota.remaining}/{quota.limit}")
    print(f"Rate Limiting: Active")
    print(f"Webhook Support: Ready")
    print("="*80)


if __name__ == "__main__":
    main()