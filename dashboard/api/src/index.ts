import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import path from 'path';
import dotenv from 'dotenv';

import { AgentManager } from './services/AgentManager';
import { SystemMonitor } from './services/SystemMonitor';
import { TerminalManager } from './services/TerminalManager';
import { GitHubService } from './services/GitHubService';
import agentRoutes from './routes/agents';
import systemRoutes from './routes/system';
import githubRoutes from './routes/github';

dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: process.env.FRONTEND_URL || 'http://localhost:5173',
    methods: ['GET', 'POST', 'PUT', 'DELETE']
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../../frontend/dist')));

// Initialize services
const agentManager = new AgentManager();
const systemMonitor = new SystemMonitor();
const terminalManager = new TerminalManager(io);
const githubService = new GitHubService();

// Make services available to routes
app.locals.agentManager = agentManager;
app.locals.systemMonitor = systemMonitor;
app.locals.terminalManager = terminalManager;
app.locals.githubService = githubService;

// Routes
app.use('/api/agents', agentRoutes);
app.use('/api/system', systemRoutes);
app.use('/api/github', githubRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      agents: agentManager.getStatus(),
      system: systemMonitor.getStatus()
    }
  });
});

// Socket.IO connections
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Send initial state
  socket.emit('agents:status', agentManager.getAllAgents());
  socket.emit('system:metrics', systemMonitor.getMetrics());

  // Terminal subscriptions
  socket.on('terminal:subscribe', (agentId: string) => {
    terminalManager.subscribe(socket, agentId);
  });

  socket.on('terminal:unsubscribe', (agentId: string) => {
    terminalManager.unsubscribe(socket, agentId);
  });

  socket.on('terminal:input', ({ agentId, data }: { agentId: string; data: string }) => {
    terminalManager.sendInput(agentId, data);
  });

  // Agent control
  socket.on('agent:start', async (agentId: string) => {
    const result = await agentManager.startAgent(agentId);
    socket.emit('agent:started', result);
    io.emit('agents:status', agentManager.getAllAgents());
  });

  socket.on('agent:stop', async (agentId: string) => {
    const result = await agentManager.stopAgent(agentId);
    socket.emit('agent:stopped', result);
    io.emit('agents:status', agentManager.getAllAgents());
  });

  socket.on('agent:restart', async (agentId: string) => {
    await agentManager.restartAgent(agentId);
    io.emit('agents:status', agentManager.getAllAgents());
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    terminalManager.unsubscribeAll(socket);
  });
});

// Start monitoring
setInterval(() => {
  // Broadcast system metrics
  io.emit('system:metrics', systemMonitor.getMetrics());
  
  // Broadcast agent status
  io.emit('agents:status', agentManager.getAllAgents());
}, 2000); // Every 2 seconds

// Start server
const PORT = process.env.PORT || 3001;
httpServer.listen(PORT, () => {
  console.log(`🚀 Agent Dashboard Backend running on http://localhost:${PORT}`);
  console.log(`📊 Frontend should connect to ws://localhost:${PORT}`);
  
  // Initialize agents on startup
  agentManager.initializeAgents();
});

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n⏹️  Shutting down gracefully...');
  await agentManager.stopAllAgents();
  process.exit(0);
});