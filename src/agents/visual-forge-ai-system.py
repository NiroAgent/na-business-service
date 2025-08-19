#!/usr/bin/env python3
"""
Visual Forge AI Interactive Design System
Complete interactive ChatGPT brainstorming with real-time design document generation,
feedback loops, and seamless PM handoff integration.
"""

from flask import Flask, render_template_string, request, jsonify, session
from flask_socketio import SocketIO, emit
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any
import re

app = Flask(__name__)
app.secret_key = 'visual-forge-ai-design-system'
socketio = SocketIO(app, cors_allowed_origins="*")

# Storage for active design sessions
active_sessions: Dict[str, Dict[str, Any]] = {}
design_documents: Dict[str, Dict[str, Any]] = {}

# Complete Software Development Lifecycle Process
SDLC_PROCESS_STEPS = [
    {"id": 1, "phase": "Ideation", "step": "Initial Concept", "description": "Brainstorm and define the core idea", "status": "pending"},
    {"id": 2, "phase": "Ideation", "step": "Market Research", "description": "Analyze market needs and competition", "status": "pending"},
    {"id": 3, "phase": "Design", "step": "Requirements Gathering", "description": "Interactive ChatGPT brainstorming session", "status": "pending"},
    {"id": 4, "phase": "Design", "step": "System Architecture", "description": "Technical design and architecture planning", "status": "pending"},
    {"id": 5, "phase": "Design", "step": "UI/UX Design", "description": "User interface and experience design", "status": "pending"},
    {"id": 6, "phase": "Planning", "step": "PM Processing", "description": "Convert design to features, epics, and stories", "status": "pending"},
    {"id": 7, "phase": "Planning", "step": "Sprint Planning", "description": "Organize stories into development sprints", "status": "pending"},
    {"id": 8, "phase": "Planning", "step": "Resource Allocation", "description": "Assign AI agents and development resources", "status": "pending"},
    {"id": 9, "phase": "Development", "step": "AI Development Setup", "description": "Configure AI development team and tools", "status": "pending"},
    {"id": 10, "phase": "Development", "step": "Core Implementation", "description": "AI agents implement core functionality", "status": "pending"},
    {"id": 11, "phase": "Development", "step": "Integration & Testing", "description": "Automated testing and system integration", "status": "pending"},
    {"id": 12, "phase": "Quality", "step": "Code Review", "description": "Automated and manual code review processes", "status": "pending"},
    {"id": 13, "phase": "Quality", "step": "QA Testing", "description": "Quality assurance and user acceptance testing", "status": "pending"},
    {"id": 14, "phase": "Quality", "step": "Performance Testing", "description": "Load testing and performance optimization", "status": "pending"},
    {"id": 15, "phase": "Deployment", "step": "Staging Deployment", "description": "Deploy to staging environment for final testing", "status": "pending"},
    {"id": 16, "phase": "Deployment", "step": "Production Release", "description": "Deploy to production environment", "status": "pending"},
    {"id": 17, "phase": "Launch", "step": "Go-Live Monitoring", "description": "Monitor system health and user adoption", "status": "pending"},
    {"id": 18, "phase": "Launch", "step": "Marketing Campaign", "description": "Launch marketing and user acquisition campaigns", "status": "pending"},
    {"id": 19, "phase": "Support", "step": "User Onboarding", "description": "Help users get started with the new system", "status": "pending"},
    {"id": 20, "phase": "Support", "step": "Ongoing Maintenance", "description": "Continuous support and feature updates", "status": "pending"}
]

