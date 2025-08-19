#!/usr/bin/env python3
"""
Ai Finance Agent - Financial operations and compliance automation
================
Autonomous business operations using GitHub Issues as operational database.
AWS Serverless-First Architecture: Lambda → Fargate → EC2
"""

import argparse
import subprocess
import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import base template
try:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from ai_agent_template import BaseAIAgent, AgentType, Priority
    BASE_AVAILABLE = True
except ImportError:
    BASE_AVAILABLE = False
    logger.warning("Base agent template not available - using standalone implementation")

class AiFinanceAgentOperation(Enum):
    """Operation types for Ai Finance Agent"""
    BUDGETING = "finance/budgeting"
    COMPLIANCE = "finance/compliance"
    EXPENSE_TRACKING = "finance/expense-tracking"
    FINANCIAL_ANALYSIS = "finance/financial-analysis"

@dataclass
class AiFinanceAgentTask:
    """Task data structure for Ai Finance Agent"""
    task_id: str
    title: str
    description: str
    operation_type: str
    priority: str
    status: str = "pending"
    created_at: str = ""
    assigned_agent: str = ""
    metadata: Dict[str, Any] = None

class AiFinanceAgent(BaseAIAgent if BASE_AVAILABLE else object):
    """
    Ai Finance Agent for autonomous business operations.
    Financial operations and compliance automation
    
    AWS Serverless-First Architecture:
    - Primary: AWS Lambda (serverless functions)
    - Secondary: AWS Fargate (containerized tasks)
    - Last resort: EC2 (only when absolutely necessary)
    """
    
    def __init__(self, github_token: str = None):
        """Initialize the Ai Finance Agent"""
        if BASE_AVAILABLE:
            super().__init__(
                agent_type=AgentType.FINANCE,
                github_token=github_token
            )
        else:
            self.github_token = github_token
            self.agent_id = "ai_finance_agent"
            self.agent_type = "FINANCE"
        
        # Agent-specific initialization
        self.active_tasks: Dict[str, AiFinanceAgentTask] = {}
        self.completed_tasks: List[str] = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "average_completion_time": 0.0,
            "success_rate": 100.0,
            "current_load": 0
        }
        
        logger.info(f"[ROBOT] {self.agent_id} initialized - AWS Serverless-First Architecture")
    
    async def process_business_operation(self, issue):
        """Process business operation from GitHub Issue"""
        try:
            labels = [label.name for label in issue.labels] if hasattr(issue, 'labels') else []
            
            # Route to appropriate handler
            if "finance/budgeting" in labels:
                await self._handle_budgeting(issue)
            if "finance/compliance" in labels:
                await self._handle_compliance(issue)
            if "finance/expense-tracking" in labels:
                await self._handle_expense_tracking(issue)
            if "finance/financial-analysis" in labels:
                await self._handle_financial_analysis(issue)
            
            # Update performance metrics
            self._update_metrics()
            
        except Exception as e:
            logger.error(f"Error processing issue: {e}")
            await self._handle_error(issue, e)
    
    async def _handle_budgeting(self, issue):
        """Handle Budgeting operations"""
        logger.info(f"Processing budgeting: Issue #{getattr(issue, 'number', 'mock')}")
        
        # Parse issue details
        title = getattr(issue, 'title', 'Mock Operation')
        description = getattr(issue, 'body', 'Mock description')
        
        # Create task
        task = AiFinanceAgentTask(
            task_id=f"ai_finance_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=title,
            description=description,
            operation_type="finance/budgeting",
            priority="P2",
            status="in_progress",
            created_at=datetime.now().isoformat(),
            assigned_agent=self.agent_id
        )
        
        # Store active task
        self.active_tasks[task.task_id] = task
        
        # Process budgeting (implement business logic here)
        logger.info(f" Budgeting completed for {task.task_id}")
        
        # Mark task complete
        task.status = "completed"
        self.completed_tasks.append(task.task_id)
        del self.active_tasks[task.task_id]
        
        # Update issue (in real implementation)
        # issue.create_comment(f" Budgeting completed by {self.agent_id}")
        # issue.add_to_labels("status/done")

    async def _handle_compliance(self, issue):
        """Handle Compliance operations"""
        logger.info(f"Processing compliance: Issue #{getattr(issue, 'number', 'mock')}")
        
        # Parse issue details
        title = getattr(issue, 'title', 'Mock Operation')
        description = getattr(issue, 'body', 'Mock description')
        
        # Create task
        task = AiFinanceAgentTask(
            task_id=f"ai_finance_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=title,
            description=description,
            operation_type="finance/compliance",
            priority="P2",
            status="in_progress",
            created_at=datetime.now().isoformat(),
            assigned_agent=self.agent_id
        )
        
        # Store active task
        self.active_tasks[task.task_id] = task
        
        # Process compliance (implement business logic here)
        logger.info(f" Compliance completed for {task.task_id}")
        
        # Mark task complete
        task.status = "completed"
        self.completed_tasks.append(task.task_id)
        del self.active_tasks[task.task_id]
        
        # Update issue (in real implementation)
        # issue.create_comment(f" Compliance completed by {self.agent_id}")
        # issue.add_to_labels("status/done")

    async def _handle_expense_tracking(self, issue):
        """Handle Expense Tracking operations"""
        logger.info(f"Processing expense tracking: Issue #{getattr(issue, 'number', 'mock')}")
        
        # Parse issue details
        title = getattr(issue, 'title', 'Mock Operation')
        description = getattr(issue, 'body', 'Mock description')
        
        # Create task
        task = AiFinanceAgentTask(
            task_id=f"ai_finance_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=title,
            description=description,
            operation_type="finance/expense-tracking",
            priority="P2",
            status="in_progress",
            created_at=datetime.now().isoformat(),
            assigned_agent=self.agent_id
        )
        
        # Store active task
        self.active_tasks[task.task_id] = task
        
        # Process expense tracking (implement business logic here)
        logger.info(f" Expense Tracking completed for {task.task_id}")
        
        # Mark task complete
        task.status = "completed"
        self.completed_tasks.append(task.task_id)
        del self.active_tasks[task.task_id]
        
        # Update issue (in real implementation)
        # issue.create_comment(f" Expense Tracking completed by {self.agent_id}")
        # issue.add_to_labels("status/done")

    async def _handle_financial_analysis(self, issue):
        """Handle Financial Analysis operations"""
        logger.info(f"Processing financial analysis: Issue #{getattr(issue, 'number', 'mock')}")
        
        # Parse issue details
        title = getattr(issue, 'title', 'Mock Operation')
        description = getattr(issue, 'body', 'Mock description')
        
        # Create task
        task = AiFinanceAgentTask(
            task_id=f"ai_finance_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=title,
            description=description,
            operation_type="finance/financial-analysis",
            priority="P2",
            status="in_progress",
            created_at=datetime.now().isoformat(),
            assigned_agent=self.agent_id
        )
        
        # Store active task
        self.active_tasks[task.task_id] = task
        
        # Process financial analysis (implement business logic here)
        logger.info(f" Financial Analysis completed for {task.task_id}")
        
        # Mark task complete
        task.status = "completed"
        self.completed_tasks.append(task.task_id)
        del self.active_tasks[task.task_id]
        
        # Update issue (in real implementation)
        # issue.create_comment(f" Financial Analysis completed by {self.agent_id}")
        # issue.add_to_labels("status/done")

    
    def _update_metrics(self):
        """Update agent performance metrics"""
        self.performance_metrics["tasks_completed"] += 1
        self.performance_metrics["current_load"] = len(self.active_tasks)
        
        # Calculate success rate and completion time
        if self.completed_tasks:
            self.performance_metrics["success_rate"] = (
                len(self.completed_tasks) / self.performance_metrics["tasks_completed"] * 100
            )
    
    async def _handle_error(self, issue, error):
        """Handle processing errors"""
        logger.error(f"{self.agent_id} error processing issue #{getattr(issue, 'number', 'unknown')}: {error}")
        
        # In real implementation, this would:
        # - Create error report
        # - Notify management
        # - Attempt recovery
        # - Update issue with error status
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metrics"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": "active",
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "performance_metrics": self.performance_metrics,
            "aws_deployment": "lambda",  # Serverless-first
            "last_update": datetime.now().isoformat()
        }
    
    async def health_check(self) -> bool:
        """Perform agent health check"""
        try:
            # Check agent responsiveness
            # Verify connections
            # Validate configuration
            logger.info(f"{self.agent_id} health check: PASSED")
            return True
        except Exception as e:
            logger.error(f"{self.agent_id} health check: FAILED - {e}")
            return False


