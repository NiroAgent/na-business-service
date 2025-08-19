#!/usr/bin/env python3
"""
VF-Design-Document-Bridge
Connects VF-Agent-Service brainstorming sessions to the AI Architect Agent pipeline
Enables seamless idea-to-implementation workflow
"""

import json
import time
import requests
import logging
import threading
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict
import re
import sys
import asyncio
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vf_design_document_bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('VFDesignDocumentBridge')

# Import AI Architect Agent for direct integration
sys.path.append(str(Path(__file__).parent))
try:
    from ai_architect_agent import AIArchitectAgent
    logger.info("Successfully imported AI Architect Agent")
    AI_ARCHITECT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AI Architect Agent not available for direct integration: {e}")
    AI_ARCHITECT_AVAILABLE = False

@dataclass
class BrainstormSession:
    """Represents a VF-Agent-Service brainstorming session"""
    session_id: str
    user_id: str
    conversation_data: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    status: str  # active, design-ready, submitted, processing, completed
    metadata: Dict[str, Any]
    extracted_requirements: Optional[Dict[str, Any]] = None
    design_document_id: Optional[str] = None
    architect_spec_id: Optional[str] = None

@dataclass
class DesignDocument:
    """Structured design document for pipeline submission"""
    document_id: str
    session_id: str
    title: str
    overview: str
    objectives: List[str]
    functional_requirements: List[Dict[str, Any]]
    non_functional_requirements: List[Dict[str, Any]]
    technical_constraints: List[str]
    user_stories: List[Dict[str, Any]]
    acceptance_criteria: List[str]
    success_metrics: List[Dict[str, Any]]
    business_context: Dict[str, Any]
    created_at: str
    submitted_at: Optional[str] = None
    pipeline_status: str = "pending"

@dataclass
class PipelineProgress:
    """Tracks progress through the development pipeline"""
    project_id: str
    session_id: str
    current_stage: str  # brainstorm, design, architect, development, testing, deployment
    progress_percentage: int
    status_message: str
    started_at: str
    updated_at: str
    completed_at: Optional[str] = None
    artifacts: List[Dict[str, Any]] = None

