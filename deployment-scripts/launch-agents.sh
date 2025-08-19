#!/bin/bash
# Launch all testing agents in parallel

echo "🚀 Launching Agent Testing Orchestrator"
echo "======================================"

# Set environment
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=816454053517

# Create agent instructions
python3 agent-orchestrator.py --create-instructions

# Launch agents for dev environment
echo "Testing Dev Environment..."
python3 agent-orchestrator.py --test-env dev --max-workers 10

# Launch agents for staging environment  
echo "Testing Staging Environment..."
python3 agent-orchestrator.py --test-env staging --max-workers 10

# Generate consolidated report
python3 agent-orchestrator.py --generate-report

echo "✅ Agent testing complete!"
