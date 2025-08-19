# PostgreSQL Policy Engine Setup Guide

## Overview
This guide helps you migrate the SDLC agent policy system from SQLite to PostgreSQL for production deployment and consistency with other solutions in the ecosystem.

## Prerequisites

1. **PostgreSQL Server**
   - Local PostgreSQL instance running on localhost
   - Or remote PostgreSQL server with connection details
   - PostgreSQL 12+ recommended

2. **Python Dependencies**
   ```bash
   pip install -r postgresql_policy_requirements.txt
   ```

## Setup Steps

### 1. Database Setup

#### Option A: Local PostgreSQL Setup
```bash
# Install PostgreSQL (if not already installed)
# Windows: Download from https://www.postgresql.org/download/windows/
# Linux: sudo apt-get install postgresql postgresql-contrib
# macOS: brew install postgresql

# Start PostgreSQL service
# Windows: Use PostgreSQL Service Manager
# Linux: sudo systemctl start postgresql
# macOS: brew services start postgresql

# Create database and user
psql -U postgres
```

```sql
-- Run in PostgreSQL shell
CREATE DATABASE niro_policies;
CREATE USER niro_user WITH PASSWORD 'niro_password';
GRANT ALL PRIVILEGES ON DATABASE niro_policies TO niro_user;
\q
```

#### Option B: Use Existing Database
If you already have a PostgreSQL instance, create a new database:
```sql
CREATE DATABASE niro_policies;
-- Grant permissions to your existing user
```

### 2. Environment Configuration

Create or update your environment variables:

```bash
# Option 1: .env file
echo "DATABASE_URL=postgresql://niro_user:niro_password@localhost:5432/niro_policies" >> .env

# Option 2: System environment
export DATABASE_URL="postgresql://niro_user:niro_password@localhost:5432/niro_policies"

# For VF-Agent-Service integration (optional)
export VF_AGENT_SERVICE_URL="http://localhost:3000"
```

### 3. Install Dependencies

```bash
# Install PostgreSQL dependencies
pip install -r postgresql_policy_requirements.txt

# Or install individually
pip install sqlalchemy>=2.0.0 psycopg2-binary>=2.9.0 alembic>=1.12.0 asyncpg>=0.28.0
```

### 4. Database Migration

#### Option A: Fresh Installation
```bash
# Initialize new PostgreSQL policy engine (creates tables and default data)
python postgresql-agent-policy-engine.py
```

#### Option B: Migrate from SQLite
```bash
# Migrate existing SQLite data to PostgreSQL
python policy-migration-tool.py
```

### 5. Verify Installation

```bash
# Test the policy engine
python -c "
from postgresql_agent_policy_engine import PostgreSQLAgentPolicyEngine
engine = PostgreSQLAgentPolicyEngine()
print('PostgreSQL Policy Engine initialized successfully!')
stats = engine.get_policy_statistics()
print(f'Policy Statistics: {stats}')
"
```

## Configuration Examples

### Database URL Formats

```bash
# Local PostgreSQL
DATABASE_URL="postgresql://username:password@localhost:5432/database_name"

# Remote PostgreSQL
DATABASE_URL="postgresql://username:password@hostname:5432/database_name"

# With SSL
DATABASE_URL="postgresql://username:password@hostname:5432/database_name?sslmode=require"

# Using environment variables in your code
DATABASE_URL="postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
```

### Policy Engine Usage

```python
from postgresql_agent_policy_engine import PostgreSQLAgentPolicyEngine

# Initialize
policy_engine = PostgreSQLAgentPolicyEngine()

# Assess content
assessment = policy_engine.assess_content_policy_compliance(
    agent_role="development-agent",
    content="your code here",
    context={"file_type": "python", "file_name": "example.py"}
)

print(f"Compliant: {assessment.is_compliant}")
print(f"Risk Level: {assessment.risk_level}")
print(f"Violations: {assessment.violations}")
```

## Integration with Existing Agents

### GitHub Issues Agent
The GitHub Issues agent automatically detects and uses the PostgreSQL policy engine:

