# Test AWS setup
Write-Host "Testing AWS Setup" -ForegroundColor Cyan

# Test AWS access
$identity = aws sts get-caller-identity 2>&1
if ($LASTEXITCODE -eq 0) {
    $callerInfo = $identity | ConvertFrom-Json
    Write-Host "AWS Account: $($callerInfo.Account)" -ForegroundColor Green
    Write-Host "User ARN: $($callerInfo.Arn)" -ForegroundColor Green
} else {
    Write-Host "Cannot access AWS" -ForegroundColor Red
    exit 1
}

# Check for OIDC provider
$oidcArn = "arn:aws:iam::816454053517:oidc-provider/token.actions.githubusercontent.com"
$oidcExists = aws iam get-open-id-connect-provider --open-id-connect-provider-arn $oidcArn 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "OIDC Provider exists" -ForegroundColor Green
} else {
    Write-Host "OIDC Provider does not exist - creating..." -ForegroundColor Yellow
    
    aws iam create-open-id-connect-provider `
        --url https://token.actions.githubusercontent.com `
        --client-id-list sts.amazonaws.com `
        --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 1c58a3a8518e8759bf075b76b750d4f2df264fcd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OIDC Provider created" -ForegroundColor Green
    } else {
        Write-Host "Failed to create OIDC Provider" -ForegroundColor Red
    }
}

# Check for GitHubActionsRole
$roleExists = aws iam get-role --role-name GitHubActionsRole 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "GitHubActionsRole exists" -ForegroundColor Green
} else {
    Write-Host "GitHubActionsRole does not exist" -ForegroundColor Yellow
    Write-Host "Please run the full setup script to create it" -ForegroundColor Yellow
}

Write-Host "Done!" -ForegroundColor Cyan