// anthropic-client.js
// Example of using the Anthropic API with runtime key retrieval

const { getAnthropicApiKey } = require('./get-anthropic-key');
const Anthropic = require('@anthropic-ai/sdk');

let anthropicClient = null;

/**
 * Gets or creates an Anthropic client with the API key from Secrets Manager
 * @returns {Promise<Anthropic>} Configured Anthropic client
 */
async function getAnthropicClient() {
    if (!anthropicClient) {
        const apiKey = await getAnthropicApiKey();
        anthropicClient = new Anthropic({
            apiKey: apiKey,
        });
    }
    return anthropicClient;
}

/**
 * Example function to send a message to Claude
 * @param {string} message - The message to send
 * @returns {Promise<string>} Claude's response
 */
async function askClaude(message) {
    try {
        const client = await getAnthropicClient();
        
        const response = await client.messages.create({
            model: 'claude-3-opus-20240229',
            max_tokens: 1000,
            messages: [
                {
                    role: 'user',
                    content: message
                }
            ]
        });
        
        return response.content[0].text;
    } catch (error) {
        console.error('Error calling Claude API:', error);
        throw error;
    }
}

module.exports = { getAnthropicClient, askClaude };