#!/usr/bin/env python3
"""
Create QA/Tester Agent Assignments
===================================
Creates testing tasks for QA agents to test existing functionality
since most services are already 75% developed.
"""

import subprocess
import json
from datetime import datetime

def create_qa_tester_tasks():
    """Create comprehensive testing tasks for QA agents"""
    
    qa_tasks = [
        {
            "title": "[QA-1] Test All NiroSubs Authentication Service (ns-auth)",
            "body": """## QA Task: Comprehensive Testing of ns-auth Service

### Service Status
- Development: 75% complete
- Deployment: Ready for testing
- Environment: vf-dev

### Test Scope

#### 1. Functional Testing
```yaml
test_suite: Authentication
test_cases:
  - login_valid_credentials:
      input: {email: "test@example.com", password: "Test123!"}
      expected: {status: 200, token: present, user: object}
      
  - login_invalid_credentials:
      input: {email: "test@example.com", password: "wrong"}
      expected: {status: 401, error: "Invalid credentials"}
      
  - register_new_user:
      input: {email: "new@example.com", password: "Pass123!", name: "Test User"}
      expected: {status: 201, user_id: present}
      
  - password_reset_flow:
      steps:
        - Request reset token
        - Verify email sent
        - Use token to reset
        - Login with new password
      
  - session_management:
      tests:
        - Session creation
        - Session validation
        - Session timeout (1 hour)
        - Session refresh
        - Logout
```

#### 2. Security Testing
```python
# security_tests.py
def test_sql_injection():
    payloads = [
        "' OR '1'='1",
        "admin'--",
        "1; DROP TABLE users--"
    ]
    for payload in payloads:
        response = login(email=payload, password=payload)
        assert response.status != 200, f"SQL injection vulnerability: {payload}"

def test_brute_force_protection():
    # Try 10 rapid login attempts
    for i in range(10):
        response = login(email="test@example.com", password="wrong")
    
    # Should be rate limited after 5 attempts
    assert response.status == 429, "No rate limiting detected"

def test_jwt_token_security():
    token = login_and_get_token()
    # Try to decode without secret
    # Try to modify payload
    # Try expired token
    # Try token from different user
```

#### 3. Performance Testing
```javascript
// k6 load test
import http from 'k6/http';
import { check } from 'k6';

export let options = {
    stages: [
        { duration: '2m', target: 100 }, // Ramp up
        { duration: '5m', target: 100 }, // Stay at 100 users
        { duration: '2m', target: 0 },   // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
        http_req_failed: ['rate<0.1'],    // Error rate under 10%
    },
};

export default function() {
    let response = http.post('https://vf-dev/api/auth/login', {
        email: 'test@example.com',
        password: 'Test123!'
    });
    
    check(response, {
        'status is 200': (r) => r.status === 200,
        'token present': (r) => r.json('token') !== null,
    });
}
```

#### 4. Integration Testing
- Database connectivity
- Redis session storage
- Email service (password reset)
- Rate limiter (Redis)
- JWT token validation

### Test Data Required
```json
{
    "test_users": [
        {"email": "admin@test.com", "role": "admin"},
        {"email": "user@test.com", "role": "user"},
        {"email": "blocked@test.com", "status": "blocked"}
    ],
    "test_passwords": {
        "valid": "Test123!",
        "weak": "123",
        "expired": "OldPass1!"
    }
}
```

### Bug Report Template
```markdown
**Bug ID**: AUTH-001
**Severity**: High/Medium/Low
**Component**: Login/Register/Session/etc
**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
**Expected**: [What should happen]
**Actual**: [What actually happened]
**Environment**: vf-dev
**Screenshots/Logs**: [Attached]
```

### Test Execution Plan
1. **Day 1**: Functional testing (all endpoints)
2. **Day 2**: Security testing
3. **Day 3**: Performance testing
4. **Day 4**: Integration testing
5. **Day 5**: Bug verification and retest

### Definition of Done
- [ ] All test cases executed
- [ ] Test report generated
- [ ] Bugs logged in GitHub
- [ ] Security vulnerabilities documented
- [ ] Performance benchmarks recorded
- [ ] Test automation scripts created

**Assigned to**: QA Agent 1
**Priority**: P0
**Estimate**: 5 days""",
            "labels": ["testing", "qa", "ns-auth", "priority/P0"]
        },
        {
            "title": "[QA-2] Test Dashboard UI Across All Browsers and Devices",
            "body": """## QA Task: Cross-Browser and Responsive Testing for Dashboard

### Current State
Dashboard is built but has known issues with tab system and missing features.

### Test Scope

#### 1. Browser Compatibility Matrix
| Feature | Chrome | Firefox | Safari | Edge | Mobile Chrome | Mobile Safari |
|---------|---------|----------|---------|-------|----------------|---------------|
| Tab System | TEST | TEST | TEST | TEST | TEST | TEST |
| Real-time Updates | TEST | TEST | TEST | TEST | TEST | TEST |
| Charts/Graphs | TEST | TEST | TEST | TEST | TEST | TEST |
| WebSocket Connection | TEST | TEST | TEST | TEST | TEST | TEST |
| Local Storage | TEST | TEST | TEST | TEST | TEST | TEST |

#### 2. Responsive Design Testing
```javascript
// Viewport sizes to test
const viewports = [
    { name: 'Mobile S', width: 320, height: 568 },
    { name: 'Mobile M', width: 375, height: 667 },
    { name: 'Mobile L', width: 425, height: 812 },
    { name: 'Tablet', width: 768, height: 1024 },
    { name: 'Laptop', width: 1024, height: 768 },
    { name: 'Desktop', width: 1440, height: 900 },
    { name: '4K', width: 2560, height: 1440 }
];
```

#### 3. Functional Testing
```yaml
dashboard_tests:
  - tab_switching:
      test: Click each tab
      verify: Content loads correctly
      
  - agent_status_cards:
      test: Check all 14 agent cards
      verify: Status updates in real-time
      
  - activity_feed:
      test: Monitor for 5 minutes
      verify: New activities appear
      
  - metrics_display:
      test: Check all metrics
      verify: Numbers update correctly
      
  - search_functionality:
      test: Search for agents/issues
      verify: Correct results returned
```

#### 4. Performance Testing
- Initial load time (< 3 seconds)
- Time to interactive (< 5 seconds)
- Memory usage over time
- CPU usage during updates
- Network requests optimization

#### 5. Accessibility Testing
```javascript
// Accessibility checks
const a11yTests = {
    'keyboard_navigation': 'Can navigate with Tab key',
    'screen_reader': 'All elements have proper ARIA labels',
    'color_contrast': 'WCAG AA compliance',
    'focus_indicators': 'Visible focus states',
    'alt_text': 'Images have descriptions'
};
```

### Known Issues to Verify
1. Tab system not working
2. Cost monitoring view missing
3. Kill switch not implemented
4. Some agent cards not updating
5. WebSocket disconnection issues

### Test Automation
```javascript
// Cypress E2E tests
describe('Dashboard Tests', () => {
    beforeEach(() => {
        cy.visit('/dashboard');
    });
    
    it('should switch tabs correctly', () => {
        cy.get('[data-tab="costs"]').click();
        cy.get('#costs-content').should('be.visible');
        cy.get('#main-content').should('not.be.visible');
    });
    
    it('should update agent status in real-time', () => {
        cy.get('.agent-card').first().should('contain', 'Active');
        // Trigger status change
        cy.wait(5000);
        cy.get('.agent-card').first().should('contain', 'Updated');
    });
});
```

### Bug Tracking
Create issues with labels:
- `bug/ui` - Visual issues
- `bug/functionality` - Feature not working
- `bug/performance` - Slow or unresponsive
- `bug/compatibility` - Browser-specific issue

### Definition of Done
- [ ] Tested on all browsers
- [ ] Tested on all viewport sizes
- [ ] Accessibility audit passed
- [ ] Performance metrics recorded
- [ ] All bugs documented
- [ ] Automation tests created

**Assigned to**: QA Agent 2
**Priority**: P0
**Estimate**: 3 days""",
            "labels": ["testing", "qa", "dashboard", "ui", "priority/P0"]
        },
        {
            "title": "[QA-3] Test Payment Service (ns-payments) End-to-End",
            "body": """## QA Task: Complete Testing of Payment Service

### Service Status
- Development: 75% complete
- Critical service - handles money
- Requires thorough testing

### Test Scenarios

#### 1. Payment Processing Tests
```python
# test_payment_processing.py
import pytest
from services.payments import PaymentService

class TestPaymentProcessing:
    def test_successful_payment(self):
        payment = PaymentService()
        result = payment.process_payment(
            amount=99.99,
            currency='USD',
            card_token='tok_visa',
            customer_id='cust_123'
        )
        assert result.status == 'succeeded'
        assert result.amount == 99.99
    
    def test_declined_card(self):
        result = payment.process_payment(
            card_token='tok_decline'
        )
        assert result.status == 'failed'
        assert 'declined' in result.error
    
    def test_insufficient_funds(self):
        # Test with insufficient funds token
        pass
    
    def test_3d_secure_flow(self):
        # Test 3D Secure authentication
        pass
```

#### 2. Subscription Management Tests
```yaml
subscription_tests:
  - create_subscription:
      plan: monthly_premium
      price: 19.99
      verify: subscription_active
      
  - upgrade_subscription:
      from: basic
      to: premium
      verify: prorated_charge
      
  - cancel_subscription:
      immediate: false
      verify: active_until_period_end
      
  - renewal_processing:
      test: wait_for_renewal_date
      verify: charge_processed
      
  - failed_renewal:
      scenario: payment_fails
      verify: retry_logic_triggered
```

#### 3. Webhook Testing
```javascript
// webhook_tests.js
const webhookTests = [
    {
        event: 'payment.succeeded',
        payload: mockSuccessPayload,
        expectedAction: 'update_order_status'
    },
    {
        event: 'payment.failed',
        payload: mockFailurePayload,
        expectedAction: 'notify_customer'
    },
    {
        event: 'subscription.cancelled',
        payload: mockCancelPayload,
        expectedAction: 'revoke_access'
    }
];

// Test webhook signature validation
// Test replay attack prevention
// Test idempotency
```

#### 4. Security & Compliance Tests
- PCI compliance verification
- No card data stored in logs
- Encryption of sensitive data
- Token validation
- Rate limiting on payment endpoints
- Fraud detection triggers

#### 5. Edge Cases
```python
edge_cases = [
    "Zero amount payment",
    "Negative amount (should fail)",
    "Very large amount (>$100,000)",
    "Multiple currencies",
    "Partial refunds",
    "Double refund attempts",
    "Concurrent payment attempts",
    "Network timeout during processing"
]
```

### Test Data Requirements
- Stripe test cards
- Test customer accounts
- Various subscription plans
- Test webhook endpoints

### Performance Requirements
- Payment processing < 3 seconds
- Webhook processing < 500ms
- Can handle 100 concurrent payments
- 99.9% uptime SLA

### Definition of Done
- [ ] All payment flows tested
- [ ] Subscription lifecycle tested
- [ ] Webhook processing verified
- [ ] Security scan completed
- [ ] PCI compliance checked
- [ ] Load testing completed
- [ ] Documentation updated

**Assigned to**: QA Agent 3
**Priority**: P0 (Critical - handles money)
**Estimate**: 4 days""",
            "labels": ["testing", "qa", "payments", "critical", "priority/P0"]
        },
        {
            "title": "[QA-4] Test All VisualForge Media Processing Services",
            "body": """## QA Task: Test Media Processing Pipeline for VF Services

### Services to Test
- vf-audio (75% complete)
- vf-video (75% complete)  
- vf-image (75% complete)
- vf-text (75% complete)
- vf-bulk (75% complete)

### Test Plan

#### 1. File Upload Testing
```python
# test_file_uploads.py
test_files = {
    'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg'],
    'video': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
    'image': ['jpg', 'png', 'gif', 'webp', 'tiff'],
    'text': ['txt', 'pdf', 'docx', 'md', 'rtf']
}

def test_file_upload(service, file_type):
    file_path = f'test_files/sample.{file_type}'
    response = upload_file(service, file_path)
    
    assert response.status == 200
    assert response.job_id is not None
    assert response.estimated_time > 0
```

#### 2. Processing Pipeline Tests
```yaml
processing_tests:
  audio:
    - format_conversion: mp3_to_wav
    - bitrate_adjustment: 128kbps_to_320kbps
    - noise_reduction: enabled
    - normalization: -3db
    
  video:
    - resolution_change: 1080p_to_720p
    - format_conversion: mp4_to_webm
    - compression: h264_to_h265
    - thumbnail_generation: at_10_seconds
    
  image:
    - resize: 1920x1080
    - format_conversion: png_to_jpg
    - optimization: quality_85
    - watermark: bottom_right
```

#### 3. Performance Testing
```javascript
// Load test media processing
const loadTest = {
    scenarios: {
        'single_large_file': {
            file: '1GB_video.mp4',
            expected_time: '<10 minutes'
        },
        'multiple_small_files': {
            files: '100x10MB_images',
            expected_time: '<5 minutes total'
        },
        'concurrent_processing': {
            concurrent_jobs: 50,
            expected: 'No failures'
        }
    }
};
```

#### 4. Storage and CDN Tests
- S3 upload verification
- CDN URL generation
- Cache invalidation
- Signed URL expiration
- Storage cleanup after processing

#### 5. Error Handling Tests
```python
error_scenarios = [
    "Corrupted file upload",
    "Unsupported format",
    "File too large (>5GB)",
    "Processing timeout",
    "Storage quota exceeded",
    "Invalid parameters",
    "Network interruption during upload"
]
```

### Integration Tests
- Webhook notifications on completion
- Database status updates
- Queue message handling
- Multi-service workflows (video + thumbnail + transcription)

### Bulk Processing Tests
```yaml
bulk_tests:
  - batch_upload:
      files: 100
      parallel_processing: true
      verify: all_complete
      
  - progress_tracking:
      monitor: real_time_updates
      verify: accurate_percentage
      
  - failure_handling:
      scenario: 5_files_fail
      verify: others_continue
```

### Definition of Done
- [ ] All file formats tested
- [ ] Processing pipeline verified
- [ ] Performance benchmarks met
- [ ] Error handling confirmed
- [ ] CDN delivery working
- [ ] Bulk processing tested
- [ ] Integration points verified

**Assigned to**: QA Agent 4
**Priority**: P1
**Estimate**: 5 days""",
            "labels": ["testing", "qa", "media-processing", "visualforge", "priority/P1"]
        },
        {
            "title": "[QA-5] Test Chat Interface on Web, Mobile, and Desktop",
            "body": """## QA Task: Comprehensive Chat Interface Testing

### Platforms to Test
- Web (Chrome, Firefox, Safari, Edge)
- Mobile (iOS app, Android app)
- Desktop (Windows, macOS, Linux)

### Test Coverage

#### 1. Text Chat Testing
```javascript
// text_chat_tests.js
const textTests = [
    'Send simple message',
    'Send emoji 😀',
    'Send long message (>1000 chars)',
    'Send message with URL',
    'Send message with mention @user',
    'Send code block with syntax',
    'Edit sent message',
    'Delete message',
    'Reply to thread',
    'Search messages'
];

function testMessageDelivery() {
    const message = 'Test message ' + Date.now();
    sendMessage(message);
    
    // Verify on all connected devices
    verifyOnWeb(message);
    verifyOnMobile(message);
    verifyOnDesktop(message);
    
    // Check delivery time < 1 second
}
```

#### 2. Voice Chat Testing
```python
# test_voice_chat.py
def test_voice_recording():
    # Start recording
    recording = start_voice_recording()
    time.sleep(3)  # Record for 3 seconds
    audio_file = stop_recording()
    
    # Verify audio properties
    assert audio_file.duration == 3
    assert audio_file.format == 'webm'
    assert audio_file.bitrate >= 128
    
def test_voice_to_text():
    audio = record_sample("Hello, this is a test")
    transcription = voice_to_text(audio)
    
    assert similarity(transcription, "Hello, this is a test") > 0.9
    
def test_push_to_talk():
    # Test PTT on each platform
    pass
```

#### 3. Cross-Platform Sync Testing
```yaml
sync_tests:
  - message_sync:
      send_from: web
      verify_on: [mobile, desktop]
      max_delay: 1_second
      
  - typing_indicator:
      start_typing: mobile
      see_indicator: [web, desktop]
      
  - read_receipts:
      read_on: desktop
      verify_receipt: [web, mobile]
      
  - notification_sync:
      send_to: offline_device
      verify: notification_received_on_return
```

#### 4. Performance Testing
```javascript
// Performance benchmarks
const performanceTests = {
    'message_latency': {
        target: '<100ms',
        test: () => measureLatency()
    },
    'voice_latency': {
        target: '<200ms',
        test: () => measureVoiceLatency()
    },
    'ui_responsiveness': {
        target: '<50ms',
        test: () => measureUIResponse()
    },
    'memory_usage': {
        target: '<200MB',
        test: () => measureMemoryUsage()
    }
};
```

#### 5. Network Condition Testing
```python
network_conditions = [
    {"name": "3G", "bandwidth": "1.6Mbps", "latency": "300ms"},
    {"name": "4G", "bandwidth": "12Mbps", "latency": "70ms"},
    {"name": "WiFi", "bandwidth": "30Mbps", "latency": "10ms"},
    {"name": "Offline", "bandwidth": "0", "behavior": "queue_messages"},
    {"name": "Intermittent", "packet_loss": "10%"}
]

for condition in network_conditions:
    simulate_network(condition)
    test_chat_functionality()
```

#### 6. Accessibility Testing
- Screen reader compatibility
- Keyboard navigation
- Voice control
- High contrast mode
- Font size adjustment

### Platform-Specific Tests

#### iOS
- Background app behavior
- Push notifications
- Handoff between devices
- Face ID/Touch ID for secure chats

#### Android  
- Different Android versions (8-14)
- Various screen sizes
- Battery optimization impact
- Notification channels

#### Desktop
- System tray integration
- Keyboard shortcuts
- File drag-and-drop
- Multiple window support

### Bug Categories
- `bug/chat` - Message issues
- `bug/voice` - Audio problems
- `bug/sync` - Synchronization issues
- `bug/platform/ios` - iOS specific
- `bug/platform/android` - Android specific
- `bug/platform/desktop` - Desktop specific

### Definition of Done
- [ ] All platforms tested
- [ ] Voice features verified
- [ ] Sync working across devices
- [ ] Performance targets met
- [ ] Accessibility compliant
- [ ] Network resilience confirmed
- [ ] Bug reports filed

**Assigned to**: QA Agent 5
**Priority**: P0
**Estimate**: 6 days""",
            "labels": ["testing", "qa", "chat", "cross-platform", "priority/P0"]
        }
    ]
    
    # Create issues
    repo = "NiroAgentV2/business-operations"
    created_issues = []
    
    print("\n" + "="*80)
    print("CREATING QA/TESTER AGENT TASKS")
    print("="*80)
    
    for task in qa_tasks:
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
    
    issues = create_qa_tester_tasks()
    
    print("\n" + "="*80)
    print("QA/TESTER TASKS CREATED")
    print("="*80)
    
    print(f"\n[CREATED] {len(issues)} QA testing tasks")
    
    print("\n[QA AGENTS WILL TEST:]")
    print("1. ns-auth service (authentication)")
    print("2. Dashboard UI (cross-browser)")
    print("3. ns-payments (critical - money handling)")
    print("4. VisualForge media services")
    print("5. Chat interface (all platforms)")
    
    print("\n[TEST COVERAGE:]")
    print("- Functional testing")
    print("- Security testing")
    print("- Performance testing")
    print("- Integration testing")
    print("- Cross-platform testing")
    
    print("\n[EXPECTED OUTCOMES:]")
    print("- Bug reports for developers to fix")
    print("- Performance benchmarks")
    print("- Security vulnerabilities identified")
    print("- Test automation scripts created")
    print("- Quality metrics established")
    
    print("\n[WORKFLOW:]")
    print("1. QA tests existing 75% complete code")
    print("2. QA creates bug reports")
    print("3. Developers fix bugs")
    print("4. QA retests fixes")
    print("5. Services reach 100% completion")
    
    print("\n[SUCCESS!]")
    print("Testing first makes sense - find bugs in existing code!")

if __name__ == "__main__":
    main()