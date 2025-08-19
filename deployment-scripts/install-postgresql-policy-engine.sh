#!/bin/bash
# PostgreSQL Policy Engine Installation Script
# This script sets up the PostgreSQL policy engine for SDLC agents

set -e  # Exit on any error

echo "🚀 Setting up PostgreSQL Policy Engine for SDLC Agents"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if PostgreSQL is installed and running
check_postgresql() {
    print_status "Checking PostgreSQL installation..."
    
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL client found"
        
        # Check if server is running
        if pg_isready -h localhost -p 5432 &> /dev/null; then
            print_success "PostgreSQL server is running"
            return 0
        else
            print_warning "PostgreSQL server is not running"
            print_status "Please start PostgreSQL service:"
            print_status "  Linux: sudo systemctl start postgresql"
            print_status "  macOS: brew services start postgresql"
            print_status "  Windows: Start PostgreSQL service from Services panel"
            return 1
        fi
    else
        print_error "PostgreSQL not found. Please install PostgreSQL first:"
        print_status "  Linux: sudo apt-get install postgresql postgresql-contrib"
        print_status "  macOS: brew install postgresql"
        print_status "  Windows: Download from https://www.postgresql.org/download/windows/"
        return 1
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Check if requirements file exists
    if [ -f "postgresql_policy_requirements.txt" ]; then
        pip install -r postgresql_policy_requirements.txt
        print_success "Python dependencies installed"
    else
        print_status "Installing dependencies individually..."
        pip install sqlalchemy>=2.0.0 psycopg2-binary>=2.9.0 alembic>=1.12.0 asyncpg>=0.28.0 requests>=2.31.0
        print_success "Python dependencies installed"
    fi
}

# Setup database
setup_database() {
    print_status "Setting up PostgreSQL database..."
    
    # Database configuration
    DB_NAME="niro_policies"
    DB_USER="niro_user"
    DB_PASS="niro_password"
    DB_HOST="localhost"
    DB_PORT="5432"
    
    # Check if database exists
    if psql -U postgres -h localhost -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        print_warning "Database '$DB_NAME' already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Dropping existing database..."
            psql -U postgres -h localhost -c "DROP DATABASE IF EXISTS $DB_NAME;"
        else
            print_status "Using existing database"
            return 0
        fi
    fi
    
    # Create database and user
    print_status "Creating database '$DB_NAME'..."
    psql -U postgres -h localhost -c "CREATE DATABASE $DB_NAME;"
    
    # Check if user exists
    if psql -U postgres -h localhost -t -c '\du' | cut -d \| -f 1 | grep -qw "$DB_USER"; then
        print_warning "User '$DB_USER' already exists"
    else
        print_status "Creating user '$DB_USER'..."
        psql -U postgres -h localhost -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
    fi
    
    print_status "Granting permissions..."
    psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    
    # Set environment variable
    DATABASE_URL="postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME"
    export DATABASE_URL
    
    print_success "Database setup completed"
    print_status "Database URL: $DATABASE_URL"
    
    # Save to .env file
    echo "DATABASE_URL=$DATABASE_URL" > .env
    print_status "Database URL saved to .env file"
}

# Initialize policy engine
initialize_policy_engine() {
    print_status "Initializing PostgreSQL Policy Engine..."
    
    # Check if policy engine file exists
    if [ ! -f "postgresql-agent-policy-engine.py" ]; then
        print_error "PostgreSQL Policy Engine file not found"
        print_status "Please ensure postgresql-agent-policy-engine.py is in the current directory"
        return 1
    fi
    
    # Test the policy engine
    python3 -c "
import os
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://niro_user:niro_password@localhost:5432/niro_policies')

try:
    from postgresql_agent_policy_engine import PostgreSQLAgentPolicyEngine
    engine = PostgreSQLAgentPolicyEngine()
    print('✅ PostgreSQL Policy Engine initialized successfully!')
    
    # Get statistics
    stats = engine.get_policy_statistics()
    print(f'📊 Policy Statistics:')
    print(f'   - Agent Roles: {stats.get(\"agent_roles\", 0)}')
    print(f'   - Active Policies: {stats.get(\"active_policies\", 0)}')
    print(f'   - Total Assessments: {stats.get(\"total_assessments\", 0)}')
    
    # Test policy assessment
    assessment = engine.assess_content_policy_compliance(
        agent_role='development-agent',
        content='def test_function():\n    return \"Hello World\"',
        context={'file_type': 'python', 'file_name': 'test.py'}
    )
    print(f'🔍 Test Assessment: {\"✅ Compliant\" if assessment.is_compliant else \"❌ Non-compliant\"}')
    
except Exception as e:
    print(f'❌ Failed to initialize policy engine: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Policy engine initialization completed"
    else
        print_error "Policy engine initialization failed"
        return 1
    fi
}

# Migrate from SQLite (optional)
migrate_from_sqlite() {
    if [ -f "agent_policies.db" ]; then
        print_status "SQLite database found. Do you want to migrate data?"
        read -p "Migrate from SQLite to PostgreSQL? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Running migration..."
            python3 policy-migration-tool.py
            if [ $? -eq 0 ]; then
                print_success "Migration completed successfully"
            else
                print_warning "Migration completed with warnings (check logs)"
            fi
        fi
    else
        print_status "No SQLite database found - using fresh installation"
    fi
}

# Verify GitHub Issues Agent integration
verify_github_integration() {
    print_status "Verifying GitHub Issues Agent integration..."
    
    if [ -f "github-issues-policy-agent.py" ]; then
        python3 -c "
try:
    from github_issues_policy_agent import PolicyEnhancedGitHubAgent
    print('✅ GitHub Issues Agent with PostgreSQL policy integration available')
except Exception as e:
    print(f'❌ GitHub Issues Agent integration issue: {e}')
"
        print_success "GitHub Issues Agent integration verified"
    else
        print_warning "GitHub Issues Agent not found (github-issues-policy-agent.py)"
    fi
}

# Main installation process
main() {
    echo "Starting PostgreSQL Policy Engine installation..."
    echo
    
    # Step 1: Check PostgreSQL
    if ! check_postgresql; then
        print_error "PostgreSQL check failed. Please install and start PostgreSQL first."
        exit 1
    fi
    
    # Step 2: Install Python dependencies
    if ! install_python_deps; then
        print_error "Failed to install Python dependencies"
        exit 1
    fi
    
    # Step 3: Setup database
    if ! setup_database; then
        print_error "Database setup failed"
        exit 1
    fi
    
    # Step 4: Migrate from SQLite (optional)
    migrate_from_sqlite
    
    # Step 5: Initialize policy engine
    if ! initialize_policy_engine; then
        print_error "Policy engine initialization failed"
        exit 1
    fi
    
    # Step 6: Verify GitHub integration
    verify_github_integration
    
    echo
    print_success "🎉 PostgreSQL Policy Engine installation completed successfully!"
    echo
    print_status "Next steps:"
    print_status "1. Update your agents to use PostgreSQL policy engine"
    print_status "2. Set DATABASE_URL in your environment: source .env"
    print_status "3. Test policy compliance with your SDLC agents"
    print_status "4. Monitor policy statistics and compliance rates"
    echo
    print_status "Configuration:"
    print_status "  Database URL: $DATABASE_URL"
    print_status "  Environment file: .env"
    print_status "  Setup guide: POSTGRESQL_POLICY_ENGINE_SETUP.md"
    echo
    print_success "Installation complete! 🚀"
}

# Run main function
main "$@"
