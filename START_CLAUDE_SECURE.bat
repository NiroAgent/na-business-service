@echo off
echo ========================================
echo STARTING CLAUDE SYSTEM INTERFACE
echo ========================================
echo.

cd vf-agent-service-local

REM Retrieve API key from AWS Secrets Manager
echo Retrieving API key from AWS Secrets Manager...
for /f "tokens=*" %%i in ('aws secretsmanager get-secret-value --secret-id anthropic-api-key --query SecretString --output text 2^>nul') do set ANTHROPIC_API_KEY=%%i

if "%ANTHROPIC_API_KEY%"=="" (
    echo ERROR: Failed to retrieve API key from AWS Secrets Manager
    echo.
    echo Make sure:
    echo 1. AWS CLI is configured: aws configure
    echo 2. Secret exists: aws secretsmanager describe-secret --secret-id anthropic-api-key
    echo 3. You have permission to access the secret
    echo.
    echo To create the secret:
    echo   aws secretsmanager create-secret --name anthropic-api-key --secret-string "your-api-key-here"
    echo.
    pause
    exit /b 1
)

echo API key retrieved successfully from AWS Secrets Manager
echo.

echo Checking for dependencies...
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo.
echo Starting service...
call npm run anthropic

pause