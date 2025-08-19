#!/usr/bin/env python3
"""
Test Real AI Agents Locally Before EC2 Deployment
Verifies that the agents can execute without errors
"""

import sys
import os
import subprocess
import json
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LocalAgentTester')

class LocalAgentTester:
    """Tests real agents locally"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.agent_dir = self.base_dir / 'ai-agent-deployment'
        self.test_results = {}
        
    def test_qa_agent(self) -> bool:
        """Test the real QA agent"""
        logger.info("Testing Real QA Agent...")
        
        try:
            # Set environment variables for testing
            env = os.environ.copy()
            env['QA_BASE_DIR'] = str(self.base_dir)
            env['TEST_LIMIT_PER_SERVICE'] = '1'  # Only test 1 file per service
            env['GITHUB_TOKEN'] = 'test-token'  # Placeholder for testing
            
            # Run the agent with a short timeout
            qa_script = self.agent_dir / 'ai-qa-agent-real.py'
            
            if not qa_script.exists():
                logger.error(f"QA Agent script not found: {qa_script}")
                return False
                
            # Just check if the script can be imported and initialized
            script_content = f'''
import sys
sys.path.insert(0, r"{self.agent_dir}")
try:
    from pathlib import Path
    import os
    os.environ['QA_BASE_DIR'] = r"{self.base_dir}"
    os.environ['TEST_LIMIT_PER_SERVICE'] = '1'
    os.environ['GITHUB_TOKEN'] = 'test-token'
    
    # Import and initialize (don't run main)
    import importlib.util
    spec = importlib.util.spec_from_file_location("qa_agent", r"{qa_script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Try to create agent instance
    agent = module.RealAIQAAgent(r"{self.base_dir}")
    print("SUCCESS: QA Agent initialized successfully")
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
'''
            result = subprocess.run([
                sys.executable, '-c', script_content
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "SUCCESS" in result.stdout:
                logger.info("QA Agent test passed")
                self.test_results['qa_agent'] = {'status': 'passed', 'output': result.stdout}
                return True
            else:
                logger.error(f"QA Agent test failed: {result.stderr}")
                self.test_results['qa_agent'] = {'status': 'failed', 'error': result.stderr, 'output': result.stdout}
                return False
                
        except Exception as e:
            logger.error(f"QA Agent test error: {e}")
            self.test_results['qa_agent'] = {'status': 'error', 'error': str(e)}
            return False
            
    def test_developer_agent(self) -> bool:
        """Test the real Developer agent"""
        logger.info("Testing Real Developer Agent...")
        
        try:
            # Set environment variables for testing
            env = os.environ.copy()
            env['DEV_BASE_DIR'] = str(self.base_dir)
            env['GITHUB_TOKEN'] = 'test-token'  # Placeholder for testing
            
            dev_script = self.agent_dir / 'ai-developer-agent-real.py'
            
            if not dev_script.exists():
                logger.error(f"Developer Agent script not found: {dev_script}")
                return False
                
            # Just check if the script can be imported and initialized
            script_content = f'''
import sys
sys.path.insert(0, r"{self.agent_dir}")
try:
    from pathlib import Path
    import os
    os.environ['DEV_BASE_DIR'] = r"{self.base_dir}"
    os.environ['GITHUB_TOKEN'] = 'test-token'
    
    # Import and initialize (don't run main)
    import importlib.util
    spec = importlib.util.spec_from_file_location("dev_agent", r"{dev_script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Try to create agent instance
    agent = module.RealAIDeveloperAgent(r"{self.base_dir}")
    print("SUCCESS: Developer Agent initialized successfully")
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
'''
            result = subprocess.run([
                sys.executable, '-c', script_content
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "SUCCESS" in result.stdout:
                logger.info("Developer Agent test passed")
                self.test_results['developer_agent'] = {'status': 'passed', 'output': result.stdout}
                return True
            else:
                logger.error(f"Developer Agent test failed: {result.stderr}")
                self.test_results['developer_agent'] = {'status': 'failed', 'error': result.stderr, 'output': result.stdout}
                return False
                
        except Exception as e:
            logger.error(f"Developer Agent test error: {e}")
            self.test_results['developer_agent'] = {'status': 'error', 'error': str(e)}
            return False
            
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        logger.info("Checking dependencies...")
        
        required_modules = [
            'requests',
            'json',
            'subprocess', 
            'pathlib',
            'datetime',
            'logging',
            'os',
            'sys',
            'uuid',
            'time'
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
                
        if missing_modules:
            logger.error(f"Missing required modules: {missing_modules}")
            self.test_results['dependencies'] = {'status': 'failed', 'missing': missing_modules}
            return False
        else:
            logger.info("All required dependencies available")
            self.test_results['dependencies'] = {'status': 'passed'}
            return True
            
    def check_repository_structure(self) -> bool:
        """Check if the expected repository structure exists"""
        logger.info("Checking repository structure...")
        
        expected_paths = [
            self.base_dir / 'VisualForgeMediaV2',
            self.base_dir / 'ai-agent-deployment',
            self.agent_dir / 'ai-qa-agent-real.py',
            self.agent_dir / 'ai-developer-agent-real.py'
        ]
        
        missing_paths = []
        
        for path in expected_paths:
            if not path.exists():
                missing_paths.append(str(path))
                
        if missing_paths:
            logger.warning(f"Missing paths (may not be critical): {missing_paths}")
            self.test_results['structure'] = {'status': 'partial', 'missing': missing_paths}
            return True  # Not critical for agent initialization
        else:
            logger.info("Repository structure looks good")
            self.test_results['structure'] = {'status': 'passed'}
            return True
            
    def run_all_tests(self) -> bool:
        """Run all tests"""
        logger.info("Starting local agent tests...")
        
        results = []
        
        # Check dependencies
        results.append(self.check_dependencies())
        
        # Check repository structure
        results.append(self.check_repository_structure())
        
        # Test agents
        results.append(self.test_qa_agent())
        results.append(self.test_developer_agent())
        
        return all(results)
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("LOCAL AGENT TEST RESULTS")
        print("="*60)
        
        for test_name, result in self.test_results.items():
            status = result['status']
            if status == 'passed':
                print(f"PASS {test_name.replace('_', ' ').title()}: PASSED")
            elif status == 'partial':
                print(f"PART {test_name.replace('_', ' ').title()}: PARTIAL")
            else:
                print(f"FAIL {test_name.replace('_', ' ').title()}: FAILED")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
                    
        print("\n" + "="*60)
        
        all_passed = all(r['status'] in ['passed', 'partial'] for r in self.test_results.values())
        
        if all_passed:
            print("ALL TESTS PASSED - Ready for EC2 deployment!")
            print("Next step: Run ./deploy-real-agents-to-ec2.sh")
        else:
            print("Some tests failed - Fix issues before deployment")
            
        return all_passed
        
    def save_results(self):
        """Save test results to file"""
        results_file = self.base_dir / 'local-agent-test-results.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
            
        logger.info(f"Test results saved to: {results_file}")

def main():
    """Main function"""
    print("Testing Real AI Agents Locally")
    print("="*40)
    
    tester = LocalAgentTester()
    
    try:
        success = tester.run_all_tests()
        tester.save_results()
        tester.print_summary()
        
        if success:
            print("\nLocal testing completed successfully!")
            sys.exit(0)
        else:
            print("\nLocal testing failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()