#!/usr/bin/env node

const { exec } = require('child_process');

const API_PORT = 4001;
const FRONTEND_PORT = 3001;

function log(message) {
  console.log(`[TEST-CLEANUP] ${new Date().toISOString()} - ${message}`);
}

function killPort(port) {
  return new Promise((resolve) => {
    log(`Killing processes on port ${port}...`);
    
    // Windows-compatible approach
    exec(`npx kill-port ${port}`, (error, stdout, stderr) => {
      if (error) {
        log(`Error killing port ${port}: ${error.message}`);
      } else {
        log(`Successfully killed port ${port}`);
      }
      resolve();
    });
  });
}

function killByName(processName) {
  return new Promise((resolve) => {
    log(`Killing processes by name: ${processName}...`);
    
    // Windows-compatible approach
    exec(`taskkill /F /IM ${processName}.exe 2>nul || true`, (error) => {
      if (error) {
        log(`No ${processName} processes to kill`);
      } else {
        log(`Killed ${processName} processes`);
      }
      resolve();
    });
  });
}

async function cleanup() {
  try {
    log('Cleaning up test servers...');
    
    // Kill by port
    await Promise.all([
      killPort(API_PORT),
      killPort(FRONTEND_PORT)
    ]);
    
    // Kill by process name
    await Promise.all([
      killByName('node'),
      killByName('nodemon')
    ]);
    
    log('Cleanup complete! ✅');
    
  } catch (error) {
    log(`Error during cleanup: ${error.message}`);
  }
}

if (require.main === module) {
  cleanup().then(() => process.exit(0));
}

module.exports = { cleanup };
