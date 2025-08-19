#!/usr/bin/env python3
"""
Testing and Validation Agent
Specialized agent for testing the policy engine integration and suggesting improvements
"""

import os
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TestingAgent')

class TestingValidationAgent:
    """Comprehensive testing agent for SDLC policy integration"""
    
    def __init__(self):
        self.name = "testing-validation-agent"
        self.test_results = {}
        self.recommendations = []
        
    def run_comprehensive_tests(self):
        """Run comprehensive integration tests"""
        logger.info("🧪 Starting comprehensive testing suite...")
        
        test_suite = {
            "policy_engine_tests": self.test_policy_engine(),
            "github_integration_tests": self.test_github_integration(),
            "agent_coordination_tests": self.test_agent_coordination(),
            "performance_tests": self.test_performance(),
            "security_tests": self.test_security_compliance(),
            "end_to_end_tests": self.test_end_to_end_workflow()
        }
        
        # Calculate overall score
        total_tests = sum(len(results.get("tests", [])) for results in test_suite.values())
        passed_tests = sum(
            sum(1 for test in results.get("tests", []) if test.get("passed", False))
            for results in test_suite.values()
        )
        
        overall_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        final_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": overall_score,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_suite": test_suite,
            "recommendations": self.generate_recommendations(test_suite),
            "next_actions": self.generate_next_actions(test_suite)
        }
        
        # Save comprehensive report
        with open("COMPREHENSIVE_TEST_REPORT.json", "w") as f:
            json.dump(final_report, f, indent=2)
        
        logger.info(f"✅ Testing complete - Score: {overall_score:.1f}% ({passed_tests}/{total_tests})")
        return final_report
    
    def test_policy_engine(self):
        """Test policy engine functionality"""
        logger.info("🔍 Testing policy engine...")
        
        tests = []
        
        # Test 1: Policy engine initialization
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("agent_policy_engine", "agent-policy-engine.py")
            policy_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(policy_module)
            
            policy_engine = policy_module.AgentPolicyEngine()
            tests.append({
                "name": "Policy Engine Initialization",
                "passed": True,
                "details": "Successfully initialized SQLite policy engine"
            })
        except Exception as e:
            tests.append({
                "name": "Policy Engine Initialization",
                "passed": False,
                "error": str(e)
            })
            return {"tests": tests, "success": False}
        
        # Test 2: Agent role creation
        try:
            roles = policy_engine.get_all_roles()
            tests.append({
                "name": "Agent Roles Available",
                "passed": len(roles) > 0,
                "details": f"Found {len(roles)} agent roles"
            })
        except Exception as e:
            tests.append({
                "name": "Agent Roles Available",
                "passed": False,
                "error": str(e)
            })
        
        # Test 3: Policy assessment functionality
        try:
            test_assessment = policy_engine.assess_agent_action(
                agent_id="test-agent",
                role_id="completion-agent",
                content="def test_function():\n    return 'Hello World'"
            )
            
            tests.append({
                "name": "Policy Assessment",
                "passed": isinstance(test_assessment, dict),
                "details": f"Assessment returned: {test_assessment.get('assessment_summary', 'N/A')}"
            })
        except Exception as e:
            tests.append({
                "name": "Policy Assessment",
                "passed": False,
                "error": str(e)
            })
        
        # Test 4: Security violation detection
        try:
            security_test = policy_engine.assess_agent_action(
                agent_id="security-test",
                role_id="security-agent",
                content="password = 'hardcoded123'\napi_key = 'secret_key_here'"
            )
            
            # Should detect security violations
            violations_detected = security_test.get("risk_level", 0) > 2
            tests.append({
                "name": "Security Violation Detection",
                "passed": violations_detected,
                "details": f"Risk level: {security_test.get('risk_level', 0)}"
            })
        except Exception as e:
            tests.append({
                "name": "Security Violation Detection",
                "passed": False,
                "error": str(e)
            })
        
        success_rate = sum(1 for test in tests if test.get("passed", False)) / len(tests)
        return {
            "tests": tests,
            "success": success_rate >= 0.75,
            "success_rate": success_rate
        }
    
    def test_github_integration(self):
        """Test GitHub integration functionality"""
        logger.info("🔗 Testing GitHub integration...")
        
        tests = []
        
        # Test 1: GitHub agent initialization
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("github_issues_policy_agent", "github-issues-policy-agent.py")
            github_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(github_module)
            
            github_agent = github_module.PolicyEnhancedGitHubAgent()
            tests.append({
                "name": "GitHub Agent Initialization",
                "passed": True,
                "details": "Successfully initialized GitHub Issues agent"
            })
        except Exception as e:
            tests.append({
                "name": "GitHub Agent Initialization",
                "passed": False,
                "error": str(e)
            })
            return {"tests": tests, "success": False}
        
        # Test 2: Policy engine integration
        policy_integrated = github_agent.policy_engine is not None
        tests.append({
            "name": "Policy Engine Integration",
            "passed": policy_integrated,
            "details": f"Policy engine type: {type(github_agent.policy_engine).__name__ if policy_integrated else 'None'}"
        })
        
        # Test 3: GitHub token availability
        github_token = os.getenv("GITHUB_TOKEN")
        tests.append({
            "name": "GitHub Token Available",
            "passed": github_token is not None and len(github_token) > 0,
            "details": f"Token length: {len(github_token) if github_token else 0}"
        })
        
        # Test 4: Role mapping configuration
        role_mapping_valid = hasattr(github_agent, 'role_mapping') and len(github_agent.role_mapping) > 0
        tests.append({
            "name": "Role Mapping Configuration",
            "passed": role_mapping_valid,
            "details": f"Roles mapped: {len(github_agent.role_mapping) if role_mapping_valid else 0}"
        })
        
        success_rate = sum(1 for test in tests if test.get("passed", False)) / len(tests)
        return {
            "tests": tests,
            "success": success_rate >= 0.5,  # Lower threshold since GitHub token might not be set
            "success_rate": success_rate
        }
    
    def test_agent_coordination(self):
        """Test agent coordination functionality"""
        logger.info("🤝 Testing agent coordination...")
        
        tests = []
        
        # Test 1: Communication hub availability
        try:
            if os.path.exists("team-communication-protocol.py"):
                import importlib.util
                spec = importlib.util.spec_from_file_location("team_communication_protocol", "team-communication-protocol.py")
                comm_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(comm_module)
                
                tests.append({
                    "name": "Communication Hub Available",
                    "passed": True,
                    "details": "Team communication protocol found"
                })
            else:
                tests.append({
                    "name": "Communication Hub Available",
                    "passed": False,
                    "details": "team-communication-protocol.py not found"
                })
        except Exception as e:
            tests.append({
                "name": "Communication Hub Available",
                "passed": False,
                "error": str(e)
            })
        
        # Test 2: Work queue manager
        try:
            if os.path.exists("work-queue-manager.py"):
                tests.append({
                    "name": "Work Queue Manager Available",
                    "passed": True,
                    "details": "Work queue manager found"
                })
            else:
                tests.append({
                    "name": "Work Queue Manager Available",
                    "passed": False,
                    "details": "work-queue-manager.py not found"
                })
        except Exception as e:
            tests.append({
                "name": "Work Queue Manager Available",
                "passed": False,
                "error": str(e)
            })
        
        # Test 3: Agent coordination files
        coordination_files = [
            "agent-coordinator-postgresql-integration.py",
            "github-setup-agent.py"
        ]
        
        available_files = sum(1 for file in coordination_files if os.path.exists(file))
        tests.append({
            "name": "Coordination Components",
            "passed": available_files >= len(coordination_files) * 0.5,
            "details": f"Available: {available_files}/{len(coordination_files)}"
        })
        
        success_rate = sum(1 for test in tests if test.get("passed", False)) / len(tests)
        return {
            "tests": tests,
            "success": success_rate >= 0.6,
            "success_rate": success_rate
        }
    
    def test_performance(self):
        """Test performance characteristics"""
        logger.info("⚡ Testing performance...")
        
        tests = []
        
        # Test 1: Policy assessment speed
        try:
            import importlib.util
            import time
            
            spec = importlib.util.spec_from_file_location("agent_policy_engine", "agent-policy-engine.py")
            policy_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(policy_module)
            
            policy_engine = policy_module.AgentPolicyEngine()
            
            start_time = time.time()
            for i in range(5):
                policy_engine.assess_agent_action(
                    agent_id=f"perf-test-{i}",
                    role_id="completion-agent",
                    content=f"def test_function_{i}():\n    return 'test'"
                )
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 5
            tests.append({
                "name": "Policy Assessment Speed",
                "passed": avg_time < 1.0,  # Should be under 1 second per assessment
                "details": f"Average time: {avg_time:.3f}s per assessment"
            })
        except Exception as e:
            tests.append({
                "name": "Policy Assessment Speed",
                "passed": False,
                "error": str(e)
            })
        
        # Test 2: Database file size
        try:
            if os.path.exists("agent_policies.db"):
                file_size = os.path.getsize("agent_policies.db") / 1024 / 1024  # MB
                tests.append({
                    "name": "Database Size",
                    "passed": file_size < 10,  # Should be under 10MB
                    "details": f"Database size: {file_size:.2f}MB"
                })
            else:
                tests.append({
                    "name": "Database Size",
                    "passed": False,
                    "details": "Database file not found"
                })
        except Exception as e:
            tests.append({
                "name": "Database Size",
                "passed": False,
                "error": str(e)
            })
        
        success_rate = sum(1 for test in tests if test.get("passed", False)) / len(tests)
        return {
            "tests": tests,
            "success": success_rate >= 0.5,
            "success_rate": success_rate
        }
    
    def test_security_compliance(self):
        """Test security compliance features"""
        logger.info("🔒 Testing security compliance...")
        
        tests = []
        
        # Test 1: Hardcoded secret detection
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("agent_policy_engine", "agent-policy-engine.py")
            policy_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(policy_module)
            
            policy_engine = policy_module.AgentPolicyEngine()
            
            # Test with obvious security violations
            security_violations = [
                "password = 'admin123'",
                "api_key = 'sk-1234567890abcdef'",
                "secret_token = 'hardcoded_token'"
            ]
            
            violations_detected = 0
            for violation in security_violations:
                result = policy_engine.assess_agent_action(
                    agent_id="security-test",
                    role_id="security-agent", 
                    content=violation
                )
                if result.get("risk_level", 0) > 2:
                    violations_detected += 1
            
            tests.append({
                "name": "Security Violation Detection",
                "passed": violations_detected >= len(security_violations) * 0.5,
                "details": f"Detected {violations_detected}/{len(security_violations)} violations"
            })
        except Exception as e:
            tests.append({
                "name": "Security Violation Detection",
                "passed": False,
                "error": str(e)
            })
        
        # Test 2: Policy rule coverage
        try:
            policy_rules = policy_engine.get_all_policy_rules()
            security_rules = [rule for rule in policy_rules if "security" in rule.get("name", "").lower()]
            
            tests.append({
                "name": "Security Policy Coverage",
                "passed": len(security_rules) > 0,
                "details": f"Security rules: {len(security_rules)}/{len(policy_rules)}"
            })
        except Exception as e:
            tests.append({
                "name": "Security Policy Coverage",
                "passed": False,
                "error": str(e)
            })
        
        success_rate = sum(1 for test in tests if test.get("passed", False)) / len(tests)
        return {
            "tests": tests,
            "success": success_rate >= 0.5,
            "success_rate": success_rate
        }
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        logger.info("🎯 Testing end-to-end workflow...")
        
        tests = []
        
        # Test 1: Complete policy assessment workflow
        try:
            import importlib.util
            
            # Load policy engine
            spec = importlib.util.spec_from_file_location("agent_policy_engine", "agent-policy-engine.py")
            policy_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(policy_module)
            policy_engine = policy_module.AgentPolicyEngine()
            
            # Load GitHub agent
            spec = importlib.util.spec_from_file_location("github_issues_policy_agent", "github-issues-policy-agent.py")
            github_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(github_module)
            github_agent = github_module.PolicyEnhancedGitHubAgent()
            
            # Simulate workflow: GitHub Issue → Policy Check → Agent Assignment
            test_issue_content = '''
# Feature Request: Add User Authentication

## Description
Add user authentication system with login/logout functionality.

## Requirements
- Secure password storage
- Session management
- Password strength validation

## Code Example
```python
def authenticate_user(username, password):
    # TODO: Implement secure authentication
    return True
```
'''
            
            # Test policy assessment
            assessment = policy_engine.assess_agent_action(
                agent_id="github-issue-processor",
                role_id="completion-agent",
                content=test_issue_content
            )
            
            workflow_success = (
                assessment is not None and
                isinstance(assessment, dict) and
                "assessment_summary" in assessment
            )
            
            tests.append({
                "name": "End-to-End Policy Workflow",
                "passed": workflow_success,
                "details": f"Workflow completed with assessment: {assessment.get('assessment_summary', 'N/A')}"
            })
            
        except Exception as e:
            tests.append({
                "name": "End-to-End Policy Workflow",
                "passed": False,
                "error": str(e)
            })
        
        # Test 2: Integration points validation
        integration_files = [
            "agent-policy-engine.py",
            "github-issues-policy-agent.py",
            "postgresql-agent-policy-engine.py"
        ]
        
        available_integrations = sum(1 for file in integration_files if os.path.exists(file))
        tests.append({
            "name": "Integration Points Available",
            "passed": available_integrations >= len(integration_files) * 0.75,
            "details": f"Available: {available_integrations}/{len(integration_files)}"
        })
        
        success_rate = sum(1 for test in tests if test.get("passed", False)) / len(tests)
        return {
            "tests": tests,
            "success": success_rate >= 0.5,
            "success_rate": success_rate
        }
    
    def generate_recommendations(self, test_suite):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Policy engine recommendations
        policy_tests = test_suite.get("policy_engine_tests", {})
        if not policy_tests.get("success", False):
            recommendations.append({
                "category": "Policy Engine",
                "priority": "HIGH",
                "recommendation": "Fix policy engine initialization and assessment functionality",
                "details": "Core policy engine is not functioning correctly"
            })
        
        # GitHub integration recommendations
        github_tests = test_suite.get("github_integration_tests", {})
        if github_tests.get("success_rate", 0) < 0.75:
            recommendations.append({
                "category": "GitHub Integration",
                "priority": "MEDIUM",
                "recommendation": "Set up GitHub token and improve integration",
                "details": "GitHub integration needs token configuration"
            })
        
        # Performance recommendations
        performance_tests = test_suite.get("performance_tests", {})
        if not performance_tests.get("success", False):
            recommendations.append({
                "category": "Performance",
                "priority": "MEDIUM",
                "recommendation": "Optimize policy assessment performance",
                "details": "Policy assessments are taking too long"
            })
        
        # Security recommendations
        security_tests = test_suite.get("security_tests", {})
        if not security_tests.get("success", False):
            recommendations.append({
                "category": "Security",
                "priority": "HIGH",
                "recommendation": "Improve security violation detection",
                "details": "Security compliance testing is not adequate"
            })
        
        return recommendations
    
    def generate_next_actions(self, test_suite):
        """Generate specific next actions"""
        actions = []
        
        # Check overall health
        total_success = sum(
            1 for test_category in test_suite.values() 
            if test_category.get("success", False)
        )
        
        if total_success < len(test_suite) * 0.5:
            actions.extend([
                "Fix critical policy engine issues",
                "Ensure all dependencies are installed",
                "Review and update configuration files"
            ])
        
        # GitHub specific actions
        github_tests = test_suite.get("github_integration_tests", {})
        if github_tests.get("success_rate", 0) < 0.5:
            actions.extend([
                "Set GITHUB_TOKEN environment variable",
                "Test GitHub API connectivity",
                "Verify repository permissions"
            ])
        
        # PostgreSQL migration actions
        actions.extend([
            "Set up PostgreSQL database when ready",
            "Run policy migration from SQLite to PostgreSQL",
            "Test PostgreSQL policy engine performance"
        ])
        
        # Coordination actions
        actions.extend([
            "Start policy-aware development workflow",
            "Monitor policy compliance metrics",
            "Set up automated policy checking in CI/CD"
        ])
        
        return actions


def main():
    """Main testing function"""
    logger.info("🧪 Starting Testing and Validation Agent")
    
    testing_agent = TestingValidationAgent()
    
    # Run comprehensive tests
    test_report = testing_agent.run_comprehensive_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE TEST REPORT SUMMARY")
    print("="*60)
    print(f"Overall Score: {test_report['overall_score']:.1f}%")
    print(f"Tests Passed: {test_report['passed_tests']}/{test_report['total_tests']}")
    print(f"Test Categories: {len(test_report['test_suite'])}")
    
    print("\n🎯 KEY RECOMMENDATIONS:")
    for i, rec in enumerate(test_report['recommendations'][:3], 1):
        print(f"{i}. [{rec['priority']}] {rec['recommendation']}")
    
    print("\n🚀 NEXT ACTIONS:")
    for i, action in enumerate(test_report['next_actions'][:5], 1):
        print(f"{i}. {action}")
    
    print(f"\n📄 Full report saved to: COMPREHENSIVE_TEST_REPORT.json")
    print("="*60)
    
    return test_report


if __name__ == "__main__":
    main()
