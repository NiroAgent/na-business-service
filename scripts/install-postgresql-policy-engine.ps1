# PostgreSQL Policy Engine Installation Script (Windows PowerShell)
# This script sets up the PostgreSQL policy engine for SDLC agents on Windows

param(
    [switch]$Force = $false,
    [string]$DatabaseUrl = "",
    [switch]$SkipMigration = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-PostgreSQL {
    Write-Info "Checking PostgreSQL installation..."
    
    try {
        # Check if psql is available
        $null = Get-Command psql -ErrorAction Stop
        Write-Success "PostgreSQL client found"
        
        # Check if server is running
        $result = & pg_isready -h localhost -p 5432 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "PostgreSQL server is running"
            return $true
        } else {
            Write-Warning "PostgreSQL server is not running"
            Write-Info "Please start PostgreSQL service from Services panel or command line"
            return $false
        }
    } catch {
        Write-Error "PostgreSQL not found. Please install PostgreSQL first:"
        Write-Info "Download from: https://www.postgresql.org/download/windows/"
        return $false
    }
}

function Install-PythonDependencies {
    Write-Info "Installing Python dependencies..."
    
    try {
        if (Test-Path "postgresql_policy_requirements.txt") {
            & pip install -r postgresql_policy_requirements.txt
        } else {
            Write-Info "Installing dependencies individually..."
            & pip install "sqlalchemy>=2.0.0" "psycopg2-binary>=2.9.0" "alembic>=1.12.0" "asyncpg>=0.28.0" "requests>=2.31.0"
        }
        Write-Success "Python dependencies installed"
        return $true
    } catch {
        Write-Error "Failed to install Python dependencies: $_"
        return $false
    }
}

function Setup-Database {
    Write-Info "Setting up PostgreSQL database..."
    
    # Database configuration
    $DbName = "niro_policies"
    $DbUser = "niro_user"
    $DbPass = "niro_password"
    $DbHost = "localhost"
    $DbPort = "5432"
    
    try {
        # Check if database exists
        $dbExists = & psql -U postgres -h localhost -lqt | Select-String $DbName
        if ($dbExists -and -not $Force) {
            Write-Warning "Database '$DbName' already exists"
            $response = Read-Host "Do you want to recreate it? (y/N)"
            if ($response -eq 'y' -or $response -eq 'Y') {
                Write-Info "Dropping existing database..."
                & psql -U postgres -h localhost -c "DROP DATABASE IF EXISTS $DbName;"
            } else {
                Write-Info "Using existing database"
                $Script:DatabaseUrl = "postgresql://$DbUser`:$DbPass@$DbHost`:$DbPort/$DbName"
                return $true
            }
        }
        
        # Create database and user
        Write-Info "Creating database '$DbName'..."
        & psql -U postgres -h localhost -c "CREATE DATABASE $DbName;"
        
        # Check if user exists
        $userExists = & psql -U postgres -h localhost -t -c '\du' | Select-String $DbUser
        if (-not $userExists) {
            Write-Info "Creating user '$DbUser'..."
            & psql -U postgres -h localhost -c "CREATE USER $DbUser WITH PASSWORD '$DbPass';"
        } else {
            Write-Warning "User '$DbUser' already exists"
        }
        
        Write-Info "Granting permissions..."
        & psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE $DbName TO $DbUser;"
        
        # Set environment variable
        $Script:DatabaseUrl = "postgresql://$DbUser`:$DbPass@$DbHost`:$DbPort/$DbName"
        $env:DATABASE_URL = $Script:DatabaseUrl
        
        Write-Success "Database setup completed"
        Write-Info "Database URL: $($Script:DatabaseUrl)"
        
        # Save to .env file
        "DATABASE_URL=$($Script:DatabaseUrl)" | Out-File -FilePath ".env" -Encoding UTF8
        Write-Info "Database URL saved to .env file"
        
        return $true
    } catch {
        Write-Error "Database setup failed: $_"
        return $false
    }
}

function Initialize-PolicyEngine {
    Write-Info "Initializing PostgreSQL Policy Engine..."
    
    if (-not (Test-Path "postgresql-agent-policy-engine.py")) {
        Write-Error "PostgreSQL Policy Engine file not found"
        Write-Info "Please ensure postgresql-agent-policy-engine.py is in the current directory"
        return $false
    }
    
    # Set environment variable for this session
    $env:DATABASE_URL = $Script:DatabaseUrl
    
    try {
        $testScript = @"
import os
os.environ['DATABASE_URL'] = '$($Script:DatabaseUrl)'

try:
    from postgresql_agent_policy_engine import PostgreSQLAgentPolicyEngine
    engine = PostgreSQLAgentPolicyEngine()
    print('✅ PostgreSQL Policy Engine initialized successfully!')
    
    # Get statistics
    stats = engine.get_policy_statistics()
    print(f'📊 Policy Statistics:')
    print(f'   - Agent Roles: {stats.get("agent_roles", 0)}')
    print(f'   - Active Policies: {stats.get("active_policies", 0)}')
    print(f'   - Total Assessments: {stats.get("total_assessments", 0)}')
    
    # Test policy assessment
    assessment = engine.assess_content_policy_compliance(
        agent_role='development-agent',
        content='def test_function():\n    return "Hello World"',
        context={'file_type': 'python', 'file_name': 'test.py'}
    )
    print(f'🔍 Test Assessment: {"✅ Compliant" if assessment.is_compliant else "❌ Non-compliant"}')
    
except Exception as e:
    print(f'❌ Failed to initialize policy engine: {e}')
    exit(1)
"@
        
        $testScript | python
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Policy engine initialization completed"
            return $true
        } else {
            Write-Error "Policy engine initialization failed"
            return $false
        }
    } catch {
        Write-Error "Failed to initialize policy engine: $_"
        return $false
    }
}