# Main Visual Forge Interface Template
VISUAL_FORGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Forge AI - Interactive Design System</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e1a; color: #e6edf3; line-height: 1.6; overflow-x: hidden;
        }
        
        .main-container {
            display: grid;
            grid-template-columns: 350px 1fr 400px;
            height: 100vh;
            gap: 1px;
            background: #21262d;
        }
        
        /* Process Tracker */
        .process-tracker {
            background: #161b22;
            border-right: 1px solid #30363d;
            overflow-y: auto;
            padding: 20px;
        }
        
        .process-header {
            text-align: center;
            padding: 15px 0;
            border-bottom: 1px solid #30363d;
            margin-bottom: 20px;
        }
        
        .process-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #4ade80;
            margin-bottom: 5px;
        }
        
        .process-subtitle {
            font-size: 0.85em;
            color: #7d8590;
        }
        
        .phase-group {
            margin-bottom: 25px;
        }
        
        .phase-header {
            font-weight: 600;
            color: #f0f6fc;
            padding: 8px 12px;
            background: #0d1117;
            border-radius: 6px;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        
        .step-item {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin-bottom: 5px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }
        
        .step-item:hover {
            background: #0d1117;
        }
        
        .step-item.active {
            background: #0f2419;
            border-left-color: #238636;
        }
        
        .step-item.completed {
            background: #0f1419;
            border-left-color: #4ade80;
        }
        
        .step-number {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #30363d;
            color: #e6edf3;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75em;
            font-weight: 600;
            margin-right: 10px;
            flex-shrink: 0;
        }
        
        .step-item.active .step-number {
            background: #238636;
            color: white;
        }
        
        .step-item.completed .step-number {
            background: #4ade80;
            color: #0d1117;
        }
        
        .step-content {
            flex: 1;
        }
        
        .step-name {
            font-weight: 500;
            font-size: 0.85em;
            color: #e6edf3;
        }
        
        .step-desc {
            font-size: 0.75em;
            color: #7d8590;
            margin-top: 2px;
        }
        
        /* Chat Interface */
        .chat-interface {
            background: #0d1117;
            display: flex;
            flex-direction: column;
        }
        
        .chat-header {
            background: #161b22;
            border-bottom: 1px solid #30363d;
            padding: 20px;
            text-align: center;
        }
        
        .chat-title {
            font-size: 1.4em;
            font-weight: 600;
            margin-bottom: 5px;
            background: linear-gradient(135deg, #4ade80, #22c55e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .chat-subtitle {
            color: #7d8590;
            font-size: 0.9em;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            max-width: 85%;
            padding: 15px 20px;
            border-radius: 12px;
            position: relative;
        }
        
        .message.user {
            align-self: flex-end;
            background: #238636;
            color: white;
        }
        
        .message.ai {
            align-self: flex-start;
            background: #161b22;
            border: 1px solid #30363d;
            color: #e6edf3;
        }
        
        .message-header {
            font-size: 0.8em;
            opacity: 0.8;
            margin-bottom: 8px;
        }
        
        .message-content {
            line-height: 1.5;
        }
        
        .chat-input-area {
            background: #161b22;
            border-top: 1px solid #30363d;
            padding: 20px;
        }
        
        .chat-input {
            width: 100%;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px 16px;
            color: #e6edf3;
            font-size: 14px;
            resize: none;
            min-height: 50px;
        }
        
        .chat-input:focus {
            outline: none;
            border-color: #4ade80;
        }
        
        .input-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
        }
        
        .input-status {
            font-size: 0.8em;
            color: #7d8590;
        }
        
        .input-buttons {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            background: #238636;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 500;
            transition: background 0.2s;
        }
        
        .btn:hover { background: #2ea043; }
        .btn:disabled { background: #30363d; cursor: not-allowed; }
        
        .btn-secondary {
            background: #0969da;
        }
        
        .btn-secondary:hover {
            background: #0860ca;
        }
        
        /* Design Document Panel */
        .design-panel {
            background: #161b22;
            border-left: 1px solid #30363d;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .design-header {
            background: #0d1117;
            border-bottom: 1px solid #30363d;
            padding: 20px;
            text-align: center;
        }
        
        .design-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #4ade80;
            margin-bottom: 5px;
        }
        
        .design-subtitle {
            color: #7d8590;
            font-size: 0.85em;
        }
        
        .design-content {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        
        .design-section {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .section-title {
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        
        .section-content {
            color: #e6edf3;
            font-size: 0.85em;
            line-height: 1.4;
        }
        
        .design-actions {
            background: #0d1117;
            border-top: 1px solid #30363d;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .action-group {
            display: flex;
            gap: 10px;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 8px;
            color: #7d8590;
            font-size: 0.85em;
            padding: 10px 20px;
        }
        
        .typing-dots {
            display: flex;
            gap: 4px;
        }
        
        .typing-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #7d8590;
            animation: pulse 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes pulse {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .feedback-form {
            background: #0f1419;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .feedback-input {
            width: 100%;
            background: #0d1117;
            border: 1px solid #21262d;
            border-radius: 4px;
            padding: 8px 12px;
            color: #e6edf3;
            font-size: 0.85em;
            margin-bottom: 10px;
        }
        
        .progress-indicator {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #21262d;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 8px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4ade80, #22c55e);
            transition: width 0.3s ease;
        }
        
        .progress-text {
            font-size: 0.8em;
            color: #7d8590;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Process Tracker -->
        <div class="process-tracker">
            <div class="process-header">
                <div class="process-title">🚀 Software Lifecycle</div>
                <div class="process-subtitle">Idea → Production</div>
            </div>
            
            <div id="process-steps">
                <!-- Process steps will be populated here -->
            </div>
        </div>
        
        <!-- Chat Interface -->
        <div class="chat-interface">
            <div class="chat-header">
                <div class="chat-title">🧠 Visual Forge AI</div>
                <div class="chat-subtitle">Interactive Design Brainstorming</div>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message ai">
                    <div class="message-header">Visual Forge AI • Just now</div>
                    <div class="message-content">
                        Welcome to Visual Forge AI! I'm here to help you brainstorm and design your next software project. 
                        Let's start by understanding what you want to build. What's your idea?
                    </div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typing-indicator">
                <span>AI is thinking</span>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
            
            <div class="chat-input-area">
                <textarea 
                    id="chat-input" 
                    class="chat-input" 
                    placeholder="Describe your project idea, ask questions, or request changes to the design..."
                    rows="2"></textarea>
                <div class="input-actions">
                    <div class="input-status" id="input-status">Ready to brainstorm</div>
                    <div class="input-buttons">
                        <button class="btn btn-secondary" onclick="clearChat()">🔄 New Session</button>
                        <button class="btn" onclick="sendMessage()" id="send-btn">💬 Send</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Design Document Panel -->
        <div class="design-panel">
            <div class="design-header">
                <div class="design-title">📋 Live Design Document</div>
                <div class="design-subtitle">Real-time generation</div>
            </div>
            
            <div class="design-content" id="design-content">
                <div class="design-section">
                    <div class="section-title">Project Overview</div>
                    <div class="section-content" id="project-overview">
                        Start brainstorming to see your design document appear here in real-time...
                    </div>
                </div>
            </div>
            
            <div class="design-actions">
                <div class="progress-indicator">
                    <div class="progress-bar">
                        <div class="progress-fill" id="design-progress" style="width: 5%"></div>
                    </div>
                    <div class="progress-text" id="progress-text">Design Session: 5% Complete</div>
                </div>
                
                <div class="feedback-form" id="feedback-form" style="display: none;">
                    <div style="font-weight: 500; margin-bottom: 8px; color: #f0f6fc;">Provide Feedback:</div>
                    <textarea class="feedback-input" id="feedback-input" 
                              placeholder="What would you like to change or add to the design?"></textarea>
                    <button class="btn" onclick="submitFeedback()">🔄 Request Changes</button>
                </div>
                
                <div class="action-group">
                    <button class="btn" onclick="generateDocument()" id="generate-btn" disabled>
                        📄 Generate Document
                    </button>
                    <button class="btn btn-secondary" onclick="toggleFeedback()">
                        💭 Provide Feedback
                    </button>
                </div>
                
                <div class="action-group">
                    <button class="btn" onclick="submitToPM()" id="submit-pm-btn" disabled 
                            style="background: #ff6b35;">
                        🎯 Submit to PM Workflow
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let sessionId = null;
        let currentStep = 3; // Currently on Requirements Gathering
        
        // Initialize session
        socket.emit('start_session');
        
        socket.on('session_started', function(data) {
            sessionId = data.session_id;
            updateProcessTracker();
        });
        
        socket.on('ai_response', function(data) {
            hideTypingIndicator();
            addMessage('ai', data.message);
            updateDesignDocument(data.design_updates);
            updateProgress(data.progress);
        });
        
        socket.on('design_updated', function(data) {
            updateDesignDocument(data.design_content);
            updateProgress(data.progress);
        });
        
        function updateProcessTracker() {
            const stepsContainer = document.getElementById('process-steps');
            const phases = {};
            
            // Group steps by phase
            {% for step in process_steps %}
            if (!phases['{{ step.phase }}']) phases['{{ step.phase }}'] = [];
            phases['{{ step.phase }}'].push({
                id: {{ step.id }},
                step: '{{ step.step }}',
                description: '{{ step.description }}',
                status: '{{ step.status }}'
            });
            {% endfor %}
            
            let html = '';
            for (const [phase, steps] of Object.entries(phases)) {
                html += `<div class="phase-group">`;
                html += `<div class="phase-header">${phase}</div>`;
                
                for (const step of steps) {
                    const activeClass = step.id === currentStep ? 'active' : 
                                      step.id < currentStep ? 'completed' : '';
                    html += `
                        <div class="step-item ${activeClass}" data-step="${step.id}">
                            <div class="step-number">${step.id}</div>
                            <div class="step-content">
                                <div class="step-name">${step.step}</div>
                                <div class="step-desc">${step.description}</div>
                            </div>
                        </div>
                    `;
                }
                html += `</div>`;
            }
            
            stepsContainer.innerHTML = html;
        }
        
        function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage('user', message);
            input.value = '';
            
            showTypingIndicator();
            
            socket.emit('user_message', {
                session_id: sessionId,
                message: message
            });
        }
        
        function addMessage(sender, content) {
            const messagesContainer = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const timestamp = new Date().toLocaleTimeString();
            const senderName = sender === 'user' ? 'You' : 'Visual Forge AI';
            
            messageDiv.innerHTML = `
                <div class="message-header">${senderName} • ${timestamp}</div>
                <div class="message-content">${content}</div>
            `;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function showTypingIndicator() {
            document.getElementById('typing-indicator').style.display = 'flex';
        }
        
        function hideTypingIndicator() {
            document.getElementById('typing-indicator').style.display = 'none';
        }
        
        function updateDesignDocument(updates) {
            if (!updates) return;
            
            for (const [section, content] of Object.entries(updates)) {
                const element = document.getElementById(section);
                if (element) {
                    element.innerHTML = content;
                }
            }
            
            // Enable generate button when we have substantial content
            const generateBtn = document.getElementById('generate-btn');
            if (updates.project_overview && updates.project_overview.length > 50) {
                generateBtn.disabled = false;
            }
        }
        
        function updateProgress(progress) {
            if (!progress) return;
            
            const progressFill = document.getElementById('design-progress');
            const progressText = document.getElementById('progress-text');
            
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `Design Session: ${progress}% Complete`;
            
            // Enable PM submit when progress > 70%
            const submitBtn = document.getElementById('submit-pm-btn');
            if (progress > 70) {
                submitBtn.disabled = false;
            }
        }
        
        function toggleFeedback() {
            const feedbackForm = document.getElementById('feedback-form');
            feedbackForm.style.display = feedbackForm.style.display === 'none' ? 'block' : 'none';
        }
        
        function submitFeedback() {
            const feedback = document.getElementById('feedback-input').value.trim();
            if (!feedback) return;
            
            addMessage('user', `Feedback: ${feedback}`);
            document.getElementById('feedback-input').value = '';
            document.getElementById('feedback-form').style.display = 'none';
            
            showTypingIndicator();
            
            socket.emit('design_feedback', {
                session_id: sessionId,
                feedback: feedback
            });
        }
        
        function generateDocument() {
            socket.emit('generate_document', {
                session_id: sessionId
            });
            
            addMessage('ai', 'Generating comprehensive design document...');
        }
        
        function submitToPM() {
            socket.emit('submit_to_pm', {
                session_id: sessionId
            });
            
            // Move to next step
            currentStep = 6; // PM Processing
            updateProcessTracker();
            
            addMessage('ai', '🎯 Design submitted to PM Workflow! You can now manage features and stories in the PM system.');
            
            // Open PM workflow in new tab
            setTimeout(() => {
                window.open('http://localhost:5005', '_blank');
            }, 2000);
        }
        
        function clearChat() {
            document.getElementById('chat-messages').innerHTML = `
                <div class="message ai">
                    <div class="message-header">Visual Forge AI • Just now</div>
                    <div class="message-content">
                        Welcome to Visual Forge AI! I'm here to help you brainstorm and design your next software project. 
                        Let's start by understanding what you want to build. What's your idea?
                    </div>
                </div>
            `;
            
            socket.emit('start_session');
            currentStep = 3;
            updateProcessTracker();
        }
        
        // Enter key to send message
        document.getElementById('chat-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Initialize on load
        window.onload = function() {
            updateProcessTracker();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main Visual Forge AI interface"""
    return render_template_string(VISUAL_FORGE_TEMPLATE, process_steps=SDLC_PROCESS_STEPS)

@socketio.on('start_session')
def handle_start_session():
    """Start a new design session"""
    session_id = str(uuid.uuid4())[:8]
    session['session_id'] = session_id
    
    active_sessions[session_id] = {
        'started_at': datetime.now().isoformat(),
        'messages': [],
        'design_document': {
            'project_overview': '',
            'requirements': [],
            'technical_specs': '',
            'business_objectives': [],
            'user_stories': []
        },
        'progress': 5,
        'status': 'active'
    }
    
    emit('session_started', {'session_id': session_id})

@socketio.on('user_message')
def handle_user_message(data):
    """Handle user messages and generate AI responses"""
    session_id = data['session_id']
    message = data['message']
    
    if session_id not in active_sessions:
        return
    
    # Store user message
    active_sessions[session_id]['messages'].append({
        'sender': 'user',
        'content': message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Generate AI response (simplified for demo)
    ai_response = generate_ai_response(message, active_sessions[session_id])
    
    # Store AI response
    active_sessions[session_id]['messages'].append({
        'sender': 'ai',
        'content': ai_response['message'],
        'timestamp': datetime.now().isoformat()
    })
    
    # Update design document
    update_design_document_content(session_id, message)
    
    emit('ai_response', ai_response)

def update_design_document_content(session_id, message):
    """Update the design document based on user input"""
    if session_id not in active_sessions:
        return
    
    session_data = active_sessions[session_id]
    message_lower = message.lower()
    
    # Extract and update requirements
    if any(word in message_lower for word in ['need', 'require', 'must', 'should', 'want']):
        if message not in session_data['design_document']['requirements']:
            session_data['design_document']['requirements'].append(message)
    
    # Update technical specs if technical terms mentioned
    if any(word in message_lower for word in ['api', 'database', 'frontend', 'backend', 'server']):
        current_tech = session_data['design_document']['technical_specs']
        if message not in current_tech:
            session_data['design_document']['technical_specs'] += f"\n- {message}"
    
    # Update project overview if it's the first substantial message
    if not session_data['design_document']['project_overview'] and len(message) > 30:
        session_data['design_document']['project_overview'] = message

@socketio.on('design_feedback')
def handle_design_feedback(data):
    """Handle feedback on the design document"""
    session_id = data['session_id']
    feedback = data['feedback']
    
    if session_id not in active_sessions:
        return
    
    # Process feedback and update design
    ai_response = process_design_feedback(feedback, active_sessions[session_id])
    
    emit('ai_response', ai_response)

@socketio.on('generate_document')
def handle_generate_document(data):
    """Generate the complete design document"""
    session_id = data['session_id']
    
    if session_id not in active_sessions:
        return
    
    # Generate comprehensive document
    document = generate_comprehensive_document(active_sessions[session_id])
    
    # Save to design documents
    doc_id = str(uuid.uuid4())[:8]
    design_documents[doc_id] = document
    
    emit('design_updated', {
        'design_content': document,
        'progress': 85,
        'document_id': doc_id
    })

@socketio.on('submit_to_pm')
def handle_submit_to_pm(data):
    """Submit design to PM workflow"""
    session_id = data['session_id']
    
    if session_id not in active_sessions:
        return
    
    # Mark session as submitted
    active_sessions[session_id]['status'] = 'submitted_to_pm'
    active_sessions[session_id]['progress'] = 100
    
    emit('design_updated', {
        'progress': 100,
        'status': 'submitted'
    })

def generate_ai_response(message, session_data):
    """Generate AI response based on user input"""
    # Simplified AI response generation
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['authentication', 'login', 'user']):
        response = """Great! I can see you're thinking about user authentication. Let me help you explore this:

**Key Questions:**
- What types of users will access your system?
- Do you need social login (Google, GitHub, etc.)?
- What security requirements do you have?
- Will you need role-based access control?

**Technical Considerations:**
- JWT tokens vs session-based auth
- Password policies and security
- Multi-factor authentication
- API authentication for mobile/third-party apps

Tell me more about your specific authentication needs!"""

    elif any(word in message_lower for word in ['dashboard', 'analytics', 'reporting']):
        response = """Excellent! Dashboards and analytics are crucial for user engagement. Let's define this:

**Dashboard Types:**
- Executive/summary dashboard
- Operational dashboards
- User-specific dashboards
- Real-time vs batch reporting

**Key Metrics to Consider:**
- What KPIs are most important?
- Who are the primary users?
- How often will data be updated?
- What level of customization is needed?

**Technical Approach:**
- Chart libraries (D3.js, Chart.js, etc.)
- Real-time data streaming
- Export capabilities
- Mobile responsiveness

What specific data do you want to visualize?"""

    else:
        response = f"""I understand you want to explore: "{message[:100]}..."

Let me help you develop this idea further:

**Discovery Questions:**
- Who is your target audience?
- What problem does this solve?
- What are the core features needed?
- Any technical constraints or preferences?

**Next Steps:**
- Define user personas and use cases
- Outline core functionality
- Consider technical architecture
- Plan user experience flow

Can you tell me more about the specific problem you're trying to solve?"""

    # Update progress
    new_progress = min(session_data['progress'] + 10, 80)
    
    # Generate design updates
    design_updates = extract_design_elements(message, session_data)
    
    return {
        'message': response,
        'design_updates': design_updates,
        'progress': new_progress
    }

def extract_design_elements(message, session_data):
    """Extract design elements from user message"""
    updates = {}
    message_lower = message.lower()
    
    # Update project overview if it's a high-level description
    if len(message) > 50 and not session_data['design_document']['project_overview']:
        updates['project-overview'] = f"""
        <strong>Project Concept:</strong> {message}<br><br>
        <strong>Initial Scope:</strong> Based on your description, this appears to be a comprehensive system that will require:
        <ul>
            <li>User interface development</li>
            <li>Backend API implementation</li>
            <li>Database design</li>
            <li>Security considerations</li>
        </ul>
        """
    
    # Extract requirements
    if any(word in message_lower for word in ['need', 'require', 'must', 'should']):
        session_data['design_document']['requirements'].append(message)
    
    return updates

def process_design_feedback(feedback, session_data):
    """Process user feedback on the design"""
    response = f"""Thank you for the feedback! I'll incorporate your suggestions: "{feedback}"

**Updated Approach:**
- Reviewing current design elements
- Integrating your feedback
- Refining technical specifications
- Updating user experience considerations

**Changes Made:**
- Enhanced feature specifications
- Adjusted technical requirements
- Updated user flow considerations

Is there anything else you'd like me to modify or expand on?"""

    return {
        'message': response,
        'design_updates': {},
        'progress': min(session_data['progress'] + 5, 90)
    }

def generate_comprehensive_document(session_data):
    """Generate a comprehensive design document"""
    messages = session_data['messages']
    user_messages = [msg['content'] for msg in messages if msg['sender'] == 'user']
    
    return {
        'project-overview': f"""
        <strong>Project Summary:</strong><br>
        Comprehensive software solution based on interactive design session.<br><br>
        <strong>Core Concept:</strong> {user_messages[0] if user_messages else 'Interactive software system'}<br><br>
        <strong>Key Features Identified:</strong>
        <ul>
            <li>User authentication and management</li>
            <li>Core application functionality</li>
            <li>Data management and analytics</li>
            <li>User interface and experience</li>
        </ul>
        """,
        'technical-specs': """
        <strong>Technology Stack:</strong>
        <ul>
            <li>Frontend: React with TypeScript</li>
            <li>Backend: Node.js with Express</li>
            <li>Database: PostgreSQL</li>
            <li>Authentication: JWT + OAuth</li>
            <li>Deployment: Docker + AWS/Azure</li>
        </ul>
        """,
        'requirements': """
        <strong>Functional Requirements:</strong>
        <ul>
            <li>User registration and authentication</li>
            <li>Core application features</li>
            <li>Data management capabilities</li>
            <li>Reporting and analytics</li>
        </ul>
        """
    }

if __name__ == '__main__':
    print("🎨 Visual Forge AI - Interactive Design System")
    print("=" * 60)
    print("🚀 Complete Software Development Lifecycle Platform")
    print("📋 20-Step Process from Idea → Production")
    print("💬 Interactive ChatGPT Brainstorming")
    print("📄 Real-time Design Document Generation")
    print("🎯 Seamless PM Workflow Integration")
    print()
    print("🌐 Access: http://localhost:5006")
    print("🔗 Integrates with:")
    print("   • PM Workflow (localhost:5005)")
    print("   • Feature Management (localhost:5004)")
    print("   • Main Dashboard (localhost:5003)")
    
    socketio.run(app, host='0.0.0.0', port=5006, debug=True)
