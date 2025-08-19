#!/usr/bin/env node

const { spawn } = require('child_process');

function log(message) {
  console.log(`[QUICK-TEST] ${new Date().toISOString()} - ${message}`);
}

async function runQuickTest() {
  try {
    log('🚀 Running quick dashboard test...');
    
    const testProcess = spawn('npm', ['run', 'test:e2e', '--', '--grep', 'should load the dashboard homepage', '--workers=1', '--project=chromium'], {
      cwd: process.cwd(),
      stdio: 'inherit',
      shell: true
    });
    
    testProcess.on('close', (code) => {
      if (code === 0) {
        log('✅ Quick test passed! Dashboard is working correctly.');
        log('🎯 You can now run full tests with: npm run test:e2e');
        log('🌐 Or view the dashboard at: http://localhost:3001');
        log('📊 API available at: http://localhost:4001');
      } else {
        log('❌ Quick test failed. Check the logs above for details.');
      }
      process.exit(code);
    });
    
    testProcess.on('error', (error) => {
      log(`Error running test: ${error.message}`);
      process.exit(1);
    });
    
  } catch (error) {
    log(`Error: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  runQuickTest();
}

module.exports = { runQuickTest };
