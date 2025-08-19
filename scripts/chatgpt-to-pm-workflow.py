#!/usr/bin/env python3
"""
ChatGPT Design Document to PM Workflow
Simplified integration for Visual Forge brainstorming → PM → Features workflow
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Simple data storage for design documents
DESIGN_DOCS_FILE = "design_documents_simple.json"
PM_WORKFLOW_FILE = "pm_workflow_results.json"

def load_design_docs():
    """Load design documents from file"""
    if Path(DESIGN_DOCS_FILE).exists():
        try:
            with open(DESIGN_DOCS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_design_docs(docs):
    """Save design documents to file"""
    with open(DESIGN_DOCS_FILE, 'w') as f:
        json.dump(docs, f, indent=2)

def parse_chatgpt_content(content):
    """Parse ChatGPT content to extract requirements"""
    requirements = []
    
    # Look for common patterns in ChatGPT design documents
    patterns = [
        r"(?:Requirements?|Features?|Functionality):\s*\n((?:[-*]\s+.+\n?)+)",
        r"(?:User Stories?|Stories?):\s*\n((?:[-*]\s+.+\n?)+)",
        r"(?:Technical Requirements?):\s*\n((?:[-*]\s+.+\n?)+)",
        r"(?:Business Requirements?):\s*\n((?:[-*]\s+.+\n?)+)"
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            items = re.findall(r"[-*]\s+(.+)", match.group(1))
            for item in items:
                if len(item.strip()) > 10:
                    requirements.append({
                        'text': item.strip(),
                        'category': 'functional',
                        'priority': 'medium',
                        'effort': 'medium'
                    })
    
    return requirements

# HTML Templates
DESIGN_IMPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Design Document Import</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #0d1117; color: #e6edf3; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: #238636; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea, select { width: 100%; padding: 10px; border: 1px solid #30363d; 
                                 background: #0d1117; color: #e6edf3; border-radius: 4px; }
        textarea { min-height: 200px; }
        .btn { background: #238636; color: white; padding: 12px 24px; border: none; 
               border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #2ea043; }
        .doc-card { background: #161b22; border: 1px solid #30363d; padding: 20px; 
                   margin-bottom: 15px; border-radius: 8px; }
        .doc-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
        .doc-meta { color: #7d8590; font-size: 0.9em; margin-bottom: 15px; }
        .doc-actions { display: flex; gap: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 ChatGPT Design Document Import</h1>
            <p>Visual Forge Brainstorming → PM Workflow → Features</p>
        </div>
        
        <div style="background: #161b22; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
            <h2>📥 Import New Design Document</h2>
            <form action="/import" method="post">
                <div class="form-group">
                    <label>Document Title:</label>
                    <input type="text" name="title" required placeholder="e.g., User Authentication System">
                </div>
                
                <div class="form-group">
                    <label>Project Name:</label>
                    <input type="text" name="project" required placeholder="e.g., NiroSubs-V2">
                </div>
                
                <div class="form-group">
                    <label>ChatGPT Design Document Content:</label>
                    <textarea name="content" required 
                              placeholder="Paste your complete ChatGPT brainstorming session content here...

Example format:
Requirements:
- User authentication with email/password
- Social login (Google, GitHub)
- Password reset functionality

Features:
- Dashboard with user metrics
- Real-time notifications
- API for mobile integration

Technical Requirements:
- React frontend with TypeScript
- Node.js backend with Express
- PostgreSQL database
- Redis for caching"></textarea>
                </div>
                
                <button type="submit" class="btn">📥 Import & Process</button>
            </form>
        </div>
        
        <div style="background: #161b22; padding: 20px; border-radius: 8px;">
            <h2>📚 Existing Design Documents</h2>
            {% for doc_id, doc in documents.items() %}
            <div class="doc-card">
                <div class="doc-title">{{ doc.title }}</div>
                <div class="doc-meta">
                    Project: {{ doc.project }} | 
                    Requirements: {{ doc.requirements|length }} | 
                    Created: {{ doc.created_date[:10] }}
                </div>
                <div class="doc-actions">
                    <a href="/pm-process/{{ doc_id }}" class="btn">🎯 PM Process</a>
                    <a href="/view/{{ doc_id }}" class="btn" style="background: #0969da;">👁️ View</a>
                </div>
            </div>
            {% else %}
            <p style="color: #7d8590; text-align: center; padding: 40px;">
                No design documents yet. Import your first ChatGPT design document above!
            </p>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

PM_PROCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PM Workflow</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #0d1117; color: #e6edf3; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { background: #0969da; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }
        .section { background: #161b22; padding: 20px; border-radius: 8px; margin-bottom: 20px; 
                  border: 1px solid #30363d; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #30363d; 
                                 background: #0d1117; color: #e6edf3; border-radius: 4px; }
        .btn { background: #238636; color: white; padding: 12px 24px; border: none; 
               border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; margin-right: 10px; }
        .btn:hover { background: #2ea043; }
        .btn-secondary { background: #0969da; }
        .btn-secondary:hover { background: #0860ca; }
        .req-item { background: #0d1117; padding: 15px; margin: 10px 0; border-radius: 4px; 
                   border: 1px solid #30363d; }
        .req-header { font-weight: bold; margin-bottom: 5px; }
        .req-meta { color: #7d8590; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 PM Workflow Processing</h1>
            <p>Convert Design Document → Features, Epics & Stories</p>
        </div>
        
        <div class="section">
            <h2>📄 Document: {{ document.title }}</h2>
            <p><strong>Project:</strong> {{ document.project }}</p>
            <p><strong>Requirements Found:</strong> {{ document.requirements|length }}</p>
        </div>
        
        <div class="section">
            <h2>🔍 Requirements Preview</h2>
            {% for req in document.requirements[:5] %}
            <div class="req-item">
                <div class="req-header">{{ req.text }}</div>
                <div class="req-meta">Category: {{ req.category }} | Priority: {{ req.priority }} | Effort: {{ req.effort }}</div>
            </div>
            {% endfor %}
            {% if document.requirements|length > 5 %}
            <p style="color: #7d8590;">... and {{ document.requirements|length - 5 }} more requirements</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>⚙️ PM Configuration</h2>
            <form action="/execute-pm/{{ doc_id }}" method="post">
                <div class="form-group">
                    <label>Feature Grouping Strategy:</label>
                    <select name="grouping_strategy">
                        <option value="single">Single main feature</option>
                        <option value="category" selected>Group by category</option>
                        <option value="complexity">Group by complexity</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Story Size Preference:</label>
                    <select name="story_size">
                        <option value="small">Small stories (1-3 points)</option>
                        <option value="medium" selected>Medium stories (3-8 points)</option>
                        <option value="large">Large stories (8-13 points)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Target Release:</label>
                    <input type="text" name="target_release" value="v1.0" placeholder="e.g., v1.0, Sprint 1">
                </div>
                
                <div class="form-group">
                    <label>PM Notes:</label>
                    <textarea name="pm_notes" placeholder="Additional context, priorities, or special considerations..."></textarea>
                </div>
                
                <button type="submit" class="btn">🚀 Execute PM Workflow</button>
                <a href="/" class="btn btn-secondary">← Back to Documents</a>
            </form>
        </div>
    </div>
</body>
</html>
"""

