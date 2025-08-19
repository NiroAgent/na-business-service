# Quick GitHub Copilot Testing Script

param(
    [string]$Repo = "NiroSubs-V2",
    [string]$Service = "ns-auth",
    [string]$Environment = "dev"
)

Write-Host "🧪 Testing $Service in $Repo ($Environment)" -ForegroundColor Cyan

# Navigate to Projects folder
Set-Location "E:\Projects"

# Build instruction path
$instructionPath = "$Repo\$Service\AGENT_INSTRUCTIONS_$($Environment.ToUpper()).md"

# Test command
$testPrompt = "Test and remediate $Service in $Repo using instructions at $instructionPath. Focus on health checks, functional tests, security, and performance."

# Run gh copilot
Write-Host "🤖 Running GitHub Copilot..." -ForegroundColor Yellow
gh copilot suggest "$testPrompt"

# Offer follow-up
Write-Host "`n💬 Need a follow-up command? (Enter command or press Enter to skip)" -ForegroundColor Green
$followUp = Read-Host ">"
if ($followUp) {
    $followUpPrompt = "For $Service in ${Repo} - $followUp"
    gh copilot suggest $followUpPrompt
}
