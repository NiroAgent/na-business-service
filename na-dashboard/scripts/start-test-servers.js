#!/usr/bin/env node

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const TIMEOUT = 60000; // 60 seconds
const API_PORT = 4001;
const FRONTEND_PORT = 3001;

let apiProcess = null;
let frontendProcess = null;

function log(message) {
  console.log(`[TEST-STARTUP] ${new Date().toISOString()} - ${message}`);
}

function cleanup() {
  log('Cleaning up processes...');
  
  if (apiProcess) {
    try {
      process.kill(-apiProcess.pid, 'SIGTERM');
    } catch (e) {
      log(`Error killing API process: ${e.message}`);
    }
  }
  
  if (frontendProcess) {
    try {
      process.kill(-frontendProcess.pid, 'SIGTERM');
    } catch (e) {
      log(`Error killing frontend process: ${e.message}`);
    }
  }
  
  // Kill any remaining processes on our ports
  exec(`npx kill-port ${API_PORT} ${FRONTEND_PORT}`, (error) => {
    if (error) {
      log(`Error killing ports: ${error.message}`);
    }
    process.exit(0);
  });
}

function isPortOpen(port) {
  return new Promise((resolve) => {
    const net = require('net');
    const socket = new net.Socket();
    
    socket.setTimeout(1000);
    socket.on('connect', () => {
      socket.destroy();
      resolve(true);
    });
    
    socket.on('timeout', () => {
      socket.destroy();
      resolve(false);
    });
    
    socket.on('error', () => {
      resolve(false);
    });
    
    socket.connect(port, 'localhost');
  });
}

async function waitForPort(port, maxWaitTime = 30000) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < maxWaitTime) {
    if (await isPortOpen(port)) {
      log(`Port ${port} is ready!`);
      return true;
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  log(`Timeout waiting for port ${port}`);
  return false;
}

async function startAPI() {
  return new Promise((resolve, reject) => {
    log('Starting API server...');
    
    const apiDir = path.join(__dirname, '..', 'services', 'dashboard-api');
    
    apiProcess = spawn('npm', ['run', 'dev'], {
      cwd: apiDir,
      stdio: ['pipe', 'pipe', 'pipe'],
      detached: true,
      shell: true
    });
    
    let output = '';
    
    apiProcess.stdout.on('data', (data) => {
      output += data.toString();
      const lines = data.toString().split('\n');
      lines.forEach(line => {
        if (line.trim()) {
          log(`[API] ${line.trim()}`);
        }
      });
      
      if (output.includes('Server running on port') || output.includes('listening on')) {
        resolve();
      }
    });
    
    apiProcess.stderr.on('data', (data) => {
      const lines = data.toString().split('\n');
      lines.forEach(line => {
        if (line.trim()) {
          log(`[API-ERROR] ${line.trim()}`);
        }
      });
    });
    
    apiProcess.on('error', (error) => {
      log(`API process error: ${error.message}`);
      reject(error);
    });
    
    apiProcess.on('exit', (code) => {
      if (code !== 0) {
        log(`API process exited with code ${code}`);
        reject(new Error(`API process exited with code ${code}`));
      }
    });
    
    // Timeout fallback
    setTimeout(() => {
      resolve(); // Resolve anyway and check port
    }, 15000);
  });
}

async function startFrontend() {
  return new Promise((resolve, reject) => {
    log('Starting frontend server...');
    
    const frontendDir = path.join(__dirname, '..', 'services', 'dashboard-mfe');
    
    frontendProcess = spawn('npm', ['run', 'dev'], {
      cwd: frontendDir,
      stdio: ['pipe', 'pipe', 'pipe'],
      detached: true,
      shell: true
    });
    
    let output = '';
    
    frontendProcess.stdout.on('data', (data) => {
      output += data.toString();
      const lines = data.toString().split('\n');
      lines.forEach(line => {
        if (line.trim()) {
          log(`[FRONTEND] ${line.trim()}`);
        }
      });
      
      if (output.includes('Local:') || output.includes('ready')) {
        resolve();
      }
    });
    
    frontendProcess.stderr.on('data', (data) => {
      const lines = data.toString().split('\n');
      lines.forEach(line => {
        if (line.trim()) {
          log(`[FRONTEND-ERROR] ${line.trim()}`);
        }
      });
    });
    
    frontendProcess.on('error', (error) => {
      log(`Frontend process error: ${error.message}`);
      reject(error);
    });
    
    frontendProcess.on('exit', (code) => {
      if (code !== 0) {
        log(`Frontend process exited with code ${code}`);
        reject(new Error(`Frontend process exited with code ${code}`));
      }
    });
    
    // Timeout fallback
    setTimeout(() => {
      resolve(); // Resolve anyway and check port
    }, 15000);
  });
}

async function main() {
  try {
    log('Starting test servers...');
    
    // Set up cleanup handlers
    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);
    process.on('exit', cleanup);
    
    // Start both servers in parallel
    await Promise.all([
      startAPI(),
      startFrontend()
    ]);
    
    // Wait for both ports to be ready
    log('Waiting for services to be ready...');
    const apiReady = await waitForPort(API_PORT);
    const frontendReady = await waitForPort(FRONTEND_PORT);
    
    if (!apiReady) {
      throw new Error(`API server not ready on port ${API_PORT}`);
    }
    
    if (!frontendReady) {
      throw new Error(`Frontend server not ready on port ${FRONTEND_PORT}`);
    }
    
    log('All services are ready! 🚀');
    log(`API: http://localhost:${API_PORT}`);
    log(`Frontend: http://localhost:${FRONTEND_PORT}`);
    
    // Keep the process alive
    setInterval(() => {
      // Health check every 30 seconds
    }, 30000);
    
  } catch (error) {
    log(`Error starting servers: ${error.message}`);
    cleanup();
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { main, cleanup };
