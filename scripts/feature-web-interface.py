#!/usr/bin/env python3
"""
Feature Entry Web Interface
Web-based interface for creating and managing features, epics, and user stories
"""

import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, render_template_string
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from feature_management_system import feature_manager, Priority, FeatureStatus, StoryStatus, create_feature_set
except ImportError:
    print("Feature management system not available")
    feature_manager = None

app = Flask(__name__)

@app.route('/')
def index():
    """Main feature management dashboard"""
    if not feature_manager:
        return "Feature management system not available", 500
    
    features = list(feature_manager.features.values())
    epics = list(feature_manager.epics.values())
    stories = feature_manager.get_backlog()
    
    return render_template_string(FEATURE_DASHBOARD_TEMPLATE, 
                                features=features, epics=epics, stories=stories)

@app.route('/create_feature', methods=['GET', 'POST'])
def create_feature():
    """Create new feature form"""
    if request.method == 'POST':
        if not feature_manager:
            return jsonify({"error": "Feature management not available"}), 500
        
        try:
            feature_id = feature_manager.create_feature(
                title=request.form['title'],
                description=request.form['description'],
                business_justification=request.form['business_justification'],
                user_impact=request.form['user_impact'],
                owner=request.form.get('owner')
            )
            
            return redirect(url_for('feature_detail', feature_id=feature_id))
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    return render_template_string(CREATE_FEATURE_TEMPLATE)

@app.route('/feature/<feature_id>')
def feature_detail(feature_id):
    """Feature detail view with epics and stories"""
    if not feature_manager or feature_id not in feature_manager.features:
        return "Feature not found", 404
    
    feature = feature_manager.features[feature_id]
    progress = feature_manager.get_feature_progress(feature_id)
    
    # Get associated epics and stories
    epics = [feature_manager.epics[epic_id] for epic_id in feature.epics if epic_id in feature_manager.epics]
    stories = [feature_manager.user_stories[story_id] for story_id in feature.user_stories if story_id in feature_manager.user_stories]
    
    return render_template_string(FEATURE_DETAIL_TEMPLATE, 
                                feature=feature, epics=epics, stories=stories, progress=progress)

@app.route('/create_epic/<feature_id>', methods=['POST'])
def create_epic(feature_id):
    """Create epic for a feature"""
    if not feature_manager:
        return jsonify({"error": "Feature management not available"}), 500
    
    try:
        epic_id = feature_manager.create_epic(
            title=request.form['title'],
            description=request.form['description'],
            business_value=request.form['business_value'],
            feature_id=feature_id,
            owner=request.form.get('owner')
        )
        
        return redirect(url_for('feature_detail', feature_id=feature_id))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/create_story/<epic_id>', methods=['POST'])
def create_story(epic_id):
    """Create user story for an epic"""
    if not feature_manager:
        return jsonify({"error": "Feature management not available"}), 500
    
    try:
        # Get feature_id from epic
        epic = feature_manager.epics.get(epic_id)
        feature_id = None
        for fid, feature in feature_manager.features.items():
            if epic_id in feature.epics:
                feature_id = fid
                break
        
        story_id = feature_manager.create_user_story(
            title=request.form['title'],
            user_persona=request.form['user_persona'],
            user_want=request.form['user_want'],
            user_benefit=request.form['user_benefit'],
            epic_id=epic_id,
            feature_id=feature_id,
            story_points=int(request.form.get('story_points', 3))
        )
        
        # Add acceptance criteria if provided
        criteria_text = request.form.get('acceptance_criteria', '').strip()
        if criteria_text:
            for criteria in criteria_text.split('\n'):
                if criteria.strip():
                    feature_manager.add_acceptance_criteria(story_id, criteria.strip())
        
        return redirect(url_for('feature_detail', feature_id=feature_id))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/features')
def api_features():
    """API endpoint for features data"""
    if not feature_manager:
        return jsonify({"error": "Feature management not available"}), 500
    
    features_data = []
    for feature in feature_manager.features.values():
        feature_dict = {
            "id": feature.id,
            "title": feature.title,
            "description": feature.description,
            "status": feature.status.value,
            "priority": feature.priority.value,
            "progress": feature_manager.get_feature_progress(feature.id),
            "epics_count": len(feature.epics),
            "stories_count": len(feature.user_stories)
        }
        features_data.append(feature_dict)
    
    return jsonify(features_data)

