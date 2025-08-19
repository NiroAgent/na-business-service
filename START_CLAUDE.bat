@echo off
echo ========================================
echo STARTING CLAUDE SYSTEM INTERFACE
echo ========================================
echo.
echo API Key will be retrieved from AWS Secrets Manager at runtime
echo.

cd vf-agent-service-local

REM No need to set API key here - it's retrieved in the code

echo Checking for dependencies...
if not exist node_modules (
    echo Installing dependencies...
    call npm install
    call npm install aws-sdk @anthropic-ai/sdk
)

echo.
echo Starting service...
echo Note: The application will retrieve the API key from AWS Secrets Manager
call npm run anthropic

pause