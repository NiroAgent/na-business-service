import { Router } from 'express';
import { 
  CostExplorerClient, 
  GetCostAndUsageCommand,
  GetDimensionValuesCommand 
} from '@aws-sdk/client-cost-explorer';
import { STSClient, AssumeRoleCommand } from '@aws-sdk/client-sts';

const router = Router();

// AWS Configuration - Cost Explorer is only available in us-east-1
const AWS_ACCOUNTS = {
  'vf-dev': {
    accountId: '319040880702',
    roleArn: 'arn:aws:iam::319040880702:role/CrossAccountDashboardRole'
  },
  'vf-staging': {
    accountId: '275057778147', 
    roleArn: 'arn:aws:iam::275057778147:role/CrossAccountDashboardRole'
  },
  'vf-production': {
    accountId: '229742714212',
    roleArn: 'arn:aws:iam::229742714212:role/CrossAccountDashboardRole'
  }
};

// Get AWS credentials for specific account
async function getAccountCredentials(environment: string) {
  const account = AWS_ACCOUNTS[environment as keyof typeof AWS_ACCOUNTS];
  if (!account) {
    throw new Error(`Unknown environment: ${environment}`);
  }

  const stsClient = new STSClient({ region: 'us-east-1' });
  
  try {
    const assumeRoleCommand = new AssumeRoleCommand({
      RoleArn: account.roleArn,
      RoleSessionName: `dashboard-cost-${environment}-${Date.now()}`,
      DurationSeconds: 3600
    });

    const response = await stsClient.send(assumeRoleCommand);
    
    if (!response.Credentials) {
      throw new Error('Failed to assume role');
    }

    return {
      accessKeyId: response.Credentials.AccessKeyId!,
      secretAccessKey: response.Credentials.SecretAccessKey!,
      sessionToken: response.Credentials.SessionToken!
    };
  } catch (error) {
    console.error(`Failed to assume role for ${environment}:`, error);
    throw error;
  }
}

