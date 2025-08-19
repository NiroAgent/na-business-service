"""
Migration script to migrate from SQLite to PostgreSQL
Converts existing SQLite policy data to PostgreSQL format
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Any
from datetime import datetime

# Import PostgreSQL engine (will need SQLAlchemy installed)
try:
    from postgresql_agent_policy_engine import PostgreSQLAgentPolicyEngine, SessionLocal, AgentRole, PolicyRule, KnowledgeBase
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    print("PostgreSQL dependencies not available. Install with: pip install sqlalchemy psycopg2-binary")

class PolicyMigrationTool:
    """Tool to migrate policy data from SQLite to PostgreSQL"""
    
    def __init__(self, sqlite_db_path: str = "agent_policies.db", postgresql_url: str = None):
        self.sqlite_db_path = sqlite_db_path
        self.postgresql_url = postgresql_url or os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/niro_policies")
        self.logger = logging.getLogger(__name__)
        
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("PostgreSQL dependencies not available")
        
        self.pg_engine = PostgreSQLAgentPolicyEngine(self.postgresql_url)
    
    def migrate_data(self) -> bool:
        """Migrate all data from SQLite to PostgreSQL"""
        try:
            # Check if SQLite database exists
            if not os.path.exists(self.sqlite_db_path):
                self.logger.warning(f"SQLite database not found: {self.sqlite_db_path}")
                self.logger.info("Creating fresh PostgreSQL database with initial data")
                return True  # PostgreSQL engine already creates initial data
            
            # Connect to SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            sqlite_conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Migrate in order: roles -> policies -> knowledge base -> assessments
            self._migrate_agent_roles(sqlite_conn)
            self._migrate_policy_rules(sqlite_conn)
            self._migrate_knowledge_base(sqlite_conn)
            self._migrate_assessments(sqlite_conn)
            
            sqlite_conn.close()
            
            self.logger.info("Migration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            return False
    
    def _migrate_agent_roles(self, sqlite_conn: sqlite3.Connection):
        """Migrate agent roles from SQLite to PostgreSQL"""
        cursor = sqlite_conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM agent_roles")
            roles = cursor.fetchall()
            
            if not roles:
                self.logger.info("No agent roles found in SQLite - using default data")
                return
            
            # Clear existing roles in PostgreSQL (if any)
            db = SessionLocal()
            try:
                db.query(AgentRole).delete()
                db.commit()
                
                # Insert migrated roles
                for row in roles:
                    role_data = {
                        "name": row["name"],
                        "description": row["description"],
                        "primary_responsibilities": json.loads(row["primary_responsibilities"]) if row["primary_responsibilities"] else [],
                        "skill_set": json.loads(row["skill_set"]) if row["skill_set"] else [],
                        "authority_level": row.get("authority_level", 1),
                        "can_approve_deployments": bool(row.get("can_approve_deployments", False)),
                        "can_modify_policies": bool(row.get("can_modify_policies", False))
                    }
                    
                    role = AgentRole(**role_data)
                    db.add(role)
                
                db.commit()
                self.logger.info(f"Migrated {len(roles)} agent roles")
                
            finally:
                db.close()
                
        except sqlite3.OperationalError as e:
            self.logger.warning(f"SQLite agent_roles table not found: {e}")
    
    def _migrate_policy_rules(self, sqlite_conn: sqlite3.Connection):
        """Migrate policy rules from SQLite to PostgreSQL"""
        cursor = sqlite_conn.cursor()
        
        try:
            cursor.execute("""
                SELECT pr.*, ar.name as role_name 
                FROM policy_rules pr 
                LEFT JOIN agent_roles ar ON pr.agent_role_id = ar.id
            """)
            policies = cursor.fetchall()
            
            if not policies:
                self.logger.info("No policy rules found in SQLite - using default data")
                return
            
            # Get PostgreSQL roles for mapping
            db = SessionLocal()
            try:
                pg_roles = {role.name: role.id for role in db.query(AgentRole).all()}
                
                # Clear existing policies
                db.query(PolicyRule).delete()
                db.commit()
                
                # Insert migrated policies
                for row in policies:
                    role_name = row["role_name"]
                    if role_name not in pg_roles:
                        self.logger.warning(f"Role not found for policy {row['name']}: {role_name}")
                        continue
                    
                    policy_data = {
                        "name": row["name"],
                        "description": row["description"],
                        "policy_type": row["policy_type"],
                        "agent_role_id": pg_roles[role_name],
                        "rule_content": json.loads(row["rule_content"]) if row["rule_content"] else {},
                        "examples": json.loads(row["examples"]) if row["examples"] else {},
                        "enforcement_level": row.get("enforcement_level", "warning"),
                        "is_active": bool(row.get("is_active", True)),
                        "priority": row.get("priority", 5)
                    }
                    
                    policy = PolicyRule(**policy_data)
                    db.add(policy)
                
                db.commit()
                self.logger.info(f"Migrated {len(policies)} policy rules")
                
            finally:
                db.close()
                
        except sqlite3.OperationalError as e:
            self.logger.warning(f"SQLite policy_rules table not found: {e}")
    
    def _migrate_knowledge_base(self, sqlite_conn: sqlite3.Connection):
        """Migrate knowledge base entries from SQLite to PostgreSQL"""
        cursor = sqlite_conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM knowledge_base")
            entries = cursor.fetchall()
            
            if not entries:
                self.logger.info("No knowledge base entries found in SQLite - using default data")
                return
            
            db = SessionLocal()
            try:
                # Clear existing entries
                db.query(KnowledgeBase).delete()
                db.commit()
                
                # Insert migrated entries
                for row in entries:
                    entry_data = {
                        "title": row["title"],
                        "content": row["content"],
                        "category": row["category"],
                        "tags": json.loads(row["tags"]) if row["tags"] else [],
                        "source_url": row.get("source_url"),
                        "confidence_score": row.get("confidence_score", 1.0),
                        "usage_count": row.get("usage_count", 0),
                        "last_accessed": datetime.fromisoformat(row["last_accessed"]) if row.get("last_accessed") else None
                    }
                    
                    entry = KnowledgeBase(**entry_data)
                    db.add(entry)
                
                db.commit()
                self.logger.info(f"Migrated {len(entries)} knowledge base entries")
                
            finally:
                db.close()
                
        except sqlite3.OperationalError as e:
            self.logger.warning(f"SQLite knowledge_base table not found: {e}")
    
    def _migrate_assessments(self, sqlite_conn: sqlite3.Connection):
        """Migrate policy assessments from SQLite to PostgreSQL"""
        cursor = sqlite_conn.cursor()
        
        try:
            cursor.execute("""
                SELECT pa.*, ar.name as role_name, pr.name as policy_name
                FROM policy_assessments pa
                LEFT JOIN agent_roles ar ON pa.agent_role_id = ar.id
                LEFT JOIN policy_rules pr ON pa.policy_rule_id = pr.id
                ORDER BY pa.created_at DESC
                LIMIT 1000
            """)
            assessments = cursor.fetchall()
            
            if not assessments:
                self.logger.info("No policy assessments found in SQLite")
                return
            
            # Note: For assessments, we'll skip migration as they are historical data
            # and new assessments will be created in PostgreSQL going forward
            self.logger.info(f"Found {len(assessments)} historical assessments (not migrated - new assessments will be created)")
            
        except sqlite3.OperationalError as e:
            self.logger.warning(f"SQLite policy_assessments table not found: {e}")
    
    def validate_migration(self) -> Dict[str, Any]:
        """Validate the migration by comparing counts"""
        try:
            # Check SQLite counts
            sqlite_counts = {}
            if os.path.exists(self.sqlite_db_path):
                sqlite_conn = sqlite3.connect(self.sqlite_db_path)
                cursor = sqlite_conn.cursor()
                
                tables = ["agent_roles", "policy_rules", "knowledge_base", "policy_assessments"]
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        sqlite_counts[table] = cursor.fetchone()[0]
                    except sqlite3.OperationalError:
                        sqlite_counts[table] = 0
                
                sqlite_conn.close()
            else:
                sqlite_counts = {table: 0 for table in ["agent_roles", "policy_rules", "knowledge_base", "policy_assessments"]}
            
            # Check PostgreSQL counts
            db = SessionLocal()
            try:
                pg_counts = {
                    "agent_roles": db.query(AgentRole).count(),
                    "policy_rules": db.query(PolicyRule).count(),
                    "knowledge_base": db.query(KnowledgeBase).count(),
                    "policy_assessments": 0  # New assessments start fresh
                }
            finally:
                db.close()
            
            return {
                "sqlite_counts": sqlite_counts,
                "postgresql_counts": pg_counts,
                "migration_status": "completed",
                "validation_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return {"error": str(e)}


def create_database_setup_script():
    """Create a setup script for PostgreSQL database"""
    setup_script = '''-- PostgreSQL Database Setup for NIRO Policy Engine
-- Run this script to create the database and user

-- Create database
CREATE DATABASE niro_policies;

-- Create user (optional, you can use existing user)
-- CREATE USER niro_user WITH PASSWORD 'niro_password';

-- Grant permissions
-- GRANT ALL PRIVILEGES ON DATABASE niro_policies TO niro_user;

-- Connect to the database
\\c niro_policies;

-- Create schema (optional, tables will be created by SQLAlchemy)
-- CREATE SCHEMA IF NOT EXISTS policy_engine;

-- The application will automatically create tables using SQLAlchemy migrations
'''
    
    with open("e:\\Projects\\postgresql_setup.sql", "w") as f:
        f.write(setup_script)
    
    print("Created postgresql_setup.sql - run this to set up your database")


def create_requirements_file():
    """Create requirements file for PostgreSQL dependencies"""
    requirements = '''# PostgreSQL Policy Engine Dependencies
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.12.0  # For database migrations
asyncpg>=0.28.0  # For async PostgreSQL support

# Existing dependencies (if not already installed)
requests>=2.31.0
'''
    
    with open("e:\\Projects\\postgresql_policy_requirements.txt", "w") as f:
        f.write(requirements)
    
    print("Created postgresql_policy_requirements.txt")
    print("Install with: pip install -r postgresql_policy_requirements.txt")


def main():
    """Main migration function"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create setup files
    create_database_setup_script()
    create_requirements_file()
    
    print("\nMigration Setup Complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r postgresql_policy_requirements.txt")
    print("2. Set up PostgreSQL database (if not already done)")
    print("3. Update DATABASE_URL environment variable")
    print("4. Run the migration:")
    print("   python policy-migration-tool.py")
    
    # Check if dependencies are available
    if not POSTGRESQL_AVAILABLE:
        print("\nNote: Install PostgreSQL dependencies first before running migration")
        return
    
    # Run migration if PostgreSQL is available
    try:
        # Example migration (customize DATABASE_URL as needed)
        database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/niro_policies")
        
        migrator = PolicyMigrationTool(
            sqlite_db_path="agent_policies.db",  # Update path as needed
            postgresql_url=database_url
        )
        
        success = migrator.migrate_data()
        
        if success:
            validation = migrator.validate_migration()
            print(f"\nMigration validation: {json.dumps(validation, indent=2)}")
        else:
            print("Migration failed - check logs for details")
            
    except Exception as e:
        print(f"Migration error: {e}")


if __name__ == "__main__":
    main()
