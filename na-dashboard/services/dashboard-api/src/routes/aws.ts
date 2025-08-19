import { Router } from 'express';
import { 
  EC2Client, 
  DescribeInstancesCommand,
  DescribeRegionsCommand 
} from '@aws-sdk/client-ec2';
import { 
  CloudWatchClient, 
  GetMetricStatisticsCommand,
  ListMetricsCommand 
} from '@aws-sdk/client-cloudwatch';
import { STSClient, AssumeRoleCommand } from '@aws-sdk/client-sts';

const router = Router();

// AWS Configuration
const AWS_ACCOUNTS = {
  'vf-dev': {
    accountId: '319040880702',
    roleArn: 'arn:aws:iam::319040880702:role/CrossAccountDashboardRole',
    region: 'us-east-1'
  },
  'vf-staging': {
    accountId: '275057778147', 
    roleArn: 'arn:aws:iam::275057778147:role/CrossAccountDashboardRole',
    region: 'us-east-1'
  },
  'vf-production': {
    accountId: '229742714212',
    roleArn: 'arn:aws:iam::229742714212:role/CrossAccountDashboardRole', 
    region: 'us-east-1'
  }
};

// Get AWS credentials for specific account
async function getAccountCredentials(environment: string) {
  const account = AWS_ACCOUNTS[environment as keyof typeof AWS_ACCOUNTS];
  if (!account) {
    throw new Error(`Unknown environment: ${environment}`);
  }

  const stsClient = new STSClient({ region: account.region });
  
  try {
    const assumeRoleCommand = new AssumeRoleCommand({
      RoleArn: account.roleArn,
      RoleSessionName: `dashboard-${environment}-${Date.now()}`,
      DurationSeconds: 3600
    });

    const response = await stsClient.send(assumeRoleCommand);
    
    if (!response.Credentials) {
      throw new Error('Failed to assume role');
    }

    return {
      accessKeyId: response.Credentials.AccessKeyId!,
      secretAccessKey: response.Credentials.SecretAccessKey!,
      sessionToken: response.Credentials.SessionToken!,
      region: account.region
    };
  } catch (error) {
    console.error(`Failed to assume role for ${environment}:`, error);
    throw error;
  }
}

// Get EC2 instances for an environment
router.get('/instances/:environment', async (req, res) => {
  try {
    const { environment } = req.params;
    const credentials = await getAccountCredentials(environment);
    
    const ec2Client = new EC2Client({
      credentials,
      region: credentials.region
    });

    const command = new DescribeInstancesCommand({});
    const response = await ec2Client.send(command);

    const instances = response.Reservations?.flatMap(reservation => 
      reservation.Instances?.map(instance => ({
        instanceId: instance.InstanceId,
        instanceType: instance.InstanceType,
        state: instance.State?.Name,
        launchTime: instance.LaunchTime,
        publicIpAddress: instance.PublicIpAddress,
        privateIpAddress: instance.PrivateIpAddress,
        tags: instance.Tags?.reduce((acc, tag) => {
          if (tag.Key && tag.Value) {
            acc[tag.Key] = tag.Value;
          }
          return acc;
        }, {} as Record<string, string>),
        environment,
        accountId: AWS_ACCOUNTS[environment as keyof typeof AWS_ACCOUNTS].accountId
      })) || []
    ) || [];

    res.json({
      environment,
      instanceCount: instances.length,
      instances,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error(`Error fetching instances for ${req.params.environment}:`, error);
    res.status(500).json({
      error: 'Failed to fetch instances',
      environment: req.params.environment,
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get instances across all environments
router.get('/instances', async (req, res) => {
  try {
    const allInstances: any[] = [];
    const errors: any[] = [];

    for (const environment of Object.keys(AWS_ACCOUNTS)) {
      try {
        const credentials = await getAccountCredentials(environment);
        
        const ec2Client = new EC2Client({
          credentials,
          region: credentials.region
        });

        const command = new DescribeInstancesCommand({});
        const response = await ec2Client.send(command);

        const instances = response.Reservations?.flatMap(reservation => 
          reservation.Instances?.map(instance => ({
            instanceId: instance.InstanceId,
            instanceType: instance.InstanceType,
            state: instance.State?.Name,
            launchTime: instance.LaunchTime,
            publicIpAddress: instance.PublicIpAddress,
            privateIpAddress: instance.PrivateIpAddress,
            tags: instance.Tags?.reduce((acc, tag) => {
              if (tag.Key && tag.Value) {
                acc[tag.Key] = tag.Value;
              }
              return acc;
            }, {} as Record<string, string>),
            environment,
            accountId: AWS_ACCOUNTS[environment as keyof typeof AWS_ACCOUNTS].accountId
          })) || []
        ) || [];

        allInstances.push(...instances);

  } catch (error) {
    console.error(`Error fetching instances for ${environment}:`, error);
    errors.push({
      environment,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
    }

    res.json({
      totalInstances: allInstances.length,
      instancesByEnvironment: Object.keys(AWS_ACCOUNTS).reduce((acc, env) => {
        acc[env] = allInstances.filter(i => i.environment === env).length;
        return acc;
      }, {} as Record<string, number>),
      instances: allInstances,
      errors: errors.length > 0 ? errors : undefined,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching all instances:', error);
    res.status(500).json({
      error: 'Failed to fetch instances',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get CloudWatch metrics for an instance
router.get('/metrics/:environment/:instanceId', async (req, res) => {
  try {
    const { environment, instanceId } = req.params;
    const credentials = await getAccountCredentials(environment);
    
    const cloudWatchClient = new CloudWatchClient({
      credentials,
      region: credentials.region
    });

    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - (24 * 60 * 60 * 1000)); // 24 hours ago

    // Get CPU utilization
    const cpuCommand = new GetMetricStatisticsCommand({
      Namespace: 'AWS/EC2',
      MetricName: 'CPUUtilization',
      Dimensions: [
        {
          Name: 'InstanceId',
          Value: instanceId
        }
      ],
      StartTime: startTime,
      EndTime: endTime,
      Period: 3600, // 1 hour intervals
      Statistics: ['Average', 'Maximum']
    });

    const cpuResponse = await cloudWatchClient.send(cpuCommand);

    res.json({
      instanceId,
      environment,
      metrics: {
        cpu: {
          datapoints: cpuResponse.Datapoints?.map(dp => ({
            timestamp: dp.Timestamp,
            average: dp.Average,
            maximum: dp.Maximum
          })) || []
        }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error(`Error fetching metrics for ${req.params.instanceId}:`, error);
    res.status(500).json({
      error: 'Failed to fetch metrics',
      instanceId: req.params.instanceId,
      environment: req.params.environment,
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get available AWS regions
router.get('/regions', async (req, res) => {
  try {
    // Use first available account credentials to list regions
    const environment = Object.keys(AWS_ACCOUNTS)[0];
    const credentials = await getAccountCredentials(environment);
    
    const ec2Client = new EC2Client({
      credentials,
      region: credentials.region
    });

    const command = new DescribeRegionsCommand({});
    const response = await ec2Client.send(command);

    const regions = response.Regions?.map(region => ({
      regionName: region.RegionName,
      endpoint: region.Endpoint
    })) || [];

    res.json({
      regions,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching regions:', error);
    res.status(500).json({
      error: 'Failed to fetch regions',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export { router as awsRouter };
