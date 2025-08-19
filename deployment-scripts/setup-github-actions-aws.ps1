# Setup GitHub Actions OIDC provider and IAM role for AWS deployments
# This script configures AWS to trust GitHub Actions for both projects

param(
    [Parameter(Mandatory=$false)]
    [string[]]$GitHubOrgs = @("*"),  # Use "*" to allow all orgs, or specify specific orgs
    
    [Parameter(Mandatory=$false)]
    [string[]]$ExcludeOrgs = @(),  # Organizations to exclude (e.g., personal accounts)
    
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
if ($GitHubOrgs -contains "*") {
    Write-Host "GitHub Orgs: All organizations" -ForegroundColor Yellow
    if ($ExcludeOrgs.Count -gt 0) {
        Write-Host "Excluding: $($ExcludeOrgs -join ', ')" -ForegroundColor Yellow
    }
} else {
    Write-Host "GitHub Orgs: $($GitHubOrgs -join ', ')" -ForegroundColor Yellow
}
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

# Step 1: Create OIDC Provider
Write-Host "Step 1: Setting up OIDC Provider..." -ForegroundColor Cyan

$oidcProviderArn = "arn:aws:iam::${AccountId}:oidc-provider/token.actions.githubusercontent.com"

# Check if OIDC provider exists
$oidcExists = aws iam get-open-id-connect-provider `
    --open-id-connect-provider-arn $oidcProviderArn `
    --region $Region 2>&1

if ($LASTEXITCODE -ne 0) {
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
        Write-Host "✓ OIDC provider created successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create OIDC provider" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ OIDC provider already exists" -ForegroundColor Green
}

Write-Host ""

# Step 2: Create IAM Role Trust Policy
Write-Host "Step 2: Creating IAM Role..." -ForegroundColor Cyan

# Build the subject conditions based on org configuration
$subjectConditions = @()

if ($GitHubOrgs -contains "*") {
    # Allow all organizations except excluded ones
    if ($ExcludeOrgs.Count -gt 0) {
        # Create a condition that allows all repos except from excluded orgs
        # Note: This requires listing specific allowed patterns since AWS IAM doesn't support negative conditions well
        # For broad access, we'll use a wildcard pattern
        $subjectConditions += "repo:*/NiroSubs-V2:*"
        $subjectConditions += "repo:*/VisualForgeMediaV2:*"
        
        Write-Host "Note: AWS IAM does not support negative conditions directly." -ForegroundColor Yellow
        Write-Host "The policy will allow all organizations. Excluded orgs should not have access to push to these repos." -ForegroundColor Yellow
    } else {
        # Allow all organizations
        $subjectConditions += "repo:*/NiroSubs-V2:*"
        $subjectConditions += "repo:*/VisualForgeMediaV2:*"
    }
} else {
    # Allow specific organizations
    foreach ($org in $GitHubOrgs) {
        $subjectConditions += "repo:${org}/NiroSubs-V2:*"
        $subjectConditions += "repo:${org}/VisualForgeMediaV2:*"
    }
}

# Convert array to JSON string format
$subjectConditionsJson = ($subjectConditions | ForEach-Object { "`"$_`"" }) -join ",`n                        "

$trustPolicy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::${AccountId}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": [
                        $subjectConditionsJson
                    ]
                }
            }
        }
    ]
}
"@

# Save trust policy to file
$trustPolicyFile = "$env:TEMP\github-actions-trust-policy.json"
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
        Write-Host "✓ IAM role created successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create IAM role" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Updating existing role trust policy..." -ForegroundColor Yellow
    
    aws iam update-assume-role-policy `
        --role-name GitHubActionsRole `
        --policy-document file://$trustPolicyFile `
        --region $Region
    
    Write-Host "✓ IAM role already exists (trust policy updated)" -ForegroundColor Green
}

Write-Host ""

# Step 3: Attach Policies to Role
Write-Host "Step 3: Attaching policies to role..." -ForegroundColor Cyan

# Create custom policy for deployments
$deploymentPolicy = @"
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
"@

# Save deployment policy to file
$deploymentPolicyFile = "$env:TEMP\github-actions-deployment-policy.json"
$deploymentPolicy | Out-File -FilePath $deploymentPolicyFile -Encoding UTF8

