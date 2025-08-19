# Script to reorganize repositories into org-named folders

Write-Host "========================================" -ForegroundColor Blue
Write-Host "Reorganizing Repository Structure" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Define source and destination paths
$sourcePath = "E:\Projects\Niro-Subs-Projects"
$v1Path = "E:\Projects\NiroSubs-V1"
$v2Path = "E:\Projects\NiroSubs-V2"

# Create directories if they don't exist
New-Item -ItemType Directory -Path $v1Path -Force | Out-Null
New-Item -ItemType Directory -Path $v2Path -Force | Out-Null

Write-Host "Moving V1 repositories to: $v1Path" -ForegroundColor Cyan

# Move V1 repositories
$v1Repos = @(
    "Niro-SubsV1",
    "vf-dashboard-spa",
    "vf-dashboard-api",
    "vf-payments-api",
    "vf-user-api",
    "vf-core-service",
    "vf-shell-spa",
    "vf-types",
    "vf-sdk"
)

foreach ($repo in $v1Repos) {
    $source = Join-Path $sourcePath $repo
    $dest = Join-Path $v1Path $repo
    
    if (Test-Path $source) {
        Write-Host "  Moving $repo..." -ForegroundColor White
        Move-Item -Path $source -Destination $dest -Force -ErrorAction SilentlyContinue
        if (Test-Path $dest) {
            Write-Host "    [OK] Moved successfully" -ForegroundColor Green
        }
    } elseif (Test-Path $dest) {
        Write-Host "  $repo already in correct location" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Moving V2 repository to: $v2Path" -ForegroundColor Cyan

# Move V2 repository
$v2Source = Join-Path $sourcePath "NiroSubsV2"
$v2Dest = Join-Path $v2Path "nirosubs-v2-platform"

if (Test-Path $v2Source) {
    Write-Host "  Moving NiroSubsV2 -> nirosubs-v2-platform..." -ForegroundColor White
    Move-Item -Path $v2Source -Destination $v2Dest -Force -ErrorAction SilentlyContinue
    if (Test-Path $v2Dest) {
        Write-Host "    [OK] Moved successfully" -ForegroundColor Green
    }
} elseif (Test-Path $v2Dest) {
    Write-Host "  nirosubs-v2-platform already in correct location" -ForegroundColor Yellow
}

# Move workspace and script files to V2 folder
Write-Host ""
Write-Host "Moving workspace files..." -ForegroundColor Cyan

$workspaceFiles = @(
    "niro-subs.code-workspace",
    "WORKSPACE_SUMMARY.md",
    "create-nirosubs-v2-org.ps1",
    "setup-workspace.ps1",
    "rename-v1-repo.ps1"
)

foreach ($file in $workspaceFiles) {
    $source = Join-Path $sourcePath $file
    $dest = Join-Path $v2Path $file
    
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $dest -Force
        Write-Host "  [OK] Copied $file" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "Reorganization Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""
Write-Host "New Structure:" -ForegroundColor Cyan
Write-Host "  V1 Repositories: $v1Path" -ForegroundColor White
Write-Host "  V2 Platform: $v2Path" -ForegroundColor White
Write-Host ""
Write-Host "Repositories organized by organization:" -ForegroundColor Yellow
Write-Host "  - NiroSubs-V1 org -> $v1Path" -ForegroundColor White
Write-Host "  - NiroSubs-V2 org -> $v2Path" -ForegroundColor White