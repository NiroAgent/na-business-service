# Script to update all V1 repository remotes to new organization name

Write-Host "========================================" -ForegroundColor Blue
Write-Host "Updating V1 Repository Remotes" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

$v1Path = "E:\Projects\NiroSubs-V1"
$newOrgName = "NiroSubs-V1"

# List of V1 repositories
$repositories = @(
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

Write-Host "Updating remotes to organization: $newOrgName" -ForegroundColor Cyan
Write-Host ""

foreach ($repo in $repositories) {
    $repoPath = Join-Path $v1Path $repo
    
    if (Test-Path $repoPath) {
        Push-Location $repoPath
        
        # Get current remote
        $currentRemote = git remote get-url origin 2>&1
        
        if ($currentRemote -match "github.com") {
            # Update remote URL to new organization
            $newRemote = "https://github.com/$newOrgName/$repo.git"
            
            Write-Host "Updating $repo" -ForegroundColor White
            Write-Host "  From: $currentRemote" -ForegroundColor Gray
            Write-Host "  To: $newRemote" -ForegroundColor Green
            
            git remote set-url origin $newRemote
            
            # Verify update
            $updatedRemote = git remote get-url origin
            if ($updatedRemote -eq $newRemote) {
                Write-Host "  [OK] Remote updated successfully" -ForegroundColor Green
            } else {
                Write-Host "  [WARNING] Remote update may have failed" -ForegroundColor Yellow
            }
        }
        
        Pop-Location
        Write-Host ""
    } else {
        Write-Host "[SKIP] $repo - Directory not found" -ForegroundColor Yellow
    }
}

Write-Host "========================================" -ForegroundColor Blue
Write-Host "Remote Update Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""
Write-Host "All V1 repositories now point to: github.com/$newOrgName" -ForegroundColor Cyan