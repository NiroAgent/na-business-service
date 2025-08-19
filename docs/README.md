# Autonomous Business System - Repository Structure

## 🏗️ Repository Organization

This repository has been organized for optimal development workflow, maintainability, and scalability. The structure supports our 50-agent system with 95% cost optimization through spot instances.

## 📁 Directory Structure

```
autonomous-business-system/
├── 🤖 src/                      # Source Code
│   ├── agents/                  # Agent implementations (50 specialized agents)
│   ├── dashboard/               # Real-time monitoring dashboards
│   ├── integrations/           # GitHub, VF, AWS integrations
│   └── monitoring/             # System monitoring and health checks
│
├── 🛠️ tools/                    # Development Tools
│   ├── deployment/             # Deployment automation tools
│   ├── testing/                # Testing utilities and validators
│   ├── generators/             # Code and project generators
│   └── gh_copilot/            # GitHub Copilot integration tools
│
├── ⚙️ config/                   # Configuration
│   ├── agents.json             # 50-agent configuration
│   ├── aws-*.json              # AWS configurations
│   └── *.json                  # Service configurations
│
├── 📚 docs/                     # Documentation
│   ├── IMPLEMENTATION_COMPLETE.md
│   ├── CUSTOM_FIELD_AGENT_SYSTEM.md
│   └── *.md                    # All project documentation
│
├── 🧪 tests/                    # Testing Infrastructure
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   ├── data/                   # Test data
│   └── results/                # Test results
│
├── 📊 logs/                     # Logging
│   ├── agent_logs/             # Agent execution logs
│   ├── system_logs/            # System logs
│   └── *.log                   # Application logs
│
├── 📈 reports/                  # Generated Reports
│   ├── deployment/             # Deployment reports
│   ├── performance/            # Performance analysis
│   └── cost/                   # Cost optimization reports
│
├── 💾 data/                     # Runtime Data
│   ├── cache/                  # Application cache
│   ├── state/                  # System state persistence
│   ├── temp/                   # Temporary files
│   └── tokens/                 # Authentication tokens
│
├── 📋 work/                     # Work Management
│   ├── queue/                  # Work item queue
│   ├── assignments/            # Agent assignments
│   └── messages/               # Inter-agent communication
│
├── 📡 monitoring/               # Monitoring & Analytics
│   ├── reports/                # Monitoring reports
│   ├── results/                # Analysis results
│   └── qa/                     # Quality assurance reports
│
├── 🏛️ architecture/             # Architecture & Design
│   ├── specs/                  # Architecture specifications
│   ├── designs/                # Design documents
│   └── submissions/            # VF submissions
│
├── ☁️ infrastructure/           # Infrastructure as Code
│   ├── cloudformation/         # AWS CloudFormation templates
│   ├── docker/                 # Docker configurations
│   └── github-actions/         # GitHub Actions workflows
│
├── 🚀 deployment-scripts/       # Deployment Automation
│   ├── setup-*.sh              # Environment setup scripts
│   ├── deploy-*.sh             # Deployment scripts
│   └── *.ps1                   # PowerShell deployment scripts
│
├── 🔄 github-actions/           # GitHub Integration
│   ├── agent-assignment.yml    # Custom field assignment workflow
│   ├── setup-custom-fields.sh  # GitHub custom fields setup
│   ├── agent-picker.py         # Interactive agent selection
│   └── *.yml                   # GitHub Actions workflows
│
├── 🎼 orchestration/            # Agent Orchestration
│   ├── *-orchestrator.py       # Orchestration systems
│   └── coordination/           # Multi-agent coordination
│
├── 💰 cost-optimization/        # Cost Optimization
│   ├── spot-instance-*.py      # Spot instance management
│   ├── cost-monitoring.py      # Cost tracking
│   └── optimization-*.py       # Cost optimization strategies
│
├── 🧩 scripts/                  # Utility Scripts
│   ├── maintenance/            # Maintenance scripts
│   ├── migration/              # Data migration scripts
│   └── utilities/              # General utilities
│
└── 📦 Submodules               # Related Projects
    ├── NiroSubs-V2/            # NiroSubs V2 project
    ├── VisualForgeMediaV2/     # Visual Forge Media V2
    └── Projects-repo/          # Additional projects
```

## 🎯 Key Features

### 🤖 50-Agent System
- **20 Developer Agents:** Frontend, backend, fullstack, API, performance
- **10 QA Agents:** Automation, manual, performance, security
- **5 DevOps Agents:** CI/CD, infrastructure, monitoring
- **5 Manager Agents:** Project, product, coordination
- **5 Architect Agents:** System, platform, integration
- **3 Security Agents:** Assessment, compliance, code review
- **2 Analytics Agents:** Performance, business intelligence

### 💰 95% Cost Optimization
- **Spot Instances:** $8-15/month vs $150-300 Lambda
- **Processing Cost:** $0.05/hour vs $0.50+/hour
- **Monthly Savings:** $135-285 per deployment

### 📝 GitHub Custom Fields
- `assigned_agent` - Definitive agent assignment
- `agent_status` - Real-time status tracking
- `priority_level` - P0-P4 priority system
- Timeline tracking and communication

## 🚀 Quick Start

### 1. Setup Custom Fields
```bash
./github-actions/setup-custom-fields.sh
```

### 2. Assign Agents to Issues
```bash
# Interactive assignment
python github-actions/agent-picker.py

# Quick dashboard assignment
./github-actions/assign-dashboard-issue.sh
```

### 3. Monitor Processing
- GitHub custom fields show real-time status
- CloudWatch metrics track cost optimization
- Dashboard provides system overview

## 🔄 Development Workflow

1. **Issue Creation** → GitHub Issues with custom fields
2. **Agent Assignment** → Custom field-based assignment
3. **Processing** → Spot instance deployment
4. **Monitoring** → Real-time status tracking
5. **Completion** → Automated status updates

## 🏆 Organizational Benefits

- ✅ **Reduced Complexity:** From 242 to 74 root files
- ✅ **Clear Separation:** Logical grouping by function
- ✅ **Scalable Structure:** Supports 50+ agents
- ✅ **Cost Optimized:** 95% infrastructure savings
- ✅ **Developer Friendly:** Intuitive navigation
- ✅ **CI/CD Ready:** Automated workflows

## 📊 Repository Metrics

- **Total Agents:** 50 specialized agents
- **Cost Savings:** 95% vs traditional Lambda
- **Repositories:** 3 main repositories
- **Custom Fields:** 6 GitHub custom fields
- **Workflow Automation:** Complete GitHub Actions integration

## 🎯 Next Steps

1. Opus continues dashboard issue processing
2. Expand agent assignments to other issues
3. Monitor cost optimization metrics
4. Scale to additional repositories

---

*Repository organized for maximum efficiency and 95% cost optimization*
