@echo off
echo ========================================
echo STARTING CLAUDE SERVICE (SIMPLE MODE)
echo ========================================
echo.

cd vf-agent-service-local

REM Install dependencies if needed
if not exist node_modules\express (
    echo Installing required packages...
    npm install express cors
)

echo.
echo Starting Claude service on port 3003...
echo.

node api/src/simple-claude-server.js