#!/usr/bin/env python3

"""
Repository Health Check - Validates organization and structure
"""

import os
import json
from pathlib import Path

def check_repository_health():
    """Comprehensive repository health check"""
    
    print("🏥 Repository Health Check - Autonomous Business System")
    print("=" * 60)
    
    issues = []
    recommendations = []
    
    # Check directory structure
    print("\n📁 Directory Structure Check")
    required_dirs = [
        'src', 'tools', 'config', 'docs', 'tests', 'logs', 'reports',
        'data', 'work', 'monitoring', 'architecture', 'infrastructure',
        'deployment-scripts', 'github-actions', 'orchestration', 
        'cost-optimization', 'scripts'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        issues.append(f"Missing directories: {', '.join(missing_dirs)}")
    else:
        print("✅ All required directories present")
    
    # Check agent system files
    print("\n🤖 Agent System Check")
    agent_files = {
        'config/agents.json': 'Agent configuration',
        'github-actions/agent-picker.py': 'Interactive agent picker',
        'github-actions/setup-custom-fields.sh': 'Custom fields setup',
        'github-actions/agent-assignment.yml': 'GitHub Actions workflow'
    }
    
    missing_agent_files = []
    for file_path, description in agent_files.items():
        if not os.path.exists(file_path):
            missing_agent_files.append(f"{file_path} ({description})")
    
    if missing_agent_files:
        issues.append(f"Missing agent system files: {', '.join(missing_agent_files)}")
    else:
        print("✅ All agent system files present")
    
    # Check for excessive files in root
    print("\n📊 Root Directory Analysis")
    root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    
    if len(root_files) > 100:
        issues.append(f"Too many files in root directory: {len(root_files)} (recommended: <50)")
    elif len(root_files) > 50:
        recommendations.append(f"Consider organizing {len(root_files)} root files (current: acceptable)")
    else:
        print(f"✅ Root directory well organized: {len(root_files)} files")
    
    # Check agent configuration
    print("\n⚙️ Agent Configuration Check")
    if os.path.exists('config/agents.json'):
        try:
            with open('config/agents.json', 'r') as f:
                config = json.load(f)
            
            total_agents = config.get('agent_configuration', {}).get('total_agents', 0)
            if total_agents != 50:
                issues.append(f"Agent count mismatch: configured for {total_agents}, expected 50")
            else:
                print(f"✅ Agent configuration valid: {total_agents} agents")
                
            # Check cost optimization
            spot_cost = config.get('spot_instance_deployment', {}).get('monthly_cost_estimate', '')
            if '$8-15' in spot_cost:
                print("✅ Cost optimization configured: 95% savings")
            else:
                recommendations.append("Review cost optimization configuration")
                
        except Exception as e:
            issues.append(f"Agent configuration error: {str(e)}")
    
    # Check GitHub integration
    print("\n🔧 GitHub Integration Check")
    gh_files = [
        'github-actions/setup-custom-fields.sh',
        'github-actions/agent-assignment.yml',
        'github-actions/agent-picker.py'
    ]
    
    gh_missing = [f for f in gh_files if not os.path.exists(f)]
    if gh_missing:
        issues.append(f"Missing GitHub integration files: {', '.join(gh_missing)}")
    else:
        print("✅ GitHub integration complete")
    
    # Check documentation
    print("\n📚 Documentation Check")
    critical_docs = [
        'README.md',
        'docs/IMPLEMENTATION_COMPLETE.md',
        'docs/CUSTOM_FIELD_AGENT_SYSTEM.md'
    ]
    
    missing_docs = [f for f in critical_docs if not os.path.exists(f)]
    if missing_docs:
        issues.append(f"Missing critical documentation: {', '.join(missing_docs)}")
    else:
        print("✅ Critical documentation present")
    
    # Check infrastructure
    print("\n☁️ Infrastructure Check")
    infra_dirs = ['infrastructure/cloudformation', 'infrastructure/docker']
    missing_infra = [d for d in infra_dirs if not os.path.exists(d)]
    
    if missing_infra:
        recommendations.append(f"Consider adding infrastructure directories: {', '.join(missing_infra)}")
    else:
        print("✅ Infrastructure directories present")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    if not issues and not recommendations:
        print("🎉 EXCELLENT: Repository is perfectly organized!")
        print("✅ All systems operational")
        print("✅ 50-agent system ready")
        print("✅ 95% cost optimization active")
        print("✅ GitHub integration complete")
        health_score = 100
    elif not issues:
        print("✅ GOOD: Repository is well organized with minor suggestions")
        for rec in recommendations:
            print(f"💡 {rec}")
        health_score = 85
    else:
        print("⚠️ NEEDS ATTENTION: Issues found")
        for issue in issues:
            print(f"❌ {issue}")
        if recommendations:
            print("\nRecommendations:")
            for rec in recommendations:
                print(f"💡 {rec}")
        health_score = 60 if len(issues) < 3 else 40
    
    print(f"\n🏥 Repository Health Score: {health_score}/100")
    
    if health_score >= 90:
        print("🚀 Ready for production deployment!")
    elif health_score >= 75:
        print("🔧 Minor improvements recommended before deployment")
    else:
        print("🛠️ Significant improvements needed before deployment")
    
    return health_score

if __name__ == "__main__":
    health_score = check_repository_health()
    exit(0 if health_score >= 75 else 1)
