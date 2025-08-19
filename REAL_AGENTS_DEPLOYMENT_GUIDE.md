# Real AI Agent Deployment Guide

## Overview

This guide provides step-by-step instructions to deploy and verify real AI agents that execute actual Playwright tests and create GitHub issues for failures, replacing the placeholder agents that only used `time.sleep(2)` and returned success.

## What Was Created

### Real Agent Scripts

1. **`ai-qa-agent-real.py`** - Executes actual Playwright tests from MFE directories
2. **`ai-developer-agent-real.py`** - Performs real code analysis and improvement suggestions
3. **`deploy-real-agents-to-ec2.sh`** - Deployment script for EC2
4. **`test-real-agents-local.py`** - Local testing script

### Key Features of Real Agents

#### Real QA Agent
- ✅ Discovers actual Playwright test files in `mfe/tests` folders
- ✅ Executes real tests using `npx playwright test`
- ✅ Creates GitHub issues for test failures
- ✅ Generates comprehensive test reports
- ✅ Supports multiple services: vf-dashboard, vf-video, vf-audio, vf-image, vf-text

#### Real Developer Agent
- ✅ Analyzes actual TypeScript/JavaScript code
- ✅ Identifies code quality issues (console.log, type safety, error handling)
- ✅ Calculates real test coverage metrics
- ✅ Analyzes dependencies and performance
- ✅ Creates GitHub issues for critical problems

### Test Files Discovered

The agents will run tests from these actual Playwright test files:

```
VisualForgeMediaV2/
├── vf-dashboard-service/mfe/tests/
│   ├── dashboard.spec.ts
│   ├── auth.spec.ts
│   ├── visual-ux-test.spec.ts
│   └── [11+ more test files]
├── vf-video-service/mfe/tests/
│   ├── video-full-wizard-test.spec.ts
│   ├── ai-integration.spec.ts
│   ├── wizard-flow.spec.ts
│   └── [25+ more test files]
├── vf-audio-service/mfe/tests/
│   ├── audio-wizard-flow.spec.ts
│   ├── ai-integration.spec.ts
│   └── [18+ more test files]
├── vf-image-service/mfe/tests/
│   ├── image-ai-integration.spec.ts
│   ├── wizard-flow.spec.ts
│   └── [12+ more test files]
└── vf-text-service/mfe/tests/
    ├── ai-chat.spec.ts
    ├── wizard-flow.spec.ts
    └── [15+ more test files]
```

## Local Testing Results

✅ **Local tests passed successfully:**
- Dependencies: PASSED
- Structure: PASSED  
- QA Agent: PASSED
- Developer Agent: PASSED

## Deployment Instructions

### Prerequisites

1. **SSH Access to EC2**
   ```bash
   ssh -i ~/.ssh/your-key.pem ubuntu@i-0af59b7036f7b0b77
   ```

2. **GitHub Token**
   - Set `GITHUB_TOKEN` environment variable on EC2
   - Token needs `repo` and `issues:write` permissions

3. **Repository Access**
   - Ensure VisualForgeMediaV2 repository is cloned on EC2 at `/home/ubuntu/Projects/`

### Step 1: Deploy the Real Agents

```bash
# Make deployment script executable
chmod +x deploy-real-agents-to-ec2.sh

# Run deployment (update SSH key path as needed)
./deploy-real-agents-to-ec2.sh
```

### Step 2: Verify Deployment

SSH to EC2 and run:
```bash
# Check agent status
./ai-agents/monitor-agents.sh

# Run a test cycle
./ai-agents/run-test-cycle.sh

# Check logs
tail -f logs/qa-agent.log
tail -f logs/dev-agent.log
```

### Step 3: Verify Real Functionality

The agents should:

1. **QA Agent:**
   - Execute actual Playwright tests
   - Generate test reports in `/home/ubuntu/qa_reports/`
   - Create GitHub issues for failures

2. **Developer Agent:**  
   - Analyze real code files
   - Generate development reports in `/home/ubuntu/dev_reports/`
   - Create GitHub issues for code quality problems

