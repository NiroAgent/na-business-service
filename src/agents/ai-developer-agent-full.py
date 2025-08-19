#!/usr/bin/env python3
"""
AI Developer Agent - Phase 3 Implementation
Receives technical specifications from AI Architect Agent and generates production-ready code
"""

import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AIDeveloperAgent')


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    GO = "go"
    JAVA = "java"
    CSHARP = "csharp"


class Framework(Enum):
    """Supported frameworks"""
    FASTAPI = "fastapi"
    FLASK = "flask"
    EXPRESS = "express"
    NEXTJS = "nextjs"
    SPRING = "spring"
    DOTNET = "dotnet"
    GIN = "gin"


@dataclass
class TechnicalSpecification:
    """Technical specification from AI Architect Agent"""
    spec_id: str
    project_name: str
    description: str
    requirements: List[str]
    technology_stack: Dict[str, Any]
    architecture: Dict[str, Any]
    api_design: Dict[str, Any]
    database_design: Dict[str, Any]
    security_requirements: List[str] = field(default_factory=list)
    performance_requirements: List[str] = field(default_factory=list)
    deployment_requirements: List[str] = field(default_factory=list)
    testing_requirements: List[str] = field(default_factory=list)


@dataclass
class CodeFile:
    """Represents a generated code file"""
    path: str
    content: str
    language: str
    file_type: str  # source, test, config, doc
    lines_of_code: int = 0
    
    def __post_init__(self):
        self.lines_of_code = len(self.content.splitlines())


@dataclass
class GeneratedProject:
    """Represents a complete generated project"""
    project_id: str
    spec_id: str
    project_name: str
    root_path: str
    generated_files: List[str]
    total_lines: int
    test_coverage: float
    documentation_generated: bool
    deployment_ready: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return asdict(self)


class CodeGeneratorBase:
    """Base class for code generators"""
    
    def __init__(self, spec: TechnicalSpecification):
        self.spec = spec
        self.generated_files: List[CodeFile] = []
        
    def generate_project_structure(self) -> Dict[str, Any]:
        """Generate project directory structure"""
        raise NotImplementedError
        
    def generate_source_code(self) -> List[CodeFile]:
        """Generate source code files"""
        raise NotImplementedError
        
    def generate_tests(self) -> List[CodeFile]:
        """Generate test files"""
        raise NotImplementedError
        
    def generate_config_files(self) -> List[CodeFile]:
        """Generate configuration files"""
        raise NotImplementedError
        
    def generate_documentation(self) -> List[CodeFile]:
        """Generate documentation files"""
        raise NotImplementedError


