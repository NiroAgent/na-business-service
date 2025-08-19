# GitHub Token Setup Instructions

## Step 1: Create Personal Access Token

1. Go to GitHub: https://github.com/settings/tokens
2. Click "Generate new token" -> "Generate new token (classic)"
3. Give it a descriptive name: "SDLC Agent Integration"
4. Set expiration (recommend 90 days or No expiration for development)
5. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `write:packages` (Upload packages to GitHub Package Registry)
   - `read:org` (Read org and team membership)

## Step 2: Copy and Set Token

1. Copy the generated token (starts with `ghp_` or `github_pat_`)
2. Set environment variable:

### Windows (Command Prompt):
```cmd
set GITHUB_TOKEN=your_token_here
```

### Windows (PowerShell):
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

### Linux/Mac:
```bash
export GITHUB_TOKEN=your_token_here
```

### Or use .env file:
Add this line to `.env` file:
```
GITHUB_TOKEN=your_token_here
```

## Step 3: Test Integration

Run the test command:
```bash
python github-setup-agent.py
```

## Step 4: Verify Policy Integration

Test the GitHub Issues agent:
```bash
python github-issues-policy-agent.py
```

## Security Notes

- Never commit tokens to version control
- Use environment variables or secure vaults
- Rotate tokens regularly
- Use minimal required permissions

## Troubleshooting

- If token is invalid: regenerate on GitHub
- If API fails: check network/firewall
- If permissions fail: verify token scopes
