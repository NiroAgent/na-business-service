import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global test teardown...');
  
  try {
    // Clean up test data
    console.log('🗑️ Cleaning up test data...');
    
    // Stop docker containers if running in CI
    if (process.env.CI) {
      const { exec } = require('child_process');
      await new Promise((resolve, reject) => {
        exec('docker-compose down', (error: any, stdout: string, stderr: string) => {
          if (error) {
            console.warn('Warning: Could not stop docker containers:', error);
          } else {
            console.log('🐳 Docker containers stopped');
          }
          resolve(void 0);
        });
      });
    }
    
    console.log('✅ Global teardown complete');
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error here as it would fail the entire test suite
  }
}

export default globalTeardown;