class PythonFastAPIGenerator(CodeGeneratorBase):
    """Code generator for Python FastAPI projects"""
    
    def generate_project_structure(self) -> Dict[str, Any]:
        """Generate FastAPI project structure"""
        return {
            'src': {
                'main.py': 'Application entry point',
                'api': {
                    '__init__.py': '',
                    'routes': {},
                    'dependencies.py': 'Dependency injection'
                },
                'models': {
                    '__init__.py': '',
                    'database.py': 'Database models',
                    'schemas.py': 'Pydantic schemas'
                },
                'services': {
                    '__init__.py': '',
                    'business_logic.py': 'Business logic'
                },
                'core': {
                    '__init__.py': '',
                    'config.py': 'Configuration',
                    'security.py': 'Security utilities',
                    'database.py': 'Database connection'
                },
                'utils': {
                    '__init__.py': '',
                    'helpers.py': 'Helper functions'
                }
            },
            'tests': {
                '__init__.py': '',
                'test_api.py': 'API tests',
                'test_services.py': 'Service tests',
                'test_models.py': 'Model tests'
            },
            'docs': {
                'README.md': 'Project documentation',
                'API.md': 'API documentation',
                'DEPLOYMENT.md': 'Deployment guide'
            },
            'config': {
                'requirements.txt': 'Python dependencies',
                'Dockerfile': 'Docker configuration',
                'docker-compose.yml': 'Docker Compose',
                '.env.example': 'Environment variables'
            }
        }
    
    def generate_source_code(self) -> List[CodeFile]:
        """Generate FastAPI source code"""
        files = []
        
        # Main application file
        main_content = self._generate_main_py()
        files.append(CodeFile(
            path='src/main.py',
            content=main_content,
            language='python',
            file_type='source'
        ))
        
        # Database models
        models_content = self._generate_database_models()
        files.append(CodeFile(
            path='src/models/database.py',
            content=models_content,
            language='python',
            file_type='source'
        ))
        
        # Pydantic schemas
        schemas_content = self._generate_schemas()
        files.append(CodeFile(
            path='src/models/schemas.py',
            content=schemas_content,
            language='python',
            file_type='source'
        ))
        
        # API routes
        for endpoint in self.spec.api_design.get('endpoints', []):
            route_content = self._generate_route(endpoint)
            route_name = endpoint.get('path', '/').replace('/', '_').strip('_') or 'root'
            files.append(CodeFile(
                path=f'src/api/routes/{route_name}.py',
                content=route_content,
                language='python',
                file_type='source'
            ))
        
        # Services
        services_content = self._generate_services()
        files.append(CodeFile(
            path='src/services/business_logic.py',
            content=services_content,
            language='python',
            file_type='source'
        ))
        
        # Configuration
        config_content = self._generate_config()
        files.append(CodeFile(
            path='src/core/config.py',
            content=config_content,
            language='python',
            file_type='source'
        ))
        
        # Security
        security_content = self._generate_security()
        files.append(CodeFile(
            path='src/core/security.py',
            content=security_content,
            language='python',
            file_type='source'
        ))
        
        # Database connection
        db_connection_content = self._generate_db_connection()
        files.append(CodeFile(
            path='src/core/database.py',
            content=db_connection_content,
            language='python',
            file_type='source'
        ))
        
        return files
    
    def generate_tests(self) -> List[CodeFile]:
        """Generate test files"""
        files = []
        
        # API tests
        api_tests = self._generate_api_tests()
        files.append(CodeFile(
            path='tests/test_api.py',
            content=api_tests,
            language='python',
            file_type='test'
        ))
        
        # Service tests
        service_tests = self._generate_service_tests()
        files.append(CodeFile(
            path='tests/test_services.py',
            content=service_tests,
            language='python',
            file_type='test'
        ))
        
        # Model tests
        model_tests = self._generate_model_tests()
        files.append(CodeFile(
            path='tests/test_models.py',
            content=model_tests,
            language='python',
            file_type='test'
        ))
        
        # Integration tests
        integration_tests = self._generate_integration_tests()
        files.append(CodeFile(
            path='tests/test_integration.py',
            content=integration_tests,
            language='python',
            file_type='test'
        ))
        
        return files
    
    def generate_config_files(self) -> List[CodeFile]:
        """Generate configuration files"""
        files = []
        
        # Requirements.txt
        requirements = self._generate_requirements()
        files.append(CodeFile(
            path='requirements.txt',
            content=requirements,
            language='text',
            file_type='config'
        ))
        
        # Dockerfile
        dockerfile = self._generate_dockerfile()
        files.append(CodeFile(
            path='Dockerfile',
            content=dockerfile,
            language='dockerfile',
            file_type='config'
        ))
        
        # Docker Compose
        docker_compose = self._generate_docker_compose()
        files.append(CodeFile(
            path='docker-compose.yml',
            content=docker_compose,
            language='yaml',
            file_type='config'
        ))
        
        # Environment variables
        env_example = self._generate_env_example()
        files.append(CodeFile(
            path='.env.example',
            content=env_example,
            language='text',
            file_type='config'
        ))
        
        # pytest.ini
        pytest_ini = self._generate_pytest_ini()
        files.append(CodeFile(
            path='pytest.ini',
            content=pytest_ini,
            language='ini',
            file_type='config'
        ))
        
        return files
    
    def generate_documentation(self) -> List[CodeFile]:
        """Generate documentation files"""
        files = []
        
        # README
        readme = self._generate_readme()
        files.append(CodeFile(
            path='README.md',
            content=readme,
            language='markdown',
            file_type='doc'
        ))
        
        # API Documentation
        api_doc = self._generate_api_documentation()
        files.append(CodeFile(
            path='docs/API.md',
            content=api_doc,
            language='markdown',
            file_type='doc'
        ))
        
        # Deployment Guide
        deployment = self._generate_deployment_guide()
        files.append(CodeFile(
            path='docs/DEPLOYMENT.md',
            content=deployment,
            language='markdown',
            file_type='doc'
        ))
        
        return files
    
    # Private helper methods for generating specific files
    def _generate_main_py(self) -> str:
        """Generate main.py content"""
        return '''"""
FastAPI Application Entry Point
Generated by AI Developer Agent
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from src.core.config import settings
from src.core.database import engine, Base
from src.api.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "API is running",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
'''
    
    def _generate_database_models(self) -> str:
        """Generate database models based on specification"""
        models = []
        
        # Base imports
        content = '''"""
Database Models
Generated by AI Developer Agent
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

'''
        
        # Generate models from database design
        for table in self.spec.database_design.get('tables', []):
            model = self._generate_model_class(table)
            models.append(model)
        
        return content + '\n\n'.join(models)
    
    def _generate_model_class(self, table: Dict[str, Any]) -> str:
        """Generate a SQLAlchemy model class"""
        table_name = table.get('name', 'Table')
        class_name = self._to_camel_case(table_name)
        
        model = f'''class {class_name}(Base):
    """
    {table.get('description', f'{class_name} model')}
    """
    __tablename__ = "{table_name.lower()}"
    
'''
        
        # Add columns
        for column in table.get('columns', []):
            col_def = self._generate_column_definition(column)
            model += f"    {col_def}\n"
        
        # Add relationships if any
        for rel in table.get('relationships', []):
            rel_def = self._generate_relationship_definition(rel)
            model += f"    {rel_def}\n"
        
        # Add timestamps
        model += '''    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''
        
        return model
    
    def _generate_column_definition(self, column: Dict[str, Any]) -> str:
        """Generate SQLAlchemy column definition"""
        name = column.get('name', 'column')
        col_type = column.get('type', 'String')
        
        # Map types
        type_mapping = {
            'string': 'String(255)',
            'text': 'Text',
            'integer': 'Integer',
            'float': 'Float',
            'boolean': 'Boolean',
            'datetime': 'DateTime',
            'uuid': 'String(36)'
        }
        
        sql_type = type_mapping.get(col_type.lower(), 'String(255)')
        
        # Build column definition
        col_def = f"{name} = Column({sql_type}"
        
        if column.get('primary_key'):
            col_def += ", primary_key=True"
        if column.get('unique'):
            col_def += ", unique=True"
        if column.get('nullable', True):
            col_def += ", nullable=True"
        else:
            col_def += ", nullable=False"
        if column.get('index'):
            col_def += ", index=True"
            
        col_def += ")"
        
        return col_def
    
    def _generate_relationship_definition(self, relationship: Dict[str, Any]) -> str:
        """Generate SQLAlchemy relationship definition"""
        name = relationship.get('name', 'related')
        target = relationship.get('target', 'Model')
        rel_type = relationship.get('type', 'one-to-many')
        
        if rel_type == 'one-to-many':
            return f'{name} = relationship("{target}", back_populates="{name}")'
        elif rel_type == 'many-to-one':
            return f'{name} = relationship("{target}", back_populates="{name}")'
        else:
            return f'{name} = relationship("{target}")'
    
    def _generate_schemas(self) -> str:
        """Generate Pydantic schemas"""
        content = '''"""
Pydantic Schemas for Request/Response Models
Generated by AI Developer Agent
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

'''
        
        schemas = []
        
        # Generate schemas based on API design
        for endpoint in self.spec.api_design.get('endpoints', []):
            # Request schema
            if endpoint.get('request_body'):
                schema = self._generate_schema_class(
                    f"{endpoint.get('operation_id', 'Operation')}Request",
                    endpoint['request_body']
                )
                schemas.append(schema)
            
            # Response schema
            if endpoint.get('response'):
                schema = self._generate_schema_class(
                    f"{endpoint.get('operation_id', 'Operation')}Response",
                    endpoint['response']
                )
                schemas.append(schema)
        
        return content + '\n\n'.join(schemas)
    
    def _generate_schema_class(self, name: str, schema_def: Dict[str, Any]) -> str:
        """Generate a Pydantic schema class"""
        class_def = f'''class {name}(BaseModel):
    """
    {schema_def.get('description', f'{name} schema')}
    """
'''
        
        # Add fields
        for field_name, field_def in schema_def.get('properties', {}).items():
            field_type = self._get_python_type(field_def.get('type', 'str'))
            required = field_name in schema_def.get('required', [])
            
            if required:
                class_def += f"    {field_name}: {field_type}\n"
            else:
                class_def += f"    {field_name}: Optional[{field_type}] = None\n"
        
        # Add config
        class_def += '''
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {}
        }
'''
        
        return class_def
    
    def _generate_route(self, endpoint: Dict[str, Any]) -> str:
        """Generate API route handler"""
        path = endpoint.get('path', '/')
        method = endpoint.get('method', 'GET').lower()
        operation_id = endpoint.get('operation_id', 'operation')
        
        content = f'''"""
