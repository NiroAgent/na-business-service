#!/bin/bash

# Repository Organization Script
# Organizes the autonomous-business-system repository structure for optimal maintainability

echo "🏗️ Organizing Repository Structure for Optimal Development"
echo "========================================================"

# Create main directory structure
echo "📁 Creating standardized directory structure..."

# Move data directories
echo "📊 Organizing data and temporary directories..."
mkdir -p data/{cache,state,temp,tokens,generated}
mv cache/* data/cache/ 2>/dev/null || echo "No cache files to move"
mv state/* data/state/ 2>/dev/null || echo "No state files to move"
mv temp/* data/temp/ 2>/dev/null || echo "No temp files to move"
mv tokens/* data/tokens/ 2>/dev/null || echo "No token files to move"
mv generated_projects/* data/generated/ 2>/dev/null || echo "No generated projects to move"

# Organize testing directories
echo "🧪 Organizing testing infrastructure..."
mkdir -p tests/{unit,integration,e2e,data,results}
mv test_data/* tests/data/ 2>/dev/null || echo "No test data to move"
mv test_results/* tests/results/ 2>/dev/null || echo "No test results to move"
mv test-projects/* tests/e2e/ 2>/dev/null || echo "No test projects to move"

# Organize work queue directories
echo "📋 Organizing work management..."
mkdir -p work/{queue,assignments,messages}
mv work_queue/* work/queue/ 2>/dev/null || echo "No work queue items to move"
mv work_queues/* work/queue/ 2>/dev/null || echo "No work queues to move"
mv agent_assignments/* work/assignments/ 2>/dev/null || echo "No agent assignments to move"
mv communication_messages/* work/messages/ 2>/dev/null || echo "No communication messages to move"

# Organize reports and monitoring
echo "📈 Organizing reports and monitoring..."
mkdir -p monitoring/{reports,results,qa}
mv qa_reports/* monitoring/qa/ 2>/dev/null || echo "No QA reports to move"
mv deployment_reports/* reports/ 2>/dev/null || echo "No deployment reports to move"
mv orchestration_results/* monitoring/results/ 2>/dev/null || echo "No orchestration results to move"

# Organize VF submissions and architecture
echo "🏛️ Organizing architecture and submissions..."
mkdir -p architecture/{specs,designs,submissions}
mv architecture_specs/* architecture/specs/ 2>/dev/null || echo "No architecture specs to move"
mv design_documents/* architecture/designs/ 2>/dev/null || echo "No design documents to move"
mv vf_submissions/* architecture/submissions/ 2>/dev/null || echo "No VF submissions to move"

# Organize additional tooling
echo "🛠️ Organizing additional tools..."
mkdir -p tools/{gh_copilot,templates,resolution_plans}
mv gh_copilot_results/* tools/gh_copilot/ 2>/dev/null || echo "No GH Copilot results to move"
mv templates/* tools/templates/ 2>/dev/null || echo "No templates to move"
mv resolution_plans/* tools/resolution_plans/ 2>/dev/null || echo "No resolution plans to move"

# Clean up empty directories
echo "🧹 Cleaning up empty directories..."
find . -maxdepth 1 -type d -empty -not -path "./.git" -not -path "./.venv" -delete 2>/dev/null

echo "✅ Repository organization complete!"
echo ""
echo "📁 Final Directory Structure:"
echo "├── src/              # Source code (agents, dashboard, integrations, monitoring)"
echo "├── tools/            # Development and deployment tools"
echo "├── config/           # Configuration files (.json, .yaml)"
echo "├── docs/             # Documentation"
echo "├── tests/            # Testing infrastructure"
echo "├── logs/             # Log files and monitoring data"
echo "├── reports/          # Generated reports"
echo "├── data/             # Runtime data (cache, state, temp)"
echo "├── work/             # Work management (queue, assignments)"
echo "├── monitoring/       # Monitoring and analytics"
echo "├── architecture/     # Architecture specs and designs"
echo "├── infrastructure/   # CloudFormation, Docker, configs"
echo "├── deployment-scripts/ # Deployment automation"
echo "├── github-actions/   # GitHub Actions workflows"
echo "├── orchestration/    # Agent orchestration systems"
echo "├── cost-optimization/ # Cost optimization strategies"
echo "└── scripts/          # Utility scripts"
echo ""
echo "🚀 Repository ready for optimal development workflow!"
