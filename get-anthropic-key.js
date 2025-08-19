// get-anthropic-key.js
// Retrieves Anthropic API key from AWS Secrets Manager at runtime

const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager({ region: 'us-east-1' });

let cachedApiKey = null;
let cacheExpiry = null;

/**
 * Retrieves the Anthropic API key from AWS Secrets Manager
 * Caches the key for 1 hour to avoid excessive API calls
 * @returns {Promise<string>} The API key
 */
async function getAnthropicApiKey() {
    // Check cache first
    if (cachedApiKey && cacheExpiry && new Date() < cacheExpiry) {
        return cachedApiKey;
    }

    try {
        const secret = await secretsManager.getSecretValue({ 
            SecretId: 'visualforge-ai/api-keys/development' 
        }).promise();
        
        // Parse the JSON secret and extract the Anthropic key
        const secretData = JSON.parse(secret.SecretString);
        cachedApiKey = secretData.ANTHROPIC_API_KEY;
        
        if (!cachedApiKey) {
            throw new Error('ANTHROPIC_API_KEY not found in secret');
        }
        
        cacheExpiry = new Date(Date.now() + 3600000); // Cache for 1 hour
        
        return cachedApiKey;
    } catch (error) {
        console.error('Failed to retrieve API key from Secrets Manager:', error);
        throw new Error('Unable to retrieve Anthropic API key');
    }
}

module.exports = { getAnthropicApiKey };