API Route: {path}
Generated by AI Developer Agent
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from src.core.database import get_db
from src.models import schemas, database
from src.services import business_logic

router = APIRouter()

@router.{method}("{path}")
async def {operation_id}(
'''
        
        # Add parameters
        params = []
        for param in endpoint.get('parameters', []):
            param_def = self._generate_parameter(param)
            params.append(param_def)
        
        if endpoint.get('request_body'):
            params.append(f"request_body: schemas.{operation_id.title()}Request")
        
        params.append("db: Session = Depends(get_db)")
        
        content += ',\n    '.join(params)
        content += '\n):\n'
        
        # Add docstring
        content += f'''    """
    {endpoint.get('description', 'API endpoint')}
    """
    try:
        # Business logic here
        result = await business_logic.{operation_id}(db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
'''
        
        return content
    
    def _generate_parameter(self, param: Dict[str, Any]) -> str:
        """Generate function parameter"""
        name = param.get('name', 'param')
        param_type = self._get_python_type(param.get('type', 'str'))
        required = param.get('required', False)
        
        if required:
            return f"{name}: {param_type}"
        else:
            return f"{name}: Optional[{param_type}] = None"
    
    def _generate_services(self) -> str:
        """Generate service layer"""
        content = '''"""
Business Logic Services
Generated by AI Developer Agent
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from src.models import database, schemas
import logging

logger = logging.getLogger(__name__)

'''
        
        # Generate service functions for each endpoint
        for endpoint in self.spec.api_design.get('endpoints', []):
            operation_id = endpoint.get('operation_id', 'operation')
            
            content += f'''
async def {operation_id}(db: Session, **kwargs) -> Any:
    """
    Service function for {operation_id}
    """
    try:
        # Implement business logic here
        logger.info(f"Executing {operation_id}")
        
        # Example implementation
        # result = db.query(database.Model).all()
        # return result
        
        return {{"message": "Operation successful"}}
        
    except Exception as e:
        logger.error(f"Error in {operation_id}: {{e}}")
        raise
'''
        
        return content
    
    def _generate_config(self) -> str:
        """Generate configuration file"""
        return '''"""
Application Configuration
Generated by AI Developer Agent
"""

from pydantic import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Project Info
    PROJECT_NAME: str = "''' + self.spec.project_name + '''"
    PROJECT_DESCRIPTION: str = "''' + self.spec.description + '''"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/dbname"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # External Services
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
'''
    
    def _generate_security(self) -> str:
        """Generate security utilities"""
        return '''"""
Security Utilities
Generated by AI Developer Agent
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
'''
    
    def _generate_db_connection(self) -> str:
        """Generate database connection setup"""
        return '''"""
Database Connection Setup
Generated by AI Developer Agent
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
    
    def _generate_api_tests(self) -> str:
        """Generate API tests"""
        content = '''"""
API Tests
Generated by AI Developer Agent
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

'''
        
        # Generate tests for each endpoint
        for endpoint in self.spec.api_design.get('endpoints', []):
            path = endpoint.get('path', '/')
            method = endpoint.get('method', 'GET').lower()
            operation_id = endpoint.get('operation_id', 'operation')
            
            # Handle path parameters - fixed string replacement
            test_path = path
            for param in endpoint.get('parameters', []):
                if param.get('in') == 'path':
                    param_name = param.get('name', '')
                    test_path = test_path.replace(f'{{{param_name}}}', 'test_id')
            
            content += f'''
def test_{operation_id}():
    """Test {operation_id} endpoint"""
    response = client.{method}("/api/v1{test_path}")
    # Add assertions based on expected response
    assert response.status_code in [200, 201, 204]
'''
        
        return content
    
    def _generate_service_tests(self) -> str:
        """Generate service tests"""
        return '''"""
Service Layer Tests
Generated by AI Developer Agent
"""

import pytest
from unittest.mock import Mock, patch
from src.services import business_logic

@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()

'''
    
    def _generate_model_tests(self) -> str:
        """Generate model tests"""
        return '''"""
Model Tests
Generated by AI Developer Agent
"""

import pytest
from src.models import database, schemas

def test_model_creation():
    """Test model creation"""
    # Add model creation tests
    pass

def test_schema_validation():
    """Test schema validation"""
    # Add schema validation tests
    pass
'''
    
    def _generate_integration_tests(self) -> str:
        """Generate integration tests"""
        return '''"""
Integration Tests
Generated by AI Developer Agent
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.core.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_full_workflow():
    """Test complete workflow"""
    # Add comprehensive workflow tests
    pass
'''
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        tech_stack = self.spec.technology_stack
        
        requirements = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "sqlalchemy==2.0.23",
            "alembic==1.12.1",
            "pydantic==2.5.0",
            "python-jose[cryptography]==3.3.0",
            "passlib[bcrypt]==1.7.4",
            "python-multipart==0.0.6",
            "python-dotenv==1.0.0",
            "redis==5.0.1",
            "celery==5.3.4",
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "httpx==0.25.1"
        ]
        
        # Add database driver
        if 'postgresql' in str(tech_stack).lower():
            requirements.append("psycopg2-binary==2.9.9")
        elif 'mysql' in str(tech_stack).lower():
            requirements.append("pymysql==1.1.0")
        
        # Add additional dependencies based on requirements
        if 'stripe' in str(self.spec.requirements).lower():
            requirements.append("stripe==7.0.0")
        if 'sendgrid' in str(self.spec.requirements).lower():
            requirements.append("sendgrid==6.11.0")
        if 'aws' in str(tech_stack).lower():
            requirements.append("boto3==1.29.7")
        
        return '\n'.join(requirements)
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile"""
        return '''# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml"""
        return '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./src:/app/src
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app

volumes:
  postgres_data:
'''
    
    def _generate_env_example(self) -> str:
        """Generate .env.example file"""
        return '''# Application
DEBUG=False
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379

# External Services
STRIPE_API_KEY=
SENDGRID_API_KEY=

# AWS (if using)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Monitoring
SENTRY_DSN=
'''
    
    def _generate_pytest_ini(self) -> str:
        """Generate pytest.ini"""
        return '''[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
'''
    
    def _generate_readme(self) -> str:
        """Generate README.md"""
        return f'''# {self.spec.project_name}

{self.spec.description}

## Features

{self._format_requirements_list(self.spec.requirements)}

## Technology Stack

{self._format_tech_stack(self.spec.technology_stack)}

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis

### Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the application:
   ```bash
   uvicorn src.main:app --reload
   ```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Docker Deployment

Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---
Generated by AI Developer Agent
'''
    
    def _generate_api_documentation(self) -> str:
        """Generate API documentation"""
        content = f'''# API Documentation

## Overview

{self.spec.description}

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

This API uses JWT Bearer token authentication. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

'''
        
        # Document each endpoint
        for endpoint in self.spec.api_design.get('endpoints', []):
            content += self._document_endpoint(endpoint)
        
        return content
    
    def _document_endpoint(self, endpoint: Dict[str, Any]) -> str:
        """Document a single endpoint"""
        return f'''
### {endpoint.get('method', 'GET')} {endpoint.get('path', '/')}

**Description:** {endpoint.get('description', 'API endpoint')}

**Parameters:**
{self._format_parameters(endpoint.get('parameters', []))}

**Request Body:**
```json
{json.dumps(endpoint.get('request_body', {}), indent=2)}
```

**Response:**
```json
{json.dumps(endpoint.get('response', {}), indent=2)}
```

---
'''
    
    def _generate_deployment_guide(self) -> str:
        """Generate deployment guide"""
        return '''# Deployment Guide

## Production Deployment

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t api-app .
   ```

2. Run with environment variables:
   ```bash
   docker run -p 8000:8000 --env-file .env api-app
   ```

### Using Docker Compose

1. Configure production environment variables in `.env`

2. Start services:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Kubernetes Deployment

1. Create ConfigMap for environment variables:
   ```bash
   kubectl create configmap api-config --from-env-file=.env
   ```

2. Apply deployment:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

3. Apply service:
   ```bash
   kubectl apply -f k8s/service.yaml
   ```

## Environment Variables

See `.env.example` for all required environment variables.

## Database Migrations

Run migrations before deploying new versions:
```bash
alembic upgrade head
```

## Monitoring

- Health check endpoint: `/health`
- Metrics endpoint: `/metrics`
- Logs are written to stdout/stderr

## Scaling

### Horizontal Scaling

The application is stateless and can be scaled horizontally:

```bash
kubectl scale deployment api-app --replicas=5
```

### Database Connection Pooling

Configure connection pool settings in `DATABASE_URL`:
```
postgresql://user:password@host/db?pool_size=20&max_overflow=40
```

## Security Considerations

1. Always use HTTPS in production
2. Keep SECRET_KEY secure and rotate regularly
3. Use strong database passwords
4. Enable rate limiting
5. Keep dependencies updated

---
Generated by AI Developer Agent
'''
    
    # Helper methods
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to CamelCase"""
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)
    
    def _get_python_type(self, json_type: str) -> str:
        """Convert JSON type to Python type"""
        type_map = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'List',
            'object': 'Dict[str, Any]'
        }
        return type_map.get(json_type, 'Any')
    
    def _format_requirements_list(self, requirements: List[str]) -> str:
        """Format requirements as markdown list"""
        return '\n'.join(f"- {req}" for req in requirements[:10])
    
    def _format_tech_stack(self, tech_stack: Dict[str, Any]) -> str:
        """Format technology stack"""
        lines = []
        for category, tech in tech_stack.items():
            if isinstance(tech, list):
                tech_str = ', '.join(tech)
            else:
                tech_str = str(tech)
            lines.append(f"- **{category}:** {tech_str}")
        return '\n'.join(lines)
    
    def _format_parameters(self, parameters: List[Dict[str, Any]]) -> str:
        """Format API parameters"""
        if not parameters:
            return "None"
        
        lines = []
        for param in parameters:
            lines.append(f"- **{param.get('name')}** ({param.get('type', 'string')}): {param.get('description', '')}")
        return '\n'.join(lines)


class TypeScriptExpressGenerator(CodeGeneratorBase):
    """Code generator for TypeScript/Express projects"""
    
    def generate_project_structure(self) -> Dict[str, Any]:
        """Generate Express project structure"""
        return {
            'src': {
                'index.ts': 'Application entry point',
                'app.ts': 'Express app configuration',
                'routes': {
                    'index.ts': 'Route definitions'
                },
                'controllers': {
                    'index.ts': 'Controller logic'
                },
                'models': {
                    'index.ts': 'Data models'
                },
                'services': {
                    'index.ts': 'Business logic'
                },
                'middleware': {
                    'auth.ts': 'Authentication middleware',
                    'error.ts': 'Error handling'
                },
                'utils': {
                    'logger.ts': 'Logging utility',
                    'database.ts': 'Database connection'
                },
                'types': {
                    'index.d.ts': 'TypeScript type definitions'
                }
            },
            'tests': {
                'unit': {},
                'integration': {}
            },
            'config': {
                'package.json': 'NPM configuration',
                'tsconfig.json': 'TypeScript configuration',
                'Dockerfile': 'Docker configuration',
                '.env.example': 'Environment variables'
            }
        }
    
    def generate_source_code(self) -> List[CodeFile]:
        """Generate Express source code"""
        files = []
        
        # Add TypeScript/Express implementation
        # Similar structure to Python generator but for TypeScript
        
        return files
    
    def generate_tests(self) -> List[CodeFile]:
        """Generate Jest/Mocha tests"""
        files = []
        
        # Add test files
        
        return files
    
    def generate_config_files(self) -> List[CodeFile]:
        """Generate configuration files"""
        files = []
        
        # package.json
        package_json = self._generate_package_json()
        files.append(CodeFile(
            path='package.json',
            content=package_json,
            language='json',
            file_type='config'
        ))
        
        # tsconfig.json
        tsconfig = self._generate_tsconfig()
        files.append(CodeFile(
            path='tsconfig.json',
            content=tsconfig,
            language='json',
            file_type='config'
        ))
        
        return files
    
    def generate_documentation(self) -> List[CodeFile]:
        """Generate documentation"""
        files = []
        
        # Add documentation files
        
        return files
    
    def _generate_package_json(self) -> str:
        """Generate package.json"""
        return json.dumps({
            "name": self.spec.project_name,
            "version": "1.0.0",
            "description": self.spec.description,
            "main": "dist/index.js",
            "scripts": {
                "start": "node dist/index.js",
                "dev": "nodemon src/index.ts",
                "build": "tsc",
                "test": "jest",
                "lint": "eslint src/**/*.ts"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "helmet": "^7.0.0",
                "morgan": "^1.10.0",
                "dotenv": "^16.3.1",
                "jsonwebtoken": "^9.0.2",
                "bcrypt": "^5.1.1",
                "sequelize": "^6.33.0",
                "pg": "^8.11.3"
            },
            "devDependencies": {
                "@types/express": "^4.17.20",
                "@types/node": "^20.8.10",
                "typescript": "^5.2.2",
                "nodemon": "^3.0.1",
                "ts-node": "^10.9.1",
                "jest": "^29.7.0",
                "@types/jest": "^29.5.7",
                "eslint": "^8.53.0"
            }
        }, indent=2)
    
    def _generate_tsconfig(self) -> str:
        """Generate tsconfig.json"""
        return json.dumps({
            "compilerOptions": {
                "target": "ES2022",
                "module": "commonjs",
                "lib": ["ES2022"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist", "tests"]
        }, indent=2)


class AIDeveloperAgent:
    """Main AI Developer Agent"""
    
    def __init__(self):
        self.logger = logger
        self.generators = {
            'python-fastapi': PythonFastAPIGenerator,
            'typescript-express': TypeScriptExpressGenerator
        }
    
    def process_specification(self, spec: TechnicalSpecification, output_dir: str = None) -> GeneratedProject:
        """Process technical specification and generate code"""
        self.logger.info(f"Processing specification: {spec.spec_id}")
        
        # Determine technology stack
        language = self._determine_language(spec.technology_stack)
        framework = self._determine_framework(spec.technology_stack)
        
        generator_key = f"{language}-{framework}"
        
        if generator_key not in self.generators:
            raise ValueError(f"Unsupported technology stack: {generator_key}")
        
        # Initialize generator
        generator_class = self.generators[generator_key]
        generator = generator_class(spec)
        
        # Generate project structure
        structure = generator.generate_project_structure()
        
        # Generate code files
        source_files = generator.generate_source_code()
        test_files = generator.generate_tests()
        config_files = generator.generate_config_files()
        doc_files = generator.generate_documentation()
        
        all_files = source_files + test_files + config_files + doc_files
        
        # Write files to disk if output directory specified
        if output_dir:
            self._write_files(output_dir, all_files)
        
        # Calculate metrics
        total_lines = sum(f.lines_of_code for f in all_files)
        test_coverage = self._estimate_test_coverage(source_files, test_files)
        
        # Create project result
        project = GeneratedProject(
            project_id=f"proj-{uuid.uuid4().hex[:8]}",
            spec_id=spec.spec_id,
            project_name=spec.project_name,
            root_path=output_dir or "generated",
            generated_files=[f.path for f in all_files],
            total_lines=total_lines,
            test_coverage=test_coverage,
            documentation_generated=len(doc_files) > 0,
            deployment_ready=len(config_files) > 0
        )
        
        self.logger.info(f"Project generated successfully: {project.project_id}")
        self.logger.info(f"Total files: {len(all_files)}, Lines of code: {total_lines}")
        
        return project
    
    def _determine_language(self, tech_stack: Dict[str, Any]) -> str:
        """Determine programming language from tech stack"""
        backend = tech_stack.get('backend', {})
        
        if isinstance(backend, dict):
            language = backend.get('language', '').lower()
        else:
            language = str(backend).lower()
        
        if 'python' in language:
            return 'python'
        elif 'typescript' in language or 'javascript' in language:
            return 'typescript'
        elif 'go' in language:
            return 'go'
        elif 'java' in language:
            return 'java'
        elif 'csharp' in language or 'c#' in language:
            return 'csharp'
        else:
            return 'python'  # Default
    
    def _determine_framework(self, tech_stack: Dict[str, Any]) -> str:
        """Determine framework from tech stack"""
        backend = tech_stack.get('backend', {})
        
        if isinstance(backend, dict):
            framework = backend.get('framework', '').lower()
        else:
            framework = str(backend).lower()
        
        if 'fastapi' in framework:
            return 'fastapi'
        elif 'flask' in framework:
            return 'flask'
        elif 'express' in framework:
            return 'express'
        elif 'nextjs' in framework or 'next' in framework:
            return 'nextjs'
        elif 'spring' in framework:
            return 'spring'
        elif 'gin' in framework:
            return 'gin'
        elif 'dotnet' in framework or '.net' in framework:
            return 'dotnet'
        else:
            return 'fastapi'  # Default
    
    def _write_files(self, output_dir: str, files: List[CodeFile]):
        """Write generated files to disk"""
        base_path = Path(output_dir)
        base_path.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            file_path = base_path / file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file.content)
            
            self.logger.debug(f"Written: {file_path}")
    
    def _estimate_test_coverage(self, source_files: List[CodeFile], test_files: List[CodeFile]) -> float:
        """Estimate test coverage percentage"""
        if not source_files:
            return 0.0
        
        # Simple estimation based on file count and lines
        source_lines = sum(f.lines_of_code for f in source_files)
        test_lines = sum(f.lines_of_code for f in test_files)
        
        if source_lines == 0:
            return 0.0
        
        # Estimate coverage (rough approximation)
        coverage_ratio = test_lines / source_lines
        estimated_coverage = min(coverage_ratio * 100, 95.0)  # Cap at 95%
        
        return round(estimated_coverage, 1)


def main():
    """Main entry point for testing"""
    logger.info("AI Developer Agent initialized")
    
    # Test with sample specification
    test_spec = TechnicalSpecification(
        spec_id="spec-test-001",
        project_name="test-api",
        description="Test API for e-commerce platform",
        requirements=[
            "User authentication",
            "Product management",
            "Order processing"
        ],
        technology_stack={
            "backend": {
                "language": "Python",
                "framework": "FastAPI"
            },
            "database": "PostgreSQL",
            "cache": "Redis"
        },
        architecture={
            "pattern": "microservices",
            "components": ["API Gateway", "Auth Service", "Product Service"]
        },
        api_design={
            "endpoints": [
                {
                    "path": "/users",
                    "method": "POST",
                    "operation_id": "create_user",
                    "description": "Create new user"
                },
                {
                    "path": "/products",
                    "method": "GET",
                    "operation_id": "list_products",
                    "description": "List all products"
                }
            ]
        },
        database_design={
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "uuid", "primary_key": True},
                        {"name": "email", "type": "string", "unique": True},
                        {"name": "password_hash", "type": "string"}
                    ]
                },
                {
                    "name": "products",
                    "columns": [
                        {"name": "id", "type": "uuid", "primary_key": True},
                        {"name": "name", "type": "string"},
                        {"name": "price", "type": "float"}
                    ]
                }
            ]
        }
    )
    
    # Process specification
    agent = AIDeveloperAgent()
    project = agent.process_specification(test_spec, output_dir="generated_projects/test-api")
    
    logger.info(f"Generated project: {project.project_id}")
    logger.info(f"Files created: {len(project.generated_files)}")
    logger.info(f"Test coverage: {project.test_coverage}%")


if __name__ == "__main__":
    main()