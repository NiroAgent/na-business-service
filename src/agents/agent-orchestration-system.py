#!/usr/bin/env python3
"""
AI Agent Orchestration System - Master Coordinator
Manages all specialized AI agents and ensures proper coordination
"""

import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AgentOrchestrator')

class AgentStatus(Enum):
    """Agent status states"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class Priority(Enum):
    """Work item priorities"""
    CRITICAL = "P0"
    HIGH = "P1"
    MEDIUM = "P2"
    LOW = "P3"
    BACKLOG = "P4"

@dataclass
class AgentInfo:
    """Information about a registered agent"""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    status: AgentStatus
    last_heartbeat: datetime
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    uptime_start: datetime = None
    
    def to_dict(self):
        return {
            **asdict(self),
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'uptime_start': self.uptime_start.isoformat() if self.uptime_start else None,
            'status': self.status.value
        }

@dataclass
class WorkItem:
    """Work item for agent processing"""
    item_id: str
    title: str
    description: str
    item_type: str
    priority: Priority
    assigned_agent: Optional[str] = None
    status: str = "pending"
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        return {
            **asdict(self),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'priority': self.priority.value
        }

class AgentOrchestrator:
    """Master coordinator for all AI agents"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.work_queue: List[WorkItem] = []
        self.agent_capabilities: Dict[str, List[str]] = {
            # Development Team
            "ai-architect": ["system_architecture", "api_design", "database_design", "technology_selection"],
            "ai-developer": ["code_generation", "testing", "debugging", "optimization"],
            "ai-qa": ["testing", "quality_assurance", "performance_testing", "security_testing"],
            "ai-devops": ["deployment", "infrastructure", "monitoring", "ci_cd"],
            
            # Management Team
            "ai-manager": ["strategic_planning", "resource_allocation", "decision_making", "coordination"],
            "ai-project-manager": ["project_planning", "timeline_management", "resource_scheduling", "reporting"],
            
            # Business Team
            "ai-marketing": ["content_creation", "seo", "social_media", "campaigns", "brand_management"],
            "ai-sales": ["lead_generation", "sales_automation", "crm", "revenue_optimization"],
            "ai-support": ["customer_service", "ticket_management", "knowledge_base", "user_training"],
            "ai-customer-success": ["retention", "expansion", "satisfaction", "lifecycle_management"],
            
            # Intelligence Team
            "ai-analytics": ["data_analysis", "reporting", "forecasting", "business_intelligence"],
            "ai-finance": ["financial_planning", "budgeting", "compliance", "reporting"],
            
            # Operations Team
            "ai-operations": ["monitoring", "maintenance", "optimization", "incident_response"],
            "ai-security": ["threat_detection", "compliance", "vulnerability_scanning", "access_control"]
        }
        
        # AWS Backend Processing Policy Integration
        self.aws_backend_policy = {
            "priority_order": [
                "AWS Lambda (serverless functions)",
                "AWS Fargate Tasks (Batch/Step Functions)", 
                "AWS Fargate Container Service (ECS/EKS)",
                "EC2 (requires justification)"
            ],
            "orchestration_strategy": {
                "agent_coordination": "Lambda functions for lightweight coordination",
                "work_distribution": "Step Functions for complex workflows",
                "monitoring": "Lambda for real-time health checks",
                "scaling": "Auto-scale based on work queue depth"
            }
        }
        
        logger.info("🎯 Agent Orchestrator initialized with AWS Serverless-First Policy")
    
    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str]) -> bool:
        """Register a new agent with the orchestrator"""
        try:
            # Validate agent type
            if agent_type.replace("-", "_") not in self.agent_capabilities:
                logger.warning(f"Unknown agent type: {agent_type}")
            
            # Create agent info
            agent_info = AgentInfo(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities=capabilities,
                status=AgentStatus.ACTIVE,
                last_heartbeat=datetime.now(),
                uptime_start=datetime.now()
            )
            
            self.agents[agent_id] = agent_info
            logger.info(f"✅ Agent registered: {agent_id} ({agent_type})")
            
            # Auto-assign any pending work
            self._auto_assign_work()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    def update_agent_status(self, agent_id: str, status: AgentStatus, current_task: Optional[str] = None):
        """Update agent status and current task"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].last_heartbeat = datetime.now()
            if current_task:
                self.agents[agent_id].current_task = current_task
            logger.info(f"📊 Agent {agent_id} status: {status.value}")
        else:
            logger.warning(f"Unknown agent {agent_id} trying to update status")
    
    def add_work_item(self, title: str, description: str, item_type: str, 
                     priority: Priority = Priority.MEDIUM, metadata: Dict[str, Any] = None) -> str:
        """Add a new work item to the queue"""
        item_id = f"work-{int(time.time())}-{len(self.work_queue)}"
        
        work_item = WorkItem(
            item_id=item_id,
            title=title,
            description=description,
            item_type=item_type,
            priority=priority,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        # Insert based on priority
        self._insert_by_priority(work_item)
        
        logger.info(f"📋 Work item added: {title} ({priority.value})")
        
        # Try to assign immediately
        self._auto_assign_work()
        
        return item_id
    
    def _insert_by_priority(self, work_item: WorkItem):
        """Insert work item in queue based on priority"""
        priority_order = [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW, Priority.BACKLOG]
        
        for i, existing_item in enumerate(self.work_queue):
            if priority_order.index(work_item.priority) < priority_order.index(existing_item.priority):
                self.work_queue.insert(i, work_item)
                return
        
        # If not inserted, append to end
        self.work_queue.append(work_item)
    
    def _auto_assign_work(self):
        """Automatically assign work to available agents"""
        available_agents = {
            agent_id: agent for agent_id, agent in self.agents.items()
            if agent.status in [AgentStatus.ACTIVE, AgentStatus.IDLE]
        }
        
        for work_item in self.work_queue:
            if work_item.assigned_agent is None:
                # Find best agent for this work
                best_agent = self._find_best_agent(work_item, available_agents)
                if best_agent:
                    work_item.assigned_agent = best_agent.agent_id
                    work_item.status = "assigned"
                    work_item.updated_at = datetime.now()
                    
                    # Update agent status
                    best_agent.status = AgentStatus.BUSY
                    best_agent.current_task = work_item.title
                    
                    # Remove from available agents
                    available_agents.pop(best_agent.agent_id)
                    
                    logger.info(f"🎯 Assigned '{work_item.title}' to {best_agent.agent_id}")
    
    def _find_best_agent(self, work_item: WorkItem, available_agents: Dict[str, AgentInfo]) -> Optional[AgentInfo]:
        """Find the best agent for a work item based on capabilities"""
        best_agent = None
        best_score = 0
        
        for agent in available_agents.values():
            score = self._calculate_agent_score(work_item, agent)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent
    
    def _calculate_agent_score(self, work_item: WorkItem, agent: AgentInfo) -> int:
        """Calculate how well an agent matches a work item"""
        score = 0
        
        # Check if agent type matches work item type
        if work_item.item_type in agent.agent_type:
            score += 10
        
        # Check capability overlap
        work_keywords = work_item.description.lower().split()
        for capability in agent.capabilities:
            if capability.lower() in work_keywords:
                score += 5
        
        # Prefer agents with fewer current tasks
        score -= agent.tasks_completed  # Load balancing
        
        # Boost score for agents with good track record
        if agent.tasks_completed > 0:
            success_rate = agent.tasks_completed / (agent.tasks_completed + agent.tasks_failed)
            score += int(success_rate * 10)
        
        return score
    
    def complete_work_item(self, item_id: str, agent_id: str, result: Dict[str, Any] = None):
        """Mark a work item as completed"""
        for work_item in self.work_queue:
            if work_item.item_id == item_id and work_item.assigned_agent == agent_id:
                work_item.status = "completed"
                work_item.updated_at = datetime.now()
                if result:
                    work_item.metadata.update({"result": result})
                
                # Update agent stats
                if agent_id in self.agents:
                    self.agents[agent_id].tasks_completed += 1
                    self.agents[agent_id].status = AgentStatus.IDLE
                    self.agents[agent_id].current_task = None
                
                logger.info(f"✅ Work item completed: {work_item.title} by {agent_id}")
                
                # Try to assign more work
                self._auto_assign_work()
                return True
        
        logger.warning(f"Work item {item_id} not found or not assigned to {agent_id}")
        return False
    
    def fail_work_item(self, item_id: str, agent_id: str, error: str):
        """Mark a work item as failed"""
        for work_item in self.work_queue:
            if work_item.item_id == item_id and work_item.assigned_agent == agent_id:
                work_item.status = "failed"
                work_item.updated_at = datetime.now()
                work_item.metadata.update({"error": error})
                
                # Update agent stats
                if agent_id in self.agents:
                    self.agents[agent_id].tasks_failed += 1
                    self.agents[agent_id].status = AgentStatus.IDLE
                    self.agents[agent_id].current_task = None
                
                logger.error(f"❌ Work item failed: {work_item.title} by {agent_id} - {error}")
                
                # Re-queue for retry if appropriate
                if work_item.priority in [Priority.CRITICAL, Priority.HIGH]:
                    work_item.assigned_agent = None
                    work_item.status = "pending"
                    logger.info(f"🔄 Re-queuing failed high-priority item: {work_item.title}")
                
                self._auto_assign_work()
                return True
        
        logger.warning(f"Work item {item_id} not found or not assigned to {agent_id}")
        return False
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status == AgentStatus.ACTIVE]),
            "busy_agents": len([a for a in self.agents.values() if a.status == AgentStatus.BUSY]),
            "offline_agents": len([a for a in self.agents.values() if a.status == AgentStatus.OFFLINE]),
            "agents": {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()}
        }
    
    def get_work_queue_status(self) -> Dict[str, Any]:
        """Get status of work queue"""
        return {
            "total_items": len(self.work_queue),
            "pending_items": len([w for w in self.work_queue if w.status == "pending"]),
            "assigned_items": len([w for w in self.work_queue if w.status == "assigned"]),
            "completed_items": len([w for w in self.work_queue if w.status == "completed"]),
            "failed_items": len([w for w in self.work_queue if w.status == "failed"]),
            "work_items": [item.to_dict() for item in self.work_queue]
        }
    
    def health_check(self):
        """Perform health check on all agents"""
        current_time = datetime.now()
        offline_threshold = timedelta(minutes=5)
        
        for agent_id, agent in self.agents.items():
            if current_time - agent.last_heartbeat > offline_threshold:
                if agent.status != AgentStatus.OFFLINE:
                    logger.warning(f"🚨 Agent {agent_id} appears offline - no heartbeat for {current_time - agent.last_heartbeat}")
                    agent.status = AgentStatus.OFFLINE
                    
                    # Reassign any work items
                    for work_item in self.work_queue:
                        if work_item.assigned_agent == agent_id and work_item.status == "assigned":
                            work_item.assigned_agent = None
                            work_item.status = "pending"
                            logger.info(f"🔄 Re-queuing work from offline agent: {work_item.title}")
        
        # Try to assign any unassigned work
        self._auto_assign_work()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for dashboard"""
        return {
            "timestamp": datetime.now().isoformat(),
            "agents": self.get_agent_status(),
            "work_queue": self.get_work_queue_status(),
            "aws_policy": self.aws_backend_policy,
            "system_health": {
                "total_tasks_completed": sum(agent.tasks_completed for agent in self.agents.values()),
                "total_tasks_failed": sum(agent.tasks_failed for agent in self.agents.values()),
                "average_success_rate": self._calculate_average_success_rate(),
                "queue_depth": len([w for w in self.work_queue if w.status == "pending"]),
                "agents_online": len([a for a in self.agents.values() if a.status != AgentStatus.OFFLINE])
            }
        }
    
    def _calculate_average_success_rate(self) -> float:
        """Calculate average success rate across all agents"""
        total_completed = sum(agent.tasks_completed for agent in self.agents.values())
        total_failed = sum(agent.tasks_failed for agent in self.agents.values())
        
        if total_completed + total_failed == 0:
            return 100.0
        
        return (total_completed / (total_completed + total_failed)) * 100
    
    async def run(self):
        """Main orchestrator loop"""
        logger.info("🚀 Agent Orchestrator starting...")
        
        while True:
            try:
                # Perform health checks
                self.health_check()
                
                # Log status every 30 seconds
                logger.info(f"📊 Status: {len(self.agents)} agents, {len(self.work_queue)} work items")
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("🛑 Orchestrator stopping...")
                break
            except Exception as e:
                logger.error(f"Error in orchestrator loop: {e}")
                await asyncio.sleep(5)

# Global orchestrator instance
orchestrator = AgentOrchestrator()

def get_orchestrator():
    """Get the global orchestrator instance"""
    return orchestrator

if __name__ == "__main__":
    import asyncio
    
    print("\n" + "="*80)
    print("🎯 AI AGENT ORCHESTRATION SYSTEM")
    print("="*80)
    print("Master coordinator for all specialized AI agents")
    print("AWS Serverless-First Policy Enabled")
    print("Ready to coordinate autonomous business operations")
    print("="*80 + "\n")
    
    # Run the orchestrator
    asyncio.run(orchestrator.run())
