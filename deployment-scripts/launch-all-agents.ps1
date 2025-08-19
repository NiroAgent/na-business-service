# PowerShell script to launch all agents and dashboard
# This script starts the agents and dashboard for monitoring

Write-Host "🚀 Launching Agent Orchestration System" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan

# Define paths
$ProjectsDir = "E:\Projects"
$PythonExe = "$ProjectsDir\.venv\Scripts\python.exe"

# Check if Python virtual environment exists
if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ Python virtual environment not found at: $PythonExe" -ForegroundColor Red
    Write-Host "Please run setup first or check the path." -ForegroundColor Yellow
    exit 1
}

# Change to projects directory
Set-Location $ProjectsDir

Write-Host "`n🔧 Starting Agent Dashboard..." -ForegroundColor Yellow
# Start the dashboard in a new window
$DashboardProcess = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Write-Host 'Agent Dashboard' -ForegroundColor Magenta; cd '$ProjectsDir'; & '$PythonExe' simple-agent-dashboard.py"
) -PassThru

# Wait for dashboard to start
Start-Sleep -Seconds 3

Write-Host "✅ Dashboard started on http://localhost:5000" -ForegroundColor Green

Write-Host "`n🤖 Starting GitHub Copilot Orchestrator..." -ForegroundColor Yellow
# Start the interactive orchestrator in a new window
$OrchestratorProcess = Start-Process powershell -ArgumentList @(
    "-NoExit", 
    "-Command",
    "Write-Host 'GitHub Copilot Orchestrator' -ForegroundColor Cyan; cd '$ProjectsDir'; & '$PythonExe' gh-copilot-orchestrator.py --interactive"
) -PassThru

Write-Host "✅ GitHub Copilot Orchestrator started" -ForegroundColor Green

Write-Host "`n🏠 Starting Local Orchestrator..." -ForegroundColor Yellow
# Start the local orchestrator in a new window  
$LocalProcess = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command", 
    "Write-Host 'Local Orchestrator' -ForegroundColor Green; cd '$ProjectsDir'; & '$PythonExe' local-orchestrator.py --auto --env dev"
) -PassThru

Write-Host "✅ Local Orchestrator started" -ForegroundColor Green

# Wait a bit for everything to initialize
Start-Sleep -Seconds 5

# Open the dashboard in browser
Write-Host "`n🌐 Opening dashboard in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:5000"

Write-Host "`n" -NoNewline
Write-Host "🎉 AGENT ORCHESTRATION SYSTEM LAUNCHED!" -ForegroundColor Green -BackgroundColor Black
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n📊 System Overview:" -ForegroundColor White
Write-Host "   🖥️  Dashboard:    http://localhost:5000" -ForegroundColor White
Write-Host "   🤖 Copilot Agent: Interactive mode in separate window" -ForegroundColor White  
Write-Host "   🏠 Local Agent:   Running automated tests" -ForegroundColor White

Write-Host "`n🎮 Usage:" -ForegroundColor White
Write-Host "   • Use the web dashboard to monitor and control agents" -ForegroundColor Gray
Write-Host "   • The Copilot Orchestrator window allows manual commands" -ForegroundColor Gray
Write-Host "   • Local Orchestrator runs automated health checks" -ForegroundColor Gray
Write-Host "   • Check GitHub for issues created by the agents" -ForegroundColor Gray

Write-Host "`n📁 Agent Results:" -ForegroundColor White
Write-Host "   • Orchestration results: $ProjectsDir\orchestration_results\" -ForegroundColor Gray
Write-Host "   • Local reports: $ProjectsDir\local_report_*.md" -ForegroundColor Gray
Write-Host "   • GitHub issues: Check your repositories" -ForegroundColor Gray

Write-Host "`n⚠️  To stop all agents:" -ForegroundColor Yellow
Write-Host "   1. Close all PowerShell windows" -ForegroundColor Gray
Write-Host "   2. Or use Ctrl+C in each window" -ForegroundColor Gray
Write-Host "   3. Or stop via the dashboard" -ForegroundColor Gray

Write-Host "`n✨ Enjoy your AI agent orchestration!" -ForegroundColor Green

# Optional: Keep this window open to show status
Write-Host "`nPress any key to exit launcher (agents will continue running)..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