```python
# Will use PostgreSQL if available, fallback to SQLite
from github_issues_policy_agent import PolicyEnhancedGitHubAgent

agent = PolicyEnhancedGitHubAgent()
# Policy compliance is automatically checked for new issues
```

### Other SDLC Agents
Update your agents to use the PostgreSQL policy engine:

```python
# Replace SQLite import
# from agent_policy_engine import AgentPolicyEngine

# With PostgreSQL import
from postgresql_agent_policy_engine import PostgreSQLAgentPolicyEngine as AgentPolicyEngine

# Usage remains the same
policy_engine = AgentPolicyEngine()
```

## Database Schema

The PostgreSQL policy engine creates the following tables:

- **agent_roles**: Agent role definitions and capabilities
- **policy_rules**: Policy rules and enforcement standards
- **knowledge_base**: Knowledge base entries and documentation
- **policy_assessments**: Policy assessment history and results

## Features

### Agent Roles
- development-agent
- devops-agent  
- qa-agent
- security-agent
- documentation-agent
- github-issues-agent

### Policy Types
- coding_standard
- security_rule
- deployment_policy
- testing_requirement
- documentation_rule
- review_guideline
- architecture_principle

### Risk Levels
- LOW: Minor policy violations
- MEDIUM: Notable violations requiring attention
- HIGH: Serious violations requiring immediate action
- CRITICAL: Severe violations blocking deployment

## Performance Benefits

### PostgreSQL Advantages
- Better concurrent access for multiple agents
- Advanced indexing and query optimization
- JSON field support for flexible policy rules
- ACID compliance for reliable assessments
- Better integration with existing infrastructure

### Scalability
- Supports multiple SDLC agents simultaneously
- Efficient policy rule lookup and assessment
- Historical assessment tracking
- Knowledge base with usage analytics

## Troubleshooting

### Common Issues

1. **Connection Errors**
   ```bash
   # Check PostgreSQL is running
   pg_isready -h localhost -p 5432
   
   # Test connection
   psql -h localhost -p 5432 -U niro_user -d niro_policies
   ```

2. **Permission Issues**
   ```sql
   -- Grant additional permissions
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO niro_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO niro_user;
   ```

3. **Import Errors**
   ```bash
   # Ensure dependencies are installed
   pip install sqlalchemy psycopg2-binary
   
   # Check PostgreSQL service
   systemctl status postgresql  # Linux
   brew services list | grep postgresql  # macOS
   ```

4. **Migration Issues**
   ```bash
   # Check SQLite database exists
   ls -la agent_policies.db
   
   # Verify PostgreSQL connection
   python -c "from postgresql_agent_policy_engine import PostgreSQLAgentPolicyEngine; print('OK')"
   ```

## Security Considerations

1. **Database Credentials**
   - Use environment variables for credentials
   - Don't commit database URLs to version control
   - Use strong passwords for database users

2. **Network Security**
   - Configure PostgreSQL to only accept necessary connections
   - Use SSL/TLS for remote connections
   - Consider connection pooling for production

3. **Access Control**
   - Create dedicated database user for the application
   - Grant minimal required permissions
   - Regular backup and recovery procedures

## Monitoring and Maintenance

### Policy Statistics
Monitor policy compliance using the built-in statistics:

```python
stats = policy_engine.get_policy_statistics()
print(f"Compliance Rate: {stats['compliance_rate']}%")
print(f"Total Assessments: {stats['total_assessments']}")
print(f"Risk Distribution: {stats['risk_distribution']}")
```

### Knowledge Base Analytics
Track knowledge base usage:

```python
kb_results = policy_engine.search_knowledge_base("security")
# Usage count is automatically updated
```

### Regular Maintenance
- Review and update policy rules periodically
- Archive old assessment records
- Update knowledge base entries
- Monitor database performance

## Next Steps

1. **Install and configure PostgreSQL**
2. **Set up environment variables**
3. **Install Python dependencies**
4. **Run migration or fresh setup**
5. **Update existing agents to use PostgreSQL**
6. **Test policy compliance**
7. **Monitor and maintain**

The PostgreSQL policy engine provides a robust, scalable foundation for policy compliance across all SDLC agents while maintaining consistency with your existing infrastructure.
