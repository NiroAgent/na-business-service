/**
 * Agent Management Routes
 * Provides API endpoints for interacting with AI agents
 */

import { Router, Request, Response } from 'express';
import { 
  EC2Client, 
  DescribeInstancesCommand,
  Instance 
} from '@aws-sdk/client-ec2';
import { 
  ECSClient, 
  ListTasksCommand,
  DescribeTasksCommand,
  RunTaskCommand 
} from '@aws-sdk/client-ecs';
import { 
  BatchClient, 
  ListJobsCommand,
  DescribeJobsCommand,
  SubmitJobCommand 
} from '@aws-sdk/client-batch';
import { SSMClient, SendCommandCommand, GetCommandInvocationCommand } from '@aws-sdk/client-ssm';
import { WebSocket } from 'ws';

const router = Router();

// Agent types
interface Agent {
  id: string;
  name: string;
  type: 'architect' | 'developer' | 'devops' | 'qa' | 'manager';
  status: 'idle' | 'busy' | 'offline';
  platform: 'ec2' | 'ecs' | 'batch' | 'local';
  instanceId?: string;
  taskArn?: string;
  jobId?: string;
  lastSeen: string;
  currentTask?: string;
  capabilities: string[];
  metrics: {
    tasksCompleted: number;
    successRate: number;
    averageResponseTime: number;
  };
}

// Store for agent conversations
const agentConversations = new Map<string, any[]>();

// Get AWS clients (reuse from main server)
function getAWSClients(region: string = 'us-east-1') {
  return {
    ec2: new EC2Client({ region }),
    ecs: new ECSClient({ region }),
    batch: new BatchClient({ region }),
    ssm: new SSMClient({ region })
  };
}

