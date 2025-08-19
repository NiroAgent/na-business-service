#!/usr/bin/env python3
"""
Docker-based Agent with File Logging for Easy Monitoring
This agent runs tests and logs everything to files that can be easily monitored
"""

import json
import subprocess
import time
import os
import sys
from datetime import datetime
from pathlib import Path
import logging

class MonitorableAgent:
    def __init__(self, agent_name="copilot-agent"):
        self.agent_name = agent_name
        self.log_dir = Path("/workspace/logs") if os.path.exists("/workspace") else Path("E:/Projects/agent_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        self.logger.info(f"AGENT_START Starting {agent_name}")
        
        # Track running status
        self.status_file = self.log_dir / f"{agent_name}_status.json"
        self.update_status("starting")
        
    def setup_logging(self):
        """Setup file and console logging"""
        log_file = self.log_dir / f"{self.agent_name}.log"
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup logger
        self.logger = logging.getLogger(self.agent_name)
        self.logger.setLevel(logging.INFO)
        
        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler with UTF-8 encoding
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Also log to a latest.log file with UTF-8 encoding
        latest_handler = logging.FileHandler(self.log_dir / "latest.log", encoding='utf-8')
        latest_handler.setFormatter(formatter)
        self.logger.addHandler(latest_handler)
    
    def update_status(self, status, details=None):
        """Update agent status file"""
        status_data = {
            "agent": self.agent_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        
        self.logger.info(f"Status: {status}")
    
    def test_service_endpoints(self):
        """Test service endpoints and log results"""
        self.logger.info("SEARCH Starting service endpoint tests")
        self.update_status("testing_endpoints")
        
        # Define services to test
        services = [
            {"name": "VisualForge Auth", "url": "http://localhost:4000/health"},
            {"name": "VisualForge Video", "url": "http://localhost:4001/health"},
            {"name": "VisualForge Image", "url": "http://localhost:4002/health"},
            {"name": "VisualForge Audio", "url": "http://localhost:4003/health"},
            {"name": "VisualForge Text", "url": "http://localhost:4004/health"},
            {"name": "VisualForge Dashboard", "url": "http://localhost:4005/health"},
            {"name": "VisualForge Bulk", "url": "http://localhost:4006/health"},
            {"name": "NiroSubs Auth", "url": "http://localhost:3001/health"},
            {"name": "NiroSubs Dashboard", "url": "http://localhost:3002/health"},
            {"name": "NiroSubs Payments", "url": "http://localhost:3003/health"},
            {"name": "NiroSubs User", "url": "http://localhost:3004/health"},
        ]
        
        results = []
        
        for service in services:
            self.logger.info(f"Testing {service['name']} at {service['url']}")
            
            try:
                # Use curl to test the endpoint
                result = subprocess.run([
                    'curl', '-s', '--connect-timeout', '5', service['url']
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.logger.info(f"SUCCESS {service['name']}: OK")
                    results.append({"service": service['name'], "status": "success", "response": result.stdout[:200]})
                else:
                    self.logger.warning(f"FAILED {service['name']}: ERROR (curl exit code: {result.returncode})")
                    results.append({"service": service['name'], "status": "failed", "error": f"curl exit code: {result.returncode}"})
                    
            except subprocess.TimeoutExpired:
                self.logger.warning(f"TIMEOUT {service['name']}: Request timed out")
                results.append({"service": service['name'], "status": "timeout"})
            except Exception as e:
                self.logger.error(f"ERROR {service['name']}: {str(e)}")
                results.append({"service": service['name'], "status": "error", "error": str(e)})
        
        # Save detailed results
        results_file = self.log_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"RESULTS Test results saved to {results_file}")
        return results
    
    def run_docker_health_checks(self):
        """Check Docker container health"""
        self.logger.info("DOCKER Checking Docker container health")
        self.update_status("checking_docker")
        
        try:
            # Check docker containers
            result = subprocess.run([
                'docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Docker containers:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.logger.info(f"  {line}")
            else:
                self.logger.warning("Failed to get Docker container status")
                
        except Exception as e:
            self.logger.error(f"Docker check failed: {e}")
    
    def run_github_copilot_tests(self):
        """Run GitHub Copilot tests with logging"""
        self.logger.info("🤖 Running GitHub Copilot tests")
        self.update_status("running_copilot_tests")
        
        try:
            # Run a simple gh copilot command
            result = subprocess.run([
                'gh', 'copilot', 'suggest', 'list running docker containers'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("GitHub Copilot response:")
                self.logger.info(result.stdout)
            else:
                self.logger.warning(f"GitHub Copilot failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.logger.warning("GitHub Copilot command timed out")
        except Exception as e:
            self.logger.error(f"GitHub Copilot error: {e}")
    
    def continuous_monitoring(self):
        """Run continuous monitoring loop"""
        self.logger.info("🔄 Starting continuous monitoring")
        self.update_status("monitoring")
        
        cycle = 0
        while True:
            try:
                cycle += 1
                self.logger.info(f"CYCLE Monitoring cycle #{cycle}")
                
                # Run tests
                self.test_service_endpoints()
                
                if cycle % 3 == 0:  # Every 3rd cycle
                    self.run_docker_health_checks()
                
                if cycle % 5 == 0:  # Every 5th cycle
                    self.run_github_copilot_tests()
                
                self.logger.info(f"😴 Sleeping for 60 seconds...")
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.logger.info("STOP Monitoring stopped by user")
                self.update_status("stopped", {"reason": "user_interrupt"})
                break
            except Exception as e:
                self.logger.error(f"ERROR Monitoring error: {e}")
                self.update_status("error", {"error": str(e)})
                time.sleep(30)  # Wait before retrying
    
    def run_single_test(self):
        """Run a single test cycle"""
        self.logger.info("🎯 Running single test cycle")
        self.update_status("single_test")
        
        # Run all tests once
        self.test_service_endpoints()
        self.run_docker_health_checks()
        self.run_github_copilot_tests()
        
        self.update_status("completed")
        self.logger.info("COMPLETE Single test cycle completed")

def main():
    """Main entry point"""
    import sys
    
    agent_name = os.environ.get('AGENT_NAME', 'copilot-agent')
    mode = sys.argv[1] if len(sys.argv) > 1 else 'continuous'
    
    agent = MonitorableAgent(agent_name)
    
    if mode == 'single':
        agent.run_single_test()
    else:
        agent.continuous_monitoring()

if __name__ == "__main__":
    main()
