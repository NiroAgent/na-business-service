# Setup GitHub Actions OIDC provider and IAM role for AWS deployments
# This script configures AWS to trust GitHub Actions for all organizations

param(
    [Parameter(Mandatory=$false)]
    [string]$AccountId = "816454053517",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up GitHub Actions AWS Access" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AWS Account: $AccountId" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host "GitHub Orgs: All organizations (wildcarded)" -ForegroundColor Yellow
Write-Host ""

# Check AWS CLI
if (!(Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: AWS CLI is not installed" -ForegroundColor Red
    exit 1
}

# Verify AWS access
Write-Host "Verifying AWS access..." -ForegroundColor Cyan
$identity = aws sts get-caller-identity --region $Region 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Cannot access AWS. Please configure credentials." -ForegroundColor Red
    exit 1
}

$callerInfo = $identity | ConvertFrom-Json
Write-Host "Authenticated as: $($callerInfo.Arn)" -ForegroundColor Green
Write-Host ""

# Step 1: OIDC Provider (already exists from test)
Write-Host "Step 1: Checking OIDC Provider..." -ForegroundColor Cyan
$oidcProviderArn = "arn:aws:iam::${AccountId}:oidc-provider/token.actions.githubusercontent.com"

$oidcExists = aws iam get-open-id-connect-provider `
    --open-id-connect-provider-arn $oidcProviderArn `
    --region $Region 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "OIDC provider already exists" -ForegroundColor Green
} else {
    Write-Host "Creating OIDC provider..." -ForegroundColor Yellow
    
    $thumbprints = @(
        "6938fd4d98bab03faadb97b34396831e3780aea1",
        "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
    )
    
    aws iam create-open-id-connect-provider `
        --url https://token.actions.githubusercontent.com `
        --client-id-list sts.amazonaws.com `
        --thumbprint-list $thumbprints `
        --region $Region
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OIDC provider created successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to create OIDC provider" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 2: Create IAM Role with Trust Policy
Write-Host "Step 2: Creating IAM Role..." -ForegroundColor Cyan

# Trust policy that allows any GitHub org to deploy these specific repos
$trustPolicy = @'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::816454053517:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": [
                        "repo:*/NiroSubs-V2:*",
                        "repo:*/VisualForgeMediaV2:*"
                    ]
                }
            }
        }
    ]
}
'@

# Save trust policy to temp file
$trustPolicyFile = "$env:TEMP\github-trust-policy.json"
$trustPolicy | Out-File -FilePath $trustPolicyFile -Encoding UTF8

# Check if role exists
$roleExists = aws iam get-role --role-name GitHubActionsRole --region $Region 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating IAM role..." -ForegroundColor Yellow
    
    aws iam create-role `
        --role-name GitHubActionsRole `
        --assume-role-policy-document file://$trustPolicyFile `
        --description "Role for GitHub Actions to deploy to AWS" `
        --region $Region
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "IAM role created successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to create IAM role" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Updating existing role trust policy..." -ForegroundColor Yellow
    
    aws iam update-assume-role-policy `
        --role-name GitHubActionsRole `
        --policy-document file://$trustPolicyFile `
        --region $Region
    
    Write-Host "IAM role trust policy updated" -ForegroundColor Green
}

Write-Host ""

# Step 3: Create and Attach Deployment Policy
Write-Host "Step 3: Attaching policies to role..." -ForegroundColor Cyan

# Create deployment policy
$deploymentPolicy = @'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:*",
                "s3:*",
                "lambda:*",
                "apigateway:*",
                "cognito-idp:*",
                "ecs:*",
                "ecr:*",
                "elasticloadbalancing:*",
                "cloudfront:*",
                "route53:*",
                "secretsmanager:*",
                "ssm:*",
                "iam:GetRole",
                "iam:PassRole",
                "iam:CreateServiceLinkedRole",
                "ec2:Describe*",
                "ec2:CreateSecurityGroup",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupEgress",
                "ec2:DeleteSecurityGroup",
                "ec2:CreateTags",
                "ec2:ModifySecurityGroupRules",
                "logs:*",
                "cloudwatch:*",
                "rds:*",
                "sns:*",
                "sqs:*"
            ],
            "Resource": "*"
        }
    ]
}
'@

# Save deployment policy to temp file
$deploymentPolicyFile = "$env:TEMP\github-deployment-policy.json"
$deploymentPolicy | Out-File -FilePath $deploymentPolicyFile -Encoding UTF8

# Create or update the deployment policy
$policyArn = "arn:aws:iam::${AccountId}:policy/GitHubActionsDeploymentPolicy"