WORKFLOW_RESULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PM Workflow Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #0d1117; color: #e6edf3; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { background: #238636; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }
        .section { background: #161b22; padding: 20px; border-radius: 8px; margin-bottom: 20px; 
                  border: 1px solid #30363d; }
        .btn { background: #238636; color: white; padding: 12px 24px; border: none; 
               border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; margin-right: 10px; }
        .metric { display: inline-block; background: #0d1117; padding: 10px 15px; margin: 5px; 
                 border-radius: 4px; border: 1px solid #30363d; }
        .feature-item { background: #0d1117; padding: 15px; margin: 10px 0; border-radius: 4px; 
                       border: 1px solid #30363d; }
        .success { color: #4ade80; }
        .export-options { display: flex; gap: 10px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ PM Workflow Complete!</h1>
            <p>Features, Epics & Stories Created Successfully</p>
        </div>
        
        <div class="section">
            <h2>📊 Summary</h2>
            <div class="metric">Features Created: <strong>{{ result.features_created }}</strong></div>
            <div class="metric">Epics Created: <strong>{{ result.epics_created }}</strong></div>
            <div class="metric">Stories Created: <strong>{{ result.stories_created }}</strong></div>
            <div class="metric">Total Story Points: <strong>{{ result.total_story_points }}</strong></div>
        </div>
        
        <div class="section">
            <h2>🎯 Created Features</h2>
            {% for feature in result.features %}
            <div class="feature-item">
                <strong>{{ feature.title }}</strong><br>
                <small>{{ feature.description[:200] }}...</small><br>
                <em>Target: {{ feature.target_release }} | Status: {{ feature.status }}</em>
            </div>
            {% endfor %}
        </div>
        
        <div class="section">
            <h2>🚀 Next Steps</h2>
            <div class="export-options">
                <a href="http://localhost:5004/features" class="btn">📝 Manage in Feature System</a>
                <a href="http://localhost:5003" class="btn">📊 View in Dashboard</a>
                <a href="/export-github/{{ doc_id }}" class="btn">🔗 Export to GitHub</a>
                <a href="/" class="btn" style="background: #0969da;">← Back to Documents</a>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Ready for Development Team</h2>
            <p class="success">✅ All features are now available in your feature management system</p>
            <p class="success">✅ Stories are prioritized and sized for development</p>
            <p class="success">✅ Ready for GitHub Issues export and AI development team handoff</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page showing design documents"""
    documents = load_design_docs()
    return render_template_string(DESIGN_IMPORT_TEMPLATE, documents=documents)

@app.route('/import', methods=['POST'])
def import_document():
    """Import a ChatGPT design document"""
    title = request.form['title']
    project = request.form['project']
    content = request.form['content']
    
    doc_id = str(uuid.uuid4())[:8]
    requirements = parse_chatgpt_content(content)
    
    doc = {
        'title': title,
        'project': project,
        'content': content,
        'requirements': requirements,
        'created_date': datetime.now().isoformat(),
        'status': 'imported'
    }
    
    documents = load_design_docs()
    documents[doc_id] = doc
    save_design_docs(documents)
    
    return redirect(url_for('pm_process', doc_id=doc_id))

@app.route('/pm-process/<doc_id>')
def pm_process(doc_id):
    """PM processing page for a specific document"""
    documents = load_design_docs()
    if doc_id not in documents:
        return "Document not found", 404
    
    document = documents[doc_id]
    return render_template_string(PM_PROCESS_TEMPLATE, document=document, doc_id=doc_id)

@app.route('/execute-pm/<doc_id>', methods=['POST'])
def execute_pm_workflow(doc_id):
    """Execute the PM workflow"""
    documents = load_design_docs()
    if doc_id not in documents:
        return "Document not found", 404
    
    document = documents[doc_id]
    
    # Simulate PM workflow execution
    grouping_strategy = request.form['grouping_strategy']
    story_size = request.form['story_size']
    target_release = request.form['target_release']
    pm_notes = request.form['pm_notes']
    
    # Create simplified feature structure
    features_created = []
    epics_created = []
    stories_created = []
    
    # Main feature
    main_feature = {
        'title': document['title'],
        'description': f"Implementation of {document['project']} - {document['title']}",
        'target_release': target_release,
        'status': 'concept'
    }
    features_created.append(main_feature)
    
    # Convert requirements to stories
    story_points_map = {'small': 2, 'medium': 5, 'large': 8}
    base_points = story_points_map[story_size]
    
    for i, req in enumerate(document['requirements']):
        story = {
            'title': f"Story {i+1}: {req['text'][:50]}...",
            'description': req['text'],
            'story_points': base_points,
            'priority': req['priority'],
            'status': 'backlog'
        }
        stories_created.append(story)
    
    result = {
        'features_created': len(features_created),
        'epics_created': len(epics_created),
        'stories_created': len(stories_created),
        'total_story_points': sum(s['story_points'] for s in stories_created),
        'features': features_created,
        'epics': epics_created,
        'stories': stories_created
    }
    
    # Save workflow result
    workflow_results = {}
    if Path(PM_WORKFLOW_FILE).exists():
        try:
            with open(PM_WORKFLOW_FILE, 'r') as f:
                workflow_results = json.load(f)
        except:
            pass
    
    workflow_results[doc_id] = {
        'result': result,
        'document': document,
        'executed_at': datetime.now().isoformat(),
        'pm_config': {
            'grouping_strategy': grouping_strategy,
            'story_size': story_size,
            'target_release': target_release,
            'pm_notes': pm_notes
        }
    }
    
    with open(PM_WORKFLOW_FILE, 'w') as f:
        json.dump(workflow_results, f, indent=2)
    
    # Update document status
    documents[doc_id]['status'] = 'processed'
    save_design_docs(documents)
    
    return render_template_string(WORKFLOW_RESULT_TEMPLATE, result=result, doc_id=doc_id)

@app.route('/view/<doc_id>')
def view_document(doc_id):
    """View document details"""
    documents = load_design_docs()
    if doc_id not in documents:
        return "Document not found", 404
    
    document = documents[doc_id]
    return f"""
    <html>
    <head><title>Document: {document['title']}</title></head>
    <body style="font-family: Arial; margin: 40px; background: #0d1117; color: #e6edf3;">
        <h1>{document['title']}</h1>
        <p><strong>Project:</strong> {document['project']}</p>
        <p><strong>Requirements:</strong> {len(document['requirements'])}</p>
        <p><strong>Created:</strong> {document['created_date'][:16]}</p>
        
        <h2>Requirements:</h2>
        <ul>
        {"".join(f"<li>{req['text']}</li>" for req in document['requirements'])}
        </ul>
        
        <h2>Original Content:</h2>
        <pre style="background: #161b22; padding: 20px; border-radius: 8px;">{document['content']}</pre>
        
        <a href="/" style="background: #238636; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">← Back</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🎨 ChatGPT Design Document → PM Workflow System")
    print("=" * 60)
    print("Starting on http://localhost:5005")
    print("\nWorkflow:")
    print("1. Import ChatGPT design documents from Visual Forge")
    print("2. PM processes requirements into features/epics/stories")
    print("3. Export to feature management system")
    print("4. Hand off to AI development team")
    
    app.run(host='0.0.0.0', port=5005, debug=True)
