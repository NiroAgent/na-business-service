# GitHub Copilot CLI Helper Script

# Function to test a service
function Test-Service {
    param(
        [string]$Service,
        [string]$Environment
    )
    
    Write-Host "Testing $Service in $Environment..." -ForegroundColor Cyan
    
    $instructionFile = "AGENT_INSTRUCTIONS_$($Environment.ToUpper()).md"
    
    if (Test-Path $instructionFile) {
        gh copilot explain "Test the $Service service based on instructions in $instructionFile and report any issues"
    } else {
        Write-Host "Instruction file not found: $instructionFile" -ForegroundColor Red
    }
}

# Function to fix issues
function Fix-Issue {
    param(
        [string]$Issue,
        [string]$File
    )
    
    Write-Host "Analyzing issue: $Issue" -ForegroundColor Yellow
    gh copilot suggest "How to fix: $Issue in file $File"
}

# Function to deploy changes
function Deploy-Service {
    param(
        [string]$Service,
        [string]$Environment
    )
    
    Write-Host "Deploying $Service to $Environment..." -ForegroundColor Green
    gh copilot explain "What are the steps to deploy $Service to AWS Lambda in $Environment environment"
}

# Main testing flow
Write-Host "GitHub Copilot Agent Testing Suite" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Magenta

# Example usage
# Test-Service -Service "ns-auth" -Environment "dev"
# Fix-Issue -Issue "Lambda timeout" -File "index.js"
# Deploy-Service -Service "ns-auth" -Environment "staging"