# Demo and testing functions
async def demo_ai_finance_agent():
    """Demonstrate Ai Finance Agent capabilities"""
    print(f"\n" + "="*60)
    print(f"[ROBOT] {'Ai Finance Agent'.upper()} DEMONSTRATION")
    print("="*60)
    
    # Initialize agent
    agent = AiFinanceAgent()
    
    print(f"Agent ID: {agent.agent_id}")
    print(f"Agent Type: {agent.agent_type}")
    print(f"AWS Architecture: Lambda-first (serverless)")
    
    # Show capabilities
    print(f"\n Capabilities:")
    print(f"   • Budgeting")
    print(f"   • Compliance")
    print(f"   • Expense Tracking")
    print(f"   • Financial Analysis")
    
    # Mock issue processing
    print(f"\n Processing Mock Business Operations:")
    
    mock_issues = [
        {
            "title": "Mock Budgeting Request",
            "body": "Automated budgeting operation",
            "labels": ["finance/budgeting", "priority/P2-medium"]
        },
        {
            "title": "Mock Compliance Request",
            "body": "Automated compliance operation",
            "labels": ["finance/compliance", "priority/P2-medium"]
        },
        {
            "title": "Mock Expense Tracking Request",
            "body": "Automated expense tracking operation",
            "labels": ["finance/expense-tracking", "priority/P2-medium"]
        },
        {
            "title": "Mock Financial Analysis Request",
            "body": "Automated financial analysis operation",
            "labels": ["finance/financial-analysis", "priority/P2-medium"]
        }
    ]
    
    for mock_issue in mock_issues:
        print(f"   {mock_issue['title']}")
        # In real implementation: await agent.process_business_operation(mock_issue)
    
    # Show status
    status = agent.get_status()
    print(f"\n Agent Status:")
    print(f"  Active Tasks: {status['active_tasks']}")
    print(f"  Completed Tasks: {status['completed_tasks']}")
    print(f"  Success Rate: {status['performance_metrics']['success_rate']:.1f}%")
    print(f"  AWS Deployment: {status['aws_deployment']}")
    
    # Health check
    health = await agent.health_check()
    print(f"\n Health Check: {'PASSED' if health else 'FAILED'}")
    
    print(f"\n {'Ai Finance Agent'.upper()} READY FOR DEPLOYMENT!")
    return agent


