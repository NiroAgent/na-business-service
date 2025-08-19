#!/usr/bin/env python3
"""
Test Project Generator - Creates real projects for agents to work on
"""

import json
import os
from datetime import datetime
from pathlib import Path

class TestProjectGenerator:
    def __init__(self):
        self.projects_dir = Path("test-projects")
        self.projects_dir.mkdir(exist_ok=True)
    
    def create_ecommerce_api_project(self):
        """Create a realistic e-commerce API project"""
        project_name = "ecommerce-api"
        project_path = self.projects_dir / project_name
        project_path.mkdir(exist_ok=True)
        
        # Create project specification
        spec = {
            "project_id": f"{project_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "name": "E-commerce API",
            "description": "RESTful API for e-commerce platform with user management, product catalog, and order processing",
            "requirements": [
                "User authentication and authorization",
                "Product catalog management",
                "Shopping cart functionality", 
                "Order processing and payment integration",
                "Inventory management",
                "Admin dashboard API endpoints"
            ],
            "technology_stack": {
                "backend": ["Python", "FastAPI", "SQLAlchemy"],
                "database": ["PostgreSQL", "Redis"],
                "auth": ["JWT", "OAuth2"],
                "deployment": ["Docker", "Kubernetes"]
            },
            "api_endpoints": [
                {"method": "POST", "path": "/auth/login", "description": "User login"},
                {"method": "POST", "path": "/auth/register", "description": "User registration"},
                {"method": "GET", "path": "/products", "description": "List products"},
                {"method": "POST", "path": "/products", "description": "Create product (admin)"},
                {"method": "GET", "path": "/products/{id}", "description": "Get product details"},
                {"method": "POST", "path": "/cart/add", "description": "Add item to cart"},
                {"method": "GET", "path": "/cart", "description": "Get cart contents"},
                {"method": "POST", "path": "/orders", "description": "Create order"},
                {"method": "GET", "path": "/orders", "description": "Get user orders"}
            ],
            "database_models": [
                {"name": "User", "fields": ["id", "email", "password_hash", "created_at"]},
                {"name": "Product", "fields": ["id", "name", "description", "price", "stock_quantity"]},
                {"name": "CartItem", "fields": ["id", "user_id", "product_id", "quantity"]},
                {"name": "Order", "fields": ["id", "user_id", "total_amount", "status", "created_at"]},
                {"name": "OrderItem", "fields": ["id", "order_id", "product_id", "quantity", "price"]}
            ]
        }
        
        # Save specification
        with open(project_path / "project_spec.json", 'w') as f:
            json.dump(spec, f, indent=2)
        
        # Create README
        readme_content = f"""# {spec['name']}

{spec['description']}

## Requirements
{chr(10).join(f"- {req}" for req in spec['requirements'])}

## Technology Stack
- **Backend:** {', '.join(spec['technology_stack']['backend'])}
- **Database:** {', '.join(spec['technology_stack']['database'])}
- **Authentication:** {', '.join(spec['technology_stack']['auth'])}
- **Deployment:** {', '.join(spec['technology_stack']['deployment'])}

## API Endpoints
{chr(10).join(f"- `{ep['method']} {ep['path']}` - {ep['description']}" for ep in spec['api_endpoints'])}

## Database Models
{chr(10).join(f"- **{model['name']}:** {', '.join(model['fields'])}" for model in spec['database_models'])}

## Development Status
- [ ] Project setup
- [ ] Database models
- [ ] Authentication system
- [ ] Product management
- [ ] Cart functionality
- [ ] Order processing
- [ ] API documentation
- [ ] Testing suite
- [ ] Deployment configuration

Generated: {datetime.now().isoformat()}
"""
        
        with open(project_path / "README.md", 'w') as f:
            f.write(readme_content)
        
        return project_path, spec
    
    def create_task_management_project(self):
        """Create a task management application project"""
        project_name = "task-manager"
        project_path = self.projects_dir / project_name
        project_path.mkdir(exist_ok=True)
        
        spec = {
            "project_id": f"{project_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "name": "Task Management System",
            "description": "Web-based task management with teams, projects, and real-time collaboration",
            "requirements": [
                "User authentication and team management",
                "Project and task organization",
                "Real-time updates and notifications",
                "File attachments and comments",
                "Time tracking and reporting",
                "Responsive web interface"
            ],
            "technology_stack": {
                "frontend": ["React", "TypeScript", "Material-UI"],
                "backend": ["Node.js", "Express", "TypeScript"],
                "database": ["MongoDB", "Redis"],
                "realtime": ["Socket.io"],
                "deployment": ["Docker", "AWS"]
            }
        }
        
        with open(project_path / "project_spec.json", 'w') as f:
            json.dump(spec, f, indent=2)
        
        return project_path, spec
    
    def create_analytics_dashboard_project(self):
        """Create an analytics dashboard project"""
        project_name = "analytics-dashboard"
        project_path = self.projects_dir / project_name
        project_path.mkdir(exist_ok=True)
        
        spec = {
            "project_id": f"{project_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "name": "Analytics Dashboard",
            "description": "Real-time analytics dashboard with data visualization and reporting",
            "requirements": [
                "Data ingestion and processing",
                "Interactive charts and visualizations",
                "Real-time data updates",
                "Custom report generation",
                "User access control",
                "Export functionality"
            ],
            "technology_stack": {
                "frontend": ["Vue.js", "TypeScript", "Chart.js", "D3.js"],
                "backend": ["Python", "Django", "Celery"],
                "database": ["PostgreSQL", "InfluxDB"],
                "queue": ["Redis"],
                "deployment": ["Docker", "Kubernetes"]
            }
        }
        
        with open(project_path / "project_spec.json", 'w') as f:
            json.dump(spec, f, indent=2)
        
        return project_path, spec
    
    def generate_all_projects(self):
        """Generate all test projects"""
        projects = []
        
        print("🏗️ Generating test projects for AI agents...")
        
        # E-commerce API
        path1, spec1 = self.create_ecommerce_api_project()
        projects.append((path1, spec1))
        print(f"✅ Created: {spec1['name']} at {path1}")
        
        # Task Management
        path2, spec2 = self.create_task_management_project()
        projects.append((path2, spec2))
        print(f"✅ Created: {spec2['name']} at {path2}")
        
        # Analytics Dashboard
        path3, spec3 = self.create_analytics_dashboard_project()
        projects.append((path3, spec3))
        print(f"✅ Created: {spec3['name']} at {path3}")
        
        # Create master project list
        project_list = {
            "generated_at": datetime.now().isoformat(),
            "projects": [
                {"path": str(path), "spec": spec} 
                for path, spec in projects
            ]
        }
        
        with open(self.projects_dir / "project_list.json", 'w') as f:
            json.dump(project_list, f, indent=2)
        
        print(f"\n📊 Generated {len(projects)} test projects")
        print(f"📁 Projects directory: {self.projects_dir.absolute()}")
        
        return projects

if __name__ == "__main__":
    generator = TestProjectGenerator()
    projects = generator.generate_all_projects()
    
    print("\n🚀 Test projects ready for AI agents!")
    print("Now agents can work on real projects and generate actual activity for the dashboard.")
