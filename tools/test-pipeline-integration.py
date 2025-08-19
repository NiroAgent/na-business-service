#!/usr/bin/env python3
"""
Pipeline Integration Test
Tests the complete flow from AI Architect Agent to AI Developer Agent
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import importlib.util

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PipelineIntegrationTest')

# Import AI Architect Agent
def import_module_from_file(module_name: str, file_path: str):
    """Import a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import agents
ai_architect = import_module_from_file("ai_architect_agent", "ai-architect-agent.py")
ai_developer = import_module_from_file("ai_developer_agent", "ai-developer-agent.py")

AIArchitectAgent = ai_architect.AIArchitectAgent
AIDeveloperAgent = ai_developer.AIDeveloperAgent
TechnicalSpecification = ai_developer.TechnicalSpecification


class PipelineIntegrationTest:
    """Test the complete pipeline from Architect to Developer"""
    
    def __init__(self):
        self.architect = AIArchitectAgent()
        self.developer = AIDeveloperAgent()
        self.test_results = []
        
    def create_test_issue(self) -> Dict[str, Any]:
        """Create a test GitHub issue for processing"""
        return {
            'number': 1001,
            'title': '[FEATURE] E-commerce API Platform',
            'body': """
## Overview
Build a comprehensive e-commerce API platform with the following requirements:

## Functional Requirements
- User registration and authentication with JWT
- Product catalog with categories and search
- Shopping cart management
- Order processing and payment integration
- Inventory tracking
- Admin dashboard for management

## Non-Functional Requirements
- Must handle 10,000 concurrent users
- API response time < 200ms
- 99.9% uptime
- Comprehensive logging and monitoring
- Docker deployment ready

## Technical Constraints
- Use Python with FastAPI for backend
- PostgreSQL for database
- Redis for caching
- Stripe for payments

## User Stories
- As a customer, I want to browse products by category
- As a customer, I want to add items to my cart
- As a customer, I want to checkout securely
- As an admin, I want to manage inventory
- As an admin, I want to view sales reports
""",
            'labels': ['feature', 'high-priority', 'backend'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'user': {'login': 'test-user'},
            'state': 'open'
        }
    
    def test_architect_to_developer_flow(self):
        """Test the complete flow from architecture to code generation"""
        logger.info("="*80)
        logger.info("TESTING COMPLETE PIPELINE: ARCHITECT -> DEVELOPER")
        logger.info("="*80)
        
        # Step 1: Create test issue
        issue = self.create_test_issue()
        logger.info(f"Created test issue: {issue['title']}")
        
        # Step 2: Process with AI Architect
        logger.info("\nStep 1: Processing with AI Architect Agent...")
        try:
            # Analyze issue
            analysis = self.architect.analyze_github_issue(issue)
            logger.info(f"Analysis complete - Complexity: {analysis['complexity_score']}")
            
            # Create architecture specification
            arch_spec = self.architect.create_architecture_specification(analysis)
            logger.info(f"Architecture specification created: {arch_spec.spec_id}")
            
            # Save architecture spec for reference
            arch_output_dir = Path("test_output/architect")
            arch_output_dir.mkdir(parents=True, exist_ok=True)
            
            arch_spec_file = arch_output_dir / f"{arch_spec.spec_id}.json"
            with open(arch_spec_file, 'w') as f:
                json.dump(arch_spec.to_dict(), f, indent=2, default=str)
            logger.info(f"Saved architecture spec to: {arch_spec_file}")
            
            self.test_results.append({
                'step': 'architecture',
                'status': 'success',
                'spec_id': arch_spec.spec_id,
                'complexity': arch_spec.complexity_score,
                'estimated_effort': arch_spec.estimated_effort
            })
            
        except Exception as e:
            logger.error(f"Architecture processing failed: {e}")
            self.test_results.append({
                'step': 'architecture',
                'status': 'failed',
                'error': str(e)
            })
            return False
        
        # Step 3: Convert to Developer Agent format
        logger.info("\nStep 2: Converting to Developer Agent specification...")
        try:
            # Create TechnicalSpecification from architecture spec
            tech_spec = TechnicalSpecification(
                spec_id=arch_spec.spec_id,
                project_name="ecommerce-api",
                description=arch_spec.overview,
                requirements=arch_spec.requirements,
                technology_stack=arch_spec.technology_stack,
                architecture=arch_spec.architecture,
                api_design=arch_spec.api_design,
                database_design=arch_spec.database_design,
                security_requirements=arch_spec.security_requirements,
                performance_requirements=arch_spec.performance_requirements,
                deployment_requirements=arch_spec.deployment_requirements,
                testing_requirements=arch_spec.testing_requirements
            )
            
            logger.info("Technical specification prepared for Developer Agent")
            
            self.test_results.append({
                'step': 'conversion',
                'status': 'success',
                'tech_stack': tech_spec.technology_stack
            })
            
        except Exception as e:
            logger.error(f"Specification conversion failed: {e}")
            self.test_results.append({
                'step': 'conversion',
                'status': 'failed',
                'error': str(e)
            })
            return False
        
        # Step 4: Generate code with AI Developer
        logger.info("\nStep 3: Generating code with AI Developer Agent...")
        try:
            # Set output directory
            dev_output_dir = Path("test_output/developer/ecommerce-api")
            
            # Process specification
            generated_project = self.developer.process_specification(
                tech_spec,
                output_dir=str(dev_output_dir)
            )
            
            logger.info(f"Code generation complete: {generated_project.project_id}")
            logger.info(f"Generated {len(generated_project.generated_files)} files")
            logger.info(f"Total lines of code: {generated_project.total_lines}")
            logger.info(f"Test coverage estimate: {generated_project.test_coverage}%")
            
            # List generated files
            logger.info("\nGenerated files:")
            for file in generated_project.generated_files[:10]:  # Show first 10
                logger.info(f"  - {file}")
            if len(generated_project.generated_files) > 10:
                logger.info(f"  ... and {len(generated_project.generated_files) - 10} more files")
            
            self.test_results.append({
                'step': 'code_generation',
                'status': 'success',
                'project_id': generated_project.project_id,
                'files_generated': len(generated_project.generated_files),
                'total_lines': generated_project.total_lines,
                'test_coverage': generated_project.test_coverage
            })
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            self.test_results.append({
                'step': 'code_generation',
                'status': 'failed',
                'error': str(e)
            })
            return False
        
        # Step 5: Verify generated project structure
        logger.info("\nStep 4: Verifying generated project structure...")
        try:
            verification_results = self.verify_generated_project(dev_output_dir)
            
            logger.info("Project structure verification:")
            for check, result in verification_results.items():
                status = "PASS" if result else "FAIL"
                logger.info(f"  - {check}: {status}")
            
            all_passed = all(verification_results.values())
            
            self.test_results.append({
                'step': 'verification',
                'status': 'success' if all_passed else 'partial',
                'checks': verification_results
            })
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            self.test_results.append({
                'step': 'verification',
                'status': 'failed',
                'error': str(e)
            })
            return False
        
        return True
    
    def verify_generated_project(self, project_dir: Path) -> Dict[str, bool]:
        """Verify the generated project structure"""
        checks = {}
        
        # Check main directories
        checks['src_directory'] = (project_dir / 'src').exists()
        checks['tests_directory'] = (project_dir / 'tests').exists()
        checks['docs_directory'] = (project_dir / 'docs').exists()
        
        # Check configuration files
        checks['requirements_txt'] = (project_dir / 'requirements.txt').exists()
        checks['dockerfile'] = (project_dir / 'Dockerfile').exists()
        checks['docker_compose'] = (project_dir / 'docker-compose.yml').exists()
        checks['readme'] = (project_dir / 'README.md').exists()
        
        # Check source files
        if checks['src_directory']:
            src_dir = project_dir / 'src'
            checks['main_py'] = (src_dir / 'main.py').exists()
            checks['models_directory'] = (src_dir / 'models').exists()
            checks['api_directory'] = (src_dir / 'api').exists()
            checks['services_directory'] = (src_dir / 'services').exists()
        
        # Check test files
        if checks['tests_directory']:
            tests_dir = project_dir / 'tests'
            checks['has_test_files'] = len(list(tests_dir.glob('test_*.py'))) > 0
        
        return checks
    
    def generate_report(self):
        """Generate a test report"""
        logger.info("\n" + "="*80)
        logger.info("PIPELINE INTEGRATION TEST REPORT")
        logger.info("="*80)
        
        # Summary
        total_steps = len(self.test_results)
        successful_steps = sum(1 for r in self.test_results if r['status'] == 'success')
        
        logger.info(f"\nSummary:")
        logger.info(f"  Total Steps: {total_steps}")
        logger.info(f"  Successful: {successful_steps}")
        logger.info(f"  Success Rate: {(successful_steps/total_steps*100):.1f}%")
        
        # Detailed results
        logger.info(f"\nDetailed Results:")
        for result in self.test_results:
            step = result['step']
            status = result['status'].upper()
            logger.info(f"\n  {step}:")
            logger.info(f"    Status: {status}")
            
            if status == 'SUCCESS':
                # Show relevant metrics
                for key, value in result.items():
                    if key not in ['step', 'status']:
                        logger.info(f"    {key}: {value}")
            else:
                # Show error
                if 'error' in result:
                    logger.info(f"    Error: {result['error']}")
        
        # Save report
        report_file = Path("test_output/pipeline_integration_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_steps': total_steps,
                    'successful_steps': successful_steps,
                    'success_rate': successful_steps/total_steps*100 if total_steps > 0 else 0
                },
                'results': self.test_results
            }, f, indent=2, default=str)
        
        logger.info(f"\nReport saved to: {report_file}")
        
        # Overall status
        pipeline_successful = successful_steps == total_steps
        logger.info("\n" + "="*80)
        if pipeline_successful:
            logger.info("PIPELINE TEST: SUCCESS - All steps completed successfully!")
        else:
            logger.info("PIPELINE TEST: PARTIAL - Some steps failed")
        logger.info("="*80)
        
        return pipeline_successful


def main():
    """Run the pipeline integration test"""
    print("\n" + "="*80)
    print("AI ARCHITECT -> AI DEVELOPER PIPELINE INTEGRATION TEST")
    print("="*80)
    print("This test validates the complete flow from architecture to code generation")
    print("="*80 + "\n")
    
    # Run test
    test = PipelineIntegrationTest()
    success = test.test_architect_to_developer_flow()
    
    # Generate report
    test.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()