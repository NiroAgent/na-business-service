#!/usr/bin/env python3
"""
PM Workflow System
Integrates with design document processor and feature management system
to create a complete workflow from design documents to implementation.
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid

# Import our existing systems
try:
    from design_document_processor import DesignDocumentProcessor, DesignDocument
    from feature_management_system import FeatureManager, Feature, Epic, UserStory, AcceptanceCriteria
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure design-document-processor.py and feature-management-system.py are available")
    sys.exit(1)

class PMWorkflowSystem:
    """
    Project Manager workflow system that bridges design documents 
    to feature/epic/story creation
    """
    
    def __init__(self):
        self.design_processor = DesignDocumentProcessor()
        self.feature_manager = FeatureManager()
        self.workflow_history: List[Dict[str, Any]] = []
        self.load_workflow_history()
        
    def load_workflow_history(self):
        """Load previous workflow executions"""
        history_file = Path("pm_workflow_history.json")
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.workflow_history = json.load(f)
            except Exception as e:
                print(f"Error loading workflow history: {e}")
                
    def save_workflow_history(self):
        """Save workflow execution history"""
        with open("pm_workflow_history.json", 'w') as f:
            json.dump(self.workflow_history, f, indent=2, default=str)
            
    def process_design_document_to_features(self, doc_id: str, pm_instructions: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main PM workflow: Convert design document to features, epics, and stories
        """
        print(f"🎯 Starting PM workflow for document: {doc_id}")
        
        # Get the design document
        doc = self.design_processor.get_document(doc_id)
        if not doc:
            return {"error": f"Design document {doc_id} not found"}
            
        # Get PM handoff package
        handoff_package = self.design_processor.prepare_pm_handoff_package(doc_id)
        
        workflow_result = {
            "workflow_id": str(uuid.uuid4())[:8],
            "document_id": doc_id,
            "document_title": doc.title,
            "started_at": datetime.now().isoformat(),
            "pm_instructions": pm_instructions or {},
            "created_features": [],
            "created_epics": [],
            "created_stories": [],
            "summary": {}
        }
        
        print(f"📋 Processing {len(doc.parsed_requirements)} requirements...")
        
        # Step 1: Create main project feature
        main_feature = self._create_main_project_feature(doc, handoff_package)
        workflow_result["created_features"].append(main_feature.id)
        
        # Step 2: Create epics based on suggested groupings
        epics_created = self._create_epics_from_suggestions(
            handoff_package["pm_recommendations"]["suggested_epics"], 
            main_feature.id
        )
        workflow_result["created_epics"].extend([epic.id for epic in epics_created])
        
        # Step 3: Create user stories from requirements
        stories_created = self._create_stories_from_requirements(
            doc.parsed_requirements, 
            epics_created, 
            main_feature.id
        )
        workflow_result["created_stories"].extend([story.id for story in stories_created])
        
        # Step 4: Generate workflow summary
        workflow_result["summary"] = {
            "total_features": 1,
            "total_epics": len(epics_created),
            "total_stories": len(stories_created),
            "requirements_processed": len(doc.parsed_requirements),
            "effort_distribution": self._calculate_effort_distribution(stories_created),
            "priority_distribution": self._calculate_priority_distribution(stories_created)
        }
        
        workflow_result["completed_at"] = datetime.now().isoformat()
        
        # Save workflow history
        self.workflow_history.append(workflow_result)
        self.save_workflow_history()
        
        # Update design document status
        self.design_processor.documents[doc_id].status = "handed-off-to-pm"
        self.design_processor.save_documents()
        
        print(f"✅ PM workflow completed!")
        print(f"   📦 Created: 1 feature, {len(epics_created)} epics, {len(stories_created)} stories")
        
        return workflow_result
        
    def _create_main_project_feature(self, doc: DesignDocument, handoff_package: Dict[str, Any]) -> Feature:
        """Create the main feature for the project"""
        
        # Generate comprehensive acceptance criteria from business objectives
        main_acceptance_criteria = []
        for objective in doc.business_objectives:
            criteria = AcceptanceCriteria(
                id=str(uuid.uuid4())[:8],
                title=f"Business Objective: {objective[:50]}...",
                description=objective,
                priority="high",
                test_scenarios=["Validate business objective is met"],
                definition_of_done=["Objective measurably achieved"]
            )
            main_acceptance_criteria.append(criteria)
            
        # Add technical acceptance criteria
        for tech in doc.technical_stack:
            criteria = AcceptanceCriteria(
                id=str(uuid.uuid4())[:8],
                title=f"Technical Implementation: {tech}",
                description=f"Successfully implement and integrate {tech}",
                priority="medium",
                test_scenarios=[f"Verify {tech} integration", f"Test {tech} functionality"],
                definition_of_done=[f"{tech} fully integrated and tested"]
            )
            main_acceptance_criteria.append(criteria)
            
        feature = Feature(
            id=str(uuid.uuid4())[:8],
            title=doc.title,
            description=f"Complete implementation of {doc.project_name}\n\n{doc.raw_content[:500]}...",
            business_value="\n".join(doc.business_objectives),
            acceptance_criteria=main_acceptance_criteria,
            priority="high",
            status="concept",
            estimated_effort="xl",
            tags=["main-feature", "project-root"] + doc.technical_stack,
            created_date=datetime.now().isoformat(),
            target_release="v1.0",
            dependencies=[],
            progress=0
        )
        
        self.feature_manager.add_feature(feature)
        print(f"📦 Created main feature: {feature.title} ({feature.id})")
        return feature
        
    def _create_epics_from_suggestions(self, suggested_epics: List[Dict[str, Any]], parent_feature_id: str) -> List[Epic]:
        """Create epics based on PM recommendations"""
        epics_created = []
        
        for suggestion in suggested_epics:
            epic = Epic(
                id=str(uuid.uuid4())[:8],
                title=suggestion["name"],
                description=suggestion["description"],
                feature_id=parent_feature_id,
                priority="medium",
                status="planned",
                estimated_effort=suggestion["estimated_effort"],
                tags=["auto-generated", "from-design-doc"],
                created_date=datetime.now().isoformat(),
                target_completion="TBD",
                progress=0
            )
            
            self.feature_manager.add_epic(epic)
            epics_created.append(epic)
            print(f"🎯 Created epic: {epic.title} ({epic.id})")
            
        return epics_created
        
    def _create_stories_from_requirements(self, requirements: List, epics: List[Epic], feature_id: str) -> List[UserStory]:
        """Convert design requirements into user stories"""
        stories_created = []
        
        # Create a mapping of requirement categories to epics
        epic_mapping = {}
        for epic in epics:
            if "functional" in epic.title.lower():
                epic_mapping["functional"] = epic.id
            elif "technical" in epic.title.lower():
                epic_mapping["technical"] = epic.id
            elif "business" in epic.title.lower():
                epic_mapping["business"] = epic.id
            else:
                epic_mapping["non-functional"] = epic.id
                
        for req in requirements:
            # Determine which epic this story belongs to
            epic_id = epic_mapping.get(req.category, epics[0].id if epics else None)
            
            # Convert requirement to user story format
            story_title = self._convert_to_user_story_title(req.title)
            
            # Generate acceptance criteria from requirement
            acceptance_criteria = [
                AcceptanceCriteria(
                    id=str(uuid.uuid4())[:8],
                    title=f"Requirement: {req.title[:50]}...",
                    description=req.description,
                    priority=req.priority,
                    test_scenarios=[f"Test {req.title}"],
                    definition_of_done=["Requirement fully implemented and tested"]
                )
            ]
            
            # Calculate story points based on effort estimate
            story_points = self._effort_to_story_points(req.estimated_effort)
            
            story = UserStory(
                id=str(uuid.uuid4())[:8],
                title=story_title,
                description=f"As a user, I want {req.description}",
                epic_id=epic_id,
                feature_id=feature_id,
                acceptance_criteria=acceptance_criteria,
                story_points=story_points,
                priority=req.priority,
                status="backlog",
                tags=[req.category, "auto-generated"] + (req.dependencies if req.dependencies else []),
                created_date=datetime.now().isoformat(),
                assigned_to="",
                sprint="TBD",
                progress=0
            )
            
            self.feature_manager.add_user_story(story)
            stories_created.append(story)
            
        print(f"📝 Created {len(stories_created)} user stories")
        return stories_created
        
    def _convert_to_user_story_title(self, requirement_title: str) -> str:
        """Convert a requirement title to user story format"""
        # Simple heuristic to make it more user-story-like
        title = requirement_title.strip()
        
        if not title.lower().startswith(("as a", "i want", "user can", "system should")):
            if "user" in title.lower():
                title = f"User can {title.lower()}"
            elif "system" in title.lower() or "api" in title.lower():
                title = f"System should {title.lower()}"
            else:
                title = f"I want to {title.lower()}"
                
        return title[:100]  # Limit length
        
    def _effort_to_story_points(self, effort: str) -> int:
        """Convert effort estimate to story points"""
        effort_mapping = {
            "small": 2,
            "medium": 5,
            "large": 8,
            "xl": 13
        }
        return effort_mapping.get(effort, 3)
        
    def _calculate_effort_distribution(self, stories: List[UserStory]) -> Dict[str, int]:
        """Calculate distribution of story points"""
        distribution = {"1-3": 0, "4-7": 0, "8-12": 0, "13+": 0}
        
        for story in stories:
            points = story.story_points
            if points <= 3:
                distribution["1-3"] += 1
            elif points <= 7:
                distribution["4-7"] += 1
            elif points <= 12:
                distribution["8-12"] += 1
            else:
                distribution["13+"] += 1
                
        return distribution
        
    def _calculate_priority_distribution(self, stories: List[UserStory]) -> Dict[str, int]:
        """Calculate priority distribution"""
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for story in stories:
            distribution[story.priority] = distribution.get(story.priority, 0) + 1
            
        return distribution
        
    def interactive_pm_workflow(self):
        """Interactive PM workflow for processing design documents"""
        print("🎯 PM Workflow System")
        print("=" * 50)
        print("Convert ChatGPT design documents → Features, Epics & Stories")
        
        # List available design documents
        docs = self.design_processor.list_documents()
        if not docs:
            print("❌ No design documents found. Import documents first using design-document-processor.py")
            return
            
        print(f"\n📋 Available design documents ({len(docs)}):")
        for i, doc in enumerate(docs, 1):
            status_emoji = "✅" if doc.status == "reviewed" else "📄" if doc.status == "draft" else "🔄"
            print(f"  {i}. {status_emoji} {doc.title} ({doc.id}) - {len(doc.parsed_requirements)} requirements")
            
        # Get PM selection
        try:
            choice = int(input(f"\nSelect document (1-{len(docs)}): ")) - 1
            if choice < 0 or choice >= len(docs):
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Invalid input")
            return
            
        selected_doc = docs[choice]
        
        # Get PM customization options
        print(f"\n🎯 Processing: {selected_doc.title}")
        print("PM Customization Options:")
        
        pm_instructions = {}
        
        # Epic naming strategy
        print("\n1. Epic Creation Strategy:")
        print("   a) Auto-generate by requirement category (default)")
        print("   b) Create single epic per major feature area")
        print("   c) Custom epic grouping")
        
        epic_strategy = input("Select (a/b/c) [a]: ").strip().lower() or 'a'
        pm_instructions["epic_strategy"] = epic_strategy
        
        # Story sizing preference
        print("\n2. Story Sizing Preference:")
        print("   a) Conservative (smaller stories, more granular)")
        print("   b) Standard (balanced approach)")
        print("   c) Aggressive (larger stories, less granular)")
        
        sizing_pref = input("Select (a/b/c) [b]: ").strip().lower() or 'b'
        pm_instructions["sizing_preference"] = sizing_pref
        
        # Target release
        target_release = input("\n3. Target Release [v1.0]: ").strip() or "v1.0"
        pm_instructions["target_release"] = target_release
        
        # Execute workflow
        print(f"\n🚀 Executing PM workflow...")
        result = self.process_design_document_to_features(selected_doc.id, pm_instructions)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
            
        # Display results
        print(f"\n✅ PM Workflow Complete!")
        print(f"📊 Summary:")
        print(f"   • Features: {result['summary']['total_features']}")
        print(f"   • Epics: {result['summary']['total_epics']}")
        print(f"   • Stories: {result['summary']['total_stories']}")
        print(f"   • Requirements Processed: {result['summary']['requirements_processed']}")
        
        print(f"\n📈 Story Points Distribution:")
        for range_key, count in result['summary']['effort_distribution'].items():
            print(f"   • {range_key} points: {count} stories")
            
        print(f"\n🎯 Priority Distribution:")
        for priority, count in result['summary']['priority_distribution'].items():
            print(f"   • {priority.title()}: {count} stories")
            
        print(f"\n🔗 Integration:")
        print(f"   • Features available in Feature Management System")
        print(f"   • Ready for GitHub Issues export")
        print(f"   • Visible in Dashboard at http://localhost:5003")
        
        # Offer next steps
        print(f"\n🚀 Next Steps:")
        print(f"   1. Review features at http://localhost:5004")
        print(f"   2. Refine stories and acceptance criteria")
        print(f"   3. Export to GitHub Issues for AI development team")
        print(f"   4. Monitor progress in main dashboard")

def main():
    """Main entry point for PM workflow system"""
    pm_workflow = PMWorkflowSystem()
    pm_workflow.interactive_pm_workflow()

if __name__ == "__main__":
    main()
