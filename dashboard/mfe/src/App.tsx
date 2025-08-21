import React, { useState, useEffect } from 'react';
import { 
  Box, 
  CssBaseline, 
  ThemeProvider, 
  createTheme,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  IconButton,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Memory as MemoryIcon,
  Terminal as TerminalIcon,
  GitHub as GitHubIcon,
  Refresh as RefreshIcon,
  PowerSettingsNew as PowerIcon,
  CloudUpload as DeployIcon
} from '@mui/icons-material';
import { Toaster } from 'react-hot-toast';

import AgentGrid from './components/AgentGrid';
import SystemMetrics from './components/SystemMetrics';
import TerminalView from './components/TerminalView';
import IssuePanel from './components/IssuePanel';
import { useSocket } from './hooks/useSocket';
import { Agent, SystemInfo } from './types';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00ff88',
    },
    secondary: {
      main: '#ff00ff',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
  typography: {
    fontFamily: '"Fira Code", "Roboto Mono", monospace',
  },
});

function App() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [showTerminal, setShowTerminal] = useState(false);
  const [showIssues, setShowIssues] = useState(false);
  
  const socket = useSocket();

  // Fetch agents data via HTTP
  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:4001/api/dashboard/agents');
      if (response.ok) {
        const data = await response.json();
        setAgents(data.agents || []);
      }
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  // Fetch initial agents data
  useEffect(() => {
    fetchAgents();
    // Refresh every 5 seconds
    const interval = setInterval(fetchAgents, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!socket) return;

    socket.on('agents:status', (data: Agent[]) => {
      setAgents(data);
    });

    socket.on('system:metrics', (data: SystemInfo) => {
      setSystemInfo(data);
    });

    return () => {
      socket.off('agents:status');
      socket.off('system:metrics');
    };
  }, [socket]);

  const handleStartAgent = async (agentId: string) => {
    try {
      const response = await fetch(`http://localhost:4001/api/dashboard/agents/${agentId}/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'start' })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Agent started:', result);
        // Refresh agents list
        fetchAgents();
      } else {
        console.error('Failed to start agent:', await response.text());
      }
    } catch (error) {
      console.error('Error starting agent:', error);
    }
  };

  const handleStopAgent = async (agentId: string) => {
    try {
      const response = await fetch(`http://localhost:4001/api/dashboard/agents/${agentId}/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'stop' })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Agent stopped:', result);
        // Refresh agents list
        fetchAgents();
      } else {
        console.error('Failed to stop agent:', await response.text());
      }
    } catch (error) {
      console.error('Error stopping agent:', error);
    }
  };

  const handleRestartAgent = async (agentId: string) => {
    try {
      const response = await fetch(`http://localhost:4001/api/dashboard/agents/${agentId}/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'restart' })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Agent restarted:', result);
        // Refresh agents list
        fetchAgents();
      } else {
        console.error('Failed to restart agent:', await response.text());
      }
    } catch (error) {
      console.error('Error restarting agent:', error);
    }
  };

  const handleViewTerminal = (agentId: string) => {
    setSelectedAgent(agentId);
    setShowTerminal(true);
  };

  const handleDeployAllAgents = async () => {
    try {
      const response = await fetch('http://localhost:4001/api/dashboard/deploy-all', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('All agents deployed:', result);
        // Refresh agents list after deployment
        setTimeout(fetchAgents, 5000); // Wait 5 seconds for deployment to complete
      } else {
        console.error('Failed to deploy agents:', await response.text());
      }
    } catch (error) {
      console.error('Error deploying agents:', error);
    }
  };

  const runningAgents = agents.filter(a => a.status === 'idle' || a.status === 'busy').length;
  const totalAgents = agents.length;

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Toaster position="top-right" />
      
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" elevation={0} sx={{ 
          background: 'linear-gradient(90deg, #1a1a1a 0%, #2a2a2a 100%)',
          borderBottom: '1px solid #00ff88'
        }}>
          <Toolbar>
            <DashboardIcon sx={{ mr: 2, color: '#00ff88' }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Agent Orchestrator Dashboard
            </Typography>
            
            <Tooltip title="System Resources">
              <IconButton color="inherit">
                <Badge badgeContent={systemInfo?.cpu.toFixed(0) + '%'} color="secondary">
                  <MemoryIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Running Agents">
              <IconButton color="inherit">
                <Badge badgeContent={`${runningAgents}/${totalAgents}`} color="primary">
                  <PowerIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            
            <Tooltip title="View Terminals">
              <IconButton 
                color="inherit" 
                onClick={() => setShowTerminal(!showTerminal)}
                sx={{ color: showTerminal ? '#00ff88' : 'inherit' }}
              >
                <TerminalIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="GitHub Issues">
              <IconButton 
                color="inherit"
                onClick={() => setShowIssues(!showIssues)}
                sx={{ color: showIssues ? '#00ff88' : 'inherit' }}
              >
                <GitHubIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Deploy All Agents">
              <IconButton 
                color="inherit" 
                onClick={handleDeployAllAgents}
                sx={{ color: '#ff8800' }}
              >
                <DeployIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Refresh All">
              <IconButton color="inherit" onClick={() => window.location.reload()}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Toolbar>
        </AppBar>

        <Container maxWidth={false} sx={{ mt: 3 }}>
          <Grid container spacing={3}>
            {/* System Metrics */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2, background: '#1a1a1a', border: '1px solid #333' }}>
                <Typography variant="h6" gutterBottom sx={{ color: '#00ff88' }}>
                  System Resources
                </Typography>
                <SystemMetrics data={systemInfo} />
              </Paper>
            </Grid>

            {/* Agent Grid */}
            <Grid item xs={12} lg={showTerminal || showIssues ? 6 : 12}>
              <Paper sx={{ p: 2, background: '#1a1a1a', border: '1px solid #333' }}>
                <Typography variant="h6" gutterBottom sx={{ color: '#00ff88' }}>
                  Agents ({runningAgents} running)
                </Typography>
                <AgentGrid 
                  agents={agents}
                  onStart={handleStartAgent}
                  onStop={handleStopAgent}
                  onRestart={handleRestartAgent}
                  onViewTerminal={handleViewTerminal}
                />
              </Paper>
            </Grid>

            {/* Terminal View */}
            {showTerminal && (
              <Grid item xs={12} lg={6}>
                <Paper sx={{ 
                  p: 2, 
                  background: '#0a0a0a', 
                  border: '1px solid #00ff88',
                  height: '600px',
                  overflow: 'hidden'
                }}>
                  <Typography variant="h6" gutterBottom sx={{ color: '#00ff88' }}>
                    Terminal - {agents.find(a => a.id === selectedAgent)?.name || 'Select Agent'}
                  </Typography>
                  {selectedAgent && (
                    <TerminalView 
                      agentId={selectedAgent} 
                      socket={socket}
                    />
                  )}
                </Paper>
              </Grid>
            )}

            {/* GitHub Issues Panel */}
            {showIssues && !showTerminal && (
              <Grid item xs={12} lg={6}>
                <Paper sx={{ 
                  p: 2, 
                  background: '#1a1a1a', 
                  border: '1px solid #333',
                  height: '600px',
                  overflow: 'auto'
                }}>
                  <Typography variant="h6" gutterBottom sx={{ color: '#00ff88' }}>
                    GitHub Issues (agent-task)
                  </Typography>
                  <IssuePanel />
                </Paper>
              </Grid>
            )}
          </Grid>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;