@app.route('/api/backlog')
def api_backlog():
    """API endpoint for backlog data"""
    if not feature_manager:
        return jsonify({"error": "Feature management not available"}), 500
    
    backlog = feature_manager.get_backlog()
    backlog_data = []
    
    for story in backlog:
        story_dict = {
            "id": story.id,
            "title": story.title,
            "status": story.status.value,
            "priority": story.priority.value,
            "story_points": story.story_points,
            "assigned_to": story.assigned_to,
            "user_story": story.to_user_story_format(),
            "acceptance_criteria_count": len(story.acceptance_criteria)
        }
        backlog_data.append(story_dict)
    
    return jsonify(backlog_data)

@app.route('/quick_feature', methods=['POST'])
def quick_feature():
    """Quick feature creation from JSON"""
    if not feature_manager:
        return jsonify({"error": "Feature management not available"}), 500
    
    try:
        data = request.get_json()
        
        result = create_feature_set(
            data['title'],
            data['description'],
            data['business_justification'],
            data.get('epics', []),
            data.get('stories', [])
        )
        
        return jsonify({"success": True, "result": result})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# HTML Templates as strings (in production, use separate template files)

FEATURE_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Feature Management Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #0d1117; color: #e6edf3; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .btn { background: #238636; color: white; padding: 10px 20px; border: none; border-radius: 6px; text-decoration: none; display: inline-block; }
        .btn:hover { background: #2ea043; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .feature-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; }
        .feature-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; color: #4ade80; }
        .feature-status { padding: 4px 8px; border-radius: 12px; font-size: 0.8em; display: inline-block; }
        .status-concept { background: #656d76; }
        .status-planned { background: #0969da; }
        .status-in_development { background: #fb8500; }
        .status-ready_for_release { background: #238636; }
        .progress-bar { width: 100%; height: 6px; background: #30363d; border-radius: 3px; margin: 10px 0; }
        .progress-fill { height: 100%; background: #4ade80; border-radius: 3px; }
        .backlog { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; }
        .story-item { padding: 10px; border-bottom: 1px solid #21262d; }
        .story-title { font-weight: bold; color: #e6edf3; }
        .story-points { background: #0969da; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Feature Management Dashboard</h1>
        <a href="/create_feature" class="btn">+ Create Feature</a>
    </div>
    
    <h2>📋 Active Features</h2>
    <div class="features-grid">
        {% for feature in features %}
        <div class="feature-card">
            <div class="feature-title">
                <a href="/feature/{{ feature.id }}" style="color: inherit; text-decoration: none;">{{ feature.title }}</a>
            </div>
            <div class="feature-status status-{{ feature.status.value }}">{{ feature.status.value.replace('_', ' ').title() }}</div>
            <p>{{ feature.description[:100] }}{% if feature.description|length > 100 %}...{% endif %}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {{ (feature.user_stories|length / (feature.epics|length + 1) * 20) if feature.epics else 0 }}%"></div>
            </div>
            <small>{{ feature.epics|length }} epics, {{ feature.user_stories|length }} stories</small>
        </div>
        {% endfor %}
    </div>
    
    <h2>📚 Product Backlog</h2>
    <div class="backlog">
        {% for story in stories[:10] %}
        <div class="story-item">
            <div class="story-title">{{ story.title }} <span class="story-points">{{ story.story_points }}</span></div>
            <small>{{ story.to_user_story_format() }}</small>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

CREATE_FEATURE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Create Feature</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #0d1117; color: #e6edf3; }
        .form-container { max-width: 600px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 10px; border: 1px solid #30363d; border-radius: 4px; background: #0d1117; color: #e6edf3; font-family: inherit; }
        textarea { height: 100px; resize: vertical; }
        .btn { background: #238636; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; }
        .btn:hover { background: #2ea043; }
        .back-link { color: #4ade80; text-decoration: none; margin-bottom: 20px; display: inline-block; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Dashboard</a>
    
    <div class="form-container">
        <h1>Create New Feature</h1>
        
        <form method="POST">
            <div class="form-group">
                <label for="title">Feature Title*</label>
                <input type="text" id="title" name="title" required>
            </div>
            
            <div class="form-group">
                <label for="description">Description*</label>
                <textarea id="description" name="description" required placeholder="Detailed description of the feature"></textarea>
            </div>
            
            <div class="form-group">
                <label for="business_justification">Business Justification*</label>
                <textarea id="business_justification" name="business_justification" required placeholder="Why is this feature important? What business value does it provide?"></textarea>
            </div>
            
            <div class="form-group">
                <label for="user_impact">User Impact*</label>
                <textarea id="user_impact" name="user_impact" required placeholder="How will this feature impact users? What problems does it solve?"></textarea>
            </div>
            
            <div class="form-group">
                <label for="owner">Feature Owner</label>
                <input type="text" id="owner" name="owner" placeholder="Product Manager or Owner">
            </div>
            
            <button type="submit" class="btn">Create Feature</button>
        </form>
    </div>
</body>
</html>
'''

FEATURE_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ feature.title }} - Feature Detail</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #0d1117; color: #e6edf3; }
        .header { margin-bottom: 30px; }
        .feature-info { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 30px; }
        .progress-section { margin: 20px 0; }
        .progress-bar { width: 100%; height: 10px; background: #30363d; border-radius: 5px; }
        .progress-fill { height: 100%; background: #4ade80; border-radius: 5px; }
        .epics-section, .stories-section { margin-bottom: 30px; }
        .epic-card, .story-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .btn { background: #238636; color: white; padding: 8px 16px; border: none; border-radius: 4px; text-decoration: none; display: inline-block; margin-right: 10px; }
        .btn-secondary { background: #0969da; }
        .form-inline { display: inline-block; margin-left: 10px; }
        .form-inline input, .form-inline textarea { margin: 5px; padding: 5px; border: 1px solid #30363d; border-radius: 3px; background: #0d1117; color: #e6edf3; }
        .back-link { color: #4ade80; text-decoration: none; margin-bottom: 20px; display: inline-block; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Dashboard</a>
    
    <div class="header">
        <h1>{{ feature.title }}</h1>
        <div class="progress-section">
            <div class="progress-bar">
                <div class="progress-fill" style="width: {{ progress.progress }}%"></div>
            </div>
            <p>{{ progress.completed_stories }}/{{ progress.total_stories }} stories completed ({{ progress.progress }}%)</p>
        </div>
    </div>
    
    <div class="feature-info">
        <h3>Feature Information</h3>
        <p><strong>Description:</strong> {{ feature.description }}</p>
        <p><strong>Business Justification:</strong> {{ feature.business_justification }}</p>
        <p><strong>User Impact:</strong> {{ feature.user_impact }}</p>
        <p><strong>Status:</strong> {{ feature.status.value.replace('_', ' ').title() }}</p>
        {% if feature.owner %}<p><strong>Owner:</strong> {{ feature.owner }}</p>{% endif %}
    </div>
    
    <div class="epics-section">
        <h3>Epics</h3>
        <button onclick="toggleForm('epic-form')" class="btn">+ Add Epic</button>
        
        <div id="epic-form" style="display: none; margin: 15px 0; padding: 15px; background: #21262d; border-radius: 6px;">
            <form method="POST" action="/create_epic/{{ feature.id }}">
                <input type="text" name="title" placeholder="Epic Title" required style="width: 100%; margin-bottom: 10px; padding: 8px; border: 1px solid #30363d; border-radius: 4px; background: #0d1117; color: #e6edf3;">
                <textarea name="description" placeholder="Epic Description" required style="width: 100%; margin-bottom: 10px; padding: 8px; border: 1px solid #30363d; border-radius: 4px; background: #0d1117; color: #e6edf3; height: 60px;"></textarea>
                <textarea name="business_value" placeholder="Business Value" style="width: 100%; margin-bottom: 10px; padding: 8px; border: 1px solid #30363d; border-radius: 4px; background: #0d1117; color: #e6edf3; height: 40px;"></textarea>
                <input type="text" name="owner" placeholder="Epic Owner" style="width: 100%; margin-bottom: 10px; padding: 8px; border: 1px solid #30363d; border-radius: 4px; background: #0d1117; color: #e6edf3;">
                <button type="submit" class="btn">Create Epic</button>
                <button type="button" onclick="toggleForm('epic-form')" class="btn btn-secondary">Cancel</button>
            </form>
        </div>
        
        {% for epic in epics %}
        <div class="epic-card">
            <h4>{{ epic.title }}</h4>
            <p>{{ epic.description }}</p>
            {% if epic.business_value %}<p><strong>Business Value:</strong> {{ epic.business_value }}</p>{% endif %}
            
            <button onclick="toggleForm('story-form-{{ epic.id }}')" class="btn btn-secondary">+ Add Story</button>
            
            <div id="story-form-{{ epic.id }}" style="display: none; margin-top: 15px; padding: 15px; background: #30363d; border-radius: 6px;">
                <form method="POST" action="/create_story/{{ epic.id }}">
                    <input type="text" name="title" placeholder="Story Title" required style="width: 100%; margin-bottom: 8px; padding: 6px; border: 1px solid #30363d; border-radius: 3px; background: #0d1117; color: #e6edf3;">
                    <input type="text" name="user_persona" placeholder="User Persona (e.g., 'customer', 'admin')" required style="width: 100%; margin-bottom: 8px; padding: 6px; border: 1px solid #30363d; border-radius: 3px; background: #0d1117; color: #e6edf3;">
                    <input type="text" name="user_want" placeholder="What the user wants" required style="width: 100%; margin-bottom: 8px; padding: 6px; border: 1px solid #30363d; border-radius: 3px; background: #0d1117; color: #e6edf3;">
                    <input type="text" name="user_benefit" placeholder="Benefit to the user" required style="width: 100%; margin-bottom: 8px; padding: 6px; border: 1px solid #30363d; border-radius: 3px; background: #0d1117; color: #e6edf3;">
                    <input type="number" name="story_points" placeholder="Story Points" value="3" min="1" max="13" style="width: 100px; margin-bottom: 8px; padding: 6px; border: 1px solid #30363d; border-radius: 3px; background: #0d1117; color: #e6edf3;">
                    <textarea name="acceptance_criteria" placeholder="Acceptance Criteria (one per line)" style="width: 100%; margin-bottom: 8px; padding: 6px; border: 1px solid #30363d; border-radius: 3px; background: #0d1117; color: #e6edf3; height: 60px;"></textarea>
                    <button type="submit" class="btn">Create Story</button>
                    <button type="button" onclick="toggleForm('story-form-{{ epic.id }}')" class="btn btn-secondary">Cancel</button>
                </form>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="stories-section">
        <h3>User Stories</h3>
        {% for story in stories %}
        <div class="story-card">
            <h4>{{ story.title }} <span style="background: #0969da; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8em;">{{ story.story_points }}</span></h4>
            <p><em>{{ story.to_user_story_format() }}</em></p>
            <p><strong>Status:</strong> {{ story.status.value.replace('_', ' ').title() }}</p>
            {% if story.assigned_to %}<p><strong>Assigned to:</strong> {{ story.assigned_to }}</p>{% endif %}
            {% if story.acceptance_criteria %}
            <details>
                <summary><strong>Acceptance Criteria ({{ story.acceptance_criteria|length }})</strong></summary>
                <ul>
                {% for criteria in story.acceptance_criteria %}
                    <li>{{ criteria.description }}</li>
                {% endfor %}
                </ul>
            </details>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    <script>
        function toggleForm(formId) {
            const form = document.getElementById(formId);
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Feature Management Web Interface")
    print("=" * 50)
    print("📊 URL: http://localhost:5004")
    print("✨ Create and manage features, epics, and user stories")
    print("🔗 Integrates with GitHub issue creation")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5004, debug=False)
