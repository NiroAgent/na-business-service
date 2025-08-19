# Smart Local Orchestrator for Windows
# Runs locally with minimal resource usage and smart scheduling

param(
    [string]$Mode = "check",  # check, test, fix, monitor
    [string]$Environment = "dev",
    [int]$MaxParallel = 1
)

# Configuration
$script:Config = @{
    MaxCPUPercent = 50
    MaxMemoryPercent = 60
    GitHubRateLimit = 60  # requests per hour
    AWSCallsPerHour = 100
    RunOnlyWhenIdle = $true
    UseGitHubActions = $false  # Set to true only for production
}

# Check if system is idle
function Test-SystemIdle {
    $cpuCounter = Get-Counter '\Processor(_Total)\% Processor Time'
    $cpu = $cpuCounter.CounterSamples[0].CookedValue
    
    $memory = Get-WmiObject Win32_OperatingSystem
    $memoryUsed = (($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100
    
    Write-Host "System Status: CPU: $([math]::Round($cpu, 2))%, Memory: $([math]::Round($memoryUsed, 2))%"
    
    if ($cpu -gt $Config.MaxCPUPercent -or $memoryUsed -gt $Config.MaxMemoryPercent) {
        Write-Host "System busy, skipping run" -ForegroundColor Yellow
        return $false
    }
    
    return $true
}

# Lightweight health check (no AWS calls)
function Test-ServiceLocal {
    param($Service, $Repo)
    
    Write-Host "`nChecking $Service locally..." -ForegroundColor Cyan
    
    $servicePath = "E:\Projects\$Repo\$Service"
    $issues = @()
    
    # Check if service directory exists
    if (-not (Test-Path $servicePath)) {
        $issues += "Service directory not found"
    }
    
    # Check package.json for outdated dependencies (no network call)
    if (Test-Path "$servicePath\package.json") {
        $packageJson = Get-Content "$servicePath\package.json" | ConvertFrom-Json
        $lastModified = (Get-Item "$servicePath\package.json").LastWriteTime
        $daysSinceUpdate = (Get-Date) - $lastModified
        
        if ($daysSinceUpdate.Days -gt 30) {
            $issues += "Dependencies may be outdated (not updated in $($daysSinceUpdate.Days) days)"
        }
    }
    
    # Check for test files
    if (-not (Test-Path "$servicePath\*.test.js") -and -not (Test-Path "$servicePath\__tests__")) {
        $issues += "No test files found"
    }
    
    # Check CloudFormation template exists
    if (-not (Test-Path "$servicePath\cloudformation.yaml") -and -not (Test-Path "$servicePath\serverless.yml")) {
        $issues += "No infrastructure template found"
    }
    
    return @{
        Service = $Service
        Repo = $Repo
        Issues = $issues
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
}

# Create GitHub issue without using API (opens browser)
function New-GitHubIssueBrowser {
    param($Repo, $Title, $Body)
    
    $encodedTitle = [System.Web.HttpUtility]::UrlEncode($Title)
    $encodedBody = [System.Web.HttpUtility]::UrlEncode($Body)
    $url = "https://github.com/stevesurles/$Repo/issues/new?title=$encodedTitle&body=$encodedBody&labels=local-agent"
    
    Write-Host "Opening browser to create issue..." -ForegroundColor Yellow
    Start-Process $url
}

# Smart decision: Should we run in cloud?
function Test-ShouldUseCloud {
    param($Environment, $Issues)
    
    # Use cloud only for:
    # 1. Production environment
    # 2. Critical issues found
    # 3. Scheduled weekly comprehensive test
    
    if ($Environment -eq "production") {
        return $true
    }
    
    $criticalIssues = $Issues | Where-Object { $_ -match "not found|error|failed" }
    if ($criticalIssues.Count -gt 3) {
        Write-Host "Critical issues found, triggering cloud workflow" -ForegroundColor Red
        return $true
    }
    
    # Check if it's Sunday (weekly comprehensive test)
    if ((Get-Date).DayOfWeek -eq "Sunday") {
        return $true
    }
    
    return $false
}

# Main orchestration
function Start-Orchestration {
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "Smart Local Orchestrator" -ForegroundColor Green
    Write-Host "Mode: $Mode | Environment: $Environment" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    
    # Check if system is idle
    if ($Config.RunOnlyWhenIdle -and -not (Test-SystemIdle)) {
        Write-Host "System busy, exiting" -ForegroundColor Yellow
        return
    }
    
    # Define services
    $services = @(
        @{Repo = "NiroSubs-V2"; Services = @("ns-auth", "ns-dashboard", "ns-payments")},
        @{Repo = "VisualForgeMediaV2"; Services = @("vf-audio-service", "vf-video-service")}
    )
    
    $allIssues = @()
    
    # Run local checks (no AWS costs)
    foreach ($repo in $services) {
        foreach ($service in $repo.Services) {
            $result = Test-ServiceLocal -Service $service -Repo $repo.Repo
            
            if ($result.Issues.Count -gt 0) {
                Write-Host "  Issues found: $($result.Issues -join ', ')" -ForegroundColor Yellow
                $allIssues += $result.Issues
            } else {
                Write-Host "  ✓ No issues" -ForegroundColor Green
            }
            
            # Rate limiting
            Start-Sleep -Seconds 2
        }
    }
    
    # Decide if we need cloud orchestration
    if (Test-ShouldUseCloud -Environment $Environment -Issues $allIssues) {
        Write-Host "`nTriggering GitHub Actions workflow..." -ForegroundColor Cyan
        
        # Trigger cloud workflow (costs apply here)
        gh workflow run master-orchestration.yml `
            --repo stevesurles/Projects `
            --field repositories=all `
            --field environment=$Environment `
            --field parallel_agents=2
    } else {
        Write-Host "`nLocal checks complete. No cloud orchestration needed." -ForegroundColor Green
        
        # Save local report
        $report = @{
            Timestamp = Get-Date
            Mode = $Mode
            Environment = $Environment
            IssuesFound = $allIssues.Count
            Issues = $allIssues
            CloudTriggered = $false
        }
        
        $reportPath = "E:\Projects\local-reports\report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        New-Item -Path (Split-Path $reportPath) -ItemType Directory -Force | Out-Null
        $report | ConvertTo-Json | Out-File $reportPath
        
        Write-Host "Report saved: $reportPath" -ForegroundColor Gray
    }
    
    Write-Host "`n==================================" -ForegroundColor Green
    Write-Host "Orchestration Complete" -ForegroundColor Green
    Write-Host "Cloud Costs: $$(if (Test-ShouldUseCloud -Environment $Environment -Issues $allIssues) {'~0.01'} else {'0.00'})" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
}

# Create scheduled task
function Install-ScheduledTask {
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
        -Argument "-NoProfile -WindowStyle Hidden -File `"E:\Projects\smart-local-orchestrator.ps1`" -Mode check -Environment dev"
    
    # Run 4 times a day when computer is idle
    $trigger = @(
        New-ScheduledTaskTrigger -Daily -At 6am
        New-ScheduledTaskTrigger -Daily -At 12pm
        New-ScheduledTaskTrigger -Daily -At 6pm
        New-ScheduledTaskTrigger -Daily -At 11pm
    )
    
    $settings = New-ScheduledTaskSettingsSet `
        -RunOnlyIfIdle `
        -IdleWaitTimeout (New-TimeSpan -Minutes 10) `
        -RestartOnIdle `
        -DontStopIfGoingOnBatteries
    
    Register-ScheduledTask `
        -TaskName "SmartAgentOrchestrator" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Smart local agent orchestrator with minimal costs" `
        -Force
    
    Write-Host "Scheduled task created: SmartAgentOrchestrator" -ForegroundColor Green
}

# Execute based on parameters
switch ($Mode) {
    "install" { Install-ScheduledTask }
    "check" { Start-Orchestration }
    "test" { 
        $Config.UseGitHubActions = $false
        Start-Orchestration 
    }
    "fix" {
        $Config.UseGitHubActions = $true
        Start-Orchestration
    }
    default { Start-Orchestration }
}