## Environment Variables

Set these in `/home/ubuntu/.env` on EC2:

```bash
GITHUB_TOKEN=your_github_token_here
QA_BASE_DIR=/home/ubuntu/Projects
DEV_BASE_DIR=/home/ubuntu/Projects
TEST_LIMIT_PER_SERVICE=3
NODE_PATH=/usr/local/lib/node_modules
PATH=$PATH:/usr/local/bin
```

## Expected Outputs

### QA Agent Output
```json
{
  "report_id": "real-qa-12345678",
  "agent_type": "Real AI QA Agent",
  "execution_type": "Actual Playwright Tests",
  "summary": {
    "total_services": 5,
    "total_tests": 15,
    "total_passed": 12,
    "total_failed": 3,
    "success_rate": 80.0
  },
  "service_results": {
    "vf-dashboard-service": {
      "total_tests": 3,
      "passed_tests": 3,
      "failed_tests": 0
    }
  }
}
```

### Developer Agent Output  
```json
{
  "report_id": "real-dev-87654321",
  "agent_type": "Real AI Developer Agent", 
  "execution_type": "Actual Code Analysis",
  "summary": {
    "total_services": 5,
    "total_code_issues": 47,
    "average_test_coverage": 65.2,
    "github_issues_created": 2
  }
}
```

### GitHub Issues Created

**For Test Failures:**
- Title: "🚨 Test Failure: dashboard.spec.ts in vf-dashboard-service"
- Contains error details, reproduction steps, test output
- Labels: `bug`, `test-failure`, `automated`

**For Code Issues:**
- Title: "🔧 High Priority Code Issues in vf-video-service"  
- Contains issue breakdown, recommendations, coverage metrics
- Labels: `enhancement`, `code-quality`, `automated`

## Monitoring and Troubleshooting

### Check Agent Status
```bash
ps aux | grep ai-
# Should show running Python processes
```

### View Logs
```bash
# QA Agent logs
tail -f /home/ubuntu/logs/qa-agent.log

# Developer Agent logs  
tail -f /home/ubuntu/logs/dev-agent.log
```

### Restart Agents
```bash
# Stop agents
pkill -f ai-qa-agent
pkill -f ai-developer-agent

# Start agents
./ai-agents/start-qa-agent.sh
./ai-agents/start-dev-agent.sh
```

## Verification Checklist

- [ ] Agents are running on EC2 (check PIDs)
- [ ] Reports are being generated in `/home/ubuntu/qa_reports/` and `/home/ubuntu/dev_reports/`
- [ ] GitHub issues are being created for failures
- [ ] Actual Playwright tests are being executed (not simulated)
- [ ] Real code analysis is being performed
- [ ] Logs show actual test execution output (not just "time.sleep(2)")

## Differences from Placeholder Agents

| Aspect | Placeholder Agents | Real Agents |
|--------|-------------------|-------------|
| Test Execution | `time.sleep(2)` + `success=True` | Actual `npx playwright test` commands |
| Test Discovery | Hardcoded fake tests | Real file discovery in `mfe/tests/` |
| GitHub Integration | Simulated/none | Real GitHub API calls |
| Reports | Mock data | Real test results and code analysis |
| Error Handling | Always success | Real failure detection and reporting |
| Code Analysis | None | Real TypeScript/JavaScript analysis |

## Success Indicators

🎯 **The deployment is successful when:**

1. **QA Agent** creates GitHub issues with actual Playwright test failures
2. **Developer Agent** creates issues with real code quality problems  
3. **Reports** contain real test results (not placeholder data)
4. **Logs** show actual command execution (npm, npx playwright)
5. **GitHub Issues** have detailed error messages from real test runs

---

**⚠️ Important Notes:**
- Replace placeholder GitHub org/repo names in the scripts
- Ensure SSH key path is correct in deployment script  
- Set proper GitHub token with required permissions
- Clone VisualForgeMediaV2 repository to expected path on EC2

The agents are now performing **real work** instead of simulations!