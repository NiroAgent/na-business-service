@echo off
echo ========================================
echo STARTING CLAUDE SYSTEM INTERFACE
echo ========================================
echo.

cd vf-agent-service-local

REM Load API key from .env file or environment variable
REM Make sure to create a .env file with ANTHROPIC_API_KEY=your-key-here
REM Or set it as a Windows environment variable

if exist ..\.env (
    echo Loading API key from .env file...
    for /f "tokens=1,2 delims==" %%a in (..\.env) do (
        if "%%a"=="ANTHROPIC_API_KEY" set ANTHROPIC_API_KEY=%%b
    )
) else (
    echo WARNING: No .env file found. Make sure ANTHROPIC_API_KEY is set in environment variables.
)

if "%ANTHROPIC_API_KEY%"=="" (
    echo ERROR: ANTHROPIC_API_KEY not found!
    echo Please create a .env file with your API key or set it as an environment variable.
    echo Example .env file:
    echo   ANTHROPIC_API_KEY=your-api-key-here
    pause
    exit /b 1
)

echo Checking for dependencies...
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo.
echo Starting service...
call npm run anthropic

pause