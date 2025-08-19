# Launch all testing agents in parallel

Write-Host "🚀 Launching Agent Testing Orchestrator" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Set environment
$env:AWS_REGION = "us-east-1"
$env:AWS_ACCOUNT_ID = "816454053517"

# Create agent instructions
Write-Host "Creating agent instructions..." -ForegroundColor Yellow
python agent-orchestrator.py --create-instructions

# Launch agents for dev environment
Write-Host "Testing Dev Environment..." -ForegroundColor Cyan
python agent-orchestrator.py --test-env dev --max-workers 10

# Launch agents for staging environment
Write-Host "Testing Staging Environment..." -ForegroundColor Cyan  
python agent-orchestrator.py --test-env staging --max-workers 10

# Generate consolidated report
Write-Host "Generating report..." -ForegroundColor Yellow
python agent-orchestrator.py --generate-report

Write-Host "✅ Agent testing complete!" -ForegroundColor Green