class VFDesignDocumentBridge:
    """Main bridge connecting VF-Agent-Service to AI Architect Agent pipeline"""
    
    def __init__(self):
        # API Endpoints
        self.vf_agent_api = "http://localhost:3001"  # VF-Agent-Service API
        self.vf_text_api = "http://localhost:4004"   # VF-Text-Service API  
        self.visual_forge_ai = "http://localhost:5006"  # Visual Forge AI
        self.pm_workflow_api = "http://localhost:5005"   # PM Workflow
        self.dashboard_api = "http://localhost:5003"     # Dashboard API
        
        # Storage
        self.active_sessions = {}
        self.design_documents = {}
        self.pipeline_progress = {}
        
        # AI Architect Agent (direct integration if available)
        self.ai_architect = None
        if AI_ARCHITECT_AVAILABLE:
            try:
                self.ai_architect = AIArchitectAgent()
                logger.info("AI Architect Agent initialized for direct integration")
            except Exception as e:
                logger.error(f"Failed to initialize AI Architect Agent: {e}")
        
        # Monitoring
        self.monitoring = True
        self.monitor_thread = None
        self.poll_interval = 5  # seconds
        
        # WebSocket for real-time updates
        self.ws_connections = {}
        
        # Metrics
        self.metrics = {
            'sessions_processed': 0,
            'documents_generated': 0,
            'pipeline_submissions': 0,
            'successful_completions': 0,
            'failed_submissions': 0,
            'avg_processing_time': 0,
            'processing_times': []
        }
        
        # Session patterns for requirement extraction
        self.requirement_patterns = {
            'functional': [
                r"(?:i need|we need|system should|app should|it should) (.+)",
                r"(?:must be able to|should be able to) (.+)",
                r"(?:feature:|requirement:) (.+)",
                r"(?:user wants to|users want to) (.+)"
            ],
            'non_functional': [
                r"(?:performance|speed|fast|quick): (.+)",
                r"(?:security|secure|authentication|authorization): (.+)",
                r"(?:scale|scalability|handle) (\d+) (?:users|requests)",
                r"(?:reliable|reliability|uptime|availability): (.+)"
            ],
            'user_story': [
                r"as a (.+), i want (.+) so that (.+)",
                r"(?:user story:|story:) (.+)",
                r"(?:scenario:|use case:) (.+)"
            ]
        }
        
    def monitor_brainstorm_sessions(self):
        """Monitor VF-Agent-Service for design-ready sessions"""
        logger.info("Starting brainstorm session monitoring...")
        
        while self.monitoring:
            try:
                # Poll VF-Agent-Service for design-ready sessions
                response = requests.get(
                    f"{self.vf_agent_api}/api/sessions",
                    params={'status': 'design-ready'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    sessions = response.json()
                    
                    for session_data in sessions:
                        session_id = session_data.get('id')
                        
                        # Skip if already processing
                        if session_id in self.active_sessions:
                            continue
                        
                        # Create session object
                        session = BrainstormSession(
                            session_id=session_id,
                            user_id=session_data.get('user_id'),
                            conversation_data=session_data.get('messages', []),
                            created_at=session_data.get('created_at'),
                            updated_at=session_data.get('updated_at'),
                            status='design-ready',
                            metadata=session_data.get('metadata', {})
                        )
                        
                        self.active_sessions[session_id] = session
                        
                        # Process in separate thread
                        threading.Thread(
                            target=self.process_session,
                            args=(session,),
                            daemon=True
                        ).start()
                        
                        logger.info(f"Processing design-ready session: {session_id}")
                
                # Also check for direct submission requests
                self._check_direct_submissions()
                
            except requests.RequestException as e:
                logger.warning(f"Error polling VF-Agent-Service: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in monitoring: {e}")
            
            time.sleep(self.poll_interval)
    
    def _check_direct_submissions(self):
        """Check for direct design document submissions"""
        try:
            # Check for submissions via file system (hot folder approach)
            submissions_dir = Path("vf_submissions")
            if submissions_dir.exists():
                for file_path in submissions_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r') as f:
                            submission = json.load(f)
                        
                        # Process submission
                        session_id = submission.get('session_id', hashlib.md5(str(file_path).encode()).hexdigest()[:8])
                        
                        if session_id not in self.active_sessions:
                            session = BrainstormSession(
                                session_id=session_id,
                                user_id=submission.get('user_id', 'direct'),
                                conversation_data=submission.get('conversation', []),
                                created_at=datetime.now().isoformat(),
                                updated_at=datetime.now().isoformat(),
                                status='design-ready',
                                metadata={'source': 'direct_submission'}
                            )
                            
                            self.active_sessions[session_id] = session
                            self.process_session(session)
                        
                        # Move processed file
                        processed_dir = submissions_dir / "processed"
                        processed_dir.mkdir(exist_ok=True)
                        file_path.rename(processed_dir / file_path.name)
                        
                    except Exception as e:
                        logger.error(f"Error processing submission file {file_path}: {e}")
        except Exception as e:
            logger.debug(f"Direct submission check error: {e}")
    
    def process_session(self, session: BrainstormSession):
        """Process a brainstorming session through the pipeline"""
        start_time = datetime.now()
        
        try:
            # Update status
            session.status = 'processing'
            self._update_progress(session.session_id, 'design', 10, "Extracting requirements...")
            
            # Extract requirements
            requirements = self.extract_design_requirements(session.conversation_data)
            session.extracted_requirements = requirements
            self._update_progress(session.session_id, 'design', 30, "Requirements extracted")
            
            # Format design document
            design_doc = self.format_design_document(requirements, session)
            self.design_documents[design_doc.document_id] = design_doc
            session.design_document_id = design_doc.document_id
            self._update_progress(session.session_id, 'design', 50, "Design document formatted")
            
            # Submit to pipeline
            pipeline_id = self.submit_to_pipeline(design_doc)
            if pipeline_id:
                session.status = 'submitted'
                self._update_progress(session.session_id, 'architect', 60, "Submitted to AI Architect Agent")
                
                # Track implementation
                self.track_implementation(pipeline_id, session)
                
                # Update metrics
                processing_time = (datetime.now() - start_time).total_seconds()
                self.metrics['processing_times'].append(processing_time)
                self.metrics['avg_processing_time'] = sum(self.metrics['processing_times']) / len(self.metrics['processing_times'])
                self.metrics['sessions_processed'] += 1
                self.metrics['successful_completions'] += 1
                
                logger.info(f"Successfully processed session {session.session_id} in {processing_time:.2f} seconds")
            else:
                session.status = 'failed'
                self.metrics['failed_submissions'] += 1
                logger.error(f"Failed to submit session {session.session_id} to pipeline")
                
        except Exception as e:
            session.status = 'error'
            self.metrics['failed_submissions'] += 1
            logger.error(f"Error processing session {session.session_id}: {e}")
            self._update_progress(session.session_id, 'error', 0, f"Error: {str(e)}")
    
    def extract_design_requirements(self, conversation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert brainstorming conversation to structured requirements"""
        
        requirements = {
            'functional': [],
            'non_functional': [],
            'user_stories': [],
            'technical_constraints': [],
            'business_objectives': [],
            'acceptance_criteria': [],
            'extracted_entities': []
        }
        
        # Combine all conversation text
        full_text = ""
        for message in conversation_data:
            if message.get('role') == 'user':
                full_text += message.get('content', '') + "\n"
        
        # Try VF-Text-Service for AI-powered extraction
        if self._use_vf_text_service(full_text, requirements):
            logger.info("Requirements extracted using VF-Text-Service")
        else:
            # Fallback to pattern-based extraction
            self._pattern_based_extraction(full_text, requirements)
            logger.info("Requirements extracted using pattern matching")
        
        # Extract entities and technical terms
        requirements['extracted_entities'] = self._extract_entities(full_text)
        
        # Infer business objectives
        requirements['business_objectives'] = self._infer_business_objectives(full_text)
        
        # Generate acceptance criteria if not found
        if not requirements['acceptance_criteria']:
            requirements['acceptance_criteria'] = self._generate_acceptance_criteria(requirements)
        
        return requirements
    
    def _use_vf_text_service(self, text: str, requirements: Dict[str, Any]) -> bool:
        """Use VF-Text-Service for AI-powered requirement extraction"""
        try:
            response = requests.post(
                f"{self.vf_text_api}/api/text/extract-requirements",
                json={'text': text},
                timeout=10
            )
            
            if response.status_code == 200:
                extracted = response.json()
                
                # Map extracted data to requirements structure
                requirements['functional'].extend(extracted.get('functional_requirements', []))
                requirements['non_functional'].extend(extracted.get('non_functional_requirements', []))
                requirements['user_stories'].extend(extracted.get('user_stories', []))
                requirements['technical_constraints'].extend(extracted.get('technical_constraints', []))
                requirements['acceptance_criteria'].extend(extracted.get('acceptance_criteria', []))
                
                return True
                
        except Exception as e:
            logger.warning(f"VF-Text-Service extraction failed: {e}")
        
        return False
    
    def _pattern_based_extraction(self, text: str, requirements: Dict[str, Any]):
        """Fallback pattern-based requirement extraction"""
        text_lower = text.lower()
        
        # Extract functional requirements
        for pattern in self.requirement_patterns['functional']:
            matches = re.findall(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                requirement = match if isinstance(match, str) else match[0]
                requirements['functional'].append({
                    'description': requirement.strip(),
                    'priority': self._determine_priority(requirement),
                    'category': 'functional'
                })
        
        # Extract non-functional requirements
        for pattern in self.requirement_patterns['non_functional']:
            matches = re.findall(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                requirement = match if isinstance(match, str) else ' '.join(match) if isinstance(match, tuple) else str(match)
                requirements['non_functional'].append({
                    'description': requirement.strip(),
                    'priority': 'high',  # Non-functional usually high priority
                    'category': 'non-functional'
                })
        
        # Extract user stories
        for pattern in self.requirement_patterns['user_story']:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 3:
                    requirements['user_stories'].append({
                        'role': match[0],
                        'feature': match[1],
                        'benefit': match[2]
                    })
                else:
                    requirements['user_stories'].append({
                        'description': str(match)
                    })
        
        # Extract technical constraints
        tech_keywords = ['database', 'api', 'framework', 'language', 'platform', 'cloud', 'aws', 'azure', 'docker']
        for keyword in tech_keywords:
            if keyword in text_lower:
                # Find sentences containing the keyword
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        requirements['technical_constraints'].append(sentence.strip())
        
        # Remove duplicates
        requirements['functional'] = list({json.dumps(r, sort_keys=True): r for r in requirements['functional']}.values())
        requirements['non_functional'] = list({json.dumps(r, sort_keys=True): r for r in requirements['non_functional']}.values())
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities and technical terms"""
        entities = []
        
        # Common technical entities
        entity_patterns = [
            r'\b(user|customer|admin|manager)\b',
            r'\b(product|order|payment|invoice)\b',
            r'\b(dashboard|report|analytics|metric)\b',
            r'\b(api|database|server|client)\b'
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, text.lower())
            entities.extend(matches)
        
        return list(set(entities))
    
    def _infer_business_objectives(self, text: str) -> List[str]:
        """Infer business objectives from conversation"""
        objectives = []
        
        objective_keywords = {
            'increase': 'Increase operational efficiency',
            'reduce': 'Reduce operational costs',
            'improve': 'Improve user experience',
            'automate': 'Automate manual processes',
            'scale': 'Enable business scaling',
            'integrate': 'Integrate with existing systems',
            'optimize': 'Optimize performance',
            'streamline': 'Streamline workflows'
        }
        
        text_lower = text.lower()
        for keyword, objective in objective_keywords.items():
            if keyword in text_lower:
                objectives.append(objective)
        
        if not objectives:
            objectives.append("Deliver business value through technology")
        
        return objectives
    
    def _generate_acceptance_criteria(self, requirements: Dict[str, Any]) -> List[str]:
        """Generate acceptance criteria from requirements"""
        criteria = []
        
        # From functional requirements
        for req in requirements.get('functional', [])[:5]:  # Top 5
            criteria.append(f"System must {req.get('description', '')}")
        
        # From non-functional requirements
        for req in requirements.get('non_functional', [])[:3]:  # Top 3
            criteria.append(f"System must meet: {req.get('description', '')}")
        
        # From user stories
        for story in requirements.get('user_stories', [])[:3]:  # Top 3
            if 'feature' in story:
                criteria.append(f"User can {story['feature']}")
        
        if not criteria:
            criteria = [
                "System functions as designed",
                "All tests pass successfully",
                "Documentation is complete"
            ]
        
        return criteria
    
    def _determine_priority(self, text: str) -> str:
        """Determine requirement priority"""
        high_priority_words = ['critical', 'urgent', 'must', 'required', 'essential']
        medium_priority_words = ['should', 'important', 'needed']
        low_priority_words = ['nice to have', 'optional', 'future', 'consider']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in high_priority_words):
            return 'high'
        elif any(word in text_lower for word in medium_priority_words):
            return 'medium'
        else:
            return 'low'
    
    def format_design_document(self, requirements: Dict[str, Any], session: BrainstormSession) -> DesignDocument:
        """Format requirements into Visual Forge AI compatible format"""
        
        # Generate document ID
        doc_id = f"dd-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{session.session_id[:6]}"
        
        # Extract title from first functional requirement or metadata
        title = "Untitled Project"
        if requirements['functional']:
            title = f"System to {requirements['functional'][0].get('description', 'implement requirements')}"
        elif session.metadata.get('title'):
            title = session.metadata['title']
        
        # Create overview
        overview = self._generate_overview(requirements, session)
        
        # Format user stories
        formatted_stories = []
        for story in requirements['user_stories']:
            if isinstance(story, dict):
                if 'role' in story and 'feature' in story:
                    formatted_stories.append({
                        'title': f"As a {story['role']}",
                        'description': f"I want {story['feature']}",
                        'benefit': story.get('benefit', 'to achieve my goals'),
                        'priority': 'medium'
                    })
                else:
                    formatted_stories.append({
                        'title': 'User Story',
                        'description': story.get('description', str(story)),
                        'priority': 'medium'
                    })
        
        # Create success metrics
        success_metrics = [
            {'metric': 'User Adoption', 'target': '80% within 3 months', 'measurement': 'Active users'},
            {'metric': 'Performance', 'target': '<200ms response time', 'measurement': 'API latency'},
            {'metric': 'Reliability', 'target': '99.9% uptime', 'measurement': 'System availability'}
        ]
        
        # Add custom metrics from requirements
        if requirements.get('non_functional'):
            for req in requirements['non_functional'][:2]:
                success_metrics.append({
                    'metric': 'Custom Requirement',
                    'target': req.get('description', 'Meet requirement'),
                    'measurement': 'Compliance check'
                })
        
        # Create design document
        design_doc = DesignDocument(
            document_id=doc_id,
            session_id=session.session_id,
            title=title[:200],  # Limit title length
            overview=overview,
            objectives=requirements.get('business_objectives', ['Deliver business value']),
            functional_requirements=requirements.get('functional', []),
            non_functional_requirements=requirements.get('non_functional', []),
            technical_constraints=requirements.get('technical_constraints', []),
            user_stories=formatted_stories,
            acceptance_criteria=requirements.get('acceptance_criteria', []),
            success_metrics=success_metrics,
            business_context={
                'domain': self._determine_domain(requirements),
                'users': requirements.get('extracted_entities', []),
                'integration_points': self._identify_integrations(requirements)
            },
            created_at=datetime.now().isoformat()
        )
        
        # Save design document
        self._save_design_document(design_doc)
        
        self.metrics['documents_generated'] += 1
        logger.info(f"Generated design document: {doc_id}")
        
        return design_doc
    
    def _generate_overview(self, requirements: Dict[str, Any], session: BrainstormSession) -> str:
        """Generate project overview"""
        overview_parts = []
        
        # Project purpose
        if requirements['functional']:
            overview_parts.append(f"This project aims to {requirements['functional'][0].get('description', 'meet user requirements')}.")
        
        # Key features
        if len(requirements['functional']) > 1:
            features = [req.get('description', '') for req in requirements['functional'][1:4]]
            if features:
                overview_parts.append(f"Key features include: {', '.join(features)}.")
        
        # Technical approach
        if requirements['technical_constraints']:
            overview_parts.append(f"Technical constraints: {', '.join(requirements['technical_constraints'][:2])}.")
        
        # Business value
        if requirements['business_objectives']:
            overview_parts.append(f"Business objectives: {', '.join(requirements['business_objectives'][:2])}.")
        
        return " ".join(overview_parts) if overview_parts else "A comprehensive solution to address user requirements."
    
    def _determine_domain(self, requirements: Dict[str, Any]) -> str:
        """Determine project domain"""
        entities = requirements.get('extracted_entities', [])
        
        domain_indicators = {
            'ecommerce': ['product', 'order', 'payment', 'cart', 'checkout'],
            'healthcare': ['patient', 'doctor', 'appointment', 'medical', 'health'],
            'finance': ['payment', 'invoice', 'transaction', 'account', 'banking'],
            'education': ['student', 'course', 'lesson', 'teacher', 'learning'],
            'social': ['user', 'profile', 'friend', 'message', 'post'],
            'enterprise': ['employee', 'department', 'workflow', 'approval', 'report']
        }
        
        for domain, indicators in domain_indicators.items():
            if any(indicator in entities for indicator in indicators):
                return domain
        
        return 'general'
    
    def _identify_integrations(self, requirements: Dict[str, Any]) -> List[str]:
        """Identify external integration points"""
        integrations = []
        
        # Check technical constraints for integration mentions
        for constraint in requirements.get('technical_constraints', []):
            constraint_lower = constraint.lower()
            
            # Common integrations
            if 'api' in constraint_lower:
                integrations.append('External APIs')
            if 'database' in constraint_lower:
                integrations.append('Database Systems')
            if 'payment' in constraint_lower:
                integrations.append('Payment Gateway')
            if 'email' in constraint_lower:
                integrations.append('Email Service')
            if 'sms' in constraint_lower:
                integrations.append('SMS Service')
            if 'cloud' in constraint_lower:
                integrations.append('Cloud Services')
        
        return list(set(integrations))
    
    def _save_design_document(self, design_doc: DesignDocument):
        """Save design document to file system"""
        docs_dir = Path("design_documents")
        docs_dir.mkdir(exist_ok=True)
        
        # Save as JSON
        json_path = docs_dir / f"{design_doc.document_id}.json"
        with open(json_path, 'w') as f:
            json.dump(asdict(design_doc), f, indent=2, default=str)
        
        # Save as Markdown
        md_path = docs_dir / f"{design_doc.document_id}.md"
        self._save_design_document_markdown(design_doc, md_path)
        
        logger.info(f"Saved design document to {json_path} and {md_path}")
    
    def _save_design_document_markdown(self, design_doc: DesignDocument, filepath: Path):
        """Save design document as markdown"""
        md_content = f"""# Design Document: {design_doc.title}

**Document ID:** {design_doc.document_id}  
**Session ID:** {design_doc.session_id}  
**Created:** {design_doc.created_at}

## Overview
{design_doc.overview}

## Business Objectives
"""
        for obj in design_doc.objectives:
            md_content += f"- {obj}\n"
        
        md_content += "\n## Functional Requirements\n"
        for req in design_doc.functional_requirements:
            md_content += f"- **{req.get('priority', 'medium')}:** {req.get('description', '')}\n"
        
        md_content += "\n## Non-Functional Requirements\n"
        for req in design_doc.non_functional_requirements:
            md_content += f"- **{req.get('category', 'general')}:** {req.get('description', '')}\n"
        
        md_content += "\n## User Stories\n"
        for story in design_doc.user_stories:
            md_content += f"### {story.get('title', 'Story')}\n"
            md_content += f"{story.get('description', '')}\n"
            if 'benefit' in story:
                md_content += f"**Benefit:** {story['benefit']}\n"
            md_content += "\n"
        
        md_content += "## Acceptance Criteria\n"
        for criteria in design_doc.acceptance_criteria:
            md_content += f"- {criteria}\n"
        
        md_content += "\n## Success Metrics\n"
        for metric in design_doc.success_metrics:
            md_content += f"- **{metric['metric']}:** {metric['target']} (Measured by: {metric['measurement']})\n"
        
        md_content += f"""
## Technical Context
**Domain:** {design_doc.business_context.get('domain', 'general')}  
**Key Entities:** {', '.join(design_doc.business_context.get('users', []))}  
**Integrations:** {', '.join(design_doc.business_context.get('integration_points', []))}

## Technical Constraints
"""
        for constraint in design_doc.technical_constraints:
            md_content += f"- {constraint}\n"
        
        with open(filepath, 'w') as f:
            f.write(md_content)
    
    def submit_to_pipeline(self, design_document: DesignDocument) -> Optional[str]:
        """Submit design document to Visual Forge AI → PM Workflow pipeline"""
        
        try:
            # Generate project ID
            project_id = f"proj-{design_document.document_id}"
            
            # Update status
            design_document.pipeline_status = 'submitting'
            design_document.submitted_at = datetime.now().isoformat()
            
            # Try direct AI Architect Agent integration first
            if self.ai_architect:
                logger.info("Using direct AI Architect Agent integration")
                
                # Convert design document to GitHub issue format for AI Architect
                issue_data = self._convert_to_github_issue(design_document)
                
                # Process directly with AI Architect Agent
                try:
                    analysis = self.ai_architect.analyze_github_issue(issue_data)
                    arch_spec = self.ai_architect.create_architecture_specification(analysis)
                    spec_file = self.ai_architect.save_architecture_specification(arch_spec)
                    
                    # Update tracking
                    design_document.pipeline_status = 'architect_complete'
                    if design_document.session_id in self.active_sessions:
                        self.active_sessions[design_document.session_id].architect_spec_id = arch_spec.spec_id
                    
                    logger.info(f"AI Architect Agent generated specification: {arch_spec.spec_id}")
                    
                    # Track in pipeline progress
                    self.pipeline_progress[project_id] = PipelineProgress(
                        project_id=project_id,
                        session_id=design_document.session_id,
                        current_stage='architect',
                        progress_percentage=80,
                        status_message=f"Architecture specification generated: {arch_spec.spec_id}",
                        started_at=design_document.submitted_at,
                        updated_at=datetime.now().isoformat(),
                        artifacts=[{
                            'type': 'architecture_spec',
                            'id': arch_spec.spec_id,
                            'path': spec_file
                        }]
                    )
                    
                    self.metrics['pipeline_submissions'] += 1
                    return project_id
                    
                except Exception as e:
                    logger.error(f"Direct AI Architect processing failed: {e}")
            
            # Fallback to Visual Forge AI System submission
            logger.info("Submitting to Visual Forge AI System")
            
            # Prepare submission payload
            payload = {
                'document_id': design_document.document_id,
                'title': design_document.title,
                'overview': design_document.overview,
                'requirements': {
                    'functional': design_document.functional_requirements,
                    'non_functional': design_document.non_functional_requirements
                },
                'user_stories': design_document.user_stories,
                'constraints': design_document.technical_constraints,
                'metadata': {
                    'session_id': design_document.session_id,
                    'created_at': design_document.created_at,
                    'source': 'vf-design-document-bridge'
                }
            }
            
            # Submit to Visual Forge AI
            response = requests.post(
                f"{self.visual_forge_ai}/api/design/submit",
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                pipeline_id = result.get('pipeline_id', project_id)
                
                design_document.pipeline_status = 'submitted'
                
                # Track in pipeline progress
                self.pipeline_progress[pipeline_id] = PipelineProgress(
                    project_id=pipeline_id,
                    session_id=design_document.session_id,
                    current_stage='visual_forge',
                    progress_percentage=40,
                    status_message="Submitted to Visual Forge AI System",
                    started_at=design_document.submitted_at,
                    updated_at=datetime.now().isoformat()
                )
                
                self.metrics['pipeline_submissions'] += 1
                logger.info(f"Submitted to Visual Forge AI with pipeline ID: {pipeline_id}")
                
                # Monitor PM Workflow processing
                self._monitor_pm_workflow(pipeline_id, design_document)
                
                return pipeline_id
            else:
                logger.error(f"Visual Forge AI submission failed: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Network error submitting to pipeline: {e}")
        except Exception as e:
            logger.error(f"Unexpected error submitting to pipeline: {e}")
        
        design_document.pipeline_status = 'failed'
        return None
    
    def _convert_to_github_issue(self, design_doc: DesignDocument) -> Dict[str, Any]:
        """Convert design document to GitHub issue format for AI Architect"""
        
        # Combine all requirements into issue body
        body_parts = [design_doc.overview, "\n\n## Requirements:\n"]
        
        # Add functional requirements
        if design_doc.functional_requirements:
            body_parts.append("\n### Functional Requirements:\n")
            for req in design_doc.functional_requirements:
                body_parts.append(f"- {req.get('description', '')}\n")
        
        # Add non-functional requirements
        if design_doc.non_functional_requirements:
            body_parts.append("\n### Non-Functional Requirements:\n")
            for req in design_doc.non_functional_requirements:
                body_parts.append(f"- {req.get('description', '')}\n")
        
        # Add user stories
        if design_doc.user_stories:
            body_parts.append("\n### User Stories:\n")
            for story in design_doc.user_stories:
                body_parts.append(f"- {story.get('description', story.get('title', ''))}\n")
        
        # Add technical constraints
        if design_doc.technical_constraints:
            body_parts.append("\n### Technical Constraints:\n")
            for constraint in design_doc.technical_constraints:
                body_parts.append(f"- {constraint}\n")
        
        # Add acceptance criteria
        if design_doc.acceptance_criteria:
            body_parts.append("\n### Acceptance Criteria:\n")
            for criteria in design_doc.acceptance_criteria:
                body_parts.append(f"- {criteria}\n")
        
        # Create issue format
        issue_data = {
            'id': design_doc.document_id,
            'title': design_doc.title,
            'body': "".join(body_parts),
            'labels': ['feature', 'from-vf-bridge'],
            'assignees': ['ai-architect']
        }
        
        return issue_data
    
    def _monitor_pm_workflow(self, pipeline_id: str, design_doc: DesignDocument):
        """Monitor PM Workflow processing"""
        
        def monitor():
            try:
                max_attempts = 60  # 5 minutes with 5-second intervals
                attempts = 0
                
                while attempts < max_attempts:
                    response = requests.get(
                        f"{self.pm_workflow_api}/api/pipeline/{pipeline_id}/status",
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        status = response.json()
                        
                        # Update progress
                        if pipeline_id in self.pipeline_progress:
                            progress = self.pipeline_progress[pipeline_id]
                            progress.current_stage = status.get('stage', 'processing')
                            progress.progress_percentage = status.get('progress', 50)
                            progress.status_message = status.get('message', 'Processing...')
                            progress.updated_at = datetime.now().isoformat()
                        
                        # Check if ready for AI Architect
                        if status.get('stage') == 'ready_for_architect':
                            logger.info(f"PM Workflow ready for AI Architect: {pipeline_id}")
                            # AI Architect should pick it up automatically
                            break
                        
                        # Check if completed
                        if status.get('stage') == 'completed':
                            logger.info(f"Pipeline completed: {pipeline_id}")
                            break
                    
                    attempts += 1
                    time.sleep(5)
                    
            except Exception as e:
                logger.error(f"Error monitoring PM Workflow: {e}")
        
        # Run in separate thread
        threading.Thread(target=monitor, daemon=True).start()
    
    def track_implementation(self, project_id: str, session: BrainstormSession):
        """Monitor progress through AI Architect → Developer pipeline"""
        
        def track():
            try:
                start_time = datetime.now()
                max_duration = timedelta(hours=1)  # Maximum tracking duration
                
                while datetime.now() - start_time < max_duration:
                    if project_id not in self.pipeline_progress:
                        break
                    
                    progress = self.pipeline_progress[project_id]
                    
                    # Check AI Architect Agent status
                    if session.architect_spec_id:
                        # Architecture complete, waiting for developer
                        progress.current_stage = 'development'
                        progress.progress_percentage = 90
                        progress.status_message = "Architecture complete, awaiting AI Developer Agent"
                        
                        # Notify user of completion
                        self.notify_completion(project_id, {
                            'status': 'architecture_complete',
                            'spec_id': session.architect_spec_id,
                            'message': 'Technical architecture specification generated successfully'
                        })
                        break
                    
                    # Check for timeout
                    if (datetime.now() - datetime.fromisoformat(progress.started_at)) > timedelta(minutes=30):
                        logger.warning(f"Pipeline timeout for project {project_id}")
                        progress.status_message = "Processing timeout - manual intervention may be required"
                        break
                    
                    time.sleep(10)  # Check every 10 seconds
                    
            except Exception as e:
                logger.error(f"Error tracking implementation: {e}")
        
        # Run in separate thread
        threading.Thread(target=track, daemon=True).start()
    
    def notify_completion(self, project_id: str, results: Dict[str, Any]):
        """Send completion notification back to VF-Agent-Service"""
        
        try:
            if project_id not in self.pipeline_progress:
                logger.warning(f"No progress tracking for project {project_id}")
                return
            
            progress = self.pipeline_progress[project_id]
            session_id = progress.session_id
            
            # Prepare notification
            notification = {
                'session_id': session_id,
                'project_id': project_id,
                'status': results.get('status', 'completed'),
                'message': results.get('message', 'Processing complete'),
                'artifacts': progress.artifacts or [],
                'completion_time': datetime.now().isoformat()
            }
            
            # Add architecture specification details if available
            if 'spec_id' in results:
                notification['architecture_spec'] = {
                    'id': results['spec_id'],
                    'location': f"architecture_specs/{results['spec_id']}.json"
                }
            
            # Send to VF-Agent-Service
            try:
                response = requests.post(
                    f"{self.vf_agent_api}/api/sessions/{session_id}/notification",
                    json=notification,
                    timeout=5
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Notification sent to VF-Agent-Service for session {session_id}")
                else:
                    logger.warning(f"Failed to notify VF-Agent-Service: {response.status_code}")
                    
            except requests.RequestException as e:
                logger.error(f"Error notifying VF-Agent-Service: {e}")
            
            # Update progress tracking
            progress.completed_at = datetime.now().isoformat()
            progress.current_stage = 'completed'
            progress.progress_percentage = 100
            progress.status_message = results.get('message', 'Complete')
            
            # Update metrics
            self.metrics['successful_completions'] += 1
            
            # Send WebSocket update if connected
            self._send_websocket_update(session_id, notification)
            
        except Exception as e:
            logger.error(f"Error in notify_completion: {e}")
    
    def _update_progress(self, session_id: str, stage: str, percentage: int, message: str):
        """Update and broadcast progress"""
        
        # Find project ID for session
        project_id = None
        for pid, progress in self.pipeline_progress.items():
            if progress.session_id == session_id:
                project_id = pid
                break
        
        if not project_id:
            # Create new progress tracking
            project_id = f"proj-{session_id[:8]}"
            self.pipeline_progress[project_id] = PipelineProgress(
                project_id=project_id,
                session_id=session_id,
                current_stage=stage,
                progress_percentage=percentage,
                status_message=message,
                started_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        else:
            # Update existing progress
            progress = self.pipeline_progress[project_id]
            progress.current_stage = stage
            progress.progress_percentage = percentage
            progress.status_message = message
            progress.updated_at = datetime.now().isoformat()
        
        # Send WebSocket update
        self._send_websocket_update(session_id, {
            'type': 'progress',
            'stage': stage,
            'percentage': percentage,
            'message': message
        })
        
        # Update dashboard
        self._update_dashboard(project_id)
    
    def _send_websocket_update(self, session_id: str, data: Dict[str, Any]):
        """Send real-time update via WebSocket"""
        if session_id in self.ws_connections:
            try:
                ws = self.ws_connections[session_id]
                ws.send(json.dumps(data))
            except Exception as e:
                logger.debug(f"WebSocket send error: {e}")
                # Remove dead connection
                del self.ws_connections[session_id]
    
    def _update_dashboard(self, project_id: str):
        """Update dashboard with pipeline status"""
        try:
            if project_id not in self.pipeline_progress:
                return
            
            progress = self.pipeline_progress[project_id]
            
            # Prepare update
            update = {
                'component': 'vf-bridge',
                'project_id': project_id,
                'session_id': progress.session_id,
                'stage': progress.current_stage,
                'progress': progress.progress_percentage,
                'message': progress.status_message,
                'timestamp': progress.updated_at
            }
            
            # Send to dashboard
            response = requests.post(
                f"{self.dashboard_api}/api/vf-bridge/update",
                json=update,
                timeout=2
            )
            
            if response.status_code == 200:
                logger.debug(f"Dashboard updated for project {project_id}")
                
        except Exception as e:
            logger.debug(f"Dashboard update error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge status and metrics"""
        return {
            'status': 'operational' if self.monitoring else 'stopped',
            'active_sessions': len(self.active_sessions),
            'design_documents': len(self.design_documents),
            'pipeline_projects': len(self.pipeline_progress),
            'metrics': self.metrics,
            'ai_architect_available': AI_ARCHITECT_AVAILABLE,
            'services': {
                'vf_agent': self._check_service_health(self.vf_agent_api),
                'vf_text': self._check_service_health(self.vf_text_api),
                'visual_forge': self._check_service_health(self.visual_forge_ai),
                'pm_workflow': self._check_service_health(self.pm_workflow_api)
            }
        }
    
    def _check_service_health(self, service_url: str) -> str:
        """Check if a service is reachable"""
        try:
            response = requests.get(f"{service_url}/health", timeout=2)
            return 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            return 'unreachable'
    
    def start(self):
        """Start the bridge monitoring"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_brainstorm_sessions, daemon=True)
            self.monitor_thread.start()
            logger.info("VF Design Document Bridge started")
    
    def stop(self):
        """Stop the bridge monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("VF Design Document Bridge stopped")


def main():
    """Main entry point"""
    bridge = VFDesignDocumentBridge()
    
    print("\n" + "="*80)
    print("VF-DESIGN-DOCUMENT-BRIDGE INITIALIZED")
    print("="*80)
    print("Connecting VF-Agent-Service to AI Architect Agent Pipeline")
    print("-"*80)
    print(f"VF-Agent-Service API: {bridge.vf_agent_api}")
    print(f"VF-Text-Service API: {bridge.vf_text_api}")
    print(f"Visual Forge AI: {bridge.visual_forge_ai}")
    print(f"PM Workflow API: {bridge.pm_workflow_api}")
    print(f"AI Architect Agent: {'Direct Integration' if AI_ARCHITECT_AVAILABLE else 'Via Pipeline'}")
    print("="*80)
    print("Status: Ready to process brainstorming sessions")
    print("="*80 + "\n")
    
    # Start monitoring
    bridge.start()
    
    try:
        while True:
            time.sleep(30)
            
            # Log status periodically
            status = bridge.get_status()
            logger.info(f"Bridge Status: {status['active_sessions']} active sessions, "
                       f"{status['metrics']['documents_generated']} documents generated, "
                       f"{status['metrics']['successful_completions']} completions")
            
    except KeyboardInterrupt:
        print("\nShutting down VF Design Document Bridge...")
        bridge.stop()


if __name__ == "__main__":
    main()