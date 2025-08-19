@echo off
echo ========================================
echo MONITORING SYSTEM STATUS CHECK
echo ========================================
echo.
echo [1] DASHBOARD LOCATIONS:
echo    - HTML Dashboard: E:\Projects\live-dashboard.html
echo    - Markdown Dashboard: E:\Projects\monitoring-dashboard.md
echo    - Setup Instructions: E:\Projects\setup-github-project.md
echo.
echo [2] MONITORING SCRIPTS:
echo    - Continuous Monitor: src\agents\continuous-system-monitor.py
echo    - Self-Managing Monitor: src\agents\self-managing-monitor.py
echo    - Ultimate Delegator: src\agents\ultimate-delegator.py
echo.
echo [3] CHECKING RECENT ACTIVITY...
gh issue list --repo VisualForgeMediaV2/business-operations --limit 5 --state all
echo.
echo [4] GITHUB PROJECT:
echo    To create the org project, run:
echo    create-org-project-with-dashboard.sh
echo.
echo    Or visit manually:
echo    https://github.com/orgs/VisualForgeMediaV2/projects
echo.
echo ========================================
echo DASHBOARD IS READY TO VIEW!
echo Open: E:\Projects\live-dashboard.html
echo ========================================
pause