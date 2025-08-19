# Deploy both NiroSubs-V2 and VisualForgeMediaV2 to vf-dev AWS account
# This script triggers the GitHub Actions pipelines for both projects

param(
    [Parameter(Mandatory=$false)]
    [string]$Branch = "dev",
    
    [Parameter(Mandatory=$false)]
    [switch]$NiroSubsOnly,
    
    [Parameter(Mandatory=$false)]
    [switch]$MediaOnly,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying to VF-Dev AWS Account" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Branch: $Branch" -ForegroundColor Yellow
Write-Host "Account ID: 816454053517" -ForegroundColor Yellow
Write-Host "Region: us-east-1" -ForegroundColor Yellow
Write-Host ""

# Check if git is installed
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if GitHub CLI is installed
$hasGitHubCLI = Get-Command gh -ErrorAction SilentlyContinue
if (!$hasGitHubCLI) {
    Write-Host "WARNING: GitHub CLI not installed. Manual deployment required." -ForegroundColor Yellow
    Write-Host "Install from: https://cli.github.com/" -ForegroundColor Gray
}

# Function to deploy a project
function Deploy-Project {
    param(
        [string]$ProjectPath,
        [string]$ProjectName,
        [string]$RepoName
    )
    
    Write-Host ""
    Write-Host "Deploying $ProjectName..." -ForegroundColor Cyan
    
    if (!(Test-Path $ProjectPath)) {
        Write-Host "ERROR: Project not found at $ProjectPath" -ForegroundColor Red
        return $false
    }
    
    Push-Location $ProjectPath
    
    try {
        # Check current branch
        $currentBranch = git branch --show-current
        Write-Host "Current branch: $currentBranch" -ForegroundColor Gray
        
        # Ensure we're on the target branch
        if ($currentBranch -ne $Branch) {
            Write-Host "Switching to $Branch branch..." -ForegroundColor Yellow
            git checkout $Branch 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "WARNING: Could not switch to $Branch branch" -ForegroundColor Yellow
                Write-Host "Creating $Branch branch..." -ForegroundColor Yellow
                git checkout -b $Branch 2>&1 | Out-Null
            }
        }
        
        # Check for uncommitted changes
        $status = git status --porcelain
        if ($status) {
            Write-Host "WARNING: Uncommitted changes detected" -ForegroundColor Yellow
            Write-Host "Please commit or stash changes before deploying" -ForegroundColor Yellow
            
            # Show uncommitted files
            Write-Host "Modified files:" -ForegroundColor Gray
            git status --short
        }
        
        # Pull latest changes
        Write-Host "Pulling latest changes..." -ForegroundColor Gray
        git pull origin $Branch 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: Could not pull from origin/$Branch" -ForegroundColor Yellow
        }
        
        # Push to trigger deployment
        Write-Host "Pushing to trigger deployment..." -ForegroundColor Gray
        git push origin $Branch 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Push successful - deployment triggered" -ForegroundColor Green
            
            # If GitHub CLI is available, check workflow status
            if ($hasGitHubCLI) {
                Write-Host "Checking workflow status..." -ForegroundColor Gray
                Start-Sleep -Seconds 5
                
                # Get latest workflow run
                $workflowRuns = gh run list --branch $Branch --limit 1 --json status,conclusion,url 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $runInfo = $workflowRuns | ConvertFrom-Json
                    if ($runInfo) {
                        Write-Host "Workflow URL: $($runInfo[0].url)" -ForegroundColor Cyan
                    }
                }
            }
        } else {
            Write-Host "✗ Push failed - check git configuration" -ForegroundColor Red
            return $false
        }
        
        return $true
    }
    finally {
        Pop-Location
    }
}

# Deploy projects based on parameters
$deploymentResults = @{}

if (!$MediaOnly) {
    Write-Host ""
    Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
    Write-Host "DEPLOYING NIROSUBS-V2" -ForegroundColor Blue
    Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
    
    $result = Deploy-Project `
        -ProjectPath "E:\Projects\NiroSubs-V2" `
        -ProjectName "NiroSubs-V2" `
        -RepoName "NiroSubs-V2"
    
    $deploymentResults["NiroSubs-V2"] = $result
}

if (!$NiroSubsOnly) {
    Write-Host ""
    Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
    Write-Host "DEPLOYING VISUALFORGEMEDIAV2" -ForegroundColor Blue
    Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
    
    $result = Deploy-Project `
        -ProjectPath "E:\Projects\VisualForgeMediaV2" `
        -ProjectName "VisualForgeMediaV2" `
        -RepoName "VisualForgeMediaV2"
    
    $deploymentResults["VisualForgeMediaV2"] = $result
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

foreach ($project in $deploymentResults.Keys) {
    $status = if ($deploymentResults[$project]) { "✓ Triggered" } else { "✗ Failed" }
    $color = if ($deploymentResults[$project]) { "Green" } else { "Red" }
    Write-Host "$project : $status" -ForegroundColor $color
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Monitor GitHub Actions workflows for deployment progress" -ForegroundColor Gray
Write-Host "2. Check AWS CloudFormation stacks in vf-dev account" -ForegroundColor Gray
Write-Host "3. Verify services are running:" -ForegroundColor Gray
Write-Host "   - NiroSubs: https://dev.visualforge.ai" -ForegroundColor Gray
Write-Host "   - Media Services: https://media-dev.visualforge.ai" -ForegroundColor Gray

if (!$SkipTests) {
    Write-Host ""
    Write-Host "4. Run integration tests after deployment completes" -ForegroundColor Gray
}

# Monitor deployment (optional)
if ($hasGitHubCLI) {
    Write-Host ""
    $monitor = Read-Host "Would you like to monitor the deployment? (y/n)"
    if ($monitor -eq 'y') {
        Write-Host ""
        Write-Host "Monitoring deployments..." -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
        Write-Host ""
        
        # Monitor both workflows
        if (!$MediaOnly) {
            Write-Host "NiroSubs-V2 Workflow:" -ForegroundColor Yellow
            Push-Location "E:\Projects\NiroSubs-V2"
            gh run watch --branch $Branch
            Pop-Location
        }
        
        if (!$NiroSubsOnly) {
            Write-Host "VisualForgeMediaV2 Workflow:" -ForegroundColor Yellow
            Push-Location "E:\Projects\VisualForgeMediaV2"
            gh run watch --branch $Branch
            Pop-Location
        }
    }
}

Write-Host ""
Write-Host "Deployment script completed!" -ForegroundColor Green