$policyExists = aws iam get-policy --policy-arn $policyArn --region $Region 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating deployment policy..." -ForegroundColor Yellow
    
    aws iam create-policy `
        --policy-name GitHubActionsDeploymentPolicy `
        --policy-document file://$deploymentPolicyFile `
        --description "Policy for GitHub Actions deployments" `
        --region $Region
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Deployment policy created" -ForegroundColor Green
    } else {
        Write-Host "Failed to create deployment policy" -ForegroundColor Red
    }
} else {
    Write-Host "Deployment policy already exists" -ForegroundColor Green
}

# Attach the policy to the role
Write-Host "Attaching policies to role..." -ForegroundColor Yellow

aws iam attach-role-policy `
    --role-name GitHubActionsRole `
    --policy-arn $policyArn `
    --region $Region 2>&1 | Out-Null

# Also attach AWS managed policies
$managedPolicies = @(
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser",
    "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
)

foreach ($policy in $managedPolicies) {
    aws iam attach-role-policy `
        --role-name GitHubActionsRole `
        --policy-arn $policy `
        --region $Region 2>&1 | Out-Null
}

Write-Host "Policies attached to role" -ForegroundColor Green
Write-Host ""

# Step 4: Create Lambda execution role
Write-Host "Step 4: Creating Lambda execution role..." -ForegroundColor Cyan

$lambdaTrustPolicy = @'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
'@

$lambdaTrustFile = "$env:TEMP\lambda-trust.json"
$lambdaTrustPolicy | Out-File -FilePath $lambdaTrustFile -Encoding UTF8

$lambdaRoleExists = aws iam get-role --role-name dev-visualforge-lambda-role --region $Region 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating Lambda execution role..." -ForegroundColor Yellow
    
    aws iam create-role `
        --role-name dev-visualforge-lambda-role `
        --assume-role-policy-document file://$lambdaTrustFile `
        --description "Execution role for Lambda functions" `
        --region $Region
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy `
        --role-name dev-visualforge-lambda-role `
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole `
        --region $Region
    
    # Attach VPC access policy
    aws iam attach-role-policy `
        --role-name dev-visualforge-lambda-role `
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole `
        --region $Region
    
    Write-Host "Lambda execution role created" -ForegroundColor Green
} else {
    Write-Host "Lambda execution role already exists" -ForegroundColor Green
}

Write-Host ""

# Clean up temp files
Remove-Item -Path $trustPolicyFile -Force -ErrorAction SilentlyContinue
Remove-Item -Path $deploymentPolicyFile -Force -ErrorAction SilentlyContinue
Remove-Item -Path $lambdaTrustFile -Force -ErrorAction SilentlyContinue

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created/Updated Resources:" -ForegroundColor Green
Write-Host "  OIDC Provider: $oidcProviderArn" -ForegroundColor Gray
Write-Host "  IAM Role: arn:aws:iam::${AccountId}:role/GitHubActionsRole" -ForegroundColor Gray
Write-Host "  Lambda Role: arn:aws:iam::${AccountId}:role/dev-visualforge-lambda-role" -ForegroundColor Gray
Write-Host "  Deployment Policy: $policyArn" -ForegroundColor Gray
Write-Host ""
Write-Host "GitHub Access Configuration:" -ForegroundColor Yellow
Write-Host "  - Any GitHub organization can deploy these repos:" -ForegroundColor Gray
Write-Host "    * NiroSubs-V2" -ForegroundColor Gray
Write-Host "    * VisualForgeMediaV2" -ForegroundColor Gray
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Initialize git repositories for both projects" -ForegroundColor Gray
Write-Host "2. Push repositories to GitHub" -ForegroundColor Gray
Write-Host "3. Create 'dev' branch in both repositories" -ForegroundColor Gray
Write-Host "4. Push to 'dev' branch to trigger deployments" -ForegroundColor Gray
Write-Host ""
Write-Host "GitHub Repository Secrets Required:" -ForegroundColor Yellow
Write-Host "  DB_PASSWORD - Database password for RDS" -ForegroundColor Gray
Write-Host "  COGNITO_USER_POOL_ID - Cognito User Pool ID (optional)" -ForegroundColor Gray
Write-Host ""

# Save configuration
$config = @{
    AccountId = $AccountId
    Region = $Region
    OIDCProviderArn = $oidcProviderArn
    GitHubActionsRoleArn = "arn:aws:iam::${AccountId}:role/GitHubActionsRole"
    LambdaRoleArn = "arn:aws:iam::${AccountId}:role/dev-visualforge-lambda-role"
    DeploymentPolicyArn = $policyArn
    AllowedRepos = @("*/NiroSubs-V2", "*/VisualForgeMediaV2")
    SetupDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

$configPath = "E:\Projects\github-actions-aws-config.json"
$config | ConvertTo-Json -Depth 3 | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "Configuration saved to: $configPath" -ForegroundColor Gray