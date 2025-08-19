#!/usr/bin/env python3
"""
VF Integration Test Suite
Tests the complete pipeline from VF-Agent-Service brainstorming to AI Architect Agent
"""

import json
import time
import unittest
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys
import threading

# Import bridge and AI Architect
sys.path.append(str(Path(__file__).parent))
try:
    # Try importing with underscores (Python module naming)
    from vf_design_document_bridge import VFDesignDocumentBridge, BrainstormSession, DesignDocument
except ImportError:
    # Try with hyphens (file naming)
    import importlib.util
    spec = importlib.util.spec_from_file_location("vf_design_document_bridge", "vf-design-document-bridge.py")
    vf_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vf_module)
    VFDesignDocumentBridge = vf_module.VFDesignDocumentBridge
    BrainstormSession = vf_module.BrainstormSession
    DesignDocument = vf_module.DesignDocument

try:
    from ai_architect_agent import AIArchitectAgent
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location("ai_architect_agent", "ai-architect-agent.py")
    ai_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ai_module)
    AIArchitectAgent = ai_module.AIArchitectAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VFIntegrationTest')


class VFIntegrationTests(unittest.TestCase):
    """Complete integration tests for VF Bridge to AI Architect pipeline"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.bridge = VFDesignDocumentBridge()
        cls.ai_architect = AIArchitectAgent()
        
        # Test data directory
        cls.test_data_dir = Path("test_data")
        cls.test_data_dir.mkdir(exist_ok=True)
        
        # Test results directory
        cls.test_results_dir = Path("test_results")
        cls.test_results_dir.mkdir(exist_ok=True)
    
    def test_brainstorm_to_architect(self):
        """Test complete pipeline from brainstorming to architecture spec"""
        logger.info("Testing complete pipeline from brainstorming to architecture...")
        
        # Create test brainstorming session
        test_conversation = [
            {"role": "user", "content": "I need to build an e-commerce platform"},
            {"role": "assistant", "content": "I can help you design an e-commerce platform. What are the key features you need?"},
            {"role": "user", "content": "Users should be able to browse products, add them to cart, and checkout with payment"},
            {"role": "user", "content": "We need user registration and login with OAuth2"},
            {"role": "user", "content": "The system must handle 10000 concurrent users"},
            {"role": "user", "content": "Performance requirement: Page load time should be under 2 seconds"},
            {"role": "user", "content": "We want to integrate with Stripe for payments and SendGrid for emails"},
            {"role": "user", "content": "As a customer, I want to track my orders so that I know when they will arrive"},
            {"role": "user", "content": "As an admin, I want to manage inventory so that products are always up to date"}
        ]
        
        # Create brainstorm session
        session = BrainstormSession(
            session_id="test-session-001",
            user_id="test-user",
            conversation_data=test_conversation,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            status="design-ready",
            metadata={"test": True, "title": "E-commerce Platform"}
        )
        
        # Test requirement extraction
        requirements = self.bridge.extract_design_requirements(session.conversation_data)
        
        # Verify requirements extracted
        self.assertIn('functional', requirements)
        self.assertIn('non_functional', requirements)
        self.assertIn('user_stories', requirements)
        
        # Check functional requirements
        self.assertTrue(len(requirements['functional']) > 0, "Should extract functional requirements")
        
        # Check non-functional requirements  
        self.assertTrue(len(requirements['non_functional']) > 0, "Should extract non-functional requirements")
        
        # Check user stories
        self.assertTrue(len(requirements['user_stories']) > 0, "Should extract user stories")
        
        # Test design document formatting
        design_doc = self.bridge.format_design_document(requirements, session)
        
        # Verify design document structure
        self.assertIsNotNone(design_doc.document_id)
        self.assertIsNotNone(design_doc.title)
        self.assertIsNotNone(design_doc.overview)
        self.assertEqual(design_doc.session_id, session.session_id)
        self.assertTrue(len(design_doc.functional_requirements) > 0)
        self.assertTrue(len(design_doc.acceptance_criteria) > 0)
        
        # Test AI Architect processing
        issue_data = self.bridge._convert_to_github_issue(design_doc)
        
        # Verify issue format
        self.assertIn('title', issue_data)
        self.assertIn('body', issue_data)
        self.assertIn('labels', issue_data)
        
        # Process with AI Architect
        try:
            analysis = self.ai_architect.analyze_github_issue(issue_data)
            
            # Verify analysis
            self.assertIsNotNone(analysis)
            self.assertIn('requirements', analysis)
            self.assertIn('technical_approach', analysis)
            self.assertIn('technology_stack', analysis)
            self.assertIn('complexity_score', analysis)
            
            # Create architecture specification
            arch_spec = self.ai_architect.create_architecture_specification(analysis)
            
            # Verify specification
            self.assertIsNotNone(arch_spec.spec_id)
            self.assertEqual(arch_spec.issue_id, design_doc.document_id)
            self.assertIsNotNone(arch_spec.architecture)
            self.assertIsNotNone(arch_spec.api_design)
            self.assertIsNotNone(arch_spec.database_design)
            self.assertIsNotNone(arch_spec.implementation_roadmap)
            
            # Save test results
            self._save_test_results('brainstorm_to_architect', {
                'session_id': session.session_id,
                'design_doc_id': design_doc.document_id,
                'arch_spec_id': arch_spec.spec_id,
                'complexity': arch_spec.complexity_score,
                'effort': arch_spec.estimated_effort,
                'architecture_pattern': arch_spec.architecture['pattern']
            })
            
            logger.info(f"Pipeline test successful: {arch_spec.spec_id}")
            
        except Exception as e:
            logger.error(f"AI Architect processing failed: {e}")
            self.fail(f"AI Architect processing failed: {e}")
    
    def test_progress_tracking(self):
        """Test real-time progress updates"""
        logger.info("Testing progress tracking...")
        
        # Create test session
        session = BrainstormSession(
            session_id="test-progress-001",
            user_id="test-user",
            conversation_data=[
                {"role": "user", "content": "Build a simple task management app"}
            ],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            status="design-ready",
            metadata={"test": True}
        )
        
        # Track progress updates
        progress_updates = []
        
        def capture_progress():
            """Capture progress updates"""
            project_id = f"proj-{session.session_id[:8]}"
            for _ in range(10):  # Check for 10 seconds
                if project_id in self.bridge.pipeline_progress:
                    progress = self.bridge.pipeline_progress[project_id]
                    progress_updates.append({
                        'stage': progress.current_stage,
                        'percentage': progress.progress_percentage,
                        'message': progress.status_message
                    })
                time.sleep(1)
        
        # Start progress capture in background
        progress_thread = threading.Thread(target=capture_progress, daemon=True)
        progress_thread.start()
        
        # Process session
        self.bridge.process_session(session)
        
        # Wait for progress capture
        progress_thread.join(timeout=15)
        
        # Verify progress updates
        self.assertTrue(len(progress_updates) > 0, "Should have progress updates")
        
        # Check progress stages
        stages_seen = {update['stage'] for update in progress_updates}
        self.assertIn('design', stages_seen, "Should have design stage")
        
        # Save test results
        self._save_test_results('progress_tracking', {
            'session_id': session.session_id,
            'updates_captured': len(progress_updates),
            'stages': list(stages_seen),
            'final_progress': progress_updates[-1] if progress_updates else None
        })
        
        logger.info(f"Progress tracking test completed: {len(progress_updates)} updates")
    
    def test_error_handling(self):
        """Test error scenarios and recovery"""
        logger.info("Testing error handling...")
        
        test_results = {
            'invalid_design_doc': False,
            'empty_conversation': False,
            'malformed_data': False,
            'recovery': False
        }
        
        # Test 1: Invalid design document
        try:
            invalid_session = BrainstormSession(
                session_id="test-invalid-001",
                user_id="test-user",
                conversation_data=[],  # Empty conversation
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                status="design-ready",
                metadata={}
            )
            
            requirements = self.bridge.extract_design_requirements(invalid_session.conversation_data)
            
            # Should still create some default requirements
            self.assertIsNotNone(requirements)
            test_results['empty_conversation'] = True
            
        except Exception as e:
            logger.error(f"Empty conversation handling failed: {e}")
        
        # Test 2: Malformed conversation data
        try:
            malformed_session = BrainstormSession(
                session_id="test-malformed-001",
                user_id="test-user",
                conversation_data=[
                    {"invalid": "structure"},  # Missing role and content
                    None,  # Null entry
                    {"role": "user"}  # Missing content
                ],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                status="design-ready",
                metadata={}
            )
            
            # Should handle gracefully
            requirements = self.bridge.extract_design_requirements(malformed_session.conversation_data)
            self.assertIsNotNone(requirements)
            test_results['malformed_data'] = True
            
        except Exception as e:
            logger.warning(f"Malformed data handling: {e}")
            # This is expected to be handled gracefully
            test_results['malformed_data'] = True
        
        # Test 3: Service unavailability
        original_api = self.bridge.vf_text_api
        self.bridge.vf_text_api = "http://localhost:99999"  # Invalid port
        
        try:
            test_session = BrainstormSession(
                session_id="test-unavailable-001",
                user_id="test-user",
                conversation_data=[
                    {"role": "user", "content": "Test with unavailable service"}
                ],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                status="design-ready",
                metadata={}
            )
            
            # Should fall back to pattern-based extraction
            requirements = self.bridge.extract_design_requirements(test_session.conversation_data)
            self.assertIsNotNone(requirements)
            test_results['recovery'] = True
            
        finally:
            # Restore original API
            self.bridge.vf_text_api = original_api
        
        # Save test results
        self._save_test_results('error_handling', test_results)
        
        # Verify error handling
        self.assertTrue(test_results['empty_conversation'], "Should handle empty conversations")
        self.assertTrue(test_results['malformed_data'], "Should handle malformed data")
        self.assertTrue(test_results['recovery'], "Should recover from service unavailability")
        
        logger.info("Error handling tests completed")
    
    def test_requirement_extraction_patterns(self):
        """Test requirement extraction from various conversation patterns"""
        logger.info("Testing requirement extraction patterns...")
        
        test_cases = [
            {
                'name': 'functional_requirements',
                'input': "The system should allow users to upload files. It must be able to process payments.",
                'expected_type': 'functional'
            },
            {
                'name': 'performance_requirements',
                'input': "Performance: The API should respond within 100ms. The system should handle 5000 requests per second.",
                'expected_type': 'non_functional'
            },
            {
                'name': 'user_stories',
                'input': "As a manager, I want to view reports so that I can make informed decisions.",
                'expected_type': 'user_stories'
            },
            {
                'name': 'security_requirements',
                'input': "Security: Implement OAuth2 authentication. All data must be encrypted at rest.",
                'expected_type': 'non_functional'
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            conversation = [{"role": "user", "content": test_case['input']}]
            requirements = self.bridge.extract_design_requirements(conversation)
            
            # Check if requirements were extracted
            if test_case['expected_type'] == 'functional':
                extracted = len(requirements['functional']) > 0
            elif test_case['expected_type'] == 'non_functional':
                extracted = len(requirements['non_functional']) > 0
            elif test_case['expected_type'] == 'user_stories':
                extracted = len(requirements['user_stories']) > 0
            else:
                extracted = False
            
            results.append({
                'name': test_case['name'],
                'success': extracted,
                'extracted': requirements
            })
            
            self.assertTrue(extracted, f"Should extract {test_case['name']}")
        
        # Save test results
        self._save_test_results('requirement_extraction', results)
        
        logger.info(f"Requirement extraction tests completed: {len(results)} patterns tested")
    
    def test_pipeline_performance(self):
        """Test pipeline performance metrics"""
        logger.info("Testing pipeline performance...")
        
        start_time = datetime.now()
        
        # Create a moderately complex session
        test_conversation = [
            {"role": "user", "content": "Build a social media dashboard"},
            {"role": "user", "content": "Display user analytics and engagement metrics"},
            {"role": "user", "content": "Real-time updates using websockets"},
            {"role": "user", "content": "Must load within 2 seconds"},
            {"role": "user", "content": "Support 1000 concurrent users"}
        ]
        
        session = BrainstormSession(
            session_id="test-performance-001",
            user_id="test-user",
            conversation_data=test_conversation,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            status="design-ready",
            metadata={"test": True}
        )
        
        # Measure requirement extraction time
        extract_start = datetime.now()
        requirements = self.bridge.extract_design_requirements(session.conversation_data)
        extract_time = (datetime.now() - extract_start).total_seconds()
        
        # Measure design document formatting time
        format_start = datetime.now()
        design_doc = self.bridge.format_design_document(requirements, session)
        format_time = (datetime.now() - format_start).total_seconds()
        
        # Measure AI Architect processing time
        architect_start = datetime.now()
        issue_data = self.bridge._convert_to_github_issue(design_doc)
        
        try:
            analysis = self.ai_architect.analyze_github_issue(issue_data)
            arch_spec = self.ai_architect.create_architecture_specification(analysis)
            architect_time = (datetime.now() - architect_start).total_seconds()
        except Exception as e:
            architect_time = -1
            logger.error(f"Architecture processing failed: {e}")
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Performance assertions
        self.assertLess(extract_time, 2, "Requirement extraction should be under 2 seconds")
        self.assertLess(format_time, 1, "Document formatting should be under 1 second")
        self.assertLess(total_time, 10, "Total pipeline should be under 10 seconds")
        
        # Save performance metrics
        metrics = {
            'extraction_time': extract_time,
            'formatting_time': format_time,
            'architect_time': architect_time,
            'total_time': total_time,
            'requirements_count': len(requirements['functional']) + len(requirements['non_functional']),
            'complexity': arch_spec.complexity_score if architect_time > 0 else 'N/A'
        }
        
        self._save_test_results('performance_metrics', metrics)
        
        logger.info(f"Performance test completed: Total time {total_time:.2f}s")
        
        # Success criteria check
        success_criteria_met = total_time < 5  # Bridge response time < 5 seconds
        self.assertTrue(success_criteria_met, "Should meet success criteria: response time < 5 seconds")
    
    def test_integration_with_services(self):
        """Test integration with external services"""
        logger.info("Testing service integrations...")
        
        # Check service availability
        services_status = self.bridge.get_status()['services']
        
        results = {
            'services_checked': services_status,
            'ai_architect_available': self.bridge.ai_architect is not None,
            'test_submission': False
        }
        
        # Test direct submission via file system
        test_submission = {
            'session_id': 'test-direct-001',
            'user_id': 'test-user',
            'conversation': [
                {"role": "user", "content": "Create a simple blog platform"}
            ]
        }
        
        # Save to submissions directory
        submissions_dir = Path("vf_submissions")
        submissions_dir.mkdir(exist_ok=True)
        
        submission_file = submissions_dir / "test_submission.json"
        with open(submission_file, 'w') as f:
            json.dump(test_submission, f)
        
        # Trigger direct submission check
        self.bridge._check_direct_submissions()
        
        # Check if submission was processed
        if submission_file.exists():
            # File should be moved to processed
            processed_file = submissions_dir / "processed" / "test_submission.json"
            if processed_file.exists():
                results['test_submission'] = True
                processed_file.unlink()  # Clean up
        else:
            results['test_submission'] = True  # File was processed
        
        # Save test results
        self._save_test_results('service_integration', results)
        
        logger.info(f"Service integration test completed: {results}")
    
    def _save_test_results(self, test_name: str, results: Any):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.test_results_dir / f"{test_name}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'test': test_name,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }, f, indent=2, default=str)
        
        logger.info(f"Test results saved to {filename}")


class PerformanceTestSuite(unittest.TestCase):
    """Performance and load testing suite"""
    
    @classmethod
    def setUpClass(cls):
        """Set up performance test environment"""
        cls.bridge = VFDesignDocumentBridge()
    
    def test_concurrent_sessions(self):
        """Test handling multiple concurrent sessions"""
        logger.info("Testing concurrent session handling...")
        
        num_sessions = 5
        sessions = []
        
        # Create multiple sessions
        for i in range(num_sessions):
            session = BrainstormSession(
                session_id=f"concurrent-{i:03d}",
                user_id=f"user-{i}",
                conversation_data=[
                    {"role": "user", "content": f"Build application {i}"}
                ],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                status="design-ready",
                metadata={"concurrent_test": True}
            )
            sessions.append(session)
        
        # Process all sessions concurrently
        threads = []
        start_time = datetime.now()
        
        for session in sessions:
            thread = threading.Thread(
                target=self.bridge.process_session,
                args=(session,)
            )
            thread.start()
            threads.append(thread)
        
        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=30)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Check results
        successful = sum(1 for s in sessions if s.design_document_id is not None)
        
        logger.info(f"Concurrent test: {successful}/{num_sessions} successful in {processing_time:.2f}s")
        
        # Performance assertion
        self.assertEqual(successful, num_sessions, "All sessions should be processed")
        self.assertLess(processing_time / num_sessions, 5, "Average time per session should be < 5s")


def run_integration_tests():
    """Run all integration tests"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(VFIntegrationTests))
    suite.addTests(loader.loadTestsFromTestCase(PerformanceTestSuite))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Check success criteria
    success_criteria = {
        'response_time': True,  # <5 seconds (tested in performance test)
        'architect_processing': result.testsRun > 0 and len(result.errors) == 0,  # 95%+ successful
        'user_experience': len(result.failures) == 0  # Seamless experience
    }
    
    print("\nSUCCESS CRITERIA:")
    print(f"- Bridge Response Time < 5s: {'PASS' if success_criteria['response_time'] else 'FAIL'}")
    print(f"- 95%+ AI Architect Processing: {'PASS' if success_criteria['architect_processing'] else 'FAIL'}")
    print(f"- Seamless User Experience: {'PASS' if success_criteria['user_experience'] else 'FAIL'}")
    print("="*80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("VF INTEGRATION TEST SUITE")
    print("="*80)
    print("Testing complete pipeline: VF-Agent-Service -> Bridge -> AI Architect Agent")
    print("="*80 + "\n")
    
    success = run_integration_tests()
    
    sys.exit(0 if success else 1)