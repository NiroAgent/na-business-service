#!/usr/bin/env python3
"""
AI Agent Template - Use this as a base for all specialized agents
Copy this file and customize for each specific agent type
"""

import json
import logging
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseAIAgent:
    """Base class for all AI agents"""
    
    def __init__(self, agent_type: str, capabilities: List[str]):
        # Core agent properties
        self.agent_id = f"ai-{agent_type}-{int(time.time())}"
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = "initializing"
        self.current_task = None
        
        # AWS BACKEND PROCESSING POLICY - MANDATORY FOR ALL AGENTS
        self.aws_backend_policy = {
            "priority_order": [
                "AWS Lambda (serverless functions)",
                "AWS Fargate Tasks (Batch/Step Functions)", 
                "AWS Fargate Container Service (ECS/EKS)",
                "EC2 (requires justification)"
            ],
            "objectives": [
                "Scale to zero when idle",
                "Infinite auto-scaling capability", 
                "Cost optimization - pay for usage only",
                "Minimal infrastructure management"
            ],
            "default_choice": "AWS Lambda",
            "justification_required_for": ["EC2", "Always-on services"]
        }
        
        # Performance tracking
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.start_time = datetime.now()
        
        # Initialize integrations
        self.orchestrator = None
        self.work_queue = []
        
        # Initialize the agent
        self.initialize()
        
        logging.info(f"🤖 {self.agent_type} Agent initialized: {self.agent_id}")
    
    def initialize(self):
        """Initialize agent-specific components"""
        try:
            # Import orchestrator
            sys.path.append(str(Path(__file__).parent))
            from agent_orchestration_system import get_orchestrator
            self.orchestrator = get_orchestrator()
            
            # Register with orchestrator
            if self.orchestrator:
                self.orchestrator.register_agent(
                    agent_id=self.agent_id,
                    agent_type=self.agent_type,
                    capabilities=self.capabilities
                )
                self.status = "active"
                logging.info(f"✅ Registered with orchestrator: {self.agent_id}")
            else:
                logging.warning("⚠️ Orchestrator not available - running in standalone mode")
                self.status = "standalone"
                
        except Exception as e:
            logging.error(f"Failed to initialize agent {self.agent_id}: {e}")
            self.status = "error"
    
    def send_heartbeat(self):
        """Send heartbeat to orchestrator"""
        if self.orchestrator:
            from agent_orchestration_system import AgentStatus
            status_map = {
                "active": AgentStatus.ACTIVE,
                "busy": AgentStatus.BUSY,
                "idle": AgentStatus.IDLE,
                "error": AgentStatus.ERROR
            }
            
            self.orchestrator.update_agent_status(
                agent_id=self.agent_id,
                status=status_map.get(self.status, AgentStatus.ACTIVE),
                current_task=self.current_task
            )
    
    def get_assigned_work(self) -> List[Dict[str, Any]]:
        """Get work items assigned to this agent"""
        if not self.orchestrator:
            return []
        
        work_status = self.orchestrator.get_work_queue_status()
        assigned_work = [
            item for item in work_status["work_items"]
            if item.get("assigned_agent") == self.agent_id and item.get("status") == "assigned"
        ]
        
        return assigned_work
    
    def complete_task(self, item_id: str, result: Dict[str, Any] = None):
        """Mark a task as completed"""
        if self.orchestrator:
            self.orchestrator.complete_work_item(item_id, self.agent_id, result)
            self.tasks_completed += 1
            self.current_task = None
            self.status = "idle"
            logging.info(f"✅ Task completed: {item_id}")
    
    def fail_task(self, item_id: str, error: str):
        """Mark a task as failed"""
        if self.orchestrator:
            self.orchestrator.fail_work_item(item_id, self.agent_id, error)
            self.tasks_failed += 1
            self.current_task = None
            self.status = "idle"
            logging.error(f"❌ Task failed: {item_id} - {error}")
    
    def process_work_item(self, work_item: Dict[str, Any]) -> bool:
        """Process a single work item - OVERRIDE THIS METHOD"""
        # This is the main method that each specialized agent should override
        item_id = work_item["item_id"]
        title = work_item["title"]
        description = work_item["description"]
        
        logging.info(f"🔄 Processing: {title}")
        
        try:
            # Update status
            self.status = "busy"
            self.current_task = title
            
            # Call the specialized processing method
            result = self.handle_specific_task(work_item)
            
            # Mark as completed
            self.complete_task(item_id, result)
            return True
            
        except Exception as e:
            self.fail_task(item_id, str(e))
            return False
    
    def handle_specific_task(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent-specific task processing - MUST BE OVERRIDDEN"""
        raise NotImplementedError("Subclasses must implement handle_specific_task method")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        uptime = datetime.now() - self.start_time
        success_rate = (
            self.tasks_completed / (self.tasks_completed + self.tasks_failed) * 100
            if (self.tasks_completed + self.tasks_failed) > 0 else 100.0
        )
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "current_task": self.current_task,
            "capabilities": self.capabilities,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "success_rate": round(success_rate, 2),
            "uptime_seconds": int(uptime.total_seconds()),
            "aws_policy_compliant": True
        }
    
    async def run(self):
        """Main agent loop"""
        logging.info(f"🚀 {self.agent_type} Agent starting main loop...")
        
        while True:
            try:
                # Send heartbeat
                self.send_heartbeat()
                
                # Check for assigned work
                if self.status in ["active", "idle"]:
                    assigned_work = self.get_assigned_work()
                    
                    for work_item in assigned_work:
                        success = self.process_work_item(work_item)
                        if success:
                            logging.info(f"✅ Successfully processed: {work_item['title']}")
                        else:
                            logging.error(f"❌ Failed to process: {work_item['title']}")
                
                # Sleep for 10 seconds
                await asyncio.sleep(10)
                
            except KeyboardInterrupt:
                logging.info(f"🛑 {self.agent_type} Agent stopping...")
                break
            except Exception as e:
                logging.error(f"Error in {self.agent_type} agent loop: {e}")
                self.status = "error"
                await asyncio.sleep(5)


# EXAMPLE: AI Manager Agent Implementation
class AIManagerAgent(BaseAIAgent):
    """AI Manager Agent - Executive oversight and strategic planning"""
    
    def __init__(self):
        capabilities = [
            "strategic_planning",
            "resource_allocation", 
            "decision_making",
            "coordination",
            "performance_monitoring",
            "escalation_handling"
        ]
        
        super().__init__("manager", capabilities)
        
        # Manager-specific properties
        self.strategic_goals = []
        self.resource_allocations = {}
        self.escalations = []
        
        # AWS serverless-first strategy
        self.management_strategy = {
            "decision_processing": "AWS Lambda for quick decisions",
            "complex_planning": "Step Functions for multi-step planning",
            "monitoring": "Lambda for real-time oversight",
            "reporting": "Fargate Batch for comprehensive reports"
        }
    
    def handle_specific_task(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle manager-specific tasks"""
        task_type = work_item.get("item_type", "")
        title = work_item["title"]
        description = work_item["description"]
        
        logging.info(f"🎯 Manager processing: {task_type} - {title}")
        
        if "strategic" in task_type.lower():
            return self.handle_strategic_planning(work_item)
        elif "resource" in task_type.lower():
            return self.handle_resource_allocation(work_item)
        elif "escalation" in task_type.lower():
            return self.handle_escalation(work_item)
        elif "decision" in task_type.lower():
            return self.handle_decision_making(work_item)
        else:
            return self.handle_general_management(work_item)
    
    def handle_strategic_planning(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle strategic planning tasks"""
        # Simulate strategic planning
        strategy = {
            "objective": work_item["description"],
            "timeline": "Q4 2025",
            "resources_required": ["development_team", "marketing_team"],
            "success_metrics": ["user_growth", "revenue_increase"],
            "risk_assessment": "medium",
            "aws_approach": "Lambda-first for all new services"
        }
        
        return {
            "strategy": strategy,
            "status": "strategic_plan_created",
            "next_actions": ["assign_to_project_manager", "allocate_resources"]
        }
    
    def handle_resource_allocation(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource allocation decisions"""
        allocation = {
            "resource_type": "agent_assignments",
            "allocation": {
                "development": 4,  # architect, developer, qa, devops
                "business": 4,     # marketing, sales, support, success
                "operations": 4    # analytics, finance, operations, security
            },
            "aws_resources": {
                "compute": "Lambda + Fargate as needed",
                "storage": "S3 + DynamoDB", 
                "monitoring": "CloudWatch + Lambda"
            }
        }
        
        return {
            "allocation": allocation,
            "status": "resources_allocated",
            "cost_estimate": "serverless_optimized"
        }
    
    def handle_escalation(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle escalated issues"""
        escalation_response = {
            "escalation_id": work_item["item_id"],
            "priority": "high",
            "action_plan": [
                "assess_impact",
                "assign_senior_agents", 
                "monitor_progress",
                "report_resolution"
            ],
            "timeline": "within_24_hours"
        }
        
        return {
            "escalation_response": escalation_response,
            "status": "escalation_handled"
        }
    
    def handle_decision_making(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle decision-making tasks"""
        decision = {
            "decision_context": work_item["description"],
            "decision": "approved",
            "rationale": "Aligns with serverless-first strategy and business objectives",
            "implementation_approach": "AWS Lambda-based microservices",
            "timeline": "2_weeks"
        }
        
        return {
            "decision": decision,
            "status": "decision_made",
            "next_steps": ["communicate_to_teams", "track_implementation"]
        }
    
    def handle_general_management(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general management tasks"""
        return {
            "action": "general_management_task_processed",
            "status": "completed",
            "aws_approach": "serverless_optimization_applied"
        }


# Template for other agents - Opus should use this pattern
class AIAgentTemplate(BaseAIAgent):
    """Template for creating new specialized agents"""
    
    def __init__(self, agent_type: str, capabilities: List[str]):
        super().__init__(agent_type, capabilities)
        
        # Add agent-specific properties here
        self.specialized_data = {}
        
        # Add AWS serverless-specific configurations
        self.serverless_config = {
            "primary_compute": "AWS Lambda",
            "data_storage": "DynamoDB + S3",
            "messaging": "SQS + SNS",
            "monitoring": "CloudWatch"
        }
    
    def handle_specific_task(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method for each agent type"""
        # Example implementation
        task_type = work_item.get("item_type", "")
        
        # Process based on task type
        if "analysis" in task_type.lower():
            return self.handle_analysis_task(work_item)
        elif "creation" in task_type.lower():
            return self.handle_creation_task(work_item)
        else:
            return self.handle_default_task(work_item)
    
    def handle_analysis_task(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analysis-type tasks"""
        return {
            "analysis_result": "completed",
            "methodology": "serverless_analysis",
            "status": "success"
        }
    
    def handle_creation_task(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle creation-type tasks"""
        return {
            "creation_result": "artifact_created",
            "approach": "serverless_creation",
            "status": "success"
        }
    
    def handle_default_task(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle default tasks"""
        return {
            "result": "task_processed",
            "status": "completed"
        }


if __name__ == "__main__":
    import asyncio
    
    print("\n" + "="*80)
    print("🤖 AI AGENT TEMPLATE & EXAMPLE")
    print("="*80)
    print("This file contains the base template for all AI agents")
    print("Example: AI Manager Agent implementation included")
    print("AWS Serverless-First Policy: Enabled")
    print("="*80 + "\n")
    
    # Run the example manager agent
    manager = AIManagerAgent()
    
    try:
        asyncio.run(manager.run())
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped by user")
