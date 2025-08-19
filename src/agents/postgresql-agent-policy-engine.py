"""
PostgreSQL Agent Policy Engine
Comprehensive policy management system for SDLC agents using PostgreSQL
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/niro_policies")
VF_AGENT_SERVICE_URL = os.getenv("VF_AGENT_SERVICE_URL", "http://localhost:3000")

# SQLAlchemy setup
Base = declarative_base()

# Create sync engine for compatibility
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create async engine for advanced operations
async_engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"), echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


class PolicyType(Enum):
    """Policy types"""
    CODING_STANDARD = "coding_standard"
    SECURITY_RULE = "security_rule"
    DEPLOYMENT_POLICY = "deployment_policy"
    TESTING_REQUIREMENT = "testing_requirement"
    DOCUMENTATION_RULE = "documentation_rule"
    REVIEW_GUIDELINE = "review_guideline"
    ARCHITECTURE_PRINCIPLE = "architecture_principle"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PolicyAssessment:
    """Policy assessment result"""
    is_compliant: bool
    risk_level: RiskLevel
    violations: List[str]
    recommendations: List[str]
    confidence_score: float
    assessment_details: Dict[str, Any]


# Database Models
class AgentRole(Base):
    """Agent roles and their capabilities"""
    __tablename__ = "agent_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    primary_responsibilities = Column(JSON)  # List of main responsibilities
    skill_set = Column(JSON)  # List of skills and technologies
    authority_level = Column(Integer, default=1)  # 1-5 scale
    can_approve_deployments = Column(Boolean, default=False)
    can_modify_policies = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    policies = relationship("PolicyRule", back_populates="agent_role")
    assessments = relationship("PolicyAssessmentRecord", back_populates="agent_role")


class PolicyRule(Base):
    """Policy rules and standards"""
    __tablename__ = "policy_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    policy_type = Column(String(50), nullable=False, index=True)
    agent_role_id = Column(Integer, ForeignKey("agent_roles.id"), nullable=False)
    rule_content = Column(JSON)  # Detailed rule specifications
    examples = Column(JSON)  # Good/bad examples
    enforcement_level = Column(String(20), default="warning")  # error, warning, info
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)  # 1-10 scale
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    agent_role = relationship("AgentRole", back_populates="policies")
    assessments = relationship("PolicyAssessmentRecord", back_populates="policy_rule")


class KnowledgeBase(Base):
    """Knowledge base entries for policies and standards"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    tags = Column(JSON)  # List of tags
    source_url = Column(String(500))
    confidence_score = Column(Float, default=1.0)
    usage_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PolicyAssessmentRecord(Base):
    """Policy assessment history and results"""
    __tablename__ = "policy_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_role_id = Column(Integer, ForeignKey("agent_roles.id"), nullable=False)
    policy_rule_id = Column(Integer, ForeignKey("policy_rules.id"), nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    is_compliant = Column(Boolean, nullable=False)
    risk_level = Column(String(20), nullable=False)
    violations = Column(JSON)  # List of violation descriptions
    recommendations = Column(JSON)  # List of recommendations
    confidence_score = Column(Float, default=1.0)
    assessment_details = Column(JSON)  # Detailed assessment data
    content_preview = Column(Text)  # First 500 chars of assessed content
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    agent_role = relationship("AgentRole", back_populates="assessments")
    policy_rule = relationship("PolicyRule", back_populates="assessments")


class PostgreSQLAgentPolicyEngine:
    """PostgreSQL-based policy engine for SDLC agents"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or DATABASE_URL
        self.vf_service_url = VF_AGENT_SERVICE_URL
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        self._populate_initial_data()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=engine)
            self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_db(self) -> Session:
        """Get database session"""
        db = SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise
    
    async def get_async_db(self) -> AsyncSession:
        """Get async database session"""
        async with AsyncSessionLocal() as session:
            yield session
    
    def _populate_initial_data(self):
        """Populate initial agent roles and policies"""
        db = self.get_db()
        try:
            # Check if data already exists
            if db.query(AgentRole).count() > 0:
                return
            
            # Create agent roles
            agent_roles = [
                {
                    "name": "development-agent",
                    "description": "Core development and coding tasks",
                    "primary_responsibilities": [
                        "Code implementation",
                        "Feature development",
                        "Bug fixes",
                        "Unit testing",
                        "Code refactoring"
                    ],
                    "skill_set": [
                        "python", "javascript", "typescript", "react", "node.js",
                        "git", "testing", "debugging", "algorithms", "data-structures"
                    ],
                    "authority_level": 3,
                    "can_approve_deployments": False,
                    "can_modify_policies": False
                },
                {
                    "name": "devops-agent",
                    "description": "Infrastructure, deployment, and CI/CD operations",
                    "primary_responsibilities": [
                        "Infrastructure management",
                        "CI/CD pipeline setup",
                        "Deployment automation",
                        "Monitoring setup",
                        "Security scanning"
                    ],
                    "skill_set": [
                        "docker", "kubernetes", "aws", "terraform", "jenkins",
                        "github-actions", "monitoring", "security", "networking"
                    ],
                    "authority_level": 4,
                    "can_approve_deployments": True,
                    "can_modify_policies": False
                },
                {
                    "name": "qa-agent",
                    "description": "Quality assurance and testing",
                    "primary_responsibilities": [
                        "Test planning",
                        "Test automation",
                        "Quality validation",
                        "Performance testing",
                        "Security testing"
                    ],
                    "skill_set": [
                        "testing", "selenium", "jest", "pytest", "performance-testing",
                        "security-testing", "test-automation", "quality-assurance"
                    ],
                    "authority_level": 3,
                    "can_approve_deployments": False,
                    "can_modify_policies": False
                },
                {
                    "name": "security-agent",
                    "description": "Security analysis and vulnerability assessment",
                    "primary_responsibilities": [
                        "Security code review",
                        "Vulnerability scanning",
                        "Security policy enforcement",
                        "Compliance checking",
                        "Risk assessment"
                    ],
                    "skill_set": [
                        "security", "vulnerability-assessment", "code-analysis",
                        "compliance", "cryptography", "authentication", "authorization"
                    ],
                    "authority_level": 5,
                    "can_approve_deployments": True,
                    "can_modify_policies": True
                },
                {
                    "name": "documentation-agent",
                    "description": "Documentation creation and maintenance",
                    "primary_responsibilities": [
                        "API documentation",
                        "User guides",
                        "Technical specifications",
                        "Code comments review",
                        "Knowledge base maintenance"
                    ],
                    "skill_set": [
                        "technical-writing", "markdown", "documentation-tools",
                        "api-documentation", "user-experience", "knowledge-management"
                    ],
                    "authority_level": 2,
                    "can_approve_deployments": False,
                    "can_modify_policies": False
                },
                {
                    "name": "github-issues-agent",
                    "description": "GitHub issues monitoring and work distribution",
                    "primary_responsibilities": [
                        "Issue monitoring",
                        "Work assignment",
                        "Progress tracking",
                        "Issue classification",
                        "Team coordination"
                    ],
                    "skill_set": [
                        "github-api", "project-management", "issue-tracking",
                        "workflow-automation", "team-coordination"
                    ],
                    "authority_level": 3,
                    "can_approve_deployments": False,
                    "can_modify_policies": False
                }
            ]
            
            # Insert agent roles
            for role_data in agent_roles:
                role = AgentRole(**role_data)
                db.add(role)
            
            db.commit()
            
            # Create policy rules
            self._create_initial_policies(db)
            self._create_knowledge_base_entries(db)
            
            self.logger.info("Initial data populated successfully")
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to populate initial data: {e}")
            raise
        finally:
            db.close()
    
    def _create_initial_policies(self, db: Session):
        """Create initial policy rules"""
        # Get agent roles
        roles = {role.name: role for role in db.query(AgentRole).all()}
        
        policies = [
            # Development policies
            {
                "name": "Python Code Standards",
                "description": "PEP 8 compliance and Python best practices",
                "policy_type": PolicyType.CODING_STANDARD.value,
                "agent_role_id": roles["development-agent"].id,
                "rule_content": {
                    "requirements": [
                        "Follow PEP 8 style guidelines",
                        "Use type hints for function parameters and returns",
                        "Include docstrings for all public functions",
                        "Maximum line length of 100 characters",
                        "Use meaningful variable and function names"
                    ],
                    "patterns_to_avoid": [
                        "Global variables in modules",
                        "Hardcoded credentials or secrets",
                        "Bare except clauses",
                        "Using eval() or exec()"
                    ]
                },
                "examples": {
                    "good": [
                        "def calculate_total(items: List[Item]) -> float:",
                        "    \"\"\"Calculate total price of items.\"\"\"",
                        "    return sum(item.price for item in items)"
                    ],
                    "bad": [
                        "def calc(x):",
                        "    return x*1.2"
                    ]
                },
                "enforcement_level": "warning",
                "priority": 8
            },
            {
                "name": "Security Code Review",
                "description": "Security vulnerabilities and code analysis",
                "policy_type": PolicyType.SECURITY_RULE.value,
                "agent_role_id": roles["security-agent"].id,
                "rule_content": {
                    "requirements": [
                        "No hardcoded passwords or API keys",
                        "Input validation for all user inputs",
                        "Use parameterized queries for database operations",
                        "Implement proper authentication and authorization",
                        "Use HTTPS for all external communications"
                    ],
                    "security_checks": [
                        "SQL injection vulnerabilities",
                        "Cross-site scripting (XSS)",
                        "Insecure direct object references",
                        "Security misconfiguration",
                        "Sensitive data exposure"
                    ]
                },
                "enforcement_level": "error",
                "priority": 10
            },
            {
                "name": "Testing Requirements",
                "description": "Unit testing and test coverage standards",
                "policy_type": PolicyType.TESTING_REQUIREMENT.value,
                "agent_role_id": roles["qa-agent"].id,
                "rule_content": {
                    "requirements": [
                        "Minimum 80% test coverage for new code",
                        "Unit tests for all public functions",
                        "Integration tests for API endpoints",
                        "Test data should not use production data",
                        "Tests should be deterministic and repeatable"
                    ],
                    "test_types": [
                        "Unit tests",
                        "Integration tests",
                        "End-to-end tests",
                        "Performance tests",
                        "Security tests"
                    ]
                },
                "enforcement_level": "warning",
                "priority": 7
            },
            {
                "name": "Deployment Safety",
                "description": "Safe deployment practices and rollback procedures",
                "policy_type": PolicyType.DEPLOYMENT_POLICY.value,
                "agent_role_id": roles["devops-agent"].id,
                "rule_content": {
                    "requirements": [
                        "All deployments must pass CI/CD pipeline",
                        "Staging environment testing required",
                        "Database migrations must be reversible",
                        "Health checks must pass before deployment completion",
                        "Rollback plan documented for each deployment"
                    ],
                    "environments": ["development", "staging", "production"],
                    "approval_required": ["staging", "production"]
                },
                "enforcement_level": "error",
                "priority": 9
            },
            {
                "name": "API Documentation",
                "description": "API documentation and specification requirements",
                "policy_type": PolicyType.DOCUMENTATION_RULE.value,
                "agent_role_id": roles["documentation-agent"].id,
                "rule_content": {
                    "requirements": [
                        "OpenAPI/Swagger specifications for all endpoints",
                        "Request/response examples for each endpoint",
                        "Error response documentation",
                        "Authentication requirements clearly specified",
                        "Rate limiting documentation"
                    ],
                    "formats": ["OpenAPI 3.0", "Swagger", "Markdown"]
                },
                "enforcement_level": "warning",
                "priority": 6
            },
            {
                "name": "GitHub Issues Management",
                "description": "Issue tracking and workflow management standards",
                "policy_type": PolicyType.REVIEW_GUIDELINE.value,
                "agent_role_id": roles["github-issues-agent"].id,
                "rule_content": {
                    "requirements": [
                        "All issues must have appropriate labels",
                        "Severity and priority must be assigned",
                        "Clear acceptance criteria required",
                        "Assigned developer within 24 hours",
                        "Regular status updates on active issues"
                    ],
                    "labels": ["bug", "feature", "enhancement", "documentation", "security"],
                    "priorities": ["low", "medium", "high", "critical"]
                },
                "enforcement_level": "info",
                "priority": 5
            }
        ]
        
        for policy_data in policies:
            policy = PolicyRule(**policy_data)
            db.add(policy)
        
        db.commit()
    
    def _create_knowledge_base_entries(self, db: Session):
        """Create initial knowledge base entries"""
        kb_entries = [
            {
                "title": "Python PEP 8 Style Guide",
                "content": "The official Python style guide covering naming conventions, code layout, and programming recommendations.",
                "category": "coding_standards",
                "tags": ["python", "pep8", "style", "coding-standards"],
                "source_url": "https://pep8.org/",
                "confidence_score": 1.0
            },
            {
                "title": "OWASP Top 10 Security Risks",
                "content": "The top 10 most critical web application security risks and how to prevent them.",
                "category": "security",
                "tags": ["security", "owasp", "vulnerabilities", "web-security"],
                "source_url": "https://owasp.org/www-project-top-ten/",
                "confidence_score": 1.0
            },
            {
                "title": "Docker Best Practices",
                "content": "Best practices for building and deploying Docker containers securely and efficiently.",
                "category": "devops",
                "tags": ["docker", "containers", "deployment", "best-practices"],
                "source_url": "https://docs.docker.com/develop/dev-best-practices/",
                "confidence_score": 0.9
            },
            {
                "title": "Test-Driven Development (TDD)",
                "content": "TDD methodology and best practices for writing tests before implementation.",
                "category": "testing",
                "tags": ["tdd", "testing", "methodology", "quality-assurance"],
                "source_url": "https://testdriven.io/",
                "confidence_score": 0.9
            },
            {
                "title": "API Documentation Standards",
                "content": "Standards for creating comprehensive and user-friendly API documentation.",
                "category": "documentation",
                "tags": ["api", "documentation", "openapi", "swagger"],
                "source_url": "https://swagger.io/specification/",
                "confidence_score": 0.8
            }
        ]
        
        for entry_data in kb_entries:
            entry = KnowledgeBase(**entry_data)
            db.add(entry)
        
        db.commit()
    
    def assess_content_policy_compliance(
        self, 
        agent_role: str, 
        content: str, 
        context: Dict[str, Any] = None
    ) -> PolicyAssessment:
        """Assess content against agent role policies"""
        db = self.get_db()
        try:
            # Get agent role
            role = db.query(AgentRole).filter(AgentRole.name == agent_role).first()
            if not role:
                return PolicyAssessment(
                    is_compliant=False,
                    risk_level=RiskLevel.HIGH,
                    violations=[f"Unknown agent role: {agent_role}"],
                    recommendations=["Use a valid agent role"],
                    confidence_score=1.0,
                    assessment_details={"error": "Invalid agent role"}
                )
            
            # Get relevant policies
            policies = db.query(PolicyRule).filter(
                PolicyRule.agent_role_id == role.id,
                PolicyRule.is_active == True
            ).all()
            
            violations = []
            recommendations = []
            risk_scores = []
            
            # Assess against each policy
            for policy in policies:
                policy_result = self._assess_single_policy(content, policy, context)
                if not policy_result["is_compliant"]:
                    violations.extend(policy_result["violations"])
                    recommendations.extend(policy_result["recommendations"])
                risk_scores.append(policy_result["risk_score"])
            
            # Calculate overall assessment
            is_compliant = len(violations) == 0
            avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            if avg_risk_score >= 0.8:
                risk_level = RiskLevel.CRITICAL
            elif avg_risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif avg_risk_score >= 0.4:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Create assessment record
            content_hash = str(hash(content))
            assessment_record = PolicyAssessmentRecord(
                agent_role_id=role.id,
                policy_rule_id=policies[0].id if policies else None,
                content_hash=content_hash,
                is_compliant=is_compliant,
                risk_level=risk_level.value,
                violations=violations,
                recommendations=recommendations,
                confidence_score=0.85,
                assessment_details={
                    "policies_checked": len(policies),
                    "context": context,
                    "risk_score": avg_risk_score
                },
                content_preview=content[:500]
            )
            db.add(assessment_record)
            db.commit()
            
            return PolicyAssessment(
                is_compliant=is_compliant,
                risk_level=risk_level,
                violations=violations,
                recommendations=recommendations,
                confidence_score=0.85,
                assessment_details={
                    "policies_checked": len(policies),
                    "context": context,
                    "risk_score": avg_risk_score
                }
            )
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Policy assessment failed: {e}")
            return PolicyAssessment(
                is_compliant=False,
                risk_level=RiskLevel.HIGH,
                violations=[f"Assessment error: {str(e)}"],
                recommendations=["Review content and try again"],
                confidence_score=0.0,
                assessment_details={"error": str(e)}
            )
        finally:
            db.close()
    
    def _assess_single_policy(
        self, 
        content: str, 
        policy: PolicyRule, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Assess content against a single policy rule"""
        violations = []
        recommendations = []
        risk_score = 0.0
        
        try:
            rule_content = policy.rule_content
            
            if policy.policy_type == PolicyType.SECURITY_RULE.value:
                # Security checks
                if "password" in content.lower() and ("=" in content or ":" in content):
                    violations.append("Potential hardcoded password detected")
                    risk_score += 0.8
                
                if "api_key" in content.lower() and ("=" in content or ":" in content):
                    violations.append("Potential hardcoded API key detected")
                    risk_score += 0.8
                
                if "eval(" in content or "exec(" in content:
                    violations.append("Use of eval() or exec() detected - security risk")
                    risk_score += 0.9
            
            elif policy.policy_type == PolicyType.CODING_STANDARD.value:
                # Coding standard checks
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if len(line) > 100:
                        violations.append(f"Line {i+1} exceeds 100 character limit")
                        risk_score += 0.2
                
                if "def " in content and '"""' not in content and "'''" not in content:
                    violations.append("Functions missing docstrings")
                    recommendations.append("Add docstrings to all functions")
                    risk_score += 0.3
            
            elif policy.policy_type == PolicyType.TESTING_REQUIREMENT.value:
                # Testing checks
                if context and context.get("file_type") == "python":
                    if "test_" not in content and "Test" not in content:
                        violations.append("No test functions found")
                        recommendations.append("Add unit tests for new functionality")
                        risk_score += 0.5
            
            # Normalize risk score
            risk_score = min(risk_score, 1.0)
            
            return {
                "is_compliant": len(violations) == 0,
                "violations": violations,
                "recommendations": recommendations,
                "risk_score": risk_score
            }
            
        except Exception as e:
            self.logger.error(f"Single policy assessment failed: {e}")
            return {
                "is_compliant": False,
                "violations": [f"Policy assessment error: {str(e)}"],
                "recommendations": ["Review policy configuration"],
                "risk_score": 0.5
            }
    
    def get_agent_policies(self, agent_role: str) -> List[Dict[str, Any]]:
        """Get all policies for an agent role"""
        db = self.get_db()
        try:
            role = db.query(AgentRole).filter(AgentRole.name == agent_role).first()
            if not role:
                return []
            
            policies = db.query(PolicyRule).filter(
                PolicyRule.agent_role_id == role.id,
                PolicyRule.is_active == True
            ).all()
            
            return [
                {
                    "id": policy.id,
                    "name": policy.name,
                    "description": policy.description,
                    "policy_type": policy.policy_type,
                    "enforcement_level": policy.enforcement_level,
                    "priority": policy.priority,
                    "rule_content": policy.rule_content,
                    "examples": policy.examples
                }
                for policy in policies
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get agent policies: {e}")
            return []
        finally:
            db.close()
    
    def search_knowledge_base(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Search knowledge base entries"""
        db = self.get_db()
        try:
            kb_query = db.query(KnowledgeBase)
            
            if category:
                kb_query = kb_query.filter(KnowledgeBase.category == category)
            
            # Simple text search (in production, you might want to use full-text search)
            kb_query = kb_query.filter(
                KnowledgeBase.title.ilike(f"%{query}%") |
                KnowledgeBase.content.ilike(f"%{query}%")
            )
            
            entries = kb_query.order_by(KnowledgeBase.confidence_score.desc()).limit(10).all()
            
            # Update usage count
            for entry in entries:
                entry.usage_count += 1
                entry.last_accessed = datetime.utcnow()
            db.commit()
            
            return [
                {
                    "id": entry.id,
                    "title": entry.title,
                    "content": entry.content,
                    "category": entry.category,
                    "tags": entry.tags,
                    "source_url": entry.source_url,
                    "confidence_score": entry.confidence_score
                }
                for entry in entries
            ]
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Knowledge base search failed: {e}")
            return []
        finally:
            db.close()
    
    def bridge_to_vf_policy_engine(self, content: str, platform: str = "github") -> Dict[str, Any]:
        """Bridge to VF-Agent-Service Universal Policy Engine"""
        try:
            response = requests.post(
                f"{self.vf_service_url}/api/policy/assess",
                json={
                    "content": content,
                    "platform": platform,
                    "context": {
                        "source": "sdlc-agent",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"VF Policy Engine returned {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.RequestException as e:
            self.logger.warning(f"VF Policy Engine unavailable: {e}")
            return {"error": "VF Policy Engine unavailable"}
    
    def get_policy_statistics(self) -> Dict[str, Any]:
        """Get policy compliance statistics"""
        db = self.get_db()
        try:
            total_assessments = db.query(PolicyAssessmentRecord).count()
            compliant_assessments = db.query(PolicyAssessmentRecord).filter(
                PolicyAssessmentRecord.is_compliant == True
            ).count()
            
            risk_distribution = db.query(
                PolicyAssessmentRecord.risk_level,
                func.count(PolicyAssessmentRecord.id)
            ).group_by(PolicyAssessmentRecord.risk_level).all()
            
            recent_assessments = db.query(PolicyAssessmentRecord).filter(
                PolicyAssessmentRecord.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            return {
                "total_assessments": total_assessments,
                "compliance_rate": (compliant_assessments / total_assessments * 100) if total_assessments > 0 else 0,
                "risk_distribution": dict(risk_distribution),
                "recent_assessments": recent_assessments,
                "active_policies": db.query(PolicyRule).filter(PolicyRule.is_active == True).count(),
                "agent_roles": db.query(AgentRole).count()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
        finally:
            db.close()


def main():
    """Initialize and test the PostgreSQL policy engine"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize policy engine
        policy_engine = PostgreSQLAgentPolicyEngine()
        
        # Test policy assessment
        test_code = '''
def process_user_data(user_input):
    password = "hardcoded_password_123"
    query = "SELECT * FROM users WHERE id = " + str(user_input)
    return query
'''
        
        assessment = policy_engine.assess_content_policy_compliance(
            agent_role="development-agent",
            content=test_code,
            context={"file_type": "python", "file_name": "test.py"}
        )
        
        print("Policy Assessment Results:")
        print(f"Compliant: {assessment.is_compliant}")
        print(f"Risk Level: {assessment.risk_level}")
        print(f"Violations: {assessment.violations}")
        print(f"Recommendations: {assessment.recommendations}")
        
        # Test knowledge base search
        kb_results = policy_engine.search_knowledge_base("security")
        print(f"\nKnowledge Base Results: {len(kb_results)} entries found")
        
        # Get statistics
        stats = policy_engine.get_policy_statistics()
        print(f"\nPolicy Statistics: {stats}")
        
        print("\nPostgreSQL Policy Engine initialized successfully!")
        
    except Exception as e:
        print(f"Failed to initialize policy engine: {e}")


if __name__ == "__main__":
    main()
