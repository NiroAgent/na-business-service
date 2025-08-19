# ⚠️ URGENT: API Key Rotation Required

## Your Anthropic API key is exposed in git history!

**Key found**: `[REDACTED - Key has been rotated and removed]`

## Immediate Actions Required:

### 1. Rotate the API Key NOW
1. Go to: https://console.anthropic.com/settings/keys
2. Delete/revoke the exposed key
3. Create a new API key
4. Copy the new key (you'll need it for step 2)

### 2. Store New Key in AWS Secrets Manager
```bash
# Store your new key securely
aws secretsmanager create-secret \
  --name anthropic-api-key \
  --description "Anthropic Claude API Key" \
  --secret-string "your-NEW-api-key-here"

# Or update if it exists
aws secretsmanager put-secret-value \
  --secret-id anthropic-api-key \
  --secret-string "your-NEW-api-key-here"
```

### 3. The Code is Ready
Your application will now:
- Retrieve the key from AWS Secrets Manager at runtime
- Never expose it in code or logs
- Cache it for performance

### 4. Clean Git History (After Key Rotation)
Once your key is rotated, we can either:
- Option A: Allow the old (revoked) key in GitHub (safe since it's dead)
- Option B: Completely rewrite git history (more complex)

## Why This Happened
The key was hardcoded in `START_CLAUDE.bat` in commit e4bac398891db3560edf28560554bf5fb8bb33bd

## Prevention
- ✅ Key now retrieved from AWS Secrets Manager
- ✅ .gitignore updated to exclude .env files
- ✅ Code updated to fetch at runtime
- ✅ No more hardcoded secrets

## Your New Secure Setup
```javascript
// Keys are fetched at runtime
const { getAnthropicApiKey } = require('./get-anthropic-key');
const apiKey = await getAnthropicApiKey(); // Retrieved from AWS
```

**ACTION REQUIRED: Rotate your key immediately at https://console.anthropic.com/settings/keys**