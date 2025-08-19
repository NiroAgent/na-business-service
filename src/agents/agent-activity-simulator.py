#!/usr/bin/env python3
"""
Agent Activity Simulator - Simulates realistic agent activity for dashboard testing
"""

import time
import json
import random
from datetime import datetime
from pathlib import Path
import threading

class AgentActivitySimulator:
    def __init__(self):
        self.agents = {
            "ai-architect-001": {
                "type": "architect",
                "status": "active",
                "current_task": "Designing e-commerce API architecture",
                "progress": 85,
                "last_activity": datetime.now().isoformat()
            },
            "ai-developer-001": {
                "type": "developer", 
                "status": "active",
                "current_task": "Implementing FastAPI endpoints",
                "progress": 65,
                "last_activity": datetime.now().isoformat()
            },
            "ai-qa-001": {
                "type": "qa",
                "status": "waiting",
                "current_task": "Waiting for code to test",
                "progress": 0,
                "last_activity": datetime.now().isoformat()
            },
            "github-issues-001": {
                "type": "github",
                "status": "active",
                "current_task": "Monitoring repositories",
                "progress": 100,
                "last_activity": datetime.now().isoformat()
            }
        }
        
        self.activities = [
            "Analyzing project requirements",
            "Generating code structure", 
            "Creating API endpoints",
            "Writing unit tests",
            "Performing security scan",
            "Updating documentation",
            "Running integration tests",
            "Optimizing database queries",
            "Reviewing code quality",
            "Deploying to staging"
        ]
        
        self.running = False
    
    def simulate_agent_activity(self):
        """Simulate realistic agent activity"""
        while self.running:
            try:
                # Update each agent
                for agent_id, agent in self.agents.items():
                    if agent["status"] == "active":
                        # Randomly update progress
                        if random.random() < 0.3:  # 30% chance of progress update
                            agent["progress"] = min(100, agent["progress"] + random.randint(1, 5))
                            agent["last_activity"] = datetime.now().isoformat()
                        
                        # Randomly change tasks
                        if random.random() < 0.1:  # 10% chance of new task
                            agent["current_task"] = random.choice(self.activities)
                            agent["last_activity"] = datetime.now().isoformat()
                        
                        # If task complete, start new one
                        if agent["progress"] >= 100:
                            agent["current_task"] = random.choice(self.activities)
                            agent["progress"] = random.randint(5, 25)
                
                # Save agent state
                self.save_agent_state()
                
                # Log activity
                self.log_activity()
                
                time.sleep(random.randint(2, 8))  # Random interval
                
            except Exception as e:
                print(f"Error in simulation: {e}")
                time.sleep(5)
    
    def save_agent_state(self):
        """Save current agent state to file"""
        try:
            state_file = Path("agent_simulation_state.json")
            with open(state_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "agents": self.agents
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def log_activity(self):
        """Log agent activity"""
        try:
            log_file = Path("agent_activity.log")
            with open(log_file, 'a') as f:
                for agent_id, agent in self.agents.items():
                    if agent["status"] == "active":
                        f.write(f"{datetime.now().isoformat()} - {agent_id} - {agent['current_task']} ({agent['progress']}%)\n")
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def generate_project_files(self):
        """Generate mock project files to simulate real work"""
        try:
            project_dir = Path("test-projects/ecommerce-api/generated")
            project_dir.mkdir(exist_ok=True)
            
            files = [
                "main.py",
                "models.py", 
                "auth.py",
                "routes/products.py",
                "routes/orders.py",
                "tests/test_auth.py",
                "tests/test_products.py",
                "docker-compose.yml",
                "requirements.txt"
            ]
            
            for filename in files:
                if random.random() < 0.2:  # 20% chance to "generate" a file
                    file_path = project_dir / filename
                    file_path.parent.mkdir(exist_ok=True)
                    
                    with open(file_path, 'w') as f:
                        f.write(f"# Generated by AI Developer Agent\n")
                        f.write(f"# File: {filename}\n")
                        f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                        f.write("# Mock content for dashboard testing\n")
                    
                    print(f"📄 Generated: {filename}")
        
        except Exception as e:
            print(f"Error generating files: {e}")
    
    def start_simulation(self):
        """Start the activity simulation"""
        print("🤖 Starting Agent Activity Simulation")
        print("=" * 50)
        
        self.running = True
        
        # Start simulation thread
        sim_thread = threading.Thread(target=self.simulate_agent_activity, daemon=True)
        sim_thread.start()
        
        # Start file generation thread
        file_thread = threading.Thread(target=self.periodic_file_generation, daemon=True)
        file_thread.start()
        
        print("✅ Simulation started")
        print("📊 Agents are now generating activity for dashboard monitoring")
        print("🔄 Check agent_activity.log for real-time updates")
        
        return sim_thread, file_thread
    
    def periodic_file_generation(self):
        """Periodically generate project files"""
        while self.running:
            try:
                self.generate_project_files()
                time.sleep(random.randint(10, 30))
            except Exception as e:
                print(f"Error in file generation: {e}")
                time.sleep(30)
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        print("🛑 Simulation stopped")
    
    def get_current_state(self):
        """Get current simulation state"""
        return {
            "running": self.running,
            "agents": self.agents,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    simulator = AgentActivitySimulator()
    
    try:
        threads = simulator.start_simulation()
        
        print("\nPress Ctrl+C to stop simulation...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        simulator.stop_simulation()
        print("\n👋 Simulation ended")
