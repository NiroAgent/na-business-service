#!/usr/bin/env python3
"""
Enhanced PM Agent - Creates Documentation Standards and Development Hierarchy
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

class EnhancedPMAgent:
    """PM Agent that creates comprehensive documentation and development structure"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        
    def process_issue(self, issue_number: int, issue_data: dict):
        """Process PM issue based on content"""
        
        title = issue_data.get('title', '')
        body = issue_data.get('body', '')
        
        print(f"\n=== ENHANCED PM AGENT PROCESSING ===")
        print(f"Issue #{issue_number}: {title}")
        
        if 'documentation' in title.lower() and 'ns-payments' in body.lower():
            self.create_documentation_structure()
        elif 'documentation' in title.lower():
            self.review_documentation(title, body)
        else:
            self.delegate_generic(title, body)
            
    def create_documentation_structure(self):
        """Create comprehensive documentation structure for ns-payments"""
        
        print("\n[DOCUMENTATION] Creating Standard Documentation Structure...")
        
        # 1. Create documentation files
        docs_to_create = [
            {
                'title': '[DOC] Create SERVICE_OVERVIEW.md for ns-payments',
                'file': 'SERVICE_OVERVIEW.md',
                'content': self.generate_service_overview()
            },
            {
                'title': '[DOC] Create API_SPECIFICATION.md for ns-payments',
                'file': 'API_SPECIFICATION.md',
                'content': self.generate_api_spec()
            },
            {
                'title': '[DOC] Create DATABASE_SCHEMA.md for ns-payments',
                'file': 'DATABASE_SCHEMA.md',
                'content': self.generate_db_schema()
            },
            {
                'title': '[DOC] Create DEPLOYMENT_GUIDE.md for ns-payments',
                'file': 'DEPLOYMENT_GUIDE.md',
                'content': self.generate_deployment_guide()
            },
            {
                'title': '[DOC] Create TESTING_GUIDE.md for ns-payments',
                'file': 'TESTING_GUIDE.md',
                'content': self.generate_testing_guide()
            },
            {
                'title': '[DOC] Create MONITORING_GUIDE.md for ns-payments',
                'file': 'MONITORING_GUIDE.md',
                'content': self.generate_monitoring_guide()
            },
            {
                'title': '[DOC] Create SECURITY_AUDIT.md for ns-payments',
                'file': 'SECURITY_AUDIT.md',
                'content': self.generate_security_audit()
            },
            {
                'title': '[DOC] Create RUNBOOK.md for ns-payments',
                'file': 'RUNBOOK.md',
                'content': self.generate_runbook()
            }
        ]
        
        # Create documentation task
        doc_task_body = """## Documentation Creation Task

Create the following standard documentation files for ns-payments service:

### Files to Create:"""
        
        for doc in docs_to_create:
            doc_task_body += f"\n- `docs/{doc['file']}`"
            
        doc_task_body += """

### Documentation Content:

Each file has been specified with required sections and content. Use the templates provided and customize for ns-payments specific functionality.

### Acceptance Criteria:
- [ ] All 8 documentation files created
- [ ] Content is accurate and complete
- [ ] Examples provided where applicable
- [ ] Reviewed by architect

assigned_agent: vf-developer-agent
priority: P0
type: documentation
"""
        
        self.create_issue('NiroSubs-V2/ns-payments', 
                         '[DEV] Create Standard Documentation Files',
                         doc_task_body)
        
        # 2. Create EPICs
        self.create_epics()
        
        # 3. Create Features
        self.create_features()
        
        # 4. Create Stories
        self.create_stories()
        
        # 5. Create QA verification task
        self.create_qa_verification()
        
    def create_epics(self):
        """Create EPICs for ns-payments"""
        
        print("\n[EPICS] Creating EPICs...")
        
        epics = [
            {
                'title': '[EPIC] Payment Gateway Integration',
                'body': '''## EPIC: Complete Payment Gateway Integration

### Business Value
Enable multiple payment methods and providers to increase conversion rates and reduce payment failures.

### Scope
- Stripe integration
- PayPal integration  
- Apple Pay / Google Pay
- Cryptocurrency payments
- Payment method vault

### Success Metrics
- Support 5+ payment methods
- < 2% payment failure rate
- < 3 second processing time
- PCI DSS compliance maintained

### Features Included
- FEATURE-001: Stripe Integration
- FEATURE-002: PayPal Integration
- FEATURE-003: Digital Wallet Support
- FEATURE-004: Payment Method Vault
- FEATURE-005: Webhook Processing

### Timeline
Q1 2025 - Q2 2025

### Dependencies
- PCI compliance certification
- Security audit completion
- API gateway setup

priority: P0
epic_id: EPIC-001
'''
            },
            {
                'title': '[EPIC] PCI Compliance and Security',
                'body': '''## EPIC: Achieve PCI DSS Level 1 Compliance

### Business Value
Ensure payment processing meets highest security standards to protect customer data and maintain trust.

### Scope
- PCI DSS assessment
- Security hardening
- Encryption implementation
- Audit logging
- Vulnerability scanning

### Success Metrics
- Pass PCI DSS Level 1 audit
- Zero security breaches
- 100% encrypted data at rest/transit
- Complete audit trail

### Timeline
Q1 2025

priority: P0
epic_id: EPIC-002
'''
            },
            {
                'title': '[EPIC] Subscription Management System',
                'body': '''## EPIC: Advanced Subscription Management

### Business Value
Reduce churn and increase LTV through flexible subscription management.

### Scope
- Flexible billing cycles
- Pause/resume subscriptions
- Upgrade/downgrade flows
- Dunning management
- Revenue recognition

### Success Metrics
- < 5% involuntary churn
- < 1 minute plan changes
- 99.9% billing accuracy

### Timeline
Q2 2025

priority: P1
epic_id: EPIC-003
'''
            }
        ]
        
        for epic in epics:
            self.create_issue('NiroSubs-V2/ns-payments', epic['title'], epic['body'])
            
    def create_features(self):
        """Create Features under EPICs"""
        
        print("\n[FEATURES] Creating Features...")
        
        features = [
            {
                'title': '[FEATURE] Stripe Payment Processing',
                'body': '''## Feature: Stripe Payment Processing

### Parent EPIC: EPIC-001 (Payment Gateway Integration)

### Description
Implement complete Stripe payment processing including cards, ACH, and SEPA.

### User Stories
- As a customer, I want to pay with credit card
- As a customer, I want to save payment methods
- As a customer, I want automatic retry on failure

### Technical Requirements
- Stripe SDK integration
- Webhook endpoint for events
- Payment intent creation
- 3D Secure support
- Idempotency handling

### Acceptance Criteria
- [ ] Process card payments
- [ ] Handle 3D Secure
- [ ] Process webhooks
- [ ] Save payment methods
- [ ] Handle failures gracefully

assigned_agent: vf-developer-agent
priority: P0
epic: EPIC-001
feature_id: FEATURE-001
'''
            },
            {
                'title': '[FEATURE] Refund Processing System',
                'body': '''## Feature: Automated Refund Processing

### Parent EPIC: EPIC-001

### Description
Implement automated and manual refund processing with audit trail.

### User Stories
- As an admin, I want to issue refunds
- As a customer, I want refund status updates
- As finance, I want refund reporting

### Technical Requirements
- Refund API endpoints
- Partial refund support
- Refund reason tracking
- Automated refund rules
- Notification system

### Acceptance Criteria
- [ ] Process full refunds
- [ ] Process partial refunds
- [ ] Send notifications
- [ ] Update subscription status
- [ ] Generate refund reports

priority: P0
epic: EPIC-001
feature_id: FEATURE-002
'''
            }
        ]
        
        for feature in features:
            self.create_issue('NiroSubs-V2/ns-payments', feature['title'], feature['body'])
            
    def create_stories(self):
        """Create User Stories under Features"""
        
        print("\n[STORIES] Creating User Stories...")
        
        stories = [
            {
                'title': '[STORY] Customer Can Pay with Credit Card',
                'body': '''## User Story: Credit Card Payment

### As a customer
### I want to pay with my credit card
### So that I can subscribe to the service

### Parent Feature: FEATURE-001 (Stripe Payment Processing)

### Acceptance Criteria
- [ ] GIVEN I am on checkout page
      WHEN I enter valid card details
      THEN payment is processed successfully
      
- [ ] GIVEN I enter invalid card
      WHEN I submit payment
      THEN I see clear error message
      
- [ ] GIVEN my card requires 3D Secure
      WHEN I submit payment
      THEN I am redirected to bank verification

### Technical Tasks
- Implement Stripe Elements
- Create payment intent endpoint
- Handle payment confirmation
- Update subscription status
- Send confirmation email

### Definition of Done
- [ ] Code complete
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security review complete
- [ ] Documentation updated

story_points: 5
priority: P0
feature: FEATURE-001
'''
            },
            {
                'title': '[STORY] Customer Receives Payment Receipt',
                'body': '''## User Story: Payment Receipt

### As a customer
### I want to receive a receipt after payment
### So that I have proof of purchase

### Parent Feature: FEATURE-001

### Acceptance Criteria
- [ ] GIVEN payment successful
      WHEN transaction completes
      THEN receipt email sent within 1 minute
      
- [ ] GIVEN receipt email sent
      WHEN customer opens email
      THEN all payment details are correct

### Technical Tasks
- Create receipt template
- Implement email service
- Generate PDF receipt
- Store receipt records

story_points: 3
priority: P0
feature: FEATURE-001
'''
            }
        ]
        
        for story in stories:
            self.create_issue('NiroSubs-V2/ns-payments', story['title'], story['body'])
            
    def create_qa_verification(self):
        """Create QA verification task"""
        
        print("\n[QA] Creating QA Verification Task...")
        
        qa_body = '''## QA Verification Task

### Objective
Verify all documentation is accurate and identify bugs in ns-payments service.

### Verification Checklist

#### Documentation Review
- [ ] SERVICE_OVERVIEW.md is accurate
- [ ] API_SPECIFICATION.md matches actual APIs
- [ ] DATABASE_SCHEMA.md reflects current schema
- [ ] DEPLOYMENT_GUIDE.md steps work
- [ ] TESTING_GUIDE.md tests can be run
- [ ] MONITORING_GUIDE.md metrics exist
- [ ] SECURITY_AUDIT.md is comprehensive
- [ ] RUNBOOK.md procedures work

#### Functional Testing
- [ ] Payment processing works
- [ ] Refunds process correctly
- [ ] Webhooks are received
- [ ] Error handling works
- [ ] Retry logic functions

#### Security Testing
- [ ] No SQL injection vulnerabilities
- [ ] API authentication required
- [ ] Rate limiting works
- [ ] Input validation complete
- [ ] PCI compliance maintained

### Bug Reporting
Create bugs for any issues found with format:
- [BUG] Description
- Severity: P0/P1/P2
- Steps to reproduce
- Expected vs Actual behavior

assigned_agent: vf-qa-agent
priority: P0
depends_on: documentation_creation
'''
        
        self.create_issue('NiroSubs-V2/ns-payments', 
                         '[QA] Verify Documentation and Test ns-payments',
                         qa_body)
                         
    def generate_service_overview(self):
        """Generate SERVICE_OVERVIEW.md content"""
        return '''# ns-payments Service Overview

## Purpose
The ns-payments service handles all payment processing for NiroSubs subscription platform.

## Architecture
- Serverless Lambda functions
- DynamoDB for transaction storage
- SQS for async processing
- Stripe/PayPal integrations

## Key Features
- Payment processing
- Subscription billing
- Refund handling
- Payment method management
- Webhook processing

## Dependencies
- Stripe API
- AWS Lambda
- DynamoDB
- SQS
- SNS for notifications
'''

    def generate_api_spec(self):
        """Generate API_SPECIFICATION.md content"""
        return '''# API Specification

## Base URL
`https://api.nirosubs.com/payments/v1`

## Endpoints

### POST /payments/process
Process a payment

Request:
```json
{
  "amount": 1000,
  "currency": "USD",
  "payment_method": "pm_xxxxx",
  "customer_id": "cus_xxxxx"
}
```

### POST /refunds/create
Create a refund

### GET /payments/{id}
Get payment details

### GET /customers/{id}/payment-methods
List customer payment methods
'''

    def generate_db_schema(self):
        """Generate DATABASE_SCHEMA.md content"""
        return '''# Database Schema

## DynamoDB Tables

### payments_table
- PK: payment_id
- SK: timestamp
- Attributes: amount, currency, status, customer_id

### refunds_table
- PK: refund_id
- SK: payment_id
- Attributes: amount, reason, status

### payment_methods_table
- PK: customer_id
- SK: payment_method_id
- Attributes: type, last4, exp_date
'''

    def generate_deployment_guide(self):
        """Generate DEPLOYMENT_GUIDE.md content"""
        return '''# Deployment Guide

## Prerequisites
- AWS CLI configured
- Node.js 18+
- Serverless Framework

## Deployment Steps
1. Install dependencies: `npm install`
2. Run tests: `npm test`
3. Deploy to dev: `serverless deploy --stage dev`
4. Deploy to prod: `serverless deploy --stage prod`

## Environment Variables
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET
- DATABASE_NAME
'''

    def generate_testing_guide(self):
        """Generate TESTING_GUIDE.md content"""
        return '''# Testing Guide

## Unit Tests
`npm run test:unit`

## Integration Tests
`npm run test:integration`

## End-to-End Tests
`npm run test:e2e`

## Test Coverage
Minimum 80% coverage required
'''

    def generate_monitoring_guide(self):
        """Generate MONITORING_GUIDE.md content"""
        return '''# Monitoring Guide

## Key Metrics
- Payment success rate
- Average processing time
- Refund rate
- Error rate

## Alerts
- Payment failures > 5%
- Processing time > 5 seconds
- Error rate > 1%

## Dashboards
- CloudWatch Dashboard: payment-metrics
- DataDog: ns-payments-overview
'''

    def generate_security_audit(self):
        """Generate SECURITY_AUDIT.md content"""
        return '''# Security Audit

## PCI Compliance
- Level 1 compliant
- No card data stored
- All data encrypted

## Security Measures
- API authentication required
- Rate limiting enabled
- Input validation
- SQL injection prevention
- XSS protection

## Audit Log
All payment operations logged
'''

    def generate_runbook(self):
        """Generate RUNBOOK.md content"""
        return '''# Operational Runbook

## Common Issues

### High Payment Failure Rate
1. Check Stripe status
2. Verify API keys
3. Check rate limits
4. Review error logs

### Webhook Processing Delays
1. Check SQS queue depth
2. Verify Lambda concurrency
3. Check DLQ for failures

## Emergency Contacts
- On-call: #payments-oncall
- Escalation: payments-team@company.com
'''

    def create_issue(self, repo: str, title: str, body: str):
        """Create a GitHub issue"""
        
        print(f"\n[CREATE] Creating: {title}")
        
        cmd = [
            'gh', 'issue', 'create',
            '--repo', repo,
            '--title', title,
            '--body', body
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   [OK] Created: {result.stdout.strip()}")
            else:
                print(f"   [FAIL] {result.stderr}")
        except Exception as e:
            print(f"   [ERROR] {e}")
            
    def review_documentation(self, title: str, body: str):
        """Generic documentation review"""
        print("\n[REVIEW] Processing documentation review...")
        
    def delegate_generic(self, title: str, body: str):
        """Generic delegation"""
        print("\n[DELEGATE] Creating generic delegation...")


def main():
    """Main entry point"""
    
    if len(sys.argv) < 3:
        print("Usage: python enhanced-pm-agent.py --process-issue <num> --issue-data <file>")
        return
        
    issue_number = None
    issue_file = None
    
    for i, arg in enumerate(sys.argv):
        if arg == '--process-issue':
            issue_number = int(sys.argv[i+1])
        elif arg == '--issue-data':
            issue_file = sys.argv[i+1]
            
    if not issue_number or not issue_file:
        print("Missing required arguments")
        return
        
    # Load issue data
    with open(issue_file, 'r') as f:
        issue_data = json.load(f)
        
    # Process with enhanced agent
    agent = EnhancedPMAgent()
    agent.process_issue(issue_number, issue_data)
    
    print("\n[COMPLETE] Enhanced PM Agent finished!")


if __name__ == '__main__':
    main()