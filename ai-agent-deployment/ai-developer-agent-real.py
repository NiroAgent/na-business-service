#!/usr/bin/env python3
"""
Real AI Developer Agent - Executes actual code analysis and improvement tasks
Replaces the placeholder version with real development work
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import uuid
import time
import ast
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RealAIDeveloperAgent')

class GitHubIntegration:
    """Handles GitHub integration for development tasks"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
    def create_development_issue(self, issue_data: Dict[str, Any]) -> Optional[str]:
        """Create a GitHub issue for development tasks"""
        if not self.github_token:
            logger.warning("No GitHub token available, cannot create issues")
            return None
            
        owner = 'YourGitHubOrg'  # Replace with actual GitHub org
        repo = 'VisualForgeMediaV2'  # Main repository
        
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        
        try:
            response = requests.post(url, headers=self.headers, json=issue_data)
            if response.status_code == 201:
                issue_url = response.json()['html_url']
                logger.info(f"Created development issue: {issue_url}")
                return issue_url
            else:
                logger.error(f"Failed to create issue: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return None

class CodeAnalyzer:
    """Analyzes actual code for improvements"""
    
    def __init__(self, base_directory: str):
        self.base_directory = Path(base_directory)
        
    def analyze_typescript_files(self, service_path: Path) -> List[Dict[str, Any]]:
        """Analyze TypeScript files for improvements"""
        issues = []
        
        # Find all TypeScript files
        ts_files = list(service_path.rglob('*.ts')) + list(service_path.rglob('*.tsx'))
        
        for file_path in ts_files:
            # Skip node_modules
            if 'node_modules' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Analyze the file
                file_issues = self._analyze_typescript_content(content, file_path)
                issues.extend(file_issues)
                
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")
                
        return issues
        
    def _analyze_typescript_content(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze TypeScript content for specific issues"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for console.log statements (should be removed in production)
            if 'console.log' in line and not line.strip().startswith('//'):
                issues.append({
                    'type': 'code_quality',
                    'severity': 'medium',
                    'file': str(file_path),
                    'line': i,
                    'issue': 'Console.log statement found',
                    'suggestion': 'Remove console.log statements or replace with proper logging',
                    'code': line.strip()
                })
                
            # Check for TODO/FIXME comments
            if ('TODO' in line or 'FIXME' in line) and ('//' in line or '/*' in line):
                issues.append({
                    'type': 'todo',
                    'severity': 'low',
                    'file': str(file_path),
                    'line': i,
                    'issue': 'TODO/FIXME comment found',
                    'suggestion': 'Address TODO/FIXME items or create GitHub issues',
                    'code': line.strip()
                })
                
            # Check for any keyword
            if 'any' in line and not line.strip().startswith('//'):
                issues.append({
                    'type': 'type_safety',
                    'severity': 'medium',
                    'file': str(file_path),
                    'line': i,
                    'issue': 'Any type usage detected',
                    'suggestion': 'Replace "any" with specific types for better type safety',
                    'code': line.strip()
                })
                
            # Check for missing error handling
            if 'fetch(' in line or 'axios.' in line:
                # Look ahead for try-catch or .catch()
                has_error_handling = False
                for j in range(max(0, i-5), min(len(lines), i+5)):
                    if 'try' in lines[j] or '.catch(' in lines[j] or 'catch(' in lines[j]:
                        has_error_handling = True
                        break
                        
                if not has_error_handling:
                    issues.append({
                        'type': 'error_handling',
                        'severity': 'high',
                        'file': str(file_path),
                        'line': i,
                        'issue': 'HTTP request without error handling',
                        'suggestion': 'Add try-catch block or .catch() for error handling',
                        'code': line.strip()
                    })
                    
        return issues
        
    def analyze_test_coverage(self, service_path: Path) -> Dict[str, Any]:
        """Analyze test coverage for a service"""
        mfe_path = service_path / 'mfe'
        if not mfe_path.exists():
            return {'coverage': 0, 'analysis': 'No MFE directory found'}
            
        # Count source files
        src_files = list(mfe_path.rglob('*.ts')) + list(mfe_path.rglob('*.tsx'))
        src_files = [f for f in src_files if 'node_modules' not in str(f) and 'tests' not in str(f)]
        
        # Count test files
        test_files = list((mfe_path / 'tests').rglob('*.spec.ts')) + list((mfe_path / 'tests').rglob('*.test.ts'))
        
        coverage_ratio = len(test_files) / len(src_files) if src_files else 0
        
        return {
            'source_files': len(src_files),
            'test_files': len(test_files),
            'coverage_ratio': round(coverage_ratio, 2),
            'estimated_coverage': min(round(coverage_ratio * 100, 1), 100),
            'analysis': f"Found {len(test_files)} test files for {len(src_files)} source files"
        }

class DependencyAnalyzer:
    """Analyzes project dependencies"""
    
    def analyze_package_json(self, service_path: Path) -> Dict[str, Any]:
        """Analyze package.json for issues"""
        package_json = service_path / 'package.json'
        
        if not package_json.exists():
            return {'error': 'No package.json found'}
            
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
                
            analysis = {
                'dependencies': len(data.get('dependencies', {})),
                'dev_dependencies': len(data.get('devDependencies', {})),
                'scripts': list(data.get('scripts', {}).keys()),
                'issues': []
            }
            
            # Check for security vulnerabilities (would need audit)
            deps = data.get('dependencies', {})
            dev_deps = data.get('devDependencies', {})
            
            # Check for outdated patterns
            all_deps = {**deps, **dev_deps}
            for dep_name, version in all_deps.items():
                if version.startswith('^0.') or version.startswith('~0.'):
                    analysis['issues'].append({
                        'type': 'dependency_version',
                        'severity': 'low',
                        'issue': f'Using pre-1.0 version: {dep_name}@{version}',
                        'suggestion': 'Consider using more stable versions'
                    })
                    
            return analysis
            
        except Exception as e:
            return {'error': f'Error analyzing package.json: {e}'}

class ServiceAnalyzer:
    """Analyzes individual services"""
    
    def __init__(self, base_directory: str):
        self.base_directory = Path(base_directory)
        self.code_analyzer = CodeAnalyzer(base_directory)
        self.dependency_analyzer = DependencyAnalyzer()
        
        # Service directories mapping
        self.service_dirs = {
            'vf-dashboard-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-dashboard-service',
            'vf-video-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-video-service',
            'vf-audio-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-audio-service',
            'vf-image-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-image-service',
            'vf-text-service': self.base_directory / 'VisualForgeMediaV2' / 'vf-text-service'
        }
        
    def analyze_service(self, service_name: str) -> Dict[str, Any]:
        """Perform comprehensive service analysis"""
        service_path = self.service_dirs.get(service_name)
        
        if not service_path or not service_path.exists():
            return {
                'service': service_name,
                'status': 'error',
                'error': f'Service directory not found: {service_path}'
            }
            
        logger.info(f"Analyzing service: {service_name}")
        
        analysis = {
            'service': service_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        try:
            # Code analysis
            code_issues = self.code_analyzer.analyze_typescript_files(service_path)
            analysis['code_analysis'] = {
                'total_issues': len(code_issues),
                'issues_by_type': self._group_issues_by_type(code_issues),
                'issues_by_severity': self._group_issues_by_severity(code_issues),
                'issues': code_issues[:10]  # Limit to first 10 for readability
            }
            
            # Test coverage analysis
            test_coverage = self.code_analyzer.analyze_test_coverage(service_path)
            analysis['test_coverage'] = test_coverage
            
            # Dependency analysis
            dependency_analysis = self.dependency_analyzer.analyze_package_json(service_path)
            analysis['dependencies'] = dependency_analysis
            
            # Performance check (file sizes, etc.)
            performance_metrics = self._analyze_performance(service_path)
            analysis['performance'] = performance_metrics
            
        except Exception as e:
            analysis['status'] = 'error'
            analysis['error'] = str(e)
            logger.error(f"Error analyzing service {service_name}: {e}")
            
        return analysis
        
    def _group_issues_by_type(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group issues by type"""
        groups = {}
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            groups[issue_type] = groups.get(issue_type, 0) + 1
        return groups
        
    def _group_issues_by_severity(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group issues by severity"""
        groups = {}
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            groups[severity] = groups.get(severity, 0) + 1
        return groups
        
    def _analyze_performance(self, service_path: Path) -> Dict[str, Any]:
        """Analyze service performance characteristics"""
        try:
            # Count files and sizes
            all_files = list(service_path.rglob('*'))
            total_files = len([f for f in all_files if f.is_file()])
            
            # Calculate total size (excluding node_modules)
            total_size = 0
            for file_path in all_files:
                if file_path.is_file() and 'node_modules' not in str(file_path):
                    total_size += file_path.stat().st_size
                    
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'large_files': self._find_large_files(service_path),
                'analysis': 'Performance metrics calculated'
            }
            
        except Exception as e:
            return {'error': f'Error analyzing performance: {e}'}
            
    def _find_large_files(self, service_path: Path) -> List[Dict[str, Any]]:
        """Find unusually large files"""
        large_files = []
        
        for file_path in service_path.rglob('*'):
            if file_path.is_file() and 'node_modules' not in str(file_path):
                size = file_path.stat().st_size
                if size > 100 * 1024:  # Files larger than 100KB
                    large_files.append({
                        'file': str(file_path.relative_to(service_path)),
                        'size_kb': round(size / 1024, 1)
                    })
                    
        return sorted(large_files, key=lambda x: x['size_kb'], reverse=True)[:5]

class RealAIDeveloperAgent:
    """Real AI Developer Agent that performs actual development tasks"""
    
    def __init__(self, base_directory: str = '/home/ubuntu'):
        self.logger = logger
        self.base_directory = base_directory
        self.service_analyzer = ServiceAnalyzer(base_directory)
        self.github = GitHubIntegration()
        self.report_directory = Path(base_directory) / 'dev_reports'
        self.report_directory.mkdir(exist_ok=True)
        
        logger.info("Real AI Developer Agent initialized - performing actual code analysis")
        
    def analyze_all_services(self) -> Dict[str, Any]:
        """Analyze all services comprehensively"""
        logger.info("Starting comprehensive service analysis")
        
        services = list(self.service_analyzer.service_dirs.keys())
        analyses = {}
        
        for service in services:
            try:
                analysis = self.service_analyzer.analyze_service(service)
                analyses[service] = analysis
                
                # Create GitHub issues for critical problems
                self._create_issues_for_critical_problems(service, analysis)
                
            except Exception as e:
                logger.error(f"Error analyzing service {service}: {e}")
                analyses[service] = {
                    'service': service,
                    'status': 'error',
                    'error': str(e)
                }
                
        return analyses
        
    def _create_issues_for_critical_problems(self, service: str, analysis: Dict[str, Any]):
        """Create GitHub issues for critical problems found"""
        if analysis.get('status') != 'completed':
            return
            
        code_analysis = analysis.get('code_analysis', {})
        issues_by_severity = code_analysis.get('issues_by_severity', {})
        
        # Create issue for high severity problems
        high_issues = issues_by_severity.get('high', 0)
        if high_issues > 0:
            title = f"🔧 High Priority Code Issues in {service}"
            body = f"""## Code Quality Issues Found

The Real AI Developer Agent has identified **{high_issues} high-priority issues** in {service}.

### Issues by Type:
"""
            issues_by_type = code_analysis.get('issues_by_type', {})
            for issue_type, count in issues_by_type.items():
                body += f"- **{issue_type}**: {count} issues\n"
                
            body += f"""
### Test Coverage:
- Current Coverage: {analysis.get('test_coverage', {}).get('estimated_coverage', 'Unknown')}%
- Test Files: {analysis.get('test_coverage', {}).get('test_files', 0)}
- Source Files: {analysis.get('test_coverage', {}).get('source_files', 0)}

### Dependencies:
- Total Dependencies: {analysis.get('dependencies', {}).get('dependencies', 0)}
- Dev Dependencies: {analysis.get('dependencies', {}).get('dev_dependencies', 0)}

### Recommended Actions:
1. Address high-severity issues first (error handling, type safety)
2. Increase test coverage if below 80%
3. Remove console.log statements from production code
4. Convert TODO comments to GitHub issues

---
*This issue was automatically created by the Real AI Developer Agent*
"""
            
            issue_data = {
                'title': title,
                'body': body,
                'labels': ['enhancement', 'code-quality', f'service:{service}', 'automated']
            }
            
            self.github.create_development_issue(issue_data)
            
    def generate_comprehensive_report(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive development report"""
        timestamp = datetime.now().isoformat()
        
        # Aggregate statistics
        total_services = len(analyses)
        successful_analyses = sum(1 for a in analyses.values() if a.get('status') == 'completed')
        
        total_code_issues = sum(
            a.get('code_analysis', {}).get('total_issues', 0) 
            for a in analyses.values() 
            if a.get('status') == 'completed'
        )
        
        avg_test_coverage = sum(
            a.get('test_coverage', {}).get('estimated_coverage', 0)
            for a in analyses.values()
            if a.get('status') == 'completed'
        ) / successful_analyses if successful_analyses > 0 else 0
        
        report = {
            'report_id': f'real-dev-{uuid.uuid4().hex[:8]}',
            'timestamp': timestamp,
            'agent_type': 'Real AI Developer Agent',
            'execution_type': 'Actual Code Analysis',
            'summary': {
                'total_services': total_services,
                'successful_analyses': successful_analyses,
                'total_code_issues': total_code_issues,
                'average_test_coverage': round(avg_test_coverage, 1),
                'github_issues_created': sum(1 for a in analyses.values() 
                                           if a.get('code_analysis', {}).get('issues_by_severity', {}).get('high', 0) > 0)
            },
            'service_analyses': analyses,
            'recommendations': self._generate_recommendations(analyses)
        }
        
        return report
        
    def _generate_recommendations(self, analyses: Dict[str, Any]) -> List[str]:
        """Generate development recommendations"""
        recommendations = []
        
        for service, analysis in analyses.items():
            if analysis.get('status') != 'completed':
                continue
                
            # Test coverage recommendations
            coverage = analysis.get('test_coverage', {}).get('estimated_coverage', 0)
            if coverage < 70:
                recommendations.append(f"Increase test coverage in {service} (currently {coverage}%)")
                
            # Code quality recommendations
            high_issues = analysis.get('code_analysis', {}).get('issues_by_severity', {}).get('high', 0)
            if high_issues > 0:
                recommendations.append(f"Address {high_issues} high-priority code issues in {service}")
                
            # Performance recommendations
            large_files = analysis.get('performance', {}).get('large_files', [])
            if len(large_files) > 2:
                recommendations.append(f"Review large files in {service} for optimization opportunities")
                
        return recommendations[:10]  # Limit to top 10
        
    def save_report(self, report: Dict[str, Any]) -> str:
        """Save development report to file"""
        report_file = self.report_directory / f"{report['report_id']}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Development report saved to: {report_file}")
        return str(report_file)
        
    def print_summary(self, report: Dict[str, Any]):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("🛠️  REAL AI DEVELOPER AGENT - ANALYSIS SUMMARY")
        print("="*60)
        
        summary = report['summary']
        print(f"📊 Overall Results:")
        print(f"   Services Analyzed: {summary['successful_analyses']}/{summary['total_services']}")
        print(f"   Total Code Issues: {summary['total_code_issues']}")
        print(f"   Average Test Coverage: {summary['average_test_coverage']}%")
        print(f"   GitHub Issues Created: {summary['github_issues_created']}")
        
        print(f"\n🔍 Service Breakdown:")
        for service_name, analysis in report['service_analyses'].items():
            if analysis.get('status') == 'completed':
                issues = analysis.get('code_analysis', {}).get('total_issues', 0)
                coverage = analysis.get('test_coverage', {}).get('estimated_coverage', 0)
                status = "✅" if issues < 5 and coverage > 70 else "⚠️"
                print(f"   {status} {service_name}: {issues} issues, {coverage}% coverage")
            else:
                print(f"   ❌ {service_name}: Analysis failed")
                
        if report['recommendations']:
            print(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(report['recommendations'][:5], 1):
                print(f"   {i}. {rec}")
                
        print("\n" + "="*60)

def main():
    """Main execution function"""
    logger.info("🚀 Starting Real AI Developer Agent")
    
    # Initialize agent with EC2 paths
    base_dir = os.getenv('DEV_BASE_DIR', '/home/ubuntu')
    agent = RealAIDeveloperAgent(base_dir)
    
    try:
        # Analyze all services
        analyses = agent.analyze_all_services()
        
        # Generate comprehensive report
        report = agent.generate_comprehensive_report(analyses)
        
        # Save report
        report_file = agent.save_report(report)
        
        # Print summary
        agent.print_summary(report)
        
        logger.info("✅ Real AI Developer Agent execution completed")
        
    except Exception as e:
        logger.error(f"❌ Real AI Developer Agent failed: {e}")
        raise

if __name__ == "__main__":
    main()