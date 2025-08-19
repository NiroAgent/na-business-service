#!/usr/bin/env python3
"""
Real AI QA Agent - Executes actual Playwright tests and creates GitHub issues for failures
Replaces the placeholder/simulation version with real test execution
"""

import json
import os
import sys
import subprocess
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid
import time
import tempfile
import shutil
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RealAIQAAgent')

@dataclass
class TestResult:
    """Result of a real test execution"""
    test_id: str
    test_file: str
    test_name: str
    status: str  # passed, failed, skipped
    error_message: Optional[str]
    duration: float
    output: str
    screenshot_path: Optional[str] = None

@dataclass
class TestSuite:
    """Collection of tests from a service"""
    service_name: str
    test_directory: str
    results: List[TestResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_time: float

class GitHubIntegration:
    """Handles GitHub issue creation for test failures"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Repository mappings for different services
        self.repo_mappings = {
            'vf-dashboard-service': 'VisualForgeMediaV2',
            'vf-video-service': 'VisualForgeMediaV2', 
            'vf-audio-service': 'VisualForgeMediaV2',
            'vf-image-service': 'VisualForgeMediaV2',
            'vf-text-service': 'VisualForgeMediaV2'
        }
        
    def create_issue_for_failure(self, test_result: TestResult, service_name: str) -> Optional[str]:
        """Create a GitHub issue for a failed test"""
        if not self.github_token:
            logger.warning("No GitHub token available, cannot create issues")
            return None
            
        repo = self.repo_mappings.get(service_name, 'VisualForgeMediaV2')
        owner = 'YourGitHubOrg'  # Replace with actual GitHub org/username
        
        # Create issue title
        title = f"🚨 Test Failure: {test_result.test_name} in {service_name}"
        
        # Create detailed issue body
        body = self._create_issue_body(test_result, service_name)
        
        # Create issue via GitHub API
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        
        issue_data = {
            'title': title,
            'body': body,
            'labels': ['bug', 'test-failure', f'service:{service_name}', 'automated']
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=issue_data)
            if response.status_code == 201:
                issue_url = response.json()['html_url']
                logger.info(f"Created GitHub issue: {issue_url}")
                return issue_url
            else:
                logger.error(f"Failed to create GitHub issue: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return None
    
    def _create_issue_body(self, test_result: TestResult, service_name: str) -> str:
        """Create detailed issue body"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        body = f"""## Test Failure Report

**Service:** {service_name}
**Test File:** `{test_result.test_file}`
**Test Name:** `{test_result.test_name}`
**Timestamp:** {timestamp}
**Duration:** {test_result.duration:.2f}s

### Error Details
```
{test_result.error_message or 'No error message available'}
```

### Test Output
```
{test_result.output}
```

### Reproduction Steps
1. Navigate to the {service_name} directory
2. Run the specific test: `npm run test -- {test_result.test_file}`
3. Observe the failure

### Environment
- **Agent:** Real AI QA Agent
- **Test Framework:** Playwright
- **Node.js Version:** Latest
- **Service Port:** Varies by service

### Next Steps
- [ ] Investigate the root cause of the failure
- [ ] Fix the underlying issue
- [ ] Verify the fix with local testing
- [ ] Update tests if necessary
- [ ] Close this issue once resolved

---
*This issue was automatically created by the Real AI QA Agent*
"""
        return body

class PlaywrightTestRunner:
    """Executes real Playwright tests"""
    
    def __init__(self, base_directory: str):
        self.base_directory = Path(base_directory)
        self.github = GitHubIntegration()
        
        # Service directories mapping
        self.service_dirs = {
            'vf-dashboard-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-dashboard-service',
            'vf-video-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-video-service',
            'vf-audio-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-audio-service',
            'vf-image-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-image-service',
            'vf-text-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-text-service'
        }
        
    def discover_test_files(self, service_name: str) -> List[Path]:
        """Discover all Playwright test files in a service"""
        service_dir = self.service_dirs.get(service_name)
        if not service_dir or not service_dir.exists():
            logger.warning(f"Service directory not found: {service_name}")
            return []
            
        test_dir = service_dir / 'mfe' / 'tests'
        if not test_dir.exists():
            logger.warning(f"Test directory not found: {test_dir}")
            return []
            
        # Find all .spec.ts and .test.ts files
        test_files = []
        for pattern in ['*.spec.ts', '*.test.ts', '*.spec.js', '*.test.js']:
            test_files.extend(test_dir.rglob(pattern))
            
        logger.info(f"Found {len(test_files)} test files in {service_name}")
        return test_files
        
    def run_service_tests(self, service_name: str, test_limit: Optional[int] = None) -> TestSuite:
        """Run all tests for a specific service"""
        logger.info(f"Running tests for service: {service_name}")
        
        start_time = time.time()
        test_files = self.discover_test_files(service_name)
        
        if test_limit:
            test_files = test_files[:test_limit]
            
        results = []
        service_dir = self.service_dirs.get(service_name)
        
        if not service_dir or not service_dir.exists():
            logger.error(f"Service directory not found: {service_name}")
            return TestSuite(service_name, str(service_dir), [], 0, 0, 0, 0.0)
            
        # Change to service directory
        original_dir = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Install dependencies if needed
            self._ensure_dependencies_installed()
            
            for test_file in test_files:
                result = self._run_single_test(test_file, service_name)
                results.append(result)
                
                # Create GitHub issue for failures
                if result.status == 'failed':
                    self.github.create_issue_for_failure(result, service_name)
                    
        finally:
            os.chdir(original_dir)
            
        execution_time = time.time() - start_time
        passed_tests = sum(1 for r in results if r.status == 'passed')
        failed_tests = sum(1 for r in results if r.status == 'failed')
        
        test_suite = TestSuite(
            service_name=service_name,
            test_directory=str(service_dir / 'mfe' / 'tests'),
            results=results,
            total_tests=len(results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            execution_time=execution_time
        )
        
        logger.info(f"Completed {service_name}: {passed_tests}/{len(results)} tests passed")
        return test_suite
        
    def _ensure_dependencies_installed(self):
        """Ensure npm dependencies are installed"""
        if Path('package.json').exists() and not Path('node_modules').exists():
            logger.info("Installing npm dependencies...")
            try:
                subprocess.run(['npm', 'install'], check=True, capture_output=True, text=True, timeout=300)
                logger.info("Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install dependencies: {e}")
            except subprocess.TimeoutExpired:
                logger.warning("Dependency installation timed out")
                
    def _run_single_test(self, test_file: Path, service_name: str) -> TestResult:
        """Run a single Playwright test"""
        test_id = f"test-{uuid.uuid4().hex[:8]}"
        relative_path = test_file.relative_to(Path.cwd())
        
        logger.info(f"Running test: {relative_path}")
        
        start_time = time.time()
        
        try:
            # Run Playwright test with JSON reporter
            cmd = ['npx', 'playwright', 'test', str(relative_path), '--reporter=json']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test
            )
            
            duration = time.time() - start_time
            
            # Parse result
            if result.returncode == 0:
                status = 'passed'
                error_message = None
            else:
                status = 'failed'
                error_message = result.stderr or "Test failed without specific error message"
            
            return TestResult(
                test_id=test_id,
                test_file=str(relative_path),
                test_name=test_file.stem,
                status=status,
                error_message=error_message,
                duration=duration,
                output=result.stdout,
                screenshot_path=None  # Could be enhanced to capture screenshots
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(
                test_id=test_id,
                test_file=str(relative_path),
                test_name=test_file.stem,
                status='failed',
                error_message='Test execution timed out after 5 minutes',
                duration=duration,
                output='Timeout occurred'
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_id=test_id,
                test_file=str(relative_path),
                test_name=test_file.stem,
                status='failed',
                error_message=f'Test execution error: {str(e)}',
                duration=duration,
                output=str(e)
            )

class RealAIQAAgent:
    """Real AI QA Agent that executes actual tests"""
    
    def __init__(self, base_directory: str = '/home/ubuntu'):
        self.logger = logger
        self.base_directory = base_directory
        self.test_runner = PlaywrightTestRunner(base_directory)
        self.report_directory = Path(base_directory) / 'qa_reports'
        self.report_directory.mkdir(exist_ok=True)
        
        logger.info("Real AI QA Agent initialized - executing actual Playwright tests")
        
    def run_all_service_tests(self, test_limit_per_service: Optional[int] = 5) -> Dict[str, TestSuite]:
        """Run tests for all services"""
        logger.info("Starting comprehensive test execution across all services")
        
        services = list(self.test_runner.service_dirs.keys())
        results = {}
        
        for service in services:
            try:
                test_suite = self.test_runner.run_service_tests(service, test_limit_per_service)
                results[service] = test_suite
                
                # Log summary for this service
                logger.info(f"Service {service}: {test_suite.passed_tests}/{test_suite.total_tests} passed")
                
            except Exception as e:
                logger.error(f"Error testing service {service}: {e}")
                # Create empty test suite for failed service
                results[service] = TestSuite(service, "", [], 0, 0, 0, 0.0)
                
        return results
        
    def generate_comprehensive_report(self, test_suites: Dict[str, TestSuite]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        timestamp = datetime.now().isoformat()
        
        total_tests = sum(suite.total_tests for suite in test_suites.values())
        total_passed = sum(suite.passed_tests for suite in test_suites.values())
        total_failed = sum(suite.failed_tests for suite in test_suites.values())
        total_time = sum(suite.execution_time for suite in test_suites.values())
        
        report = {
            'report_id': f'real-qa-{uuid.uuid4().hex[:8]}',
            'timestamp': timestamp,
            'agent_type': 'Real AI QA Agent',
            'execution_type': 'Actual Playwright Tests',
            'summary': {
                'total_services': len(test_suites),
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'success_rate': round((total_passed / total_tests * 100) if total_tests > 0 else 0, 2),
                'total_execution_time': round(total_time, 2)
            },
            'service_results': {}
        }
        
        # Add detailed results for each service
        for service_name, suite in test_suites.items():
            report['service_results'][service_name] = {
                'total_tests': suite.total_tests,
                'passed_tests': suite.passed_tests,
                'failed_tests': suite.failed_tests,
                'execution_time': round(suite.execution_time, 2),
                'success_rate': round((suite.passed_tests / suite.total_tests * 100) if suite.total_tests > 0 else 0, 2),
                'test_results': [
                    {
                        'test_id': result.test_id,
                        'test_file': result.test_file,
                        'test_name': result.test_name,
                        'status': result.status,
                        'duration': round(result.duration, 2),
                        'error_message': result.error_message,
                        'has_github_issue': result.status == 'failed'
                    }
                    for result in suite.results
                ]
            }
            
        return report
        
    def save_report(self, report: Dict[str, Any]) -> str:
        """Save report to file"""
        report_file = self.report_directory / f"{report['report_id']}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Report saved to: {report_file}")
        return str(report_file)
        
    def print_summary(self, report: Dict[str, Any]):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("🤖 REAL AI QA AGENT - TEST EXECUTION SUMMARY")
        print("="*60)
        
        summary = report['summary']
        print(f"📊 Overall Results:")
        print(f"   Services Tested: {summary['total_services']}")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['total_passed']} ✅")
        print(f"   Failed: {summary['total_failed']} ❌")
        print(f"   Success Rate: {summary['success_rate']}%")
        print(f"   Execution Time: {summary['total_execution_time']}s")
        
        print(f"\n📋 Service Breakdown:")
        for service_name, results in report['service_results'].items():
            status = "✅" if results['failed_tests'] == 0 else "❌"
            print(f"   {status} {service_name}: {results['passed_tests']}/{results['total_tests']} passed ({results['success_rate']}%)")
            
        if summary['total_failed'] > 0:
            print(f"\n🚨 GitHub Issues Created: {summary['total_failed']} issues for failed tests")
            print("   Check your GitHub repository for detailed failure reports")
            
        print("\n" + "="*60)

def main():
    """Main execution function"""
    logger.info("🚀 Starting Real AI QA Agent")
    
    # Initialize agent with EC2 paths
    base_dir = os.getenv('QA_BASE_DIR', '/home/ubuntu')
    agent = RealAIQAAgent(base_dir)
    
    try:
        # Run tests for all services (limit to 3 tests per service for demo)
        test_limit = int(os.getenv('TEST_LIMIT_PER_SERVICE', '3'))
        test_suites = agent.run_all_service_tests(test_limit)
        
        # Generate comprehensive report
        report = agent.generate_comprehensive_report(test_suites)
        
        # Save report
        report_file = agent.save_report(report)
        
        # Print summary
        agent.print_summary(report)
        
        logger.info("✅ Real AI QA Agent execution completed")
        
    except Exception as e:
        logger.error(f"❌ Real AI QA Agent failed: {e}")
        raise

if __name__ == "__main__":
    main()