// Get cost breakdown for specific environment
router.get('/breakdown/:environment', async (req, res) => {
  try {
    const { environment } = req.params;
    const { period = '30' } = req.query;
    
    const credentials = await getAccountCredentials(environment);
    
    const costExplorerClient = new CostExplorerClient({
      credentials,
      region: 'us-east-1' // Cost Explorer only available in us-east-1
    });

    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - parseInt(period as string));

    const command = new GetCostAndUsageCommand({
      TimePeriod: {
        Start: startDate.toISOString().split('T')[0],
        End: endDate.toISOString().split('T')[0]
      },
      Granularity: 'DAILY',
      Metrics: ['BlendedCost', 'UnblendedCost', 'UsageQuantity'],
      GroupBy: [
        {
          Type: 'DIMENSION',
          Key: 'SERVICE'
        }
      ]
    });

    const response = await costExplorerClient.send(command);

    // Process the cost data
    const costBreakdown = response.ResultsByTime?.map(result => ({
      date: result.TimePeriod?.Start,
      total: parseFloat(result.Total?.BlendedCost?.Amount || '0'),
      currency: result.Total?.BlendedCost?.Unit || 'USD',
      services: result.Groups?.map(group => ({
        service: group.Keys?.[0] || 'Unknown',
        cost: parseFloat(group.Metrics?.BlendedCost?.Amount || '0'),
        currency: group.Metrics?.BlendedCost?.Unit || 'USD'
      })) || []
    })) || [];

    // Calculate totals
    const totalCost = costBreakdown.reduce((sum, day) => sum + day.total, 0);
    const avgDailyCost = totalCost / Math.max(costBreakdown.length, 1);

    // Service breakdown
    const serviceMap = new Map<string, number>();
    costBreakdown.forEach(day => {
      day.services.forEach(service => {
        const current = serviceMap.get(service.service) || 0;
        serviceMap.set(service.service, current + service.cost);
      });
    });

    const topServices = Array.from(serviceMap.entries())
      .map(([service, cost]) => ({ service, cost }))
      .sort((a, b) => b.cost - a.cost)
      .slice(0, 10);

    res.json({
      environment,
      period: parseInt(period as string),
      totalCost: Math.round(totalCost * 100) / 100,
      avgDailyCost: Math.round(avgDailyCost * 100) / 100,
      currency: 'USD',
      dailyBreakdown: costBreakdown,
      topServices,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error(`Error fetching cost breakdown for ${req.params.environment}:`, error);
    res.status(500).json({
      error: 'Failed to fetch cost breakdown',
      environment: req.params.environment,
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get cost breakdown across all environments
router.get('/breakdown', async (req, res) => {
  try {
    const { period = '30' } = req.query;
    const allCosts = [];
    const errors = [];

    for (const environment of Object.keys(AWS_ACCOUNTS)) {
      try {
        const credentials = await getAccountCredentials(environment);
        
        const costExplorerClient = new CostExplorerClient({
          credentials,
          region: 'us-east-1'
        });

        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - parseInt(period as string));

        const command = new GetCostAndUsageCommand({
          TimePeriod: {
            Start: startDate.toISOString().split('T')[0],
            End: endDate.toISOString().split('T')[0]
          },
          Granularity: 'MONTHLY',
          Metrics: ['BlendedCost'],
          GroupBy: [
            {
              Type: 'DIMENSION',
              Key: 'SERVICE'
            }
          ]
        });

        const response = await costExplorerClient.send(command);

        const totalCost = response.ResultsByTime?.reduce((sum, result) => {
          return sum + parseFloat(result.Total?.BlendedCost?.Amount || '0');
        }, 0) || 0;

        const serviceBreakdown = new Map<string, number>();
        response.ResultsByTime?.forEach(result => {
          result.Groups?.forEach(group => {
            const service = group.Keys?.[0] || 'Unknown';
            const cost = parseFloat(group.Metrics?.BlendedCost?.Amount || '0');
            const current = serviceBreakdown.get(service) || 0;
            serviceBreakdown.set(service, current + cost);
          });
        });

        const topServices = Array.from(serviceBreakdown.entries())
          .map(([service, cost]) => ({ service, cost }))
          .sort((a, b) => b.cost - a.cost)
          .slice(0, 5);

        allCosts.push({
          environment,
          accountId: AWS_ACCOUNTS[environment as keyof typeof AWS_ACCOUNTS].accountId,
          totalCost: Math.round(totalCost * 100) / 100,
          topServices,
          currency: 'USD'
        });

      } catch (error) {
        console.error(`Error fetching cost for ${environment}:`, error);
        errors.push({
          environment,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }

    const grandTotal = allCosts.reduce((sum, env) => sum + env.totalCost, 0);

    res.json({
      period: parseInt(period as string),
      grandTotal: Math.round(grandTotal * 100) / 100,
      currency: 'USD',
      environments: allCosts,
      errors: errors.length > 0 ? errors : undefined,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching all costs:', error);
    res.status(500).json({
      error: 'Failed to fetch cost breakdown',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get cost trends over time
router.get('/trends/:environment', async (req, res) => {
  try {
    const { environment } = req.params;
    const { period = '90' } = req.query;
    
    const credentials = await getAccountCredentials(environment);
    
    const costExplorerClient = new CostExplorerClient({
      credentials,
      region: 'us-east-1'
    });

    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - parseInt(period as string));

    const command = new GetCostAndUsageCommand({
      TimePeriod: {
        Start: startDate.toISOString().split('T')[0],
        End: endDate.toISOString().split('T')[0]
      },
      Granularity: 'DAILY',
      Metrics: ['BlendedCost']
    });

    const response = await costExplorerClient.send(command);

    const trends = response.ResultsByTime?.map(result => ({
      date: result.TimePeriod?.Start,
      cost: parseFloat(result.Total?.BlendedCost?.Amount || '0'),
      currency: result.Total?.BlendedCost?.Unit || 'USD'
    })) || [];

    // Calculate moving averages
    const movingAverage7Day = trends.map((item, index) => {
      if (index < 6) return { ...item, movingAvg: item.cost };
      
      const sum = trends.slice(index - 6, index + 1)
        .reduce((sum, t) => sum + t.cost, 0);
      return { ...item, movingAvg: sum / 7 };
    });

    res.json({
      environment,
      period: parseInt(period as string),
      trends: movingAverage7Day,
      totalCost: trends.reduce((sum, t) => sum + t.cost, 0),
      avgDailyCost: trends.reduce((sum, t) => sum + t.cost, 0) / Math.max(trends.length, 1),
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error(`Error fetching cost trends for ${req.params.environment}:`, error);
    res.status(500).json({
      error: 'Failed to fetch cost trends',
      environment: req.params.environment,
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export { router as costRouter };
