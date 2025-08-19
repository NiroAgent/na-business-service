# GitHub Copilot CLI Examples for Agent Testing

## Overview
This document shows how to use `gh copilot` commands for automated testing and remediation of services.

## Basic Commands

### Explain Commands
```bash
# Explain what a command does
gh copilot explain "docker-compose up -d"

# Explain AWS CLI commands
gh copilot explain "aws lambda update-function-code --function-name my-function --zip-file fileb://function.zip"

# Explain complex commands
gh copilot explain "find . -name '*.js' -exec grep -l 'TODO' {} \;"
```

### Suggest Commands
```bash
# Get command suggestions
gh copilot suggest "How to list all Lambda functions in AWS"

# Deployment commands
gh copilot suggest "Deploy a zip file to AWS Lambda"

# Troubleshooting commands
gh copilot suggest "Check CloudWatch logs for Lambda errors"
```

## Service Testing Commands

### Health Check Testing
```bash
# Test health endpoint
gh copilot explain "Write a curl command to test the health endpoint of ns-auth service"

# Verify health response
gh copilot suggest "What should a healthy Lambda function response look like?"
```

### Functional Testing
```bash
# Generate test cases
gh copilot suggest -f ns-auth/index.js "Generate unit tests for this Lambda function"

# Integration testing
gh copilot explain "How to test integration between ns-auth and ns-user services"

# API testing
gh copilot suggest "Create Postman tests for these API endpoints"
```

### Security Testing
```bash
# Check for vulnerabilities
gh copilot explain -f package.json "Are there any security vulnerabilities in these dependencies?"

# Review IAM permissions
gh copilot suggest -f cloudformation.yaml "Review the IAM permissions for security issues"

# Secrets management
gh copilot explain "How to properly manage secrets in AWS Lambda"
```

### Performance Testing
```bash
# Analyze performance
gh copilot explain -f index.js "What performance improvements can be made to this Lambda?"

# Memory optimization
gh copilot suggest "How to determine optimal memory allocation for Lambda"

# Cold start optimization
gh copilot explain "Best practices for reducing Lambda cold starts"
```

## Remediation Commands

### Fix Code Issues
```bash
# Fix specific error
gh copilot suggest -f index.js "Fix: TypeError: Cannot read property 'id' of undefined"

# Refactor code
gh copilot suggest -f index.js "Refactor this function to be more maintainable"

# Add error handling
gh copilot suggest -f index.js "Add proper error handling to this Lambda function"
```

### Fix Configuration
```bash
# Fix CloudFormation
gh copilot suggest -f cloudformation.yaml "Fix: Property ProvisionedThroughput cannot be used with PAY_PER_REQUEST"

# Fix serverless.yml
gh copilot suggest -f serverless.yml "Add proper CORS configuration"

# Fix package.json
gh copilot suggest -f package.json "Update dependencies to latest secure versions"
```

## Deployment Commands

### Deploy to AWS
```bash
# Deploy Lambda
gh copilot explain "Steps to deploy this Lambda function to AWS"

# Update function code
gh copilot suggest "AWS CLI command to update Lambda function code"

# Deploy with CloudFormation
gh copilot explain -f cloudformation.yaml "How to deploy this stack"
```

### Rollback
```bash
# Rollback strategy
gh copilot suggest "How to rollback a failed Lambda deployment"

# CloudFormation rollback
gh copilot explain "How to rollback a CloudFormation stack update"
```

## Batch Testing Script

### PowerShell Script for Testing All Services
```powershell
# Test all services in an environment
$services = @("ns-auth", "ns-dashboard", "ns-payments", "ns-user", "ns-shell")
$environment = "dev"

foreach ($service in $services) {
    Write-Host "Testing $service..." -ForegroundColor Cyan
    
    # Check health
    gh copilot explain "Test health endpoint for $service in $environment"
    
    # Check security
    Push-Location $service
    gh copilot suggest -f index.js "Check for security issues"
    Pop-Location
    
    # Check performance
    gh copilot explain "Performance metrics to monitor for $service"
}
```

### Bash Script for Parallel Testing
```bash
#!/bin/bash

# Function to test a service
test_service() {
    local service=$1
    local env=$2
    
    echo "Testing $service in $env..."
    
    # Health check
    gh copilot explain "curl command to test $service health in $env"
    
    # Security check
    cd $service
    gh copilot suggest -f index.js "Security vulnerabilities to check"
    cd ..
    
    # Performance check
    gh copilot explain "How to load test $service"
}

# Test services in parallel
services=("ns-auth" "ns-dashboard" "ns-payments")
for service in "${services[@]}"; do
    test_service "$service" "dev" &
done

# Wait for all tests to complete
wait
echo "All tests completed!"
```

## Integration with VS Code

### Using gh copilot in VS Code Terminal
```bash
# Open VS Code with workspace
code ns-auth-dev-agent.code-workspace

# In integrated terminal, test the service
gh copilot explain -f AGENT_INSTRUCTIONS_DEV.md "Execute these test instructions"

# Fix issues found
gh copilot suggest -f index.js "Fix the issues found during testing"

# Deploy fixes
gh copilot explain "Deploy these changes to dev environment"
```

## Advanced Usage

### Chain Commands for Complete Workflow
```bash
# 1. Analyze current state
gh copilot explain -f . "What issues exist in this service?"

# 2. Get fix suggestions
gh copilot suggest "How to fix the identified issues"

# 3. Implement fixes (manual step)

# 4. Verify fixes
gh copilot explain "How to verify these fixes work correctly"

# 5. Deploy
gh copilot suggest "Safe deployment strategy for these changes"
```

### Custom Testing Prompts
```bash
# Comprehensive service test
gh copilot explain "Create a comprehensive test plan for a Lambda-based microservice including:
1. Unit tests
2. Integration tests
3. Performance tests
4. Security tests
5. Error handling tests"

# Automated remediation
gh copilot suggest "Create a script that:
1. Identifies common Lambda issues
2. Suggests fixes
3. Implements fixes where possible
4. Tests the fixes
5. Reports results"
```

## Tips and Best Practices

1. **Use File Context**: Always use `-f` flag when asking about specific code
2. **Be Specific**: More specific questions get better answers
3. **Chain Commands**: Use output from one command as input to next
4. **Save Responses**: Redirect output to files for documentation
5. **Automate**: Create scripts that run multiple gh copilot commands

## Example Output Capture

```bash
# Save test results
gh copilot explain -f ns-auth "Test this service" > test-results.md

# Save fix suggestions
gh copilot suggest -f index.js "Optimize performance" > optimization-suggestions.md

# Create documentation
gh copilot explain -f . "Document this service architecture" > architecture.md
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Copilot Testing
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install GitHub CLI
        run: |
          curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
          echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
          sudo apt update
          sudo apt install gh
      
      - name: Authenticate GitHub CLI
        run: gh auth login --with-token <<< "${{ secrets.GITHUB_TOKEN }}"
      
      - name: Run Copilot Tests
        run: |
          gh copilot explain -f . "Test this service and report issues"
          gh copilot suggest -f . "Suggest improvements"
```

## Troubleshooting

### Common Issues
```bash
# If gh copilot is not available
gh extension install github/gh-copilot

# If authentication fails
gh auth login

# If commands timeout
gh copilot explain --timeout 60 "Complex analysis..."
```

## Next Steps

1. Install GitHub CLI: https://cli.github.com/
2. Install Copilot extension: `gh extension install github/gh-copilot`
3. Authenticate: `gh auth login`
4. Start testing: Use the commands above to test your services