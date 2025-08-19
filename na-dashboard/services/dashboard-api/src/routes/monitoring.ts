import { Router } from 'express';
import { broadcast } from '../server';

const router = Router();

// Health monitoring endpoint
router.get('/health', (req, res) => {
  res.json({
    status: 'monitoring-active',
    checks: {
      api: 'healthy',
      websocket: 'active',
      aws: 'connected'
    },
    timestamp: new Date().toISOString()
  });
});

// Real-time monitoring status
router.get('/status', (req, res) => {
  // Simulate real-time status data
  const status = {
    environments: {
      'vf-dev': {
        status: 'healthy',
        instances: Math.floor(Math.random() * 10) + 5,
        alerts: Math.floor(Math.random() * 3),
        lastUpdate: new Date().toISOString()
      },
      'vf-staging': {
        status: 'healthy', 
        instances: Math.floor(Math.random() * 8) + 3,
        alerts: Math.floor(Math.random() * 2),
        lastUpdate: new Date().toISOString()
      },
      'vf-production': {
        status: 'healthy',
        instances: Math.floor(Math.random() * 15) + 10,
        alerts: Math.floor(Math.random() * 1),
        lastUpdate: new Date().toISOString()
      }
    },
    totalInstances: 0,
    totalAlerts: 0,
    timestamp: new Date().toISOString()
  };

  // Calculate totals
  status.totalInstances = Object.values(status.environments)
    .reduce((sum, env) => sum + env.instances, 0);
  status.totalAlerts = Object.values(status.environments)
    .reduce((sum, env) => sum + env.alerts, 0);

  res.json(status);
});

// Start real-time monitoring
router.post('/start', (req, res) => {
  const { interval = 30000 } = req.body; // Default 30 seconds

  // Simulate starting monitoring
  console.log(`Starting real-time monitoring with ${interval}ms interval`);

  // Send confirmation
  res.json({
    status: 'monitoring-started',
    interval,
    timestamp: new Date().toISOString()
  });

  // Broadcast start event
  broadcast({
    type: 'monitoring-started',
    interval,
    timestamp: new Date().toISOString()
  });
});

// Stop real-time monitoring  
router.post('/stop', (req, res) => {
  console.log('Stopping real-time monitoring');

  res.json({
    status: 'monitoring-stopped',
    timestamp: new Date().toISOString()
  });

  // Broadcast stop event
  broadcast({
    type: 'monitoring-stopped',
    timestamp: new Date().toISOString()
  });
});

// Get alerts for environment
router.get('/alerts/:environment?', (req, res) => {
  const { environment } = req.params;

  // Simulate alert data
  const alerts = [
    {
      id: '1',
      environment: environment || 'vf-production',
      type: 'warning',
      message: 'High CPU utilization detected',
      resource: 'i-1234567890abcdef0',
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 mins ago
      resolved: false
    },
    {
      id: '2', 
      environment: environment || 'vf-dev',
      type: 'info',
      message: 'Instance launched successfully',
      resource: 'i-0987654321fedcba0',
      timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(), // 1 hour ago
      resolved: true
    }
  ];

  const filteredAlerts = environment 
    ? alerts.filter(alert => alert.environment === environment)
    : alerts;

  res.json({
    environment: environment || 'all',
    alertCount: filteredAlerts.length,
    alerts: filteredAlerts,
    timestamp: new Date().toISOString()
  });
});

// Send test alert (for testing WebSocket broadcast)
router.post('/test-alert', (req, res) => {
  const { environment = 'vf-dev', type = 'info', message = 'Test alert' } = req.body;

  const alert = {
    id: `test-${Date.now()}`,
    environment,
    type,
    message,
    resource: 'test-resource',
    timestamp: new Date().toISOString(),
    resolved: false
  };

  // Broadcast alert to all connected clients
  broadcast({
    type: 'alert',
    data: alert
  });

  res.json({
    status: 'alert-sent',
    alert,
    timestamp: new Date().toISOString()
  });
});

// WebSocket endpoint for real-time updates
router.get('/stream', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');

  // Send initial connection message
  res.write(`data: ${JSON.stringify({
    type: 'connected',
    timestamp: new Date().toISOString()
  })}\n\n`);

  // Send periodic updates
  const interval = setInterval(() => {
    const data = {
      type: 'status-update',
      timestamp: new Date().toISOString(),
      data: {
        totalInstances: Math.floor(Math.random() * 30) + 20,
        activeAlerts: Math.floor(Math.random() * 5),
        environments: {
          'vf-dev': { instances: Math.floor(Math.random() * 10) + 5 },
          'vf-staging': { instances: Math.floor(Math.random() * 8) + 3 },
          'vf-production': { instances: Math.floor(Math.random() * 15) + 10 }
        }
      }
    };

    res.write(`data: ${JSON.stringify(data)}\n\n`);
  }, 10000); // Every 10 seconds

  // Clean up on client disconnect
  req.on('close', () => {
    clearInterval(interval);
  });
});

export { router as monitoringRouter };
