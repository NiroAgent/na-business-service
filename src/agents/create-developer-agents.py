#!/usr/bin/env python3
"""
Create Developer Agent Assignments
===================================
Creates actual development tasks for developer agents to implement
the features and fixes needed in the system.
"""

import subprocess
import json
from datetime import datetime

def create_developer_agent_tasks():
    """Create specific development tasks for developer agents"""
    
    developer_tasks = [
        {
            "title": "[Dev-1] Fix Tab System in Dashboard",
            "body": """## Developer Task: Fix Dashboard Tab System

### Problem
The dashboard tab system is not working - tabs don't switch properly and content doesn't load.

### Current Code Location
- File: `dashboard.html`
- Lines: 150-250 (tab switching logic)

### Required Fix
```javascript
// Current broken code
function switchTab(tabId) {
    // Not working properly
    document.getElementById(tabId).style.display = 'block';
}

// Should be:
function switchTab(tabId) {
    // Hide all tabs first
    const allTabs = document.querySelectorAll('.tab-content');
    allTabs.forEach(tab => tab.style.display = 'none');
    
    // Remove active class from all tab buttons
    const allButtons = document.querySelectorAll('.tab-button');
    allButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabId + '-content').style.display = 'block';
    document.getElementById(tabId + '-button').classList.add('active');
    
    // Save state to localStorage
    localStorage.setItem('activeTab', tabId);
}
```

### Testing Required
- Click each tab and verify content switches
- Refresh page and verify tab state persists
- Test on Chrome, Firefox, Safari, Edge

### Definition of Done
- [ ] All tabs switch correctly
- [ ] Active tab highlighted
- [ ] State persists on refresh
- [ ] No console errors
- [ ] Cross-browser compatible

**Assigned to**: Developer Agent 1
**Priority**: P0
**Estimate**: 2 hours""",
            "labels": ["bug", "dashboard", "frontend", "priority/P0"]
        },
        {
            "title": "[Dev-2] Implement Cost Monitoring API",
            "body": """## Developer Task: Build Cost Monitoring API

### Requirement
Create API endpoints to fetch and aggregate AWS cost data for the dashboard.

### Implementation Plan

#### 1. Create Cost Service
```python
# services/cost_monitor.py
import boto3
from datetime import datetime, timedelta

class CostMonitor:
    def __init__(self):
        self.ce_client = boto3.client('ce')  # Cost Explorer
        
    def get_daily_costs(self, days=7):
        end = datetime.now().date()
        start = end - timedelta(days=days)
        
        response = self.ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': str(start),
                'End': str(end)
            },
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )
        return self.format_costs(response)
    
    def get_service_breakdown(self):
        # Get costs by AWS service
        pass
    
    def get_cost_forecast(self):
        # Predict next month's costs
        pass
```

#### 2. Create API Endpoints
```python
# api/costs.py
from fastapi import APIRouter
from services.cost_monitor import CostMonitor

router = APIRouter()
monitor = CostMonitor()

@router.get("/api/costs/daily")
async def get_daily_costs(days: int = 7):
    return monitor.get_daily_costs(days)

@router.get("/api/costs/services")
async def get_service_costs():
    return monitor.get_service_breakdown()

@router.get("/api/costs/forecast")
async def get_forecast():
    return monitor.get_cost_forecast()
```

### Required Features
- Daily cost trends
- Service-level breakdown
- Cost forecasting
- Budget alerts
- Cost optimization recommendations

### Testing
- Mock AWS Cost Explorer responses
- Test data aggregation
- Verify API responses
- Load test with concurrent requests

### Definition of Done
- [ ] All endpoints implemented
- [ ] AWS integration working
- [ ] Data properly formatted for frontend
- [ ] Error handling implemented
- [ ] Tests passing
- [ ] Documentation updated

**Assigned to**: Developer Agent 2
**Priority**: P0
**Estimate**: 4 hours""",
            "labels": ["feature", "api", "backend", "cost-monitoring", "priority/P0"]
        },
        {
            "title": "[Dev-3] Implement Kill Switch Functionality",
            "body": """## Developer Task: Build Emergency Kill Switch System

### Requirement
Implement kill switch functionality to stop agents and services in emergency situations.

### Architecture
```
Frontend (Dashboard) -> API -> Agent Controller -> Agents/Services
                            -> AWS Lambda/ECS -> Terminate tasks
                            -> Audit Logger -> Store actions
```

### Implementation

#### 1. Backend Kill Switch Controller
```python
# services/kill_switch.py
import asyncio
import boto3
from typing import List, Dict
from datetime import datetime

class KillSwitchController:
    def __init__(self):
        self.ecs = boto3.client('ecs')
        self.lambda_client = boto3.client('lambda')
        self.active_agents = {}
        
    async def emergency_stop_all(self, reason: str, user: str):
        \"\"\"Master kill switch - stops everything\"\"\"
        
        # Log the action
        self.audit_log('EMERGENCY_STOP_ALL', user, reason)
        
        # Stop all ECS tasks
        tasks = await self.stop_all_ecs_tasks()
        
        # Disable all Lambda functions
        lambdas = await self.disable_all_lambdas()
        
        # Stop local agents
        agents = await self.stop_all_local_agents()
        
        return {
            'stopped_tasks': tasks,
            'disabled_lambdas': lambdas,
            'stopped_agents': agents,
            'timestamp': datetime.now().isoformat()
        }
    
    async def stop_specific_agent(self, agent_id: str, reason: str):
        \"\"\"Stop a specific agent\"\"\"
        # Implementation
        pass
    
    async def graceful_shutdown(self, service: str):
        \"\"\"Gracefully shut down a service\"\"\"
        # Allow current operations to complete
        # Then stop
        pass
```

#### 2. API Endpoints
```python
# api/kill_switch.py
from fastapi import APIRouter, HTTPException, Depends
from services.kill_switch import KillSwitchController

router = APIRouter()
controller = KillSwitchController()

@router.post("/api/kill/all")
async def emergency_stop_all(
    reason: str,
    confirmation: str,
    user: str = Depends(get_current_user)
):
    if confirmation != "CONFIRM_EMERGENCY_STOP":
        raise HTTPException(400, "Invalid confirmation")
    
    result = await controller.emergency_stop_all(reason, user)
    return result

@router.post("/api/kill/agent/{agent_id}")
async def stop_agent(agent_id: str, reason: str):
    return await controller.stop_specific_agent(agent_id, reason)
```

#### 3. Frontend Implementation
```javascript
// dashboard kill switch component
class KillSwitch {
    async emergencyStopAll() {
        const confirmed = await this.showConfirmDialog(
            'EMERGENCY STOP',
            'This will stop ALL agents and services. Are you sure?',
            'Type CONFIRM_EMERGENCY_STOP to proceed'
        );
        
        if (confirmed) {
            const response = await fetch('/api/kill/all', {
                method: 'POST',
                body: JSON.stringify({
                    reason: this.getReason(),
                    confirmation: 'CONFIRM_EMERGENCY_STOP'
                })
            });
            
            this.showResults(await response.json());
        }
    }
}
```

### Safety Features Required
- Two-factor confirmation
- Audit logging of all actions
- Gradual shutdown option
- Service dependency checking
- Rollback capability

### Testing
- Test kill switch on dev environment
- Verify audit logs created
- Test recovery procedures
- Load test under stress

### Definition of Done
- [ ] Master kill switch working
- [ ] Individual agent stops working  
- [ ] Confirmation dialogs implemented
- [ ] Audit logging functional
- [ ] Recovery procedures documented
- [ ] Tests passing

**Assigned to**: Developer Agent 3
**Priority**: P0
**Estimate**: 6 hours""",
            "labels": ["feature", "safety", "critical", "priority/P0"]
        },
        {
            "title": "[Dev-4] Fix Unicode Encoding Issues in Python Scripts",
            "body": """## Developer Task: Fix Unicode/Emoji Encoding Issues

### Problem
Windows cp1252 encoding causing failures when scripts contain emojis.

### Solution
Add proper encoding headers and environment variables to all Python scripts.

### Changes Required

#### 1. Add to all Python files:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"Module description\"\"\"

import sys
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

#### 2. Environment wrapper script:
```python
# run_with_encoding.py
import os
import sys
import subprocess

def run_with_utf8(script_path, args):
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['LANG'] = 'en_US.UTF-8'
    
    cmd = [sys.executable, script_path] + args
    
    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return result
```

#### 3. Replace emoji characters with text markers:
```python
# emoji_replacer.py
EMOJI_MAP = {
    '🚀': '[LAUNCH]',
    '✅': '[OK]',
    '❌': '[FAIL]',
    '🤖': '[ROBOT]',
    '📊': '[CHART]',
    '🎯': '[TARGET]',
    '⚠️': '[WARN]',
    '🔧': '[TOOL]'
}

def replace_emojis(text):
    for emoji, replacement in EMOJI_MAP.items():
        text = text.replace(emoji, replacement)
    return text
```

### Files to Update
- All agent Python files (14 files)
- All service scripts
- All monitoring scripts
- All test files

### Testing
- Run each script on Windows
- Verify no encoding errors
- Check output formatting
- Test with various locales

### Definition of Done
- [ ] All Python files updated
- [ ] No encoding errors on Windows
- [ ] Emoji replacements working
- [ ] Tests passing
- [ ] Documentation updated

**Assigned to**: Developer Agent 4
**Priority**: P0
**Estimate**: 3 hours""",
            "labels": ["bug", "encoding", "windows", "priority/P0"]
        },
        {
            "title": "[Dev-5] Complete Service Implementation for ns-auth",
            "body": """## Developer Task: Complete ns-auth Service (25% remaining)

### Current State
Service is 75% complete. Need to finish remaining features.

### Remaining Implementation

#### 1. Multi-Factor Authentication (MFA)
```python
# services/auth/mfa.py
import pyotp
import qrcode
from typing import Optional

class MFAService:
    def generate_secret(self, user_id: str) -> str:
        \"\"\"Generate TOTP secret for user\"\"\"
        secret = pyotp.random_base32()
        self.store_secret(user_id, secret)
        return secret
    
    def generate_qr_code(self, user_email: str, secret: str):
        \"\"\"Generate QR code for authenticator app\"\"\"
        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name='NiroSubs'
        )
        qr = qrcode.QRCode()
        qr.add_data(uri)
        return qr.make_image()
    
    def verify_token(self, user_id: str, token: str) -> bool:
        \"\"\"Verify TOTP token\"\"\"
        secret = self.get_secret(user_id)
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
```

#### 2. Session Management
```python
# services/auth/sessions.py
import redis
import uuid
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.redis = redis.Redis()
        self.session_ttl = 3600  # 1 hour
        
    def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user_id,
            'created': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat()
        }
        
        self.redis.setex(
            f'session:{session_id}',
            self.session_ttl,
            json.dumps(session_data)
        )
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[dict]:
        data = self.redis.get(f'session:{session_id}')
        if data:
            # Update last active time
            session = json.loads(data)
            session['last_active'] = datetime.now().isoformat()
            self.redis.setex(
                f'session:{session_id}',
                self.session_ttl,
                json.dumps(session)
            )
            return session
        return None
```

#### 3. Rate Limiting
```python
# services/auth/rate_limiter.py
class RateLimiter:
    def __init__(self):
        self.limits = {
            'login': (5, 300),  # 5 attempts per 5 minutes
            'register': (3, 3600),  # 3 per hour
            'password_reset': (3, 3600)  # 3 per hour
        }
    
    def check_rate_limit(self, action: str, identifier: str) -> bool:
        limit, window = self.limits.get(action, (10, 60))
        key = f'rate:{action}:{identifier}'
        
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, window)
        
        return current <= limit
```

### Testing Required
- MFA flow testing
- Session timeout testing
- Rate limit testing
- Security vulnerability scanning

### Definition of Done
- [ ] MFA fully implemented
- [ ] Session management working
- [ ] Rate limiting active
- [ ] All tests passing
- [ ] Security scan clean
- [ ] Deployed to dev environment

**Assigned to**: Developer Agent 5
**Priority**: P1
**Estimate**: 8 hours""",
            "labels": ["feature", "service", "authentication", "priority/P1"]
        }
    ]
    
    # Create issues
    repo = "NiroAgentV2/business-operations"
    created_issues = []
    
    print("\n" + "="*80)
    print("CREATING DEVELOPER AGENT TASKS")
    print("="*80)
    
    for task in developer_tasks:
        print(f"\nCreating: {task['title']}")
        
        cmd = [
            "gh", "issue", "create",
            "--repo", repo,
            "--title", task["title"],
            "--body", task["body"]
        ]
        
        for label in task.get("labels", []):
            cmd.extend(["--label", label])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                url = result.stdout.strip()
                created_issues.append(url)
                print(f"  [OK] Created: {url}")
            else:
                print(f"  [INFO] Issue may already exist")
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    return created_issues

def main():
    """Main entry point"""
    
    issues = create_developer_agent_tasks()
    
    print("\n" + "="*80)
    print("DEVELOPER AGENT TASKS CREATED")
    print("="*80)
    
    print(f"\n[CREATED] {len(issues)} development tasks")
    
    print("\n[DEVELOPER AGENTS SHOULD NOW:]")
    print("1. Fix dashboard tab system")
    print("2. Build cost monitoring API")
    print("3. Implement kill switch")
    print("4. Fix Unicode encoding issues")
    print("5. Complete ns-auth service")
    
    print("\n[WORK DISTRIBUTION:]")
    print("Dev Agent 1: Frontend fixes (Dashboard)")
    print("Dev Agent 2: Backend API (Cost monitoring)")
    print("Dev Agent 3: Critical systems (Kill switch)")
    print("Dev Agent 4: Cross-cutting concerns (Encoding)")
    print("Dev Agent 5: Service completion (ns-auth)")
    
    print("\n[PRIORITY:]")
    print("P0 Tasks: Dashboard, Costs, Kill Switch, Encoding")
    print("P1 Tasks: Service completion")
    
    print("\n[SUCCESS!]")
    print("Developer agents now have actual implementation work to do!")

if __name__ == "__main__":
    main()