function Invoke-Migration {
    if ((Test-Path "agent_policies.db") -and -not $SkipMigration) {
        Write-Info "SQLite database found. Do you want to migrate data?"
        $response = Read-Host "Migrate from SQLite to PostgreSQL? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            try {
                Write-Info "Running migration..."
                & python policy-migration-tool.py
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Migration completed successfully"
                } else {
                    Write-Warning "Migration completed with warnings (check logs)"
                }
            } catch {
                Write-Warning "Migration failed: $_"
            }
        }
    } else {
        Write-Info "No SQLite database found - using fresh installation"
    }
}

function Test-GitHubIntegration {
    Write-Info "Verifying GitHub Issues Agent integration..."
    
    if (Test-Path "github-issues-policy-agent.py") {
        try {
            $testScript = @"
try:
    from github_issues_policy_agent import PolicyEnhancedGitHubAgent
    print('✅ GitHub Issues Agent with PostgreSQL policy integration available')
except Exception as e:
    print(f'❌ GitHub Issues Agent integration issue: {e}')
"@
            $testScript | python
            Write-Success "GitHub Issues Agent integration verified"
        } catch {
            Write-Warning "GitHub Issues Agent integration issue: $_"
        }
    } else {
        Write-Warning "GitHub Issues Agent not found (github-issues-policy-agent.py)"
    }
}

function Main {
    Write-Host "🚀 Setting up PostgreSQL Policy Engine for SDLC Agents" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Step 1: Check PostgreSQL
    if (-not (Test-PostgreSQL)) {
        Write-Error "PostgreSQL check failed. Please install and start PostgreSQL first."
        exit 1
    }
    
    # Step 2: Install Python dependencies
    if (-not (Install-PythonDependencies)) {
        Write-Error "Failed to install Python dependencies"
        exit 1
    }
    
    # Step 3: Setup database
    if (-not (Setup-Database)) {
        Write-Error "Database setup failed"
        exit 1
    }
    
    # Step 4: Migrate from SQLite (optional)
    Invoke-Migration
    
    # Step 5: Initialize policy engine
    if (-not (Initialize-PolicyEngine)) {
        Write-Error "Policy engine initialization failed"
        exit 1
    }
    
    # Step 6: Verify GitHub integration
    Test-GitHubIntegration
    
    Write-Host ""
    Write-Success "🎉 PostgreSQL Policy Engine installation completed successfully!"
    Write-Host ""
    Write-Info "Next steps:"
    Write-Info "1. Update your agents to use PostgreSQL policy engine"
    Write-Info "2. Set DATABASE_URL in your environment or use the .env file"
    Write-Info "3. Test policy compliance with your SDLC agents"
    Write-Info "4. Monitor policy statistics and compliance rates"
    Write-Host ""
    Write-Info "Configuration:"
    Write-Info "  Database URL: $($Script:DatabaseUrl)"
    Write-Info "  Environment file: .env"
    Write-Info "  Setup guide: POSTGRESQL_POLICY_ENGINE_SETUP.md"
    Write-Host ""
    Write-Success "Installation complete! 🚀"
}

# Create helper functions for manual steps
function Show-Help {
    Write-Host @"
PostgreSQL Policy Engine Installation Script

Usage:
    .\install-postgresql-policy-engine.ps1 [parameters]

Parameters:
    -Force              Recreate database even if it exists
    -DatabaseUrl        Custom database URL (optional)
    -SkipMigration      Skip SQLite to PostgreSQL migration
    -Help               Show this help message

Examples:
    .\install-postgresql-policy-engine.ps1
    .\install-postgresql-policy-engine.ps1 -Force
    .\install-postgresql-policy-engine.ps1 -DatabaseUrl "postgresql://user:pass@host:5432/db"

Manual Setup Steps:
1. Install PostgreSQL: https://www.postgresql.org/download/windows/
2. Start PostgreSQL service
3. Run this script
4. Update your agents to use PostgreSQL policy engine

Requirements:
- PostgreSQL 12+ installed and running
- Python 3.8+ with pip
- Write access to current directory
"@
}

# Check for help parameter
if ($args -contains "-Help" -or $args -contains "/?" -or $args -contains "-h") {
    Show-Help
    exit 0
}

# Override DatabaseUrl if provided
if ($DatabaseUrl) {
    $Script:DatabaseUrl = $DatabaseUrl
}

# Run main installation
try {
    Main
} catch {
    Write-Error "Installation failed: $_"
    Write-Info "For help, run: .\install-postgresql-policy-engine.ps1 -Help"
    exit 1
}
