#!/usr/bin/env python3
"""
Feature Management System for AI Development Team
Manages features, epics, user stories, and acceptance criteria
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum

class FeatureStatus(Enum):
    CONCEPT = "concept"
    PLANNED = "planned"
    IN_DEVELOPMENT = "in_development"
    IN_TESTING = "in_testing"
    READY_FOR_RELEASE = "ready_for_release"
    RELEASED = "released"
    DEPRECATED = "deprecated"

class StoryStatus(Enum):
    BACKLOG = "backlog"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    TESTING = "testing"
    DONE = "done"
    BLOCKED = "blocked"

class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    NICE_TO_HAVE = 5

@dataclass
class AcceptanceCriteria:
    id: str
    description: str
    test_scenarios: List[str] = field(default_factory=list)
    completed: bool = False
    tested_by: Optional[str] = None
    test_date: Optional[datetime] = None

@dataclass
class UserStory:
    id: str
    title: str
    description: str
    user_persona: str  # "As a [user type]"
    user_want: str     # "I want [functionality]"
    user_benefit: str  # "So that [benefit]"
    acceptance_criteria: List[AcceptanceCriteria] = field(default_factory=list)
    story_points: int = 3
    priority: Priority = Priority.MEDIUM
    status: StoryStatus = StoryStatus.BACKLOG
    assigned_to: Optional[str] = None
    sprint: Optional[str] = None
    epic_id: Optional[str] = None
    feature_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    github_issues: List[str] = field(default_factory=list)
    
    def to_user_story_format(self) -> str:
        """Generate standard user story format"""
        return f"As a {self.user_persona}, I want {self.user_want} so that {self.user_benefit}."
    
    def add_acceptance_criteria(self, description: str, test_scenarios: List[str] = None) -> str:
        """Add acceptance criteria to the story"""
        criteria_id = f"AC_{self.id}_{len(self.acceptance_criteria) + 1}"
        criteria = AcceptanceCriteria(
            id=criteria_id,
            description=description,
            test_scenarios=test_scenarios or []
        )
        self.acceptance_criteria.append(criteria)
        self.updated_at = datetime.now()
        return criteria_id

@dataclass
class Epic:
    id: str
    title: str
    description: str
    business_value: str
    success_metrics: List[str] = field(default_factory=list)
    user_stories: List[str] = field(default_factory=list)  # Story IDs
    target_release: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: FeatureStatus = FeatureStatus.CONCEPT
    owner: Optional[str] = None
    stakeholders: List[str] = field(default_factory=list)
    estimated_effort: int = 0  # Total story points
    actual_effort: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None

@dataclass
class Feature:
    id: str
    title: str
    description: str
    business_justification: str
    user_impact: str
    technical_requirements: List[str] = field(default_factory=list)
    epics: List[str] = field(default_factory=list)  # Epic IDs
    user_stories: List[str] = field(default_factory=list)  # Story IDs
    status: FeatureStatus = FeatureStatus.CONCEPT
    priority: Priority = Priority.MEDIUM
    owner: Optional[str] = None
    stakeholders: List[str] = field(default_factory=list)
    target_release: Optional[str] = None
    estimated_effort: int = 0
    actual_effort: int = 0
    success_metrics: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    approved_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    release_date: Optional[datetime] = None

class FeatureManager:
    def __init__(self, data_file: str = "features_data.json"):
        self.data_file = data_file
        self.features: Dict[str, Feature] = {}
        self.epics: Dict[str, Epic] = {}
        self.user_stories: Dict[str, UserStory] = {}
        self.load_data()
    
    def load_data(self):
        """Load features, epics, and stories from file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                
                # Load features
                for feature_data in data.get('features', []):
                    feature = Feature(**self._convert_dates(feature_data))
                    self.features[feature.id] = feature
                
                # Load epics
                for epic_data in data.get('epics', []):
                    epic = Epic(**self._convert_dates(epic_data))
                    self.epics[epic.id] = epic
                
                # Load user stories
                for story_data in data.get('user_stories', []):
                    # Convert acceptance criteria
                    if 'acceptance_criteria' in story_data:
                        story_data['acceptance_criteria'] = [
                            AcceptanceCriteria(**self._convert_dates(ac))
                            for ac in story_data['acceptance_criteria']
                        ]
                    story = UserStory(**self._convert_dates(story_data))
                    self.user_stories[story.id] = story
                    
        except FileNotFoundError:
            # Start with empty data
            pass
        except Exception as e:
            print(f"Error loading feature data: {e}")
    
    def save_data(self):
        """Save all data to file"""
        try:
            data = {
                'features': [self._convert_dates_for_json(asdict(f)) for f in self.features.values()],
                'epics': [self._convert_dates_for_json(asdict(e)) for e in self.epics.values()],
                'user_stories': [self._convert_dates_for_json(asdict(s)) for s in self.user_stories.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving feature data: {e}")
    
    def _convert_dates(self, data: Dict) -> Dict:
        """Convert ISO date strings to datetime objects"""
        date_fields = ['created_at', 'updated_at', 'completed_at', 'approved_date', 
                      'start_date', 'target_date', 'completion_date', 'release_date', 'test_date']
        
        for field in date_fields:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    try:
                        data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    except:
                        data[field] = None
        
        return data
    
    def _convert_dates_for_json(self, data: Dict) -> Dict:
        """Convert datetime objects to ISO strings for JSON"""
        date_fields = ['created_at', 'updated_at', 'completed_at', 'approved_date',
                      'start_date', 'target_date', 'completion_date', 'release_date', 'test_date']
        
        for field in date_fields:
            if field in data and data[field]:
                if isinstance(data[field], datetime):
                    data[field] = data[field].isoformat()
        
        return data
    
    def create_feature(self, title: str, description: str, business_justification: str, 
                      user_impact: str, owner: str = None) -> str:
        """Create a new feature"""
        feature_id = f"FEAT_{int(time.time())}_{len(self.features) + 1}"
        
        feature = Feature(
            id=feature_id,
            title=title,
            description=description,
            business_justification=business_justification,
            user_impact=user_impact,
            owner=owner
        )
        
        self.features[feature_id] = feature
        self.save_data()
        return feature_id
    
    def create_epic(self, title: str, description: str, business_value: str, 
                   feature_id: str = None, owner: str = None) -> str:
        """Create a new epic"""
        epic_id = f"EPIC_{int(time.time())}_{len(self.epics) + 1}"
        
        epic = Epic(
            id=epic_id,
            title=title,
            description=description,
            business_value=business_value,
            owner=owner
        )
        
        self.epics[epic_id] = epic
        
        # Link to feature if provided
        if feature_id and feature_id in self.features:
            self.features[feature_id].epics.append(epic_id)
            self.features[feature_id].updated_at = datetime.now()
        
        self.save_data()
        return epic_id
    
    def create_user_story(self, title: str, user_persona: str, user_want: str, 
                         user_benefit: str, epic_id: str = None, feature_id: str = None,
                         story_points: int = 3) -> str:
        """Create a new user story"""
        story_id = f"US_{int(time.time())}_{len(self.user_stories) + 1}"
        
        story = UserStory(
            id=story_id,
            title=title,
            description=f"As a {user_persona}, I want {user_want} so that {user_benefit}.",
            user_persona=user_persona,
            user_want=user_want,
            user_benefit=user_benefit,
            story_points=story_points,
            epic_id=epic_id,
            feature_id=feature_id
        )
        
        self.user_stories[story_id] = story
        
        # Link to epic and feature
        if epic_id and epic_id in self.epics:
            self.epics[epic_id].user_stories.append(story_id)
            self.epics[epic_id].updated_at = datetime.now()
        
        if feature_id and feature_id in self.features:
            self.features[feature_id].user_stories.append(story_id)
            self.features[feature_id].updated_at = datetime.now()
        
        self.save_data()
        return story_id
    
    def add_acceptance_criteria(self, story_id: str, description: str, 
                              test_scenarios: List[str] = None) -> str:
        """Add acceptance criteria to a user story"""
        if story_id not in self.user_stories:
            raise ValueError(f"User story {story_id} not found")
        
        criteria_id = self.user_stories[story_id].add_acceptance_criteria(description, test_scenarios)
        self.save_data()
        return criteria_id
    
    def update_story_status(self, story_id: str, status: StoryStatus, assigned_to: str = None):
        """Update user story status"""
        if story_id not in self.user_stories:
            raise ValueError(f"User story {story_id} not found")
        
        story = self.user_stories[story_id]
        story.status = status
        story.updated_at = datetime.now()
        
        if assigned_to:
            story.assigned_to = assigned_to
        
        if status == StoryStatus.DONE:
            story.completed_at = datetime.now()
        
        self.save_data()
    
    def get_feature_progress(self, feature_id: str) -> Dict:
        """Get progress summary for a feature"""
        if feature_id not in self.features:
            return {}
        
        feature = self.features[feature_id]
        total_stories = len(feature.user_stories)
        
        if total_stories == 0:
            return {"progress": 0, "total_stories": 0, "completed_stories": 0}
        
        completed_stories = sum(
            1 for story_id in feature.user_stories
            if story_id in self.user_stories and self.user_stories[story_id].status == StoryStatus.DONE
        )
        
        progress = (completed_stories / total_stories) * 100
        
        return {
            "progress": round(progress, 1),
            "total_stories": total_stories,
            "completed_stories": completed_stories,
            "in_progress": sum(
                1 for story_id in feature.user_stories
                if story_id in self.user_stories and self.user_stories[story_id].status == StoryStatus.IN_PROGRESS
            ),
            "total_story_points": sum(
                self.user_stories[story_id].story_points
                for story_id in feature.user_stories
                if story_id in self.user_stories
            )
        }
    
    def get_backlog(self, status_filter: StoryStatus = None) -> List[UserStory]:
        """Get prioritized backlog of user stories"""
        stories = list(self.user_stories.values())
        
        if status_filter:
            stories = [s for s in stories if s.status == status_filter]
        
        # Sort by priority then by creation date
        stories.sort(key=lambda s: (s.priority.value, s.created_at))
        
        return stories
    
    def get_sprint_stories(self, sprint_name: str) -> List[UserStory]:
        """Get all stories for a specific sprint"""
        return [
            story for story in self.user_stories.values()
            if story.sprint == sprint_name
        ]
    
    def export_for_github(self, feature_id: str) -> Dict:
        """Export feature data for GitHub issue creation"""
        if feature_id not in self.features:
            return {}
        
        feature = self.features[feature_id]
        
        export_data = {
            "feature": asdict(feature),
            "epics": [asdict(self.epics[epic_id]) for epic_id in feature.epics if epic_id in self.epics],
            "user_stories": []
        }
        
        for story_id in feature.user_stories:
            if story_id in self.user_stories:
                story_data = asdict(self.user_stories[story_id])
                # Convert to GitHub issue format
                story_data["github_title"] = story_data["title"]
                story_data["github_body"] = self._format_story_for_github(self.user_stories[story_id])
                export_data["user_stories"].append(story_data)
        
        return export_data
    
    def _format_story_for_github(self, story: UserStory) -> str:
        """Format user story for GitHub issue body"""
        body = f"""## User Story
{story.to_user_story_format()}

## Description
{story.description}

## Acceptance Criteria
"""
        for i, criteria in enumerate(story.acceptance_criteria, 1):
            body += f"\n{i}. {criteria.description}"
            if criteria.test_scenarios:
                body += "\n   **Test Scenarios:**"
                for scenario in criteria.test_scenarios:
                    body += f"\n   - {scenario}"
        
        body += f"\n\n## Story Points: {story.story_points}"
        
        if story.dependencies:
            body += f"\n\n## Dependencies\n"
            for dep in story.dependencies:
                body += f"- {dep}\n"
        
        return body

# Global feature manager instance
feature_manager = FeatureManager()

# Convenience functions for common operations
def create_feature_set(feature_title: str, feature_description: str, business_justification: str,
                      epics_data: List[Dict], stories_data: List[Dict]) -> Dict:
    """Create a complete feature with epics and stories"""
    
    # Create feature
    feature_id = feature_manager.create_feature(
        feature_title, feature_description, business_justification, 
        "Improves user experience and business value"
    )
    
    epic_ids = []
    story_ids = []
    
    # Create epics
    for epic_data in epics_data:
        epic_id = feature_manager.create_epic(
            epic_data["title"],
            epic_data["description"], 
            epic_data.get("business_value", ""),
            feature_id
        )
        epic_ids.append(epic_id)
        
        # Create stories for this epic
        for story_data in epic_data.get("stories", []):
            story_id = feature_manager.create_user_story(
                story_data["title"],
                story_data["user_persona"],
                story_data["user_want"],
                story_data["user_benefit"],
                epic_id,
                feature_id,
                story_data.get("story_points", 3)
            )
            story_ids.append(story_id)
            
            # Add acceptance criteria
            for criteria in story_data.get("acceptance_criteria", []):
                feature_manager.add_acceptance_criteria(
                    story_id, 
                    criteria["description"],
                    criteria.get("test_scenarios", [])
                )
    
    return {
        "feature_id": feature_id,
        "epic_ids": epic_ids,
        "story_ids": story_ids
    }

if __name__ == "__main__":
    # Example usage
    fm = FeatureManager()
    
    # Create a sample feature
    feature_data = {
        "title": "User Authentication System",
        "description": "Complete user authentication and authorization system",
        "business_justification": "Required for user security and personalization",
        "epics": [
            {
                "title": "User Registration",
                "description": "Allow new users to create accounts",
                "business_value": "Increase user base",
                "stories": [
                    {
                        "title": "User can register with email",
                        "user_persona": "new user",
                        "user_want": "to register with my email address",
                        "user_benefit": "I can create an account quickly",
                        "story_points": 5,
                        "acceptance_criteria": [
                            {
                                "description": "User can enter email and password",
                                "test_scenarios": ["Valid email format", "Password strength validation"]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    result = create_feature_set(
        feature_data["title"],
        feature_data["description"],
        feature_data["business_justification"],
        feature_data["epics"],
        []
    )
    
    print(f"Created feature set: {result}")
    
    # Show backlog
    backlog = fm.get_backlog()
    print(f"Current backlog has {len(backlog)} stories")
