#!/bin/bash

echo "======================================"
echo "SETUP ANTHROPIC API KEY IN AWS"
echo "======================================"
echo ""

# Check if secret already exists
aws secretsmanager describe-secret --secret-id anthropic-api-key &>/dev/null

if [ $? -eq 0 ]; then
    echo "Secret 'anthropic-api-key' already exists in AWS Secrets Manager"
    echo ""
    echo "To update it:"
    echo "  aws secretsmanager put-secret-value --secret-id anthropic-api-key --secret-string 'your-new-api-key'"
else
    echo "Secret 'anthropic-api-key' does not exist"
    echo ""
    echo "To create it, run:"
    echo "  aws secretsmanager create-secret --name anthropic-api-key --secret-string 'your-api-key-here'"
    echo ""
    echo "Or with description:"
    echo "  aws secretsmanager create-secret \\"
    echo "    --name anthropic-api-key \\"
    echo "    --description 'Anthropic Claude API Key for development' \\"
    echo "    --secret-string 'your-api-key-here'"
fi

echo ""
echo "======================================"
echo "USAGE IN DIFFERENT ENVIRONMENTS"
echo "======================================"
echo ""
echo "Windows Batch (.bat):"
echo '  for /f "tokens=*" %%i in ('"'"'aws secretsmanager get-secret-value --secret-id anthropic-api-key --query SecretString --output text'"'"') do set ANTHROPIC_API_KEY=%%i'
echo ""
echo "PowerShell:"
echo '  $env:ANTHROPIC_API_KEY = aws secretsmanager get-secret-value --secret-id anthropic-api-key --query SecretString --output text'
echo ""
echo "Bash/Linux:"
echo '  export ANTHROPIC_API_KEY=$(aws secretsmanager get-secret-value --secret-id anthropic-api-key --query SecretString --output text)'
echo ""
echo "Python:"
echo "  import boto3"
echo "  client = boto3.client('secretsmanager')"
echo "  secret = client.get_secret_value(SecretId='anthropic-api-key')"
echo "  api_key = secret['SecretString']"
echo ""
echo "Node.js:"
echo "  const AWS = require('aws-sdk');"
echo "  const client = new AWS.SecretsManager();"
echo "  const secret = await client.getSecretValue({ SecretId: 'anthropic-api-key' }).promise();"
echo "  const apiKey = secret.SecretString;"