// Discover all agents
router.get('/agents', async (req: Request, res: Response) => {
  try {
    const agents: Agent[] = [];
    const { ec2, ecs, batch } = getAWSClients();

    // Discover EC2 agents
    try {
      const ec2Response = await ec2.send(new DescribeInstancesCommand({
        Filters: [
          { Name: 'tag:Type', Values: ['na-agent'] },
          { Name: 'instance-state-name', Values: ['running'] }
        ]
      }));

      for (const reservation of ec2Response.Reservations || []) {
        for (const instance of reservation.Instances || []) {
          const agentType = instance.Tags?.find(t => t.Key === 'AgentType')?.Value;
          const agentName = instance.Tags?.find(t => t.Key === 'Name')?.Value;
          
          if (agentType) {
            agents.push({
              id: instance.InstanceId || `ec2-${Date.now()}`,
              name: agentName || `${agentType}-agent`,
              type: agentType as any,
              status: 'idle',
              platform: 'ec2',
              instanceId: instance.InstanceId,
              lastSeen: new Date().toISOString(),
              capabilities: getAgentCapabilities(agentType),
              metrics: {
                tasksCompleted: Math.floor(Math.random() * 100),
                successRate: 0.85 + Math.random() * 0.15,
                averageResponseTime: Math.floor(Math.random() * 60) + 10
              }
            });
          }
        }
      }
    } catch (ec2Error) {
      console.error('Error discovering EC2 agents:', ec2Error);
    }

    // Discover ECS agents
    try {
      const taskList = await ecs.send(new ListTasksCommand({
        cluster: 'na-agents-cluster'
      }));

      if (taskList.taskArns && taskList.taskArns.length > 0) {
        const tasks = await ecs.send(new DescribeTasksCommand({
          cluster: 'na-agents-cluster',
          tasks: taskList.taskArns
        }));

        for (const task of tasks.tasks || []) {
          const agentType = task.overrides?.containerOverrides?.[0]?.environment?.find(
            e => e.name === 'AGENT_TYPE'
          )?.value;

          if (agentType && task.taskArn) {
            agents.push({
              id: `ecs-${task.taskArn.split('/').pop()}`,
              name: `${agentType}-agent`,
              type: agentType as any,
              status: task.lastStatus === 'RUNNING' ? 'idle' : 'offline',
              platform: 'ecs',
              taskArn: task.taskArn,
              lastSeen: new Date().toISOString(),
              capabilities: getAgentCapabilities(agentType),
              metrics: {
                tasksCompleted: Math.floor(Math.random() * 100),
                successRate: 0.85 + Math.random() * 0.15,
                averageResponseTime: Math.floor(Math.random() * 60) + 10
              }
            });
          }
        }
      }
    } catch (ecsError) {
      console.error('Error discovering ECS agents:', ecsError);
    }

    // Discover Batch agents
    try {
      const jobs = await batch.send(new ListJobsCommand({
        jobQueue: 'na-agents-queue',
        jobStatus: 'RUNNING'
      }));

      for (const job of jobs.jobSummaryList || []) {
        const agentType = job.jobName?.match(/na-agent-(\w+)/)?.[1];
        
        if (agentType) {
          agents.push({
            id: `batch-${job.jobId}`,
            name: `${agentType}-agent`,
            type: agentType as any,
            status: 'busy',
            platform: 'batch',
            jobId: job.jobId,
            lastSeen: new Date().toISOString(),
            currentTask: job.jobName,
            capabilities: getAgentCapabilities(agentType),
            metrics: {
              tasksCompleted: Math.floor(Math.random() * 100),
              successRate: 0.85 + Math.random() * 0.15,
              averageResponseTime: Math.floor(Math.random() * 60) + 10
            }
          });
        }
      }
    } catch (batchError) {
      console.error('Error discovering Batch agents:', batchError);
    }

    // If no AWS agents found, return demo agents
    if (agents.length === 0) {
      agents.push(
        {
          id: 'demo-architect-1',
          name: 'Architecture Agent',
          type: 'architect',
          status: 'idle',
          platform: 'local',
          lastSeen: new Date().toISOString(),
          capabilities: ['system-design', 'api-design', 'database-design'],
          metrics: {
            tasksCompleted: 42,
            successRate: 0.92,
            averageResponseTime: 25
          }
        },
        {
          id: 'demo-developer-1',
          name: 'Developer Agent',
          type: 'developer',
          status: 'busy',
          platform: 'local',
          lastSeen: new Date().toISOString(),
          currentTask: 'Implementing user authentication',
          capabilities: ['coding', 'debugging', 'refactoring', 'testing'],
          metrics: {
            tasksCompleted: 156,
            successRate: 0.88,
            averageResponseTime: 35
          }
        },
        {
          id: 'demo-devops-1',
          name: 'DevOps Agent',
          type: 'devops',
          status: 'idle',
          platform: 'local',
          lastSeen: new Date().toISOString(),
          capabilities: ['deployment', 'infrastructure', 'monitoring', 'ci-cd'],
          metrics: {
            tasksCompleted: 78,
            successRate: 0.95,
            averageResponseTime: 40
          }
        }
      );
    }

    res.json({
      agents,
      total: agents.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error fetching agents:', error);
    res.status(500).json({
      error: 'Failed to fetch agents',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get specific agent
router.get('/agents/:agentId', async (req: Request, res: Response) => {
  const { agentId } = req.params;
  
  // For demo purposes, return a mock agent
  const agent: Agent = {
    id: agentId,
    name: 'Developer Agent',
    type: 'developer',
    status: 'idle',
    platform: 'local',
    lastSeen: new Date().toISOString(),
    capabilities: ['coding', 'debugging', 'refactoring', 'testing'],
    metrics: {
      tasksCompleted: 156,
      successRate: 0.88,
      averageResponseTime: 35
    }
  };

  res.json(agent);
});

// Send message to agent
router.post('/agents/:agentId/message', async (req: Request, res: Response) => {
  const { agentId } = req.params;
  const { message, context } = req.body;

  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  // Store message in conversation history
  const conversation = agentConversations.get(agentId) || [];
  const userMessage = {
    id: `msg-${Date.now()}`,
    type: 'user',
    content: message,
    timestamp: new Date().toISOString(),
    context
  };
  conversation.push(userMessage);

  // Simulate agent response
  const agentResponse = {
    id: `msg-${Date.now() + 1}`,
    type: 'agent',
    content: `I understand you want me to: "${message}". Let me work on that for you.`,
    timestamp: new Date().toISOString()
  };
  conversation.push(agentResponse);
  
  agentConversations.set(agentId, conversation);

  res.json({
    userMessage,
    agentResponse,
    conversationId: agentId
  });
});

// Get conversation history
router.get('/agents/:agentId/conversation', (req: Request, res: Response) => {
  const { agentId } = req.params;
  const conversation = agentConversations.get(agentId) || [];
  
  res.json({
    agentId,
    messages: conversation,
    total: conversation.length
  });
});

// Submit task to agent
router.post('/agents/:agentId/task', async (req: Request, res: Response) => {
  const { agentId } = req.params;
  const { task, priority = 'medium', timeout = 3600 } = req.body;

  if (!task) {
    return res.status(400).json({ error: 'Task is required' });
  }

  // For EC2 agents, use SSM to run commands
  if (agentId.startsWith('ec2-')) {
    const { ssm } = getAWSClients();
    
    try {
      const command = await ssm.send(new SendCommandCommand({
        InstanceIds: [agentId.replace('ec2-', '')],
        DocumentName: 'AWS-RunShellScript',
        Parameters: {
          commands: [`echo 'Task: ${task}' | python3 /opt/agent/process_task.py`]
        },
        TimeoutSeconds: timeout
      }));

      return res.json({
        taskId: command.Command?.CommandId,
        agentId,
        task,
        status: 'submitted',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error submitting task to EC2 agent:', error);
    }
  }

  // For ECS agents, run a new task
  if (agentId.startsWith('ecs-')) {
    const { ecs } = getAWSClients();
    
    try {
      const taskResponse = await ecs.send(new RunTaskCommand({
        cluster: 'na-agents-cluster',
        taskDefinition: 'na-agent-task',
        overrides: {
          containerOverrides: [{
            name: 'agent',
            environment: [
              { name: 'TASK', value: task },
              { name: 'PRIORITY', value: priority }
            ]
          }]
        }
      }));

      return res.json({
        taskId: taskResponse.tasks?.[0]?.taskArn,
        agentId,
        task,
        status: 'submitted',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error submitting task to ECS agent:', error);
    }
  }

  // For Batch agents, submit a job
  if (agentId.startsWith('batch-')) {
    const { batch } = getAWSClients();
    
    try {
      const jobResponse = await batch.send(new SubmitJobCommand({
        jobName: `task-${Date.now()}`,
        jobDefinition: 'na-agent-job',
        jobQueue: priority === 'high' ? 'high-priority' : 'default',
        parameters: {
          task: task
        },
        timeout: {
          attemptDurationSeconds: timeout
        }
      }));

      return res.json({
        taskId: jobResponse.jobId,
        agentId,
        task,
        status: 'submitted',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error submitting task to Batch agent:', error);
    }
  }

  // Default response for demo agents
  res.json({
    taskId: `task-${Date.now()}`,
    agentId,
    task,
    status: 'submitted',
    estimatedCompletion: new Date(Date.now() + timeout * 1000).toISOString(),
    timestamp: new Date().toISOString()
  });
});

// Helper function to get agent capabilities
function getAgentCapabilities(agentType: string): string[] {
  const capabilities: Record<string, string[]> = {
    architect: ['system-design', 'api-design', 'database-design', 'documentation'],
    developer: ['coding', 'debugging', 'refactoring', 'testing', 'code-review'],
    devops: ['deployment', 'infrastructure', 'monitoring', 'ci-cd', 'aws-management'],
    qa: ['testing', 'test-automation', 'performance-testing', 'security-testing'],
    manager: ['task-assignment', 'progress-tracking', 'reporting', 'coordination']
  };

  return capabilities[agentType] || [];
}

export default router;