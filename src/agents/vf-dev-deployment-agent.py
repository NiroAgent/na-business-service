#!/usr/bin/env python3
"""
VF-Dev Deployment Agent
Ensures active progress on NiroSubs and VisualForge services in vf-dev environment
Creates and processes GitHub issues, monitors deployment status, runs tests
"""

import json
import time
import requests
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vf_dev_deployment_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('VFDevDeploymentAgent')

class VFDevDeploymentAgent:
    """
    Automated agent for VF-Dev deployment monitoring and issue management
    """
    
    def __init__(self):
        self.agent_id = "vf-dev-deployment-001"
        self.services = {
            'visual_forge': {
                'ns-auth': '/e/Projects/NiroSubs-V2/ns-auth',
                'ns-dashboard': '/e/Projects/NiroSubs-V2/ns-dashboard',
                'ns-payments': '/e/Projects/NiroSubs-V2/ns-payments',
                'ns-user': '/e/Projects/NiroSubs-V2/ns-user'
            },
            'niro_subs': {
                'vf-audio-service': '/e/Projects/VisualForgeMediaV2/vf-audio-service',
                'vf-video-service': '/e/Projects/VisualForgeMediaV2/vf-video-service',
                'vf-text-service': '/e/Projects/VisualForgeMediaV2/vf-text-service',
                'vf-agent-service': '/e/Projects/VisualForgeMediaV2/vf-agent-service'
            }
        }
        
        self.deployment_tasks = [
            "Verify service health checks",
            "Run integration tests",
            "Check deployment configurations", 
            "Validate environment variables",
            "Test service communications",
            "Monitor performance metrics",
            "Update documentation",
            "Create progress reports"
        ]
        
        self.github_integration = {
            'visual_forge': 'localhost:5006',
            'pm_workflow': 'localhost:5005',
            'dashboard': 'localhost:5003'
        }
        
        self.progress_tracking = {
            'last_check': None,
            'issues_created': 0,
            'issues_processed': 0,
            'services_tested': 0,
            'deployments_validated': 0
        }
        
    def check_service_health(self, service_path: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        try:
            # Check if service directory exists
            if not Path(service_path).exists():
                return {'status': 'missing', 'error': 'Service directory not found'}
            
            # Check for package.json or main files
            has_package = (Path(service_path) / 'package.json').exists()
            has_python = any(Path(service_path).glob('*.py'))
            has_docker = (Path(service_path) / 'Dockerfile').exists()
            
            # Check git status
            git_status = self._get_git_status(service_path)
            
            return {
                'status': 'active',
                'has_package_json': has_package,
                'has_python': has_python,
                'has_docker': has_docker,
                'git_status': git_status,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking service health for {service_path}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _get_git_status(self, service_path: str) -> Dict[str, Any]:
        """Get git status for a service"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=service_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                return {
                    'clean': len(changes) == 0,
                    'changes': len(changes),
                    'files': changes[:5]  # First 5 changed files
                }
            else:
                return {'error': 'Not a git repository or git error'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def create_deployment_issue(self, service_name: str, task: str) -> Dict[str, Any]:
        """Create a GitHub issue for deployment task"""
        issue_data = {
            'title': f"VF-Dev: {task} for {service_name}",
            'body': f"""## VF-Dev Deployment Task

**Service:** {service_name}
**Task:** {task}
**Environment:** vf-dev
**Priority:** High
**Agent:** {self.agent_id}

### Description
This issue tracks the deployment task: {task} for service {service_name} in the vf-dev environment.

### Acceptance Criteria
- [ ] Task completed successfully
- [ ] Service health verified
- [ ] Tests passing
- [ ] Documentation updated

### Environment Details
- **Environment:** vf-dev
- **Service Path:** {self.services.get('visual_forge', {}).get(service_name, self.services.get('niro_subs', {}).get(service_name, 'unknown'))}
- **Created:** {datetime.now().isoformat()}

### Related Services
{self._get_related_services(service_name)}
""",
            'labels': ['vf-dev', 'deployment', 'high-priority', 'automated'],
            'assignees': ['vf-dev-deployment-agent'],
            'milestone': 'VF-Dev Sprint'
        }
        
        # Save issue locally for processing
        issue_id = f"vfdev-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{service_name}"
        issue_file = Path(f"issues/{issue_id}.json")
        issue_file.parent.mkdir(exist_ok=True)
        
        with open(issue_file, 'w') as f:
            json.dump(issue_data, f, indent=2)
        
        logger.info(f"Created deployment issue: {issue_id}")
        self.progress_tracking['issues_created'] += 1
        
        return {'issue_id': issue_id, 'file': str(issue_file)}
    
    def _get_related_services(self, service_name: str) -> str:
        """Get related services for context"""
        if 'ns-' in service_name:
            return "Part of NiroSubs V2 ecosystem"
        elif 'vf-' in service_name:
            return "Part of VisualForge Media ecosystem"
        else:
            return "Independent service"
    
    def run_integration_tests(self, service_name: str, service_path: str) -> Dict[str, Any]:
        """Run integration tests for a service"""
        try:
            test_results = {
                'service': service_name,
                'timestamp': datetime.now().isoformat(),
                'tests': []
            }
            
            # Check for test files
            test_files = list(Path(service_path).glob('**/test*.py')) + \
                        list(Path(service_path).glob('**/test*.js')) + \
                        list(Path(service_path).glob('**/*test*.py'))
            
            if test_files:
                logger.info(f"Found {len(test_files)} test files for {service_name}")
                test_results['test_files_found'] = len(test_files)
                
                # Try to run tests
                for test_file in test_files[:3]:  # Run first 3 test files
                    try:
                        if test_file.suffix == '.py':
                            result = subprocess.run(
                                ['python', str(test_file)],
                                cwd=service_path,
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                        elif test_file.suffix == '.js':
                            result = subprocess.run(
                                ['npm', 'test'],
                                cwd=service_path,
                                capture_output=True,
                                text=True,
                                timeout=60
                            )
                        
                        test_results['tests'].append({
                            'file': str(test_file.name),
                            'status': 'passed' if result.returncode == 0 else 'failed',
                            'output': result.stdout[:500] + '...' if len(result.stdout) > 500 else result.stdout
                        })
                        
                    except subprocess.TimeoutExpired:
                        test_results['tests'].append({
                            'file': str(test_file.name),
                            'status': 'timeout',
                            'output': 'Test timed out after 30 seconds'
                        })
                    except Exception as e:
                        test_results['tests'].append({
                            'file': str(test_file.name),
                            'status': 'error',
                            'output': str(e)
                        })
            else:
                test_results['test_files_found'] = 0
                test_results['message'] = 'No test files found'
            
            self.progress_tracking['services_tested'] += 1
            return test_results
            
        except Exception as e:
            logger.error(f"Error running tests for {service_name}: {e}")
            return {'error': str(e), 'service': service_name}
    
    def validate_deployment_config(self, service_name: str, service_path: str) -> Dict[str, Any]:
        """Validate deployment configuration"""
        config_check = {
            'service': service_name,
            'path': service_path,
            'timestamp': datetime.now().isoformat(),
            'checks': []
        }
        
        # Check for essential files
        essential_files = [
            'package.json',
            'Dockerfile',
            'docker-compose.yml',
            '.env.example',
            'README.md'
        ]
        
        for file_name in essential_files:
            file_path = Path(service_path) / file_name
            config_check['checks'].append({
                'file': file_name,
                'exists': file_path.exists(),
                'size': file_path.stat().st_size if file_path.exists() else 0
            })
        
        # Check environment configuration
        env_file = Path(service_path) / '.env'
        env_example = Path(service_path) / '.env.example'
        
        config_check['environment'] = {
            'has_env': env_file.exists(),
            'has_env_example': env_example.exists(),
            'env_configured': env_file.exists() and env_file.stat().st_size > 0
        }
        
        self.progress_tracking['deployments_validated'] += 1
        return config_check
    
    def submit_to_ai_pipeline(self, issue_data: Dict[str, Any]) -> bool:
        """Submit issue to AI processing pipeline"""
        try:
            # Submit to Visual Forge AI for processing
            response = requests.post(
                f"http://{self.github_integration['visual_forge']}/api/process-issue",
                json=issue_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully submitted issue to AI pipeline")
                return True
            else:
                logger.warning(f"AI pipeline submission failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not reach AI pipeline: {e}")
            return False
    
    def generate_progress_report(self) -> Dict[str, Any]:
        """Generate deployment progress report"""
        report = {
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - getattr(self, 'start_time', time.time()),
            'progress': self.progress_tracking.copy(),
            'services': {},
            'summary': {}
        }
        
        # Check all services
        total_services = 0
        healthy_services = 0
        
        for category, services in self.services.items():
            report['services'][category] = {}
            for service_name, service_path in services.items():
                health = self.check_service_health(service_path)
                report['services'][category][service_name] = health
                total_services += 1
                if health.get('status') == 'active':
                    healthy_services += 1
        
        # Generate summary
        report['summary'] = {
            'total_services': total_services,
            'healthy_services': healthy_services,
            'service_health_percentage': (healthy_services / total_services * 100) if total_services > 0 else 0,
            'issues_created_today': self.progress_tracking['issues_created'],
            'tests_run': self.progress_tracking['services_tested'],
            'configs_validated': self.progress_tracking['deployments_validated']
        }
        
        return report
    
    def run_deployment_cycle(self):
        """Run one complete deployment monitoring cycle"""
        logger.info("🚀 Starting VF-Dev deployment monitoring cycle")
        
        # Create issues for pending deployment tasks
        for category, services in self.services.items():
            for service_name, service_path in services.items():
                # Check service health first
                health = self.check_service_health(service_path)
                
                if health.get('status') == 'active':
                    # Create deployment issues for active services
                    for task in self.deployment_tasks[:2]:  # Focus on first 2 tasks per cycle
                        issue = self.create_deployment_issue(service_name, task)
                        
                        # Submit to AI pipeline for processing
                        self.submit_to_ai_pipeline({
                            'issue_id': issue['issue_id'],
                            'service': service_name,
                            'task': task,
                            'category': category
                        })
                
                # Run tests and validation
                if health.get('status') == 'active':
                    test_results = self.run_integration_tests(service_name, service_path)
                    config_validation = self.validate_deployment_config(service_name, service_path)
                    
                    logger.info(f"✅ Completed cycle for {service_name}")
        
        # Update progress tracking
        self.progress_tracking['last_check'] = datetime.now().isoformat()
        
    def run(self):
        """Main agent loop"""
        logger.info(f"🎯 VF-Dev Deployment Agent starting...")
        logger.info(f"Agent ID: {self.agent_id}")
        logger.info(f"Monitoring {sum(len(services) for services in self.services.values())} services")
        logger.info(f"Pipeline integration: Visual Forge AI, PM Workflow, Dashboard")
        
        self.start_time = time.time()
        
        try:
            while True:
                # Run deployment monitoring cycle
                self.run_deployment_cycle()
                
                # Generate and save progress report
                report = self.generate_progress_report()
                
                with open('vf_dev_deployment_report.json', 'w') as f:
                    json.dump(report, f, indent=2)
                
                logger.info(f"📊 Cycle complete: {report['summary']}")
                
                # Wait before next cycle (every 30 minutes for deployment monitoring)
                time.sleep(1800)  # 30 minutes
                
        except KeyboardInterrupt:
            logger.info("VF-Dev Deployment Agent stopping...")
            final_report = self.generate_progress_report()
            
            logger.info(f"📋 Final Report:")
            logger.info(f"  Issues Created: {final_report['progress']['issues_created']}")
            logger.info(f"  Services Tested: {final_report['progress']['services_tested']}")
            logger.info(f"  Configs Validated: {final_report['progress']['deployments_validated']}")
            logger.info(f"  Service Health: {final_report['summary']['service_health_percentage']:.1f}%")
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)

def main():
    """Main entry point"""
    agent = VFDevDeploymentAgent()
    
    print("\n" + "="*80)
    print("VF-DEV DEPLOYMENT AGENT INITIALIZED")
    print("="*80)
    print(f"Agent ID: {agent.agent_id}")
    print(f"Services Monitored: {sum(len(services) for services in agent.services.values())}")
    print(f"NiroSubs Services: {len(agent.services['visual_forge'])}")
    print(f"VisualForge Services: {len(agent.services['niro_subs'])}")
    print("="*80)
    print("Mission: Ensure active progress on vf-dev deployment and testing")
    print("Integration: GitHub Issues → AI Pipeline → PM Workflow")
    print("="*80 + "\n")
    
    agent.run()

if __name__ == "__main__":
    main()
