#!/usr/bin/env python3
"""
AI Development Team Work Queue Manager
Manages work distribution, prioritization, and progress tracking
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import heapq

class WorkItemType(Enum):
    GITHUB_ISSUE = "github_issue"
    BUG_FIX = "bug_fix"
    FEATURE_REQUEST = "feature_request"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    SECURITY_FIX = "security_fix"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"

class WorkItemStatus(Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    TESTING = "testing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Priority(Enum):
    P0_CRITICAL = 1    # Production down, security breach
    P1_HIGH = 2        # Major feature broken, significant impact
    P2_MEDIUM = 3      # Normal features and improvements
    P3_LOW = 4         # Nice to have, technical debt
    P4_BACKLOG = 5     # Future consideration

@dataclass
class WorkItem:
    id: str
    title: str
    description: str
    work_type: WorkItemType
    priority: Priority
    estimated_effort: int  # Story points or hours
    skills_required: List[str]
    created_at: datetime
    assigned_to: Optional[str] = None
    assigned_at: Optional[datetime] = None
    status: WorkItemStatus = WorkItemStatus.QUEUED
    github_issue_id: Optional[str] = None
    github_repo: Optional[str] = None
    dependencies: List[str] = None
    blockers: List[str] = None
    progress_percentage: int = 0
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.blockers is None:
            self.blockers = []
    
    def __lt__(self, other):
        # For priority queue - lower priority value = higher priority
        return self.priority.value < other.priority.value

class AgentWorkload:
    def __init__(self, agent_id: str, max_capacity: int = 10):
        self.agent_id = agent_id
        self.max_capacity = max_capacity
        self.current_workload = []
        self.completed_items = []
        self.skills = []
        self.performance_metrics = {
            "velocity": 0,  # Story points per sprint
            "quality_score": 100,  # Based on bugs and reviews
            "reliability_score": 100  # Based on deadline adherence
        }
    
    def can_take_work(self, work_item: WorkItem) -> bool:
        """Check if agent can take on this work item"""
        # Check capacity
        current_load = sum(item.estimated_effort for item in self.current_workload)
        if current_load + work_item.estimated_effort > self.max_capacity:
            return False
        
        # Check skills
        required_skills = set(work_item.skills_required)
        agent_skills = set(self.skills)
        if not required_skills.issubset(agent_skills):
            return False
        
        return True
    
    def assign_work(self, work_item: WorkItem):
        """Assign work item to this agent"""
        work_item.assigned_to = self.agent_id
        work_item.assigned_at = datetime.now()
        work_item.status = WorkItemStatus.ASSIGNED
        self.current_workload.append(work_item)
    
    def complete_work(self, work_item_id: str):
        """Mark work item as completed"""
        for i, item in enumerate(self.current_workload):
            if item.id == work_item_id:
                item.status = WorkItemStatus.COMPLETED
                item.actual_completion = datetime.now()
                completed_item = self.current_workload.pop(i)
                self.completed_items.append(completed_item)
                return completed_item
        return None

class WorkQueueManager:
    def __init__(self):
        self.work_queue = []  # Priority queue
        self.work_items = {}  # Dict for fast lookup
        self.agents = {}  # Agent workload management
        self.assignment_history = []
        self.metrics = {
            "total_items": 0,
            "completed_items": 0,
            "average_completion_time": 0,
            "items_by_priority": {p.name: 0 for p in Priority},
            "items_by_type": {t.name: 0 for t in WorkItemType}
        }
        self.running = False
        self.assignment_thread = None
    
    def register_agent(self, agent_id: str, skills: List[str], max_capacity: int = 10):
        """Register an agent with their skills and capacity"""
        agent = AgentWorkload(agent_id, max_capacity)
        agent.skills = skills
        self.agents[agent_id] = agent
        print(f"Registered agent: {agent_id} with skills: {skills}")
    
    def add_work_item(self, work_item: WorkItem) -> bool:
        """Add a new work item to the queue"""
        try:
            # Add to priority queue
            heapq.heappush(self.work_queue, work_item)
            
            # Add to lookup dict
            self.work_items[work_item.id] = work_item
            
            # Update metrics
            self.metrics["total_items"] += 1
            self.metrics["items_by_priority"][work_item.priority.name] += 1
            self.metrics["items_by_type"][work_item.work_type.name] += 1
            
            print(f"Added work item: {work_item.id} - {work_item.title} ({work_item.priority.name})")
            return True
            
        except Exception as e:
            print(f"Error adding work item: {e}")
            return False
    
    def find_best_agent(self, work_item: WorkItem) -> Optional[str]:
        """Find the best agent for a work item based on skills and workload"""
        suitable_agents = []
        
        for agent_id, agent in self.agents.items():
            if agent.can_take_work(work_item):
                # Calculate score based on skill match and current workload
                skill_match = len(set(work_item.skills_required) & set(agent.skills))
                current_load = sum(item.estimated_effort for item in agent.current_workload)
                load_factor = 1 - (current_load / agent.max_capacity)
                
                score = skill_match * 10 + load_factor * 5 + agent.performance_metrics["quality_score"] / 20
                suitable_agents.append((agent_id, score))
        
        if suitable_agents:
            # Return agent with highest score
            return max(suitable_agents, key=lambda x: x[1])[0]
        
        return None
    
    def assign_work_automatically(self):
        """Automatically assign work items from queue to available agents"""
        while self.running:
            try:
                if self.work_queue:
                    # Get highest priority work item
                    work_item = heapq.heappop(self.work_queue)
                    
                    if work_item.status == WorkItemStatus.QUEUED:
                        # Find best agent
                        best_agent = self.find_best_agent(work_item)
                        
                        if best_agent:
                            # Assign work
                            self.agents[best_agent].assign_work(work_item)
                            self.assignment_history.append({
                                "work_item_id": work_item.id,
                                "agent_id": best_agent,
                                "assigned_at": datetime.now(),
                                "priority": work_item.priority.name
                            })
                            print(f"Assigned {work_item.id} to {best_agent}")
                        else:
                            # No available agent, put back in queue
                            heapq.heappush(self.work_queue, work_item)
                            print(f"No available agent for {work_item.id}, keeping in queue")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error in work assignment: {e}")
                time.sleep(10)
    
    def start_auto_assignment(self):
        """Start automatic work assignment in background"""
        if not self.running:
            self.running = True
            self.assignment_thread = threading.Thread(target=self.assign_work_automatically, daemon=True)
            self.assignment_thread.start()
            print("Started automatic work assignment")
    
    def stop_auto_assignment(self):
        """Stop automatic work assignment"""
        self.running = False
        if self.assignment_thread:
            self.assignment_thread.join()
        print("Stopped automatic work assignment")
    
    def update_work_progress(self, work_item_id: str, progress: int, status: WorkItemStatus = None):
        """Update progress on a work item"""
        if work_item_id in self.work_items:
            work_item = self.work_items[work_item_id]
            work_item.progress_percentage = progress
            
            if status:
                work_item.status = status
            
            print(f"Updated {work_item_id}: {progress}% complete")
            return True
        return False
    
    def complete_work_item(self, work_item_id: str, agent_id: str):
        """Mark a work item as completed"""
        if work_item_id in self.work_items and agent_id in self.agents:
            completed_item = self.agents[agent_id].complete_work(work_item_id)
            if completed_item:
                self.metrics["completed_items"] += 1
                
                # Calculate completion time
                if completed_item.assigned_at and completed_item.actual_completion:
                    completion_time = (completed_item.actual_completion - completed_item.assigned_at).total_seconds() / 3600
                    
                    # Update average completion time
                    total_completed = self.metrics["completed_items"]
                    current_avg = self.metrics["average_completion_time"]
                    self.metrics["average_completion_time"] = ((current_avg * (total_completed - 1)) + completion_time) / total_completed
                
                print(f"Completed work item: {work_item_id}")
                return True
        return False
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        return {
            "queued_items": len(self.work_queue),
            "total_items": len(self.work_items),
            "agents": {
                agent_id: {
                    "current_workload": len(agent.current_workload),
                    "capacity": agent.max_capacity,
                    "completed_items": len(agent.completed_items),
                    "skills": agent.skills
                }
                for agent_id, agent in self.agents.items()
            },
            "metrics": self.metrics
        }
    
    def get_agent_workload(self, agent_id: str) -> Optional[Dict]:
        """Get workload details for specific agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            return {
                "agent_id": agent_id,
                "current_workload": [asdict(item) for item in agent.current_workload],
                "completed_items": [asdict(item) for item in agent.completed_items],
                "capacity_used": sum(item.estimated_effort for item in agent.current_workload),
                "max_capacity": agent.max_capacity,
                "performance_metrics": agent.performance_metrics
            }
        return None

# Convenience functions for creating work items
def create_github_issue_work_item(issue_id: str, title: str, description: str, labels: List[str], repo: str) -> WorkItem:
    """Create work item from GitHub issue"""
    
    # Determine work type from labels
    work_type = WorkItemType.GITHUB_ISSUE
    if "bug" in labels:
        work_type = WorkItemType.BUG_FIX
    elif "feature" in labels:
        work_type = WorkItemType.FEATURE_REQUEST
    elif "documentation" in labels:
        work_type = WorkItemType.DOCUMENTATION
    
    # Determine priority from labels
    priority = Priority.P2_MEDIUM
    if "critical" in labels or "P0" in labels:
        priority = Priority.P0_CRITICAL
    elif "high" in labels or "P1" in labels:
        priority = Priority.P1_HIGH
    elif "low" in labels or "P3" in labels:
        priority = Priority.P3_LOW
    
    # Determine skills required
    skills_required = []
    if "backend" in labels:
        skills_required.extend(["python", "fastapi", "postgresql"])
    if "frontend" in labels:
        skills_required.extend(["react", "typescript", "css"])
    if "devops" in labels:
        skills_required.extend(["docker", "github-actions", "aws"])
    
    # Estimate effort (simple heuristic)
    effort = 3  # Default medium effort
    if "small" in labels:
        effort = 1
    elif "large" in labels:
        effort = 8
    
    return WorkItem(
        id=f"github_{issue_id}",
        title=title,
        description=description,
        work_type=work_type,
        priority=priority,
        estimated_effort=effort,
        skills_required=skills_required,
        created_at=datetime.now(),
        github_issue_id=issue_id,
        github_repo=repo
    )

# Global work queue manager
work_queue_manager = WorkQueueManager()

if __name__ == "__main__":
    # Test the work queue system
    wqm = WorkQueueManager()
    
    # Register some agents
    wqm.register_agent("backend_dev_001", ["python", "fastapi", "postgresql", "redis"], 8)
    wqm.register_agent("frontend_dev_001", ["react", "typescript", "css", "tailwind"], 6)
    wqm.register_agent("devops_001", ["docker", "github-actions", "aws", "terraform"], 5)
    
    # Create some test work items
    work1 = create_github_issue_work_item("123", "Fix user login bug", "Users can't login", ["bug", "backend", "high"], "myrepo")
    work2 = create_github_issue_work_item("124", "Add dark mode", "Implement dark theme", ["feature", "frontend", "medium"], "myrepo")
    
    # Add to queue
    wqm.add_work_item(work1)
    wqm.add_work_item(work2)
    
    # Start auto-assignment
    wqm.start_auto_assignment()
    
    # Check status
    time.sleep(2)
    status = wqm.get_queue_status()
    print(f"Queue status: {json.dumps(status, indent=2, default=str)}")
    
    # Stop
    wqm.stop_auto_assignment()
