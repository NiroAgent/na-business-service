#!/usr/bin/env python3
"""
Team Communication Protocol for AI Development Team
Standardizes messaging between specialized development agents
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class MessageType(Enum):
    WORK_ASSIGNMENT = "work_assignment"
    STATUS_UPDATE = "status_update"
    CODE_REVIEW_REQUEST = "code_review_request"
    DEPLOYMENT_REQUEST = "deployment_request"
    ESCALATION = "escalation"
    COMPLETION = "completion"
    BLOCKED = "blocked"

class AgentRole(Enum):
    PRODUCT_MANAGER = "product_manager"
    SCRUM_MASTER = "scrum_master"
    BACKEND_DEVELOPER = "backend_developer"
    FRONTEND_DEVELOPER = "frontend_developer"
    DEVOPS_ENGINEER = "devops_engineer"
    QA_ENGINEER = "qa_engineer"
    TECHNICAL_WRITER = "technical_writer"
    CODE_REVIEWER = "code_reviewer"

@dataclass
class TeamMessage:
    id: str
    timestamp: datetime
    from_agent: str
    to_agent: str
    message_type: MessageType
    priority: int  # 1-5, 1 being highest
    subject: str
    content: Dict
    requires_response: bool = False
    deadline: Optional[datetime] = None
    thread_id: Optional[str] = None

class TeamCommunicationHub:
    def __init__(self):
        self.message_queue = {}
        self.agent_registry = {}
        self.active_threads = {}
        self.message_history = []
        self.running = False
        
    def register_agent(self, agent_id: str, role: AgentRole, capabilities: List[str]):
        """Register a new agent with the communication hub"""
        self.agent_registry[agent_id] = {
            "role": role,
            "capabilities": capabilities,
            "status": "active",
            "last_seen": datetime.now(),
            "message_queue": []
        }
        print(f"Registered agent: {agent_id} ({role.value})")
    
    def send_message(self, message: TeamMessage) -> bool:
        """Send a message to another agent"""
        try:
            # Validate recipient exists
            if message.to_agent not in self.agent_registry:
                print(f"Error: Unknown recipient {message.to_agent}")
                return False
            
            # Add to recipient's queue
            self.agent_registry[message.to_agent]["message_queue"].append(message)
            
            # Add to history
            self.message_history.append(message)
            
            # Handle threading
            if message.thread_id:
                if message.thread_id not in self.active_threads:
                    self.active_threads[message.thread_id] = []
                self.active_threads[message.thread_id].append(message)
            
            print(f"Message sent: {message.from_agent} → {message.to_agent}: {message.subject}")
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_messages(self, agent_id: str) -> List[TeamMessage]:
        """Get pending messages for an agent"""
        if agent_id not in self.agent_registry:
            return []
        
        messages = self.agent_registry[agent_id]["message_queue"]
        self.agent_registry[agent_id]["message_queue"] = []  # Clear queue
        self.agent_registry[agent_id]["last_seen"] = datetime.now()
        
        return messages
    
    def find_agent_by_capability(self, capability: str) -> List[str]:
        """Find agents with specific capabilities"""
        matching_agents = []
        for agent_id, agent_info in self.agent_registry.items():
            if capability in agent_info["capabilities"]:
                matching_agents.append(agent_id)
        return matching_agents
    
    def broadcast_to_role(self, role: AgentRole, message: TeamMessage) -> int:
        """Broadcast message to all agents with specific role"""
        count = 0
        for agent_id, agent_info in self.agent_registry.items():
            if agent_info["role"] == role:
                message.to_agent = agent_id
                if self.send_message(message):
                    count += 1
        return count
    
    def get_team_status(self) -> Dict:
        """Get overall team status"""
        status = {
            "total_agents": len(self.agent_registry),
            "active_agents": sum(1 for a in self.agent_registry.values() if a["status"] == "active"),
            "pending_messages": sum(len(a["message_queue"]) for a in self.agent_registry.values()),
            "active_threads": len(self.active_threads),
            "agents_by_role": {}
        }
        
        for agent_id, agent_info in self.agent_registry.items():
            role = agent_info["role"].value
            if role not in status["agents_by_role"]:
                status["agents_by_role"][role] = []
            status["agents_by_role"][role].append({
                "id": agent_id,
                "status": agent_info["status"],
                "pending_messages": len(agent_info["message_queue"]),
                "last_seen": agent_info["last_seen"].isoformat()
            })
        
        return status

# Convenience functions for common message types
def create_work_assignment(from_agent: str, to_agent: str, issue_id: str, description: str, priority: int = 3):
    """Create a work assignment message"""
    return TeamMessage(
        id=f"work_{int(time.time())}_{issue_id}",
        timestamp=datetime.now(),
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.WORK_ASSIGNMENT,
        priority=priority,
        subject=f"Work Assignment: Issue #{issue_id}",
        content={
            "issue_id": issue_id,
            "description": description,
            "estimated_effort": "TBD",
            "dependencies": [],
            "acceptance_criteria": []
        },
        requires_response=True
    )

def create_code_review_request(from_agent: str, to_agent: str, pr_number: str, changes_summary: str):
    """Create a code review request"""
    return TeamMessage(
        id=f"review_{int(time.time())}_{pr_number}",
        timestamp=datetime.now(),
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.CODE_REVIEW_REQUEST,
        priority=2,
        subject=f"Code Review Request: PR #{pr_number}",
        content={
            "pr_number": pr_number,
            "changes_summary": changes_summary,
            "files_changed": [],
            "complexity": "medium",
            "urgency": "normal"
        },
        requires_response=True
    )

def create_status_update(from_agent: str, to_agent: str, work_item: str, status: str, progress: int):
    """Create a status update message"""
    return TeamMessage(
        id=f"status_{int(time.time())}",
        timestamp=datetime.now(),
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.STATUS_UPDATE,
        priority=4,
        subject=f"Status Update: {work_item}",
        content={
            "work_item": work_item,
            "status": status,
            "progress_percentage": progress,
            "blockers": [],
            "next_steps": []
        }
    )

# Global communication hub instance
communication_hub = TeamCommunicationHub()

if __name__ == "__main__":
    # Test the communication system
    hub = TeamCommunicationHub()
    
    # Register some test agents
    hub.register_agent("pm_001", AgentRole.PRODUCT_MANAGER, ["roadmap", "prioritization", "stakeholder_comms"])
    hub.register_agent("dev_backend_001", AgentRole.BACKEND_DEVELOPER, ["python", "fastapi", "postgresql", "redis"])
    hub.register_agent("dev_frontend_001", AgentRole.FRONTEND_DEVELOPER, ["react", "typescript", "tailwind"])
    
    # Send a test message
    work_msg = create_work_assignment("pm_001", "dev_backend_001", "123", "Implement user authentication API")
    hub.send_message(work_msg)
    
    # Check messages
    messages = hub.get_messages("dev_backend_001")
    print(f"Backend developer has {len(messages)} messages")
    
    # Get team status
    status = hub.get_team_status()
    print(f"Team status: {json.dumps(status, indent=2, default=str)}")
