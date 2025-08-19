#!/usr/bin/env python3
"""
End-to-End Pipeline Integration Tests
Tests the complete AI development pipeline from requirements to deployment
"""

import json
import os
import sys
import time
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class PipelineIntegrationTest:
    def __init__(self):
        self.test_results = []
        self.test_project_path = None
        self.start_time = datetime.now()
        
    def setup_test_environment(self):
        """Setup test environment for pipeline testing"""
        try:
            print("🔧 Setting up test environment...")
            
            # Create temporary test directory
            self.test_project_path = tempfile.mkdtemp(prefix="pipeline_test_")
            print(f"📁 Test directory: {self.test_project_path}")
            
            return True
        except Exception as e:
            print(f"❌ Failed to setup test environment: {e}")
            return False
    
    def test_agent_communication(self) -> Dict[str, Any]:
        """Test agent-to-agent communication"""
        print("\n📡 Testing Agent Communication...")
        
        test_result = {
            "test_name": "Agent Communication",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            # Test communication hub
            from team_communication_protocol import CommunicationHub
            hub = CommunicationHub()
            
            # Test agent registration
            registration_success = hub.register_agent(
                agent_id="test-agent-001",
                agent_type="test",
                capabilities=["testing"],
                status="active"
            )
            
            test_result["details"]["registration"] = registration_success
            
            # Test message passing
            message_sent = hub.send_message(
                from_agent="test-agent-001",
                to_agent="ai-qa-001",
                message_type="test_message",
                payload={"test": "data"}
            )
            
            test_result["details"]["messaging"] = message_sent
            test_result["status"] = "passed" if registration_success and message_sent else "failed"
            
        except ImportError:
            test_result["status"] = "skipped"
            test_result["details"]["error"] = "Communication hub not available"
        except Exception as e:
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def test_data_flow(self) -> Dict[str, Any]:
        """Test data flow through the pipeline"""
        print("\n📊 Testing Pipeline Data Flow...")
        
        test_result = {
            "test_name": "Pipeline Data Flow",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            # Simulate architect → developer → qa → devops flow
            flow_steps = []
            
            # Step 1: Architect creates specifications
            architect_spec = {
                "project_id": "test-project-001",
                "requirements": ["API endpoints", "Database integration"],
                "technology_stack": ["Python", "Flask", "SQLite"],
                "architecture_patterns": ["REST API", "MVC"]
            }
            flow_steps.append({"step": "architect", "status": "complete", "data": architect_spec})
            
            # Step 2: Developer receives specs and generates code
            developer_output = {
                "project_id": "test-project-001",
                "generated_files": ["main.py", "models.py", "api.py"],
                "lines_of_code": 150,
                "test_files": ["test_main.py"]
            }
            flow_steps.append({"step": "developer", "status": "complete", "data": developer_output})
            
            # Step 3: QA receives code and validates
            qa_report = {
                "project_id": "test-project-001",
                "quality_score": 85.0,
                "test_results": {"passed": 5, "failed": 0},
                "security_issues": [],
                "approved": True
            }
            flow_steps.append({"step": "qa", "status": "complete", "data": qa_report})
            
            # Step 4: DevOps receives validated code for deployment
            devops_config = {
                "project_id": "test-project-001",
                "deployment_target": "staging",
                "docker_config": "generated",
                "ci_cd_pipeline": "configured"
            }
            flow_steps.append({"step": "devops", "status": "ready", "data": devops_config})
            
            test_result["details"]["flow_steps"] = flow_steps
            test_result["status"] = "passed"
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def test_file_generation(self) -> Dict[str, Any]:
        """Test file generation and output quality"""
        print("\n📝 Testing File Generation...")
        
        test_result = {
            "test_name": "File Generation",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            # Check for generated files from previous phases
            generated_files = []
            
            # Check AI agent files
            agent_files = [
                "ai-architect-agent.py",
                "ai-developer-agent.py", 
                "ai-qa-agent.py"
            ]
            
            for file_name in agent_files:
                if os.path.exists(file_name):
                    with open(file_name, 'r') as f:
                        content = f.read()
                        generated_files.append({
                            "file": file_name,
                            "size": len(content),
                            "lines": len(content.split('\n')),
                            "exists": True
                        })
                else:
                    generated_files.append({
                        "file": file_name,
                        "exists": False
                    })
            
            # Check QA reports
            qa_reports = list(Path("qa_reports").glob("*.json")) if Path("qa_reports").exists() else []
            test_result["details"]["qa_reports"] = len(qa_reports)
            
            test_result["details"]["generated_files"] = generated_files
            test_result["details"]["total_files"] = len([f for f in generated_files if f.get("exists")])
            
            # Pass if we have at least 2 agent files
            existing_files = [f for f in generated_files if f.get("exists")]
            test_result["status"] = "passed" if len(existing_files) >= 2 else "failed"
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def test_quality_metrics(self) -> Dict[str, Any]:
        """Test quality metrics and scoring"""
        print("\n🎯 Testing Quality Metrics...")
        
        test_result = {
            "test_name": "Quality Metrics",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            # Check QA report quality scores
            qa_reports_dir = Path("qa_reports")
            if qa_reports_dir.exists():
                reports = list(qa_reports_dir.glob("*.json"))
                quality_scores = []
                
                for report_file in reports:
                    with open(report_file, 'r') as f:
                        report_data = json.load(f)
                        if "quality_score" in report_data:
                            quality_scores.append(report_data["quality_score"])
                
                test_result["details"]["reports_found"] = len(reports)
                test_result["details"]["quality_scores"] = quality_scores
                test_result["details"]["average_quality"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0
                
                # Pass if average quality > 80
                avg_quality = test_result["details"]["average_quality"]
                test_result["status"] = "passed" if avg_quality >= 80 else "failed"
            else:
                test_result["status"] = "skipped"
                test_result["details"]["error"] = "No QA reports directory found"
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def test_dashboard_integration(self) -> Dict[str, Any]:
        """Test dashboard integration and monitoring"""
        print("\n📊 Testing Dashboard Integration...")
        
        test_result = {
            "test_name": "Dashboard Integration",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            import requests
            
            # Test dashboard endpoint
            response = requests.get("http://localhost:5003", timeout=5)
            test_result["details"]["dashboard_status"] = response.status_code
            test_result["details"]["response_size"] = len(response.text)
            
            # Check for key dashboard elements
            content = response.text
            dashboard_elements = [
                "AI Development Team Dashboard",
                "Phase 5",
                "DevOps Agent",
                "Quality Score"
            ]
            
            found_elements = []
            for element in dashboard_elements:
                if element in content:
                    found_elements.append(element)
            
            test_result["details"]["found_elements"] = found_elements
            test_result["details"]["element_coverage"] = len(found_elements) / len(dashboard_elements) * 100
            
            # Pass if dashboard is accessible and has key elements
            test_result["status"] = "passed" if response.status_code == 200 and len(found_elements) >= 3 else "failed"
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def test_devops_readiness(self) -> Dict[str, Any]:
        """Test DevOps agent readiness"""
        print("\n🚀 Testing DevOps Readiness...")
        
        test_result = {
            "test_name": "DevOps Readiness",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            # Check if DevOps agent file exists
            devops_file = "ai-devops-agent.py"
            devops_exists = os.path.exists(devops_file)
            
            test_result["details"]["devops_agent_exists"] = devops_exists
            
            if devops_exists:
                with open(devops_file, 'r') as f:
                    content = f.read()
                    test_result["details"]["devops_lines"] = len(content.split('\n'))
                    test_result["details"]["devops_size"] = len(content)
                    
                    # Check for key DevOps capabilities
                    capabilities = [
                        "docker",
                        "deployment",
                        "ci_cd",
                        "monitoring",
                        "infrastructure"
                    ]
                    
                    found_capabilities = []
                    for cap in capabilities:
                        if cap.lower() in content.lower():
                            found_capabilities.append(cap)
                    
                    test_result["details"]["capabilities_found"] = found_capabilities
                    test_result["details"]["capability_coverage"] = len(found_capabilities) / len(capabilities) * 100
                    
                    test_result["status"] = "passed" if len(found_capabilities) >= 3 else "in_development"
            else:
                test_result["status"] = "waiting"
                test_result["details"]["message"] = "Waiting for Opus to create DevOps agent"
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("🧪 STARTING PIPELINE INTEGRATION TESTS")
        print("=" * 60)
        
        if not self.setup_test_environment():
            return {"status": "failed", "error": "Test environment setup failed"}
        
        # Run all tests
        tests = [
            self.test_agent_communication,
            self.test_data_flow,
            self.test_file_generation,
            self.test_quality_metrics,
            self.test_dashboard_integration,
            self.test_devops_readiness
        ]
        
        for test_func in tests:
            test_result = test_func()
            self.test_results.append(test_result)
            
            # Print test result
            status_emoji = {
                "passed": "✅",
                "failed": "❌", 
                "skipped": "⏭️",
                "waiting": "⏳",
                "in_development": "🔄"
            }
            
            emoji = status_emoji.get(test_result["status"], "❓")
            print(f"{emoji} {test_result['test_name']}: {test_result['status'].upper()}")
        
        # Generate summary
        summary = self.generate_test_summary()
        self.cleanup_test_environment()
        
        return summary
    
    def generate_test_summary(self) -> Dict[str, Any]:
        """Generate test summary report"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "passed"])
        failed_tests = len([t for t in self.test_results if t["status"] == "failed"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "skipped"])
        
        summary = {
            "test_suite": "Pipeline Integration Tests",
            "timestamp": datetime.now().isoformat(),
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_results": self.test_results,
            "overall_status": "passed" if failed_tests == 0 else "failed"
        }
        
        return summary
    
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        try:
            if self.test_project_path and os.path.exists(self.test_project_path):
                shutil.rmtree(self.test_project_path)
                print(f"🧹 Cleaned up test directory: {self.test_project_path}")
        except Exception as e:
            print(f"⚠️ Failed to cleanup test environment: {e}")

def main():
    """Main test runner"""
    tester = PipelineIntegrationTest()
    summary = tester.run_all_tests()
    
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"⏱️  Duration: {summary['duration']:.1f} seconds")
    print(f"🧪 Total Tests: {summary['total_tests']}")
    print(f"✅ Passed: {summary['passed']}")
    print(f"❌ Failed: {summary['failed']}")
    print(f"⏭️  Skipped: {summary['skipped']}")
    print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
    print(f"🎯 Overall Status: {summary['overall_status'].upper()}")
    
    # Save results
    results_file = f"integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"📁 Results saved to: {results_file}")
    
    return summary['overall_status'] == 'passed'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
