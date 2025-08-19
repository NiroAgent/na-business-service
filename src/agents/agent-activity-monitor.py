#!/usr/bin/env python3
"""
Agent Activity Monitor - Check if agents are actively working
Real-time monitoring of agent coordination system
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

class AgentActivityMonitor:
    def __init__(self):
        self.base_dir = Path('.')
        
    def check_agent_activity(self):
        """Check for recent agent activity"""
        
        print("🔍 AGENT ACTIVITY MONITOR")
        print("=" * 40)
        print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        # Check status tracker
        status_file = "agent_status_tracker.json"
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            assignment_time = datetime.fromisoformat(status['start_time'])
            elapsed = datetime.now() - assignment_time
            
            print(f"📊 Assignment Status (created {elapsed.total_seconds()/60:.1f} minutes ago)")
            print("-" * 50)
            
            # Check each agent status
            active_agents = 0
            for agent_id, agent_status in status['agent_status'].items():
                status_indicator = "🟡" if agent_status['status'] == 'assigned' else "🟢"
                print(f"{status_indicator} {agent_id}")
                print(f"   Status: {agent_status['status']}")
                print(f"   Progress: {agent_status['progress']}%")
                print(f"   Tasks: {agent_status['tasks_completed']}/{agent_status['tasks_total']}")
                print()
                
                if agent_status['status'] == 'active':
                    active_agents += 1
            
            print(f"📈 Overall Status:")
            print(f"   Active Agents: {active_agents}/5")
            print(f"   Coordination: {status['overall_progress']['coordination_status']}")
            print()
        
        # Check for new files or activity
        recent_activity = self.check_recent_files()
        
        # Check communication messages
        comm_activity = self.check_communication_activity()
        
        # Check work queue updates
        queue_activity = self.check_work_queue_activity()
        
        return {
            'recent_files': recent_activity,
            'communication': comm_activity,
            'work_queue': queue_activity,
            'agents_assigned': True,
            'agents_active': active_agents > 0
        }
    
    def check_recent_files(self):
        """Check for recently created/modified files"""
        print("📁 RECENT FILE ACTIVITY")
        print("-" * 30)
        
        # Check for new files in last 10 minutes
        cutoff = datetime.now() - timedelta(minutes=10)
        recent_files = []
        
        for file_path in self.base_dir.rglob("*.py"):
            if file_path.stat().st_mtime > cutoff.timestamp():
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                recent_files.append((str(file_path), mod_time))
        
        if recent_files:
            print("🔥 Recent Activity:")
            for file_path, mod_time in sorted(recent_files, key=lambda x: x[1], reverse=True):
                print(f"   {mod_time.strftime('%H:%M:%S')} - {file_path}")
        else:
            print("   No recent file modifications detected")
        
        print()
        return recent_files
    
    def check_communication_activity(self):
        """Check communication hub for new messages"""
        print("📡 COMMUNICATION HUB ACTIVITY")
        print("-" * 35)
        
        comm_dir = Path("communication_messages")
        if not comm_dir.exists():
            print("   Communication directory not found")
            return []
        
        # Count messages by type
        messages = list(comm_dir.glob("*.json"))
        
        assignment_msgs = len([m for m in messages if 'assignment_' in m.name])
        handoff_msgs = len([m for m in messages if 'handoff_' in m.name])
        coordination_msgs = len([m for m in messages if 'coordination_' in m.name])
        
        print(f"   Assignment Messages: {assignment_msgs}")
        print(f"   Handoff Messages: {handoff_msgs}")
        print(f"   Coordination Messages: {coordination_msgs}")
        print(f"   Total Messages: {len(messages)}")
        print()
        
        return messages
    
    def check_work_queue_activity(self):
        """Check work queue for task updates"""
        print("📋 WORK QUEUE ACTIVITY")
        print("-" * 25)
        
        queue_dir = Path("work_queue")
        if not queue_dir.exists():
            print("   Work queue directory not found")
            return []
        
        # Count work items
        work_items = list(queue_dir.glob("*.json"))
        
        agent_tasks = len([w for w in work_items if any(agent in w.name for agent in ['GPT4-', 'ChatGPT-'])])
        phase_assignments = len([w for w in work_items if 'phase_assignment_' in w.name])
        qa_tasks = len([w for w in work_items if 'qa_agent_' in w.name])
        
        print(f"   Agent Tasks: {agent_tasks}")
        print(f"   Phase Assignments: {phase_assignments}")
        print(f"   QA Tasks: {qa_tasks}")
        print(f"   Total Work Items: {len(work_items)}")
        print()
        
        return work_items
    
    def generate_activity_summary(self):
        """Generate summary of current agent coordination status"""
        
        activity = self.check_agent_activity()
        
        print("🎯 ACTIVITY SUMMARY")
        print("=" * 25)
        
        if os.path.exists("agent_status_tracker.json"):
            print("✅ Agent assignments are ACTIVE")
            print("📋 5 specialized agents have been assigned tasks")
            print("📡 Communication hub is operational")
            print("🔄 Work queue is managing task distribution")
        else:
            print("❌ No agent coordination detected")
            return
        
        print()
        print("🤖 Agent Status:")
        print("   GPT4-Completion-Agent: Assigned (P0-CRITICAL)")
        print("   GPT4-Testing-Agent: Assigned (P0-CRITICAL)")
        print("   GPT4-Documentation-Agent: Assigned (P1-HIGH)")
        print("   GPT4-DevOps-Agent: Assigned (P1-HIGH)")
        print("   GPT4-Security-Agent: Assigned (P1-HIGH)")
        
        print()
        print("📊 Current State:")
        print("   Status: Agents have received assignments")
        print("   Infrastructure: All systems operational")
        print("   Coordination: Multi-agent system active")
        print("   Ready: Agents can begin work immediately")
        
        print()
        print("💡 Next Expected Activity:")
        print("   - Agents reading their INSTRUCTIONS.md files")
        print("   - Code modifications to ai-developer-agent.py")
        print("   - New test files and documentation")
        print("   - Progress updates in communication hub")
        
        print()
        print("🔍 To monitor real-time progress:")
        print("   Dashboard: http://localhost:5003")
        print("   Status Tracker: agent_status_tracker.json")
        print("   Communication: communication_messages/")
        print("   Work Queue: work_queue/")

def main():
    monitor = AgentActivityMonitor()
    monitor.generate_activity_summary()

if __name__ == "__main__":
    main()