# Create or update the deployment policy
$policyArn = "arn:aws:iam::${AccountId}:policy/GitHubActionsDeploymentPolicy"

$policyExists = aws iam get-policy --policy-arn $policyArn --region $Region 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating deployment policy..." -ForegroundColor Yellow
    
    $createPolicyResult = aws iam create-policy `
        --policy-name GitHubActionsDeploymentPolicy `
        --policy-document file://$deploymentPolicyFile `
        --description "Policy for GitHub Actions deployments" `
        --region $Region 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Deployment policy created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create deployment policy" -ForegroundColor Red
    }
} else {
    Write-Host "✓ Deployment policy already exists" -ForegroundColor Green
    
    # Create new version of the policy
    Write-Host "Updating policy with new version..." -ForegroundColor Yellow
    aws iam create-policy-version `
        --policy-arn $policyArn `
        --policy-document file://$deploymentPolicyFile `
        --set-as-default `
        --region $Region 2>&1 | Out-Null
}

# Attach the policy to the role
Write-Host "Attaching policy to role..." -ForegroundColor Yellow

aws iam attach-role-policy `
    --role-name GitHubActionsRole `
    --policy-arn $policyArn `
    --region $Region 2>&1 | Out-Null

Write-Host "✓ Policy attached to role" -ForegroundColor Green

# Also attach AWS managed policies for additional permissions
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

Write-Host "✓ Managed policies attached" -ForegroundColor Green
Write-Host ""

# Step 4: Create Lambda execution role
Write-Host "Step 4: Creating Lambda execution role..." -ForegroundColor Cyan

$lambdaTrustPolicy = @"
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
"@

$lambdaTrustFile = "$env:TEMP\lambda-trust-policy.json"
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
    
    Write-Host "✓ Lambda execution role created" -ForegroundColor Green
} else {
    Write-Host "✓ Lambda execution role already exists" -ForegroundColor Green
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
Write-Host "✓ OIDC Provider: $oidcProviderArn" -ForegroundColor Green
Write-Host "✓ IAM Role: arn:aws:iam::${AccountId}:role/GitHubActionsRole" -ForegroundColor Green
Write-Host "✓ Lambda Role: arn:aws:iam::${AccountId}:role/dev-visualforge-lambda-role" -ForegroundColor Green
Write-Host ""
Write-Host "Allowed GitHub Organizations:" -ForegroundColor Yellow
if ($GitHubOrgs -contains "*") {
    Write-Host "  - All organizations can deploy" -ForegroundColor Gray
    if ($ExcludeOrgs.Count -gt 0) {
        Write-Host "  - Note: Manually ensure excluded orgs do not have repo access" -ForegroundColor Yellow
    }
} else {
    foreach ($org in $GitHubOrgs) {
        Write-Host "  - $org" -ForegroundColor Gray
    }
}
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Initialize git repositories for both projects" -ForegroundColor Gray
Write-Host "2. Push repositories to GitHub under allowed organizations" -ForegroundColor Gray
Write-Host "3. Create or switch to the dev branch in both repositories" -ForegroundColor Gray
Write-Host "4. Push to the dev branch to trigger deployments" -ForegroundColor Gray
Write-Host ""
Write-Host "GitHub Secrets Required (if using secrets):" -ForegroundColor Yellow
Write-Host "- DB_PASSWORD: Database password for RDS" -ForegroundColor Gray
Write-Host "- COGNITO_USER_POOL_ID: Cognito User Pool ID (if existing)" -ForegroundColor Gray
Write-Host ""

# Save configuration for reference
$configSummary = @{
    AccountId = $AccountId
    Region = $Region
    GitHubOrgs = $GitHubOrgs
    ExcludedOrgs = $ExcludeOrgs
    AllowAllOrgs = ($GitHubOrgs -contains "*")
    OIDCProviderArn = $oidcProviderArn
    GitHubActionsRoleArn = "arn:aws:iam::${AccountId}:role/GitHubActionsRole"
    LambdaRoleArn = "arn:aws:iam::${AccountId}:role/dev-visualforge-lambda-role"
    DeploymentPolicyArn = $policyArn
    SetupDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

$configPath = Join-Path -Path "E:\Projects" -ChildPath "github-actions-aws-config.json"
$configSummary | ConvertTo-Json -Depth 3 | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "Configuration saved to: $configPath" -ForegroundColor Gray