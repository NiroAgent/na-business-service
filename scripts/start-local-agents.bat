@echo off
REM Complete Local Agent System Startup
REM Runs all agents locally with zero cloud costs

echo ========================================
echo     LOCAL AGENT ORCHESTRATION SYSTEM
echo ========================================
echo.
echo Starting local agents that:
echo - Read instructions from GitHub issues
echo - Execute all tests locally
echo - Follow SDLC process (develop-test-deploy-document)
echo - Handle timeouts with automatic retry
echo - Reference master documentation (no duplicates)
echo.
echo Master Instructions: E:\Projects\MASTER_SDLC_AGENT_INSTRUCTIONS.md
echo.
echo Select operation mode:
echo.
echo 1. SDLC Iterator (Continuous until production-ready)
echo 2. Issue Monitor (Process GitHub issues)
echo 3. Quick Test (One-time run)
echo 4. Setup Scheduled Tasks
echo 5. View Documentation
echo 6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Starting SDLC Iterator Agent...
    echo This will iterate through develop-test-deploy-document until all services are production ready
    echo.
    python E:\Projects\sdlc-iterator-agent.py --continuous
) else if "%choice%"=="2" (
    echo.
    echo Starting Issue-Driven Agent...
    echo This will monitor GitHub issues and process agent-task labels
    echo.
    python E:\Projects\issue-driven-local-agent.py --monitor
) else if "%choice%"=="3" (
    echo.
    echo Running Quick Test...
    python E:\Projects\local-agent-system.py --once
) else if "%choice%"=="4" (
    echo.
    echo Setting up Windows Scheduled Tasks...
    echo.
    
    REM Create scheduled task for SDLC iterator
    schtasks /create /tn "SDLC-Iterator-Agent" /tr "python E:\Projects\sdlc-iterator-agent.py --continuous" /sc hourly /mo 6 /f
    
    REM Create scheduled task for issue monitor
    schtasks /create /tn "Issue-Monitor-Agent" /tr "python E:\Projects\issue-driven-local-agent.py --monitor" /sc minute /mo 30 /f
    
    echo.
    echo Scheduled tasks created:
    echo - SDLC-Iterator-Agent: Runs every 6 hours
    echo - Issue-Monitor-Agent: Runs every 30 minutes
    echo.
    echo To view tasks: schtasks /query /tn "*Agent"
    echo To delete tasks: schtasks /delete /tn "SDLC-Iterator-Agent" /f
    echo.
) else if "%choice%"=="5" (
    echo.
    echo Opening documentation...
    start notepad E:\Projects\MASTER_SDLC_AGENT_INSTRUCTIONS.md
    start notepad E:\Projects\AI_AGENT_INSTRUCTIONS.md
) else if "%choice%"=="6" (
    echo.
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice!
)

echo.
echo Press any key to exit...
pause > nul