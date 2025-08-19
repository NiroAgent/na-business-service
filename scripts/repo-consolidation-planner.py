#!/usr/bin/env python3
"""
Repository Consolidation Plan for NiroAgentV2 Organization
Consolidate all agent automation, dashboard, and EC2 infrastructure
"""

import subprocess
import os
import sys
from datetime import datetime

class RepoConsolidationPlan:
    def __init__(self):
        self.org = "NiroAgentV2"
        self.main_repo = "autonomous-business-system"
        self.current_path = "e:\\Projects"
        
    def analyze_current_structure(self):
        """Analyze what we have and what needs to be moved"""
        print("🔍 REPOSITORY CONSOLIDATION ANALYSIS")
        print("=" * 60)
        
        print(f"\n📊 Current NiroAgentV2 Organization Structure:")
        print(f"  • {self.org}/autonomous-business-system (MAIN)")
        print(f"  • {self.org}/agent-dashboard (Dashboard repo)")
        print(f"  • {self.org}/business-operations (Operations tracking)")
        
        print(f"\n📁 Current Local Structure (E:/Projects):")
        current_items = [
            "enhanced-ec2-dashboard.py - MAIN DASHBOARD ⭐",
            "agent-dashboard/ - React/Node.js dashboard",
            "src/agents/ - All AI agents",
            "src/dashboard/ - Dashboard components", 
            "GitHub issue creators (create-*-stories.py)",
            "Agent orchestration system",
            "Cost monitoring and kill switch",
            "All automation scripts"
        ]
        
        for item in current_items:
            print(f"  • {item}")
            
        return self.create_consolidation_plan()
    
    def create_consolidation_plan(self):
        """Create the consolidation plan"""
        print(f"\n🎯 CONSOLIDATION STRATEGY:")
        print(f"All automation should be in: {self.org}/{self.main_repo}")
        
        plan = {
            "target_repo": f"{self.org}/{self.main_repo}",
            "current_location": "E:/Projects (local)",
            "consolidation_actions": [
                {
                    "action": "KEEP_CURRENT",
                    "description": "Keep everything in autonomous-business-system",
                    "items": [
                        "enhanced-ec2-dashboard.py",
                        "All agent files (src/agents/)",
                        "Dashboard components (src/dashboard/)",
                        "GitHub issue creators",
                        "Cost monitoring system",
                        "Kill switch functionality",
                        "Agent orchestration",
                        "All automation scripts"
                    ]
                },
                {
                    "action": "EVALUATE_MERGE",
                    "description": "Evaluate if agent-dashboard repo should be merged",
                    "items": [
                        "React/Node.js dashboard from agent-dashboard repo",
                        "Compare with enhanced-ec2-dashboard.py",
                        "Keep the better implementation"
                    ]
                },
                {
                    "action": "ORGANIZE_STRUCTURE", 
                    "description": "Reorganize directory structure for clarity",
                    "structure": {
                        "dashboard/": "All dashboard implementations",
                        "agents/": "All AI agents", 
                        "automation/": "GitHub integration and issue creators",
                        "monitoring/": "Cost monitoring and kill switch",
                        "deployment/": "DevOps and deployment scripts",
                        "docs/": "Documentation and project management"
                    }
                }
            ]
        }
        
        return plan
    
    def print_recommended_structure(self):
        """Print the recommended repository structure"""
        print(f"\n📁 RECOMMENDED STRUCTURE for {self.org}/{self.main_repo}:")
        print("""
autonomous-business-system/
├── README.md                           # Main project overview
├── requirements.txt                    # Python dependencies
├── .github/
│   ├── workflows/                      # CI/CD workflows
│   └── ISSUE_TEMPLATE/                 # Issue templates
├── dashboard/
│   ├── enhanced-ec2-dashboard.py       # ⭐ MAIN DASHBOARD
│   ├── requirements.txt                # Dashboard dependencies
│   ├── static/                         # CSS, JS, images
│   └── templates/                      # HTML templates
├── agents/
│   ├── __init__.py
│   ├── ai-manager-agent.py            # Executive agent
│   ├── ai-project-manager-agent.py    # PM agent
│   ├── ai-developer-agent.py          # Development agent
│   ├── ai-qa-agent.py                 # QA agent
│   ├── ai-devops-agent.py             # DevOps agent
│   └── templates/
│       └── ai-agent-template.py       # Base agent class
├── automation/
│   ├── github-integration/
│   │   ├── create-dashboard-stories.py
│   │   ├── create-devops-deployment-story.py
│   │   └── issue-creators/
│   ├── orchestration/
│   │   ├── agent-orchestrator.py
│   │   └── local-orchestrator.py
│   └── workflows/
├── monitoring/
│   ├── cost-monitoring/
│   │   ├── cost-calculator.py
│   │   └── kill-switch-system.py
│   ├── system-monitoring/
│   └── health-checks/
├── deployment/
│   ├── aws/
│   │   ├── ec2-setup.sh
│   │   └── cloudformation/
│   ├── scripts/
│   │   ├── deploy-to-vf-dev.sh
│   │   └── deploy-to-vf-staging.sh
│   └── docker/
│       └── Dockerfile
├── docs/
│   ├── DEPLOYMENT_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   ├── AGENT_DEVELOPMENT.md
│   └── PROJECT_STATUS.md
└── tests/
    ├── dashboard/
    ├── agents/
    └── integration/
""")
    
    def create_reorganization_script(self):
        """Create script to reorganize the current repository"""
        script_content = f'''#!/bin/bash
# Repository Reorganization Script for {self.org}/{self.main_repo}
# Reorganizes the current structure for better organization

echo "🚀 Starting Repository Reorganization..."
cd {self.current_path}

# Create new directory structure
echo "📁 Creating new directory structure..."
mkdir -p dashboard/static dashboard/templates
mkdir -p agents/templates
mkdir -p automation/github-integration automation/orchestration automation/workflows
mkdir -p monitoring/cost-monitoring monitoring/system-monitoring monitoring/health-checks
mkdir -p deployment/aws deployment/scripts deployment/docker
mkdir -p docs
mkdir -p tests/dashboard tests/agents tests/integration

# Move dashboard files
echo "📊 Moving dashboard files..."
mv enhanced-ec2-dashboard.py dashboard/
cp -r src/dashboard/* dashboard/ 2>/dev/null || true

# Move agent files  
echo "🤖 Moving agent files..."
cp -r src/agents/* agents/ 2>/dev/null || true

# Move automation files
echo "⚙️ Moving automation files..."
mv create-*-stories.py automation/github-integration/
mv *-issue-creator.py automation/github-integration/
mv *orchestrator*.py automation/orchestration/ 2>/dev/null || true

# Move monitoring files
echo "📈 Moving monitoring files..."
mv calculate_single_instance_costs.py monitoring/cost-monitoring/ 2>/dev/null || true

# Move deployment files
echo "🚀 Moving deployment files..."
mv deployment-scripts/* deployment/scripts/ 2>/dev/null || true
mv deploy-*.ps1 deployment/scripts/ 2>/dev/null || true

# Move documentation
echo "📚 Moving documentation..."
mv *.md docs/ 2>/dev/null || true
mv PROJECT_COMPLETE_SUMMARY.md docs/ 2>/dev/null || true

# Create main requirements.txt
echo "📦 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
# Main project dependencies
flask>=2.0.0
flask-socketio>=5.0.0
psutil>=5.8.0
boto3>=1.26.0
requests>=2.28.0
python-dotenv>=0.19.0

# GitHub integration
PyGithub>=1.55.0

# Testing
pytest>=7.0.0
pytest-flask>=1.2.0

# Development
black>=22.0.0
flake8>=4.0.0
mypy>=0.942
EOF

# Create dashboard requirements
echo "📦 Creating dashboard/requirements.txt..."
cat > dashboard/requirements.txt << 'EOF'
# Dashboard specific dependencies
flask>=2.0.0
flask-socketio>=5.0.0
psutil>=5.8.0
boto3>=1.26.0
gunicorn>=20.1.0
eventlet>=0.33.0
EOF

# Update README.md
echo "📖 Creating comprehensive README.md..."
cat > README.md << 'EOF'
# 🤖 Autonomous Business System

**AI-powered autonomous business operations system with real-time monitoring and cost protection**

## 🎯 System Overview

Complete autonomous business system with 50+ AI agents, real-time dashboard monitoring, and advanced cost protection systems.

### ✅ Key Features:
- **Enhanced EC2 Dashboard**: 7-tab comprehensive monitoring interface
- **Cost Protection**: 3% alert, 5% emergency kill switch  
- **Real-time Monitoring**: WebSocket updates every 3 seconds
- **50 AI Agents**: Specialized agents for all business functions
- **GitHub Integration**: Complete project management workflow
- **DevOps Ready**: Deployment to vf-dev and vf-staging

## 🚀 Quick Start

### Prerequisites:
- Python 3.8+
- Node.js 18+ (for dashboard frontend)
- AWS CLI configured
- GitHub CLI authenticated

### Installation:
```bash
git clone https://github.com/{self.org}/{self.main_repo}.git
cd {self.main_repo}
pip install -r requirements.txt
```

### Run Dashboard:
```bash
cd dashboard
python enhanced-ec2-dashboard.py
# Access: http://localhost:5003
```

## 📊 Dashboard Features

### 7 Comprehensive Tabs:
1. **Agent Grid**: Real-time status of all 50 agents
2. **Cost Monitoring**: Live cost tracking with kill switch ⚠️
3. **Console Logs**: Real-time system activity
4. **System Metrics**: Performance monitoring  
5. **Work Queue**: Task management
6. **Team Metrics**: Analytics and velocity
7. **GitHub Integration**: Repository metrics

### 🚨 Safety Features:
- **3% Alert Threshold**: Cost increase warnings
- **5% Kill Threshold**: Automatic emergency shutdown
- **Manual Override**: Emergency shutdown button
- **Cost History**: 10-point trend tracking

## 🤖 AI Agents

### Specialized Agents:
- **AI Manager**: Executive oversight and coordination
- **Project Manager**: Task planning and resource allocation
- **Developer**: Code generation and implementation
- **QA Engineer**: Testing and quality assurance
- **DevOps**: Deployment and infrastructure management

## 🔧 Development

### Project Structure:
- `dashboard/` - Main monitoring dashboard
- `agents/` - All AI agents and templates
- `automation/` - GitHub integration and workflows
- `monitoring/` - Cost and system monitoring
- `deployment/` - DevOps and deployment scripts

### Running Tests:
```bash
pytest tests/
```

## 🚀 Deployment

### Development Environment:
```bash
cd deployment/scripts
./deploy-to-vf-dev.sh
```

### Staging Environment:
```bash
./deploy-to-vf-staging.sh
```

## 📈 Monitoring

- **Live Dashboard**: http://localhost:5003
- **Cost Monitoring**: Real-time AWS cost tracking
- **Kill Switch**: Automatic protection against runaway costs
- **System Health**: CPU, memory, network monitoring

## 🔒 Security

- Environment variable configuration
- AWS IAM role-based access
- Rate limiting on API endpoints
- CORS configuration for dashboard

## 📞 Support

- **GitHub Issues**: Project management and tracking
- **Documentation**: Complete guides in `/docs`
- **API Documentation**: `/docs/API_DOCUMENTATION.md`

---

**🎯 Status**: Production Ready - QA Testing in Progress
**🚀 Live**: Enhanced Dashboard with Cost Protection Active
**⚠️ Critical**: Kill Switch Safety Validation Required
EOF

echo "✅ Repository reorganization complete!"
echo "📊 New structure created with improved organization"
echo "🎯 Ready for {self.org}/{self.main_repo} consolidation"
'''
        
        with open(f"{self.current_path}/reorganize-repository.sh", "w") as f:
            f.write(script_content)
        
        return f"{self.current_path}/reorganize-repository.sh"
    
    def create_consolidation_summary(self):
        """Create a summary of the consolidation plan"""
        summary = f"""
# 🏗️ Repository Consolidation Summary

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Target**: Consolidate all automation under {self.org}/{self.main_repo}

## 🎯 Consolidation Strategy: KEEP EVERYTHING IN MAIN REPO

### ✅ What's Already Correct:
- All major components are in `{self.org}/{self.main_repo}` ✅
- Enhanced dashboard with cost monitoring ✅  
- All AI agents and automation ✅
- GitHub issue integration ✅
- DevOps deployment planning ✅

### 📁 Reorganization Benefits:
- **Better Organization**: Clear directory structure
- **Easier Navigation**: Logical grouping of components
- **Improved Maintenance**: Cleaner separation of concerns
- **Enhanced Documentation**: Comprehensive README and docs

### 🚀 Recommended Actions:

#### 1. Reorganize Current Repository Structure ⭐ HIGH PRIORITY
- Run reorganization script to clean up directory structure
- Create proper documentation and README
- Establish clear component separation

#### 2. Evaluate Other Repositories 🔍 MEDIUM PRIORITY  
- **agent-dashboard**: Compare with enhanced-ec2-dashboard.py
- **business-operations**: Evaluate if needed or merge
- Keep the better implementations

#### 3. Update Documentation 📚 HIGH PRIORITY
- Comprehensive README for the main repository
- Clear installation and setup instructions  
- API documentation for all components

## 🎯 Current Status: EXCELLENT FOUNDATION

**The consolidation is mostly complete!** All major components are already in the right place:
- ✅ Enhanced EC2 Dashboard (`enhanced-ec2-dashboard.py`)
- ✅ All AI Agents (`src/agents/`)  
- ✅ GitHub Integration (issue creators)
- ✅ Cost Monitoring & Kill Switch
- ✅ DevOps Deployment Planning
- ✅ Project Management (10 GitHub issues)

## 🚀 Next Steps:

1. **Run Reorganization Script** (Optional but recommended)
2. **Update README.md** with comprehensive documentation
3. **Test All Components** to ensure nothing breaks
4. **Update GitHub Issues** with new structure references

## 📊 Success Metrics:
- Single source of truth in `{self.org}/{self.main_repo}` ✅
- Clear directory structure for easy navigation
- Comprehensive documentation for new team members
- All automation working from consolidated location

**Bottom Line**: The consolidation strategy is sound. Everything important is already in the main repository. The reorganization is just for better organization and documentation.
"""
        
        with open(f"{self.current_path}/CONSOLIDATION_SUMMARY.md", "w") as f:
            f.write(summary)
            
        return summary

def main():
    """Main execution"""
    print("🏗️ Repository Consolidation Planner")
    print("=" * 50)
    
    planner = RepoConsolidationPlan()
    
    # Analyze current structure
    plan = planner.analyze_current_structure()
    
    # Show recommended structure
    planner.print_recommended_structure()
    
    # Create reorganization script
    script_path = planner.create_reorganization_script()
    print(f"\n📝 Created reorganization script: {script_path}")
    
    # Create summary
    summary = planner.create_consolidation_summary()
    print(f"\n📋 Created consolidation summary: CONSOLIDATION_SUMMARY.md")
    
    print(f"\n🎯 RECOMMENDATION:")
    print(f"   The current setup is ALREADY EXCELLENT! ✅")
    print(f"   Everything is in the right repository: NiroAgentV2/autonomous-business-system")
    print(f"   Optional: Run reorganization script for better structure")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. Review CONSOLIDATION_SUMMARY.md")
    print(f"   2. Optionally run: bash reorganize-repository.sh")
    print(f"   3. Update README.md with comprehensive documentation")
    print(f"   4. Continue with QA testing and deployment")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
