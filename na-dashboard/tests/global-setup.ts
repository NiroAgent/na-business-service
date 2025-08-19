import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  // Wait for services to be ready
  console.log('🚀 Starting global test setup...');
  
  // Verify API is responding
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Wait for API health check
    console.log('⏳ Waiting for API to be ready...');
    await page.goto('http://localhost:4000/health', { waitUntil: 'networkidle' });
    const apiResponse = await page.textContent('pre');
    console.log('✅ API is ready:', apiResponse);
    
    // Wait for frontend to be ready
    console.log('⏳ Waiting for frontend to be ready...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    console.log('✅ Frontend is ready');
    
    // Create test data or setup if needed
    console.log('🔧 Setting up test environment...');
    
    // You can add API calls here to set up test data
    // For example, creating mock AWS resources for testing
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
  
  console.log('✅ Global setup complete');
}

export default globalSetup;