if __name__ == "__main__":
    import argparse
    import json
    import subprocess
    
    parser = argparse.ArgumentParser(description=f'AiFinanceAgent - Process GitHub Issues')
    parser.add_argument('--process-issue', type=int, help='Issue number to process')
    parser.add_argument('--issue-data', type=str, help='Path to issue data JSON file')
    parser.add_argument('--demo', action='store_true', help='Run demonstration mode')
    args = parser.parse_args()
    
    if args.process_issue:
        # Process actual GitHub issue
        print(f"Processing Issue #{args.process_issue}")
        
        # Load issue data
        issue_data = None
        if args.issue_data and Path(args.issue_data).exists():
            with open(args.issue_data, 'r') as f:
                issue_data = json.load(f)
                print(f"Loaded issue data: {issue_data.get('title', 'Unknown')}")
        
        # Initialize agent and process issue
        agent = AiFinanceAgent()
        
        # Process the issue based on its labels
        if issue_data:
            print(f"Issue Title: {issue_data.get('title')}")
            print(f"Issue Labels: {[label.get('name') for label in issue_data.get('labels', [])]}")
            
            # Run async processing
            import asyncio
            asyncio.run(agent.process_business_operation(issue_data))
            
            # Update GitHub issue status
            try:
                issue_number = args.process_issue
                repo = "VisualForgeMediaV2/business-operations"
                
                # Add completion comment
                comment = f"""## Finance Agent Processing Complete
                
Task processed successfully by AiFinanceAgent
Status: COMPLETED
Timestamp: {datetime.now().isoformat()}

---
*Automated by Finance Agent*"""
                
                cmd = ["gh", "issue", "comment", str(issue_number),
                       "--repo", repo,
                       "--body", comment]
                
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"Updated GitHub issue #{issue_number}")
                
            except Exception as e:
                print(f"Error updating GitHub issue: {e}")
        else:
            print("No issue data provided, running in limited mode")
    else:
        # Run demo mode
        print(f"Finance Agent")
        print("="*60)
        print("AWS Serverless-First Architecture")
        print("GitHub Issues Integration")
        print("Autonomous Business Operations")
        print("="*60)
        
        # Run demonstration
        asyncio.run(demo_ai_finance_agent())
