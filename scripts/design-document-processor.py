#!/usr/bin/env python3
"""
Design Document Processor
Processes ChatGPT-generated design documents from Visual Forge brainstorming sessions
and prepares them for PM handoff to create epics, features, and stories.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

@dataclass
class DesignRequirement:
    """Individual requirement extracted from design document"""
    id: str
    title: str
    description: str
    category: str  # functional, non-functional, technical, business
    priority: str  # high, medium, low
    complexity: str  # simple, moderate, complex
    dependencies: List[str]
    acceptance_criteria: List[str]
    estimated_effort: str  # small, medium, large, xl
    
@dataclass
class DesignDocument:
    """Structured design document from ChatGPT brainstorming"""
    id: str
    title: str
    project_name: str
    created_date: str
    source: str  # visual-forge, chatgpt, manual
    raw_content: str
    parsed_requirements: List[DesignRequirement]
    technical_stack: List[str]
    business_objectives: List[str]
    success_metrics: List[str]
    status: str  # draft, reviewed, approved, handed-off-to-pm
    pm_notes: str
    
class DesignDocumentProcessor:
    """Processes design documents and prepares them for PM workflow"""
    
    def __init__(self, storage_path: str = "design_documents.json"):
        self.storage_path = Path(storage_path)
        self.documents: Dict[str, DesignDocument] = {}
        self.load_documents()
        
    def load_documents(self):
        """Load existing design documents"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for doc_data in data.get('documents', []):
                        doc = DesignDocument(**doc_data)
                        # Convert requirement dicts back to objects
                        doc.parsed_requirements = [
                            DesignRequirement(**req) if isinstance(req, dict) else req
                            for req in doc.parsed_requirements
                        ]
                        self.documents[doc.id] = doc
            except Exception as e:
                print(f"Error loading documents: {e}")
                
    def save_documents(self):
        """Save design documents to storage"""
        data = {
            'documents': [asdict(doc) for doc in self.documents.values()],
            'last_updated': datetime.now().isoformat()
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def import_visual_forge_document(self, content: str, project_name: str, title: str) -> str:
        """Import a design document from Visual Forge ChatGPT brainstorming session"""
        doc_id = str(uuid.uuid4())[:8]
        
        # Parse the ChatGPT content to extract structured information
        requirements = self._parse_requirements_from_content(content)
        tech_stack = self._extract_technical_stack(content)
        business_objectives = self._extract_business_objectives(content)
        success_metrics = self._extract_success_metrics(content)
        
        document = DesignDocument(
            id=doc_id,
            title=title,
            project_name=project_name,
            created_date=datetime.now().isoformat(),
            source="visual-forge",
            raw_content=content,
            parsed_requirements=requirements,
            technical_stack=tech_stack,
            business_objectives=business_objectives,
            success_metrics=success_metrics,
            status="draft",
            pm_notes=""
        )
        
        self.documents[doc_id] = document
        self.save_documents()
        
        print(f"✅ Imported design document: {title}")
        print(f"   - Document ID: {doc_id}")
        print(f"   - Requirements found: {len(requirements)}")
        print(f"   - Ready for PM review")
        
        return doc_id
        
    def _parse_requirements_from_content(self, content: str) -> List[DesignRequirement]:
        """Extract requirements from ChatGPT content using pattern matching"""
        requirements = []
        
        # Common patterns in ChatGPT design documents
        patterns = [
            r"(?:Requirements?|Features?|Functionality):\s*\n((?:[-*]\s+.+\n?)+)",
            r"(?:User Stories?|Stories?):\s*\n((?:[-*]\s+.+\n?)+)",
            r"(?:Technical Requirements?):\s*\n((?:[-*]\s+.+\n?)+)",
            r"(?:Business Requirements?):\s*\n((?:[-*]\s+.+\n?)+)"
        ]
        
        req_counter = 1
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                items = re.findall(r"[-*]\s+(.+)", match.group(1))
                for item in items:
                    if len(item.strip()) > 10:  # Filter out short/empty items
                        req = DesignRequirement(
                            id=f"REQ-{req_counter:03d}",
                            title=item.strip()[:100],  # First 100 chars as title
                            description=item.strip(),
                            category=self._categorize_requirement(item),
                            priority=self._estimate_priority(item),
                            complexity=self._estimate_complexity(item),
                            dependencies=[],
                            acceptance_criteria=[],
                            estimated_effort=self._estimate_effort(item)
                        )
                        requirements.append(req)
                        req_counter += 1
        
        return requirements
        
    def _categorize_requirement(self, text: str) -> str:
        """Categorize requirement based on content"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['api', 'database', 'server', 'architecture', 'security']):
            return "technical"
        elif any(word in text_lower for word in ['user', 'customer', 'interface', 'experience']):
            return "functional"
        elif any(word in text_lower for word in ['performance', 'scalability', 'reliability', 'availability']):
            return "non-functional"
        else:
            return "business"
            
    def _estimate_priority(self, text: str) -> str:
        """Estimate priority based on keywords"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['critical', 'must', 'required', 'essential']):
            return "high"
        elif any(word in text_lower for word in ['should', 'important', 'preferred']):
            return "medium"
        else:
            return "low"
            
    def _estimate_complexity(self, text: str) -> str:
        """Estimate complexity based on content"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['complex', 'advanced', 'integration', 'multiple']):
            return "complex"
        elif any(word in text_lower for word in ['moderate', 'standard', 'typical']):
            return "moderate"
        else:
            return "simple"
            
    def _estimate_effort(self, text: str) -> str:
        """Estimate effort based on complexity and scope"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['system', 'architecture', 'framework', 'platform']):
            return "xl"
        elif any(word in text_lower for word in ['integration', 'complex', 'multiple']):
            return "large"
        elif any(word in text_lower for word in ['feature', 'component', 'module']):
            return "medium"
        else:
            return "small"
            
    def _extract_technical_stack(self, content: str) -> List[str]:
        """Extract mentioned technologies from content"""
        tech_patterns = [
            r"(?:Technologies?|Tech Stack|Stack):\s*\n((?:[-*]\s+.+\n?)+)",
            r"(?:using|with|built on)\s+([A-Z][a-zA-Z0-9.+#-]+)",
        ]
        
        technologies = set()
        for pattern in tech_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if pattern.endswith("+"):  # Single tech pattern
                    technologies.add(match.group(1))
                else:  # List pattern
                    items = re.findall(r"[-*]\s+(.+)", match.group(1))
                    technologies.update(item.strip() for item in items)
                    
        return list(technologies)
        
    def _extract_business_objectives(self, content: str) -> List[str]:
        """Extract business objectives from content"""
        patterns = [
            r"(?:Business Objectives?|Goals?|Objectives?):\s*\n((?:[-*]\s+.+\n?)+)",
            r"(?:Business Value|ROI|Benefits?):\s*\n((?:[-*]\s+.+\n?)+)"
        ]
        
        objectives = []
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                items = re.findall(r"[-*]\s+(.+)", match.group(1))
                objectives.extend(item.strip() for item in items)
                
        return objectives
        
    def _extract_success_metrics(self, content: str) -> List[str]:
        """Extract success metrics from content"""
        patterns = [
            r"(?:Success Metrics?|KPIs?|Measurements?):\s*\n((?:[-*]\s+.+\n?)+)",
            r"(?:Metrics?|Measure):\s*\n((?:[-*]\s+.+\n?)+)"
        ]
        
        metrics = []
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                items = re.findall(r"[-*]\s+(.+)", match.group(1))
                metrics.extend(item.strip() for item in items)
                
        return metrics
        
    def get_document(self, doc_id: str) -> Optional[DesignDocument]:
        """Get a specific design document"""
        return self.documents.get(doc_id)
        
    def list_documents(self) -> List[DesignDocument]:
        """List all design documents"""
        return list(self.documents.values())
        
    def update_pm_notes(self, doc_id: str, notes: str):
        """Add PM notes to a document"""
        if doc_id in self.documents:
            self.documents[doc_id].pm_notes = notes
            self.save_documents()
            
    def mark_ready_for_pm(self, doc_id: str):
        """Mark document as ready for PM handoff"""
        if doc_id in self.documents:
            self.documents[doc_id].status = "reviewed"
            self.save_documents()
            
    def prepare_pm_handoff_package(self, doc_id: str) -> Dict[str, Any]:
        """Prepare a comprehensive handoff package for the PM"""
        doc = self.documents.get(doc_id)
        if not doc:
            return {}
            
        # Group requirements by category
        requirements_by_category = {}
        for req in doc.parsed_requirements:
            if req.category not in requirements_by_category:
                requirements_by_category[req.category] = []
            requirements_by_category[req.category].append(req)
            
        # Calculate effort estimates
        effort_summary = {
            'small': len([r for r in doc.parsed_requirements if r.estimated_effort == 'small']),
            'medium': len([r for r in doc.parsed_requirements if r.estimated_effort == 'medium']),
            'large': len([r for r in doc.parsed_requirements if r.estimated_effort == 'large']),
            'xl': len([r for r in doc.parsed_requirements if r.estimated_effort == 'xl'])
        }
        
        handoff_package = {
            'document_info': {
                'id': doc.id,
                'title': doc.title,
                'project_name': doc.project_name,
                'created_date': doc.created_date,
                'total_requirements': len(doc.parsed_requirements)
            },
            'business_context': {
                'objectives': doc.business_objectives,
                'success_metrics': doc.success_metrics,
                'technical_stack': doc.technical_stack
            },
            'requirements_analysis': {
                'by_category': requirements_by_category,
                'by_priority': {
                    'high': [r for r in doc.parsed_requirements if r.priority == 'high'],
                    'medium': [r for r in doc.parsed_requirements if r.priority == 'medium'],
                    'low': [r for r in doc.parsed_requirements if r.priority == 'low']
                },
                'effort_estimates': effort_summary
            },
            'pm_recommendations': {
                'suggested_epics': self._suggest_epics(doc.parsed_requirements),
                'quick_wins': [r for r in doc.parsed_requirements if r.estimated_effort == 'small' and r.priority == 'high'],
                'complex_features': [r for r in doc.parsed_requirements if r.estimated_effort in ['large', 'xl']]
            }
        }
        
        return handoff_package
        
    def _suggest_epics(self, requirements: List[DesignRequirement]) -> List[Dict[str, Any]]:
        """Suggest epic groupings based on requirements"""
        # Group by category and complexity
        epic_suggestions = []
        
        categories = set(req.category for req in requirements)
        for category in categories:
            category_reqs = [r for r in requirements if r.category == category]
            if len(category_reqs) >= 3:  # Only suggest epics with multiple requirements
                epic_suggestions.append({
                    'name': f"{category.title()} Implementation",
                    'description': f"All {category} requirements for the project",
                    'requirements': [r.id for r in category_reqs],
                    'estimated_effort': max([r.estimated_effort for r in category_reqs], key=['small', 'medium', 'large', 'xl'].index)
                })
                
        return epic_suggestions

def main():
    """CLI interface for design document processing"""
    processor = DesignDocumentProcessor()
    
    print("🎨 Design Document Processor")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Import Visual Forge document")
        print("2. List documents")
        print("3. View document details")
        print("4. Prepare PM handoff")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            title = input("Document title: ").strip()
            project_name = input("Project name: ").strip()
            print("Paste the ChatGPT design document content (Ctrl+D when done):")
            content_lines = []
            try:
                while True:
                    line = input()
                    content_lines.append(line)
            except EOFError:
                pass
            content = '\n'.join(content_lines)
            
            if content.strip():
                doc_id = processor.import_visual_forge_document(content, project_name, title)
                print(f"\n✅ Document imported with ID: {doc_id}")
            else:
                print("❌ No content provided")
                
        elif choice == '2':
            docs = processor.list_documents()
            if docs:
                print(f"\n📋 Found {len(docs)} documents:")
                for doc in docs:
                    print(f"  {doc.id}: {doc.title} ({doc.status}) - {len(doc.parsed_requirements)} requirements")
            else:
                print("\n📋 No documents found")
                
        elif choice == '3':
            doc_id = input("Document ID: ").strip()
            doc = processor.get_document(doc_id)
            if doc:
                print(f"\n📄 {doc.title}")
                print(f"Project: {doc.project_name}")
                print(f"Status: {doc.status}")
                print(f"Requirements: {len(doc.parsed_requirements)}")
                print(f"Tech Stack: {', '.join(doc.technical_stack)}")
                print("\nRequirements:")
                for req in doc.parsed_requirements[:5]:  # Show first 5
                    print(f"  {req.id}: {req.title} ({req.priority}, {req.estimated_effort})")
                if len(doc.parsed_requirements) > 5:
                    print(f"  ... and {len(doc.parsed_requirements) - 5} more")
            else:
                print("❌ Document not found")
                
        elif choice == '4':
            doc_id = input("Document ID: ").strip()
            package = processor.prepare_pm_handoff_package(doc_id)
            if package:
                print(f"\n📦 PM Handoff Package for {package['document_info']['title']}")
                print(f"Total Requirements: {package['document_info']['total_requirements']}")
                print(f"Suggested Epics: {len(package['pm_recommendations']['suggested_epics'])}")
                print(f"Quick Wins: {len(package['pm_recommendations']['quick_wins'])}")
                print(f"Complex Features: {len(package['pm_recommendations']['complex_features'])}")
                
                # Save handoff package
                handoff_file = f"pm_handoff_{doc_id}.json"
                with open(handoff_file, 'w') as f:
                    json.dump(package, f, indent=2, default=str)
                print(f"📁 Handoff package saved to: {handoff_file}")
            else:
                print("❌ Document not found")
                
        elif choice == '5':
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
