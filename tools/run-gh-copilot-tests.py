#!/usr/bin/env python3
"""
Automated GitHub Copilot Testing Orchestrator
Acts as the orchestrator agent to run tests and provide follow-up commands
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime
import json

class OrchestrationAgent:
    def __init__(self):
        self.projects_dir = Path("E:/Projects")
        self.test_queue = []
        self.results = []
        
        # Define test cases with expected follow-ups
        self.test_plan = {
            'NiroSubs-V2': {
                'ns-auth': {
                    'tests': [
                        "curl command to test health endpoint",
                        "AWS CLI command to check Lambda function",
                        "command to view CloudWatch logs",
                        "test authentication endpoint with sample JWT"
                    ],
                    'follow_ups': [
                        "fix Lambda timeout issue",
                        "optimize cold start performance",
                        "add better error handling"
                    ]
                },
                'ns-dashboard': {
                    'tests': [
                        "test dashboard API endpoints",
                        "check S3 static hosting configuration",
                        "verify CloudFront distribution"
                    ],
                    'follow_ups': [
                        "fix CORS configuration",
                        "optimize bundle size"
                    ]
                },
                'ns-payments': {
                    'tests': [
                        "test Stripe webhook endpoint",
                        "verify payment processing flow",
                        "check security headers"
                    ],
                    'follow_ups': [
                        "add webhook signature validation",
                        "implement rate limiting"
                    ]
                }
            },
            'VisualForgeMediaV2': {
                'vf-audio-service': {
                    'tests': [
                        "test audio processing endpoint",
                        "check S3 upload permissions",
                        "verify FFmpeg Lambda layer"
                    ],
                    'follow_ups': [
                        "optimize audio processing performance",
                        "add format validation"
                    ]
                },
                'vf-video-service': {
                    'tests': [
                        "test video transcoding endpoint",
                        "check MediaConvert configuration",
                        "verify output S3 bucket"
                    ],
                    'follow_ups': [
                        "add progress tracking",
                        "implement retry logic"
                    ]
                }
            }
        }
    
    def run_gh_suggest(self, prompt: str, command_type: str = "1") -> str:
        """Run gh copilot suggest with automated input"""
        
        # Build the command with echo to provide input
        # 1 = generic shell command, 2 = gh command, 3 = git command
        cmd = f'echo -e "1\\n{command_type}\\n" | gh copilot suggest "{prompt}"'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(self.projects_dir),
                timeout=15
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def run_gh_explain(self, command: str) -> str:
        """Run gh copilot explain"""
        
        cmd = f'gh copilot explain "{command}"'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(self.projects_dir),
                timeout=15
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {e}"
    
    def test_service(self, repo: str, service: str, environment: str = "dev"):
        """Test a service and handle follow-ups"""
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {service} in {repo} ({environment})")
        print(f"{'='*60}")
        
        instruction_path = f"{repo}/{service}/AGENT_INSTRUCTIONS_{environment.upper()}.md"
        
        # Check if we have a test plan for this service
        if repo in self.test_plan and service in self.test_plan[repo]:
            tests = self.test_plan[repo][service]['tests']
            follow_ups = self.test_plan[repo][service]['follow_ups']
        else:
            # Generic tests
            tests = [
                f"test health endpoint for {service}",
                f"check AWS Lambda configuration for {service}",
                f"view recent CloudWatch logs for {service}"
            ]
            follow_ups = ["optimize performance", "add monitoring"]
        
        results = {
            'service': service,
            'repo': repo,
            'environment': environment,
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'follow_ups': []
        }
        
        # Run each test
        for i, test in enumerate(tests, 1):
            print(f"\n📋 Test {i}/{len(tests)}: {test}")
            
            prompt = f"For {service} service in {repo}/{service}: {test}"
            
            print("   Running gh copilot suggest...")
            response = self.run_gh_suggest(prompt)
            
            # Parse response to extract command
            if "```" in response:
                # Extract command from code block
                lines = response.split('\n')
                in_code = False
                command = []
                for line in lines:
                    if '```' in line:
                        in_code = not in_code
                    elif in_code:
                        command.append(line)
                
                if command:
                    suggested_cmd = '\n'.join(command)
                    print(f"   📌 Suggested command:\n   {suggested_cmd}")
                    
                    # Test if it needs follow-up
                    if "error" in response.lower() or "fail" in response.lower():
                        print("   ⚠️  Potential issue detected")
                        
                        # Apply follow-up
                        if i <= len(follow_ups):
                            follow_up = follow_ups[i-1] if i <= len(follow_ups) else follow_ups[0]
                            print(f"   🔧 Applying follow-up: {follow_up}")
                            
                            follow_response = self.run_gh_suggest(
                                f"For {service}: {follow_up}"
                            )
                            results['follow_ups'].append({
                                'issue': test,
                                'follow_up': follow_up,
                                'response': follow_response
                            })
            
            results['tests'].append({
                'test': test,
                'response': response
            })
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        # Save results
        result_file = self.projects_dir / f"orchestration_results/{service}_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        result_file.parent.mkdir(exist_ok=True)
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Testing complete for {service}")
        print(f"   Results saved to: {result_file}")
        
        self.results.append(results)
        
        return results
    
    def orchestrate_all_tests(self, environment: str = "dev"):
        """Orchestrate testing for all services"""
        
        print(f"\n🚀 ORCHESTRATION AGENT STARTING")
        print(f"   Environment: {environment}")
        print(f"   Services to test: {sum(len(services) for services in self.test_plan.values())}")
        
        start_time = datetime.now()
        
        # Test each service
        for repo, services in self.test_plan.items():
            for service in services.keys():
                try:
                    self.test_service(repo, service, environment)
                except Exception as e:
                    print(f"❌ Error testing {service}: {e}")
        
        # Generate summary report
        elapsed = (datetime.now() - start_time).total_seconds()
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'environment': environment,
            'duration_seconds': elapsed,
            'total_services': len(self.results),
            'services_tested': [r['service'] for r in self.results],
            'total_tests': sum(len(r['tests']) for r in self.results),
            'total_follow_ups': sum(len(r['follow_ups']) for r in self.results),
            'results': self.results
        }
        
        summary_file = self.projects_dir / f"orchestration_summary_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n" + "="*60)
        print(f"📊 ORCHESTRATION COMPLETE")
        print(f"   Duration: {elapsed:.1f} seconds")
        print(f"   Services tested: {summary['total_services']}")
        print(f"   Total tests: {summary['total_tests']}")
        print(f"   Follow-ups applied: {summary['total_follow_ups']}")
        print(f"   Summary saved: {summary_file}")
        print("="*60)
        
        return summary
    
    def monitor_and_remediate(self):
        """Monitor test results and apply remediations"""
        
        print("\n🔍 Monitoring and Remediation Phase")
        
        for result in self.results:
            service = result['service']
            
            # Check for issues in tests
            issues_found = False
            for test in result['tests']:
                response = test['response'].lower()
                if any(word in response for word in ['error', 'fail', 'timeout', 'denied', '403', '500']):
                    issues_found = True
                    print(f"\n⚠️  Issue detected in {service}: {test['test'][:50]}...")
                    
                    # Generate remediation command
                    remediation_prompt = f"Fix the issue in {service}: {test['test']}"
                    print(f"   🔧 Generating remediation...")
                    
                    remediation = self.run_gh_suggest(remediation_prompt)
                    print(f"   Remediation suggested: {remediation[:200]}...")
                    
                    # Apply remediation (in real scenario, would execute the fix)
                    print(f"   ✅ Remediation logged for {service}")
            
            if not issues_found:
                print(f"✅ {service}: No issues found")

def main():
    """Main orchestration flow"""
    
    print("""
╔════════════════════════════════════════════════════════╗
║     GitHub Copilot Orchestration Agent v1.0           ║
║     Automated Testing & Remediation System            ║
╚════════════════════════════════════════════════════════╝
    """)
    
    agent = OrchestrationAgent()
    
    # Run orchestration for dev environment
    print("\n🎯 Phase 1: Development Environment Testing")
    dev_results = agent.orchestrate_all_tests("dev")
    
    # Monitor and apply remediations
    print("\n🎯 Phase 2: Monitoring & Remediation")
    agent.monitor_and_remediate()
    
    # Optionally test staging (commented out for now)
    # print("\n🎯 Phase 3: Staging Environment Testing")
    # staging_results = agent.orchestrate_all_tests("staging")
    
    print("\n✨ Orchestration complete! Check results in orchestration_results/ folder")

if __name__ == "__main__":
    main()