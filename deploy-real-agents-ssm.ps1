# PowerShell script to deploy real agents via SSM
$INSTANCE_ID = "i-0af59b7036f7b0b77"

Write-Host "Deploying Real AI Agents to EC2 via SSM..." -ForegroundColor Green

# Stop existing agents
Write-Host "Stopping existing placeholder agents..." -ForegroundColor Yellow
aws ssm send-command `
    --instance-ids $INSTANCE_ID `
    --document-name "AWS-RunShellScript" `
    --parameters 'commands=["pkill -f ai-qa-agent","pkill -f ai-developer-agent","pkill -f ai-operations-agent"]' `
    --output text

Start-Sleep -Seconds 5

# Create real QA agent
Write-Host "Creating real QA agent script..." -ForegroundColor Yellow
$qaAgentContent = Get-Content "ai-agent-deployment\ai-qa-agent-real.py" -Raw
$qaAgentContent = $qaAgentContent -replace "'", "'\''"

aws ssm send-command `
    --instance-ids $INSTANCE_ID `
    --document-name "AWS-RunShellScript" `
    --parameters "commands=[`"cat > /opt/ai-agents/scripts/ai-qa-agent-real.py << 'EOF'`n$qaAgentContent`nEOF`",`"chmod +x /opt/ai-agents/scripts/ai-qa-agent-real.py`"]" `
    --output text

Start-Sleep -Seconds 5

# Create real developer agent
Write-Host "Creating real developer agent script..." -ForegroundColor Yellow
$devAgentContent = Get-Content "ai-agent-deployment\ai-developer-agent-real.py" -Raw
$devAgentContent = $devAgentContent -replace "'", "'\''"

aws ssm send-command `
    --instance-ids $INSTANCE_ID `
    --document-name "AWS-RunShellScript" `
    --parameters "commands=[`"cat > /opt/ai-agents/scripts/ai-developer-agent-real.py << 'EOF'`n$devAgentContent`nEOF`",`"chmod +x /opt/ai-agents/scripts/ai-developer-agent-real.py`"]" `
    --output text

Start-Sleep -Seconds 5

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
aws ssm send-command `
    --instance-ids $INSTANCE_ID `
    --document-name "AWS-RunShellScript" `
    --parameters 'commands=["cd /opt/ai-agents","npm install -g playwright","npx playwright install chromium","pip3 install requests pytest-playwright"]' `
    --output text

Start-Sleep -Seconds 10

# Start real agents
Write-Host "Starting real agents..." -ForegroundColor Yellow
$startCmd = aws ssm send-command `
    --instance-ids $INSTANCE_ID `
    --document-name "AWS-RunShellScript" `
    --parameters 'commands=["cd /opt/ai-agents/scripts","nohup python3 ai-qa-agent-real.py > /opt/ai-agents/logs/qa-real.log 2>&1 &","nohup python3 ai-developer-agent-real.py > /opt/ai-agents/logs/dev-real.log 2>&1 &","ps aux | grep agent"]' `
    --query 'Command.CommandId' `
    --output text

Start-Sleep -Seconds 10

# Check status
Write-Host "Checking agent status..." -ForegroundColor Yellow
aws ssm get-command-invocation `
    --command-id $startCmd `
    --instance-id $INSTANCE_ID `
    --query 'StandardOutputContent' `
    --output text

Write-Host "Real agents deployed successfully!" -ForegroundColor Green