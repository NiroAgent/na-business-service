import { APIRequestContext } from '@playwright/test';

export class ApiClient {
  private baseUrl: string;

  constructor(private request: APIRequestContext, baseUrl: string = 'http://localhost:4000') {
    this.baseUrl = baseUrl;
  }

  async getHealth() {
    const response = await this.request.get(`${this.baseUrl}/health`);
    return {
      status: response.status(),
      data: await response.json()
    };
  }

  async getInstances() {
    const response = await this.request.get(`${this.baseUrl}/api/aws/instances`);
    return {
      status: response.status(),
      data: await response.json()
    };
  }

  async getCosts() {
    const response = await this.request.get(`${this.baseUrl}/api/cost/breakdown`);
    return {
      status: response.status(),
      data: await response.json()
    };
  }

  async getMonitoringStatus() {
    const response = await this.request.get(`${this.baseUrl}/api/monitoring/status`);
    return {
      status: response.status(),
      data: await response.json()
    };
  }

  async getCostTrends(environment: string) {
    const response = await this.request.get(`${this.baseUrl}/api/cost/trends/${environment}`);
    return {
      status: response.status(),
      data: await response.json()
    };
  }

  async getAlerts(environment?: string) {
    const url = environment 
      ? `${this.baseUrl}/api/monitoring/alerts/${environment}`
      : `${this.baseUrl}/api/monitoring/alerts`;
    
    const response = await this.request.get(url);
    return {
      status: response.status(),
      data: await response.json()
    };
  }

  async startMonitoring() {
    const response = await this.request.post(`${this.baseUrl}/api/monitoring/start`);
    return {
      status: response.status(),
      data: await response.json()
    };
  }

  async stopMonitoring() {
    const response = await this.request.post(`${this.baseUrl}/api/monitoring/stop`);
    return {
      status: response.status(),
      data: await response.json()
    };
  }
}

export const MockData = {
  instances: {
    totalInstances: 3,
    instancesByEnvironment: {
      'vf-dev': 1,
      'vf-staging': 1,
      'vf-production': 1
    },
    instances: [
      {
        id: 'i-test123',
        name: 'test-instance-1',
        environment: 'vf-dev',
        state: 'running',
        instanceType: 't3.micro',
        privateIP: '10.0.1.100',
        publicIP: '54.123.45.67',
        launchTime: '2025-08-19T10:30:00Z',
        tags: { Environment: 'vf-dev', Project: 'test' }
      }
    ],
    timestamp: new Date().toISOString()
  },

  costs: {
    totalCost: 142.50,
    currency: 'USD',
    period: {
      start: '2025-08-01',
      end: '2025-08-19'
    },
    byEnvironment: {
      'vf-dev': { cost: 35.20, instances: 1, percentage: 24.7 },
      'vf-staging': { cost: 48.80, instances: 1, percentage: 34.2 },
      'vf-production': { cost: 58.50, instances: 1, percentage: 41.1 }
    },
    byService: {
      'EC2': 89.30,
      'RDS': 32.40,
      'S3': 12.15,
      'CloudWatch': 5.45
    },
    trend: [
      { date: '2025-08-15', cost: 138.20 },
      { date: '2025-08-16', cost: 140.10 },
      { date: '2025-08-17', cost: 141.30 },
      { date: '2025-08-18', cost: 142.00 },
      { date: '2025-08-19', cost: 142.50 }
    ],
    timestamp: new Date().toISOString()
  },

  monitoring: {
    environments: {
      'vf-dev': {
        status: 'healthy',
        instances: 1,
        alerts: 0,
        lastUpdate: new Date().toISOString()
      },
      'vf-staging': {
        status: 'warning',
        instances: 1,
        alerts: 1,
        lastUpdate: new Date().toISOString()
      },
      'vf-production': {
        status: 'healthy',
        instances: 1,
        alerts: 0,
        lastUpdate: new Date().toISOString()
      }
    },
    totalInstances: 3,
    totalAlerts: 1,
    timestamp: new Date().toISOString()
  }
};

export function validateInstancesData(data: any) {
  const errors: string[] = [];

  if (typeof data.totalInstances !== 'number') {
    errors.push('totalInstances must be a number');
  }

  if (!data.instancesByEnvironment || typeof data.instancesByEnvironment !== 'object') {
    errors.push('instancesByEnvironment must be an object');
  }

  if (!Array.isArray(data.instances)) {
    errors.push('instances must be an array');
  }

  if (!data.timestamp || typeof data.timestamp !== 'string') {
    errors.push('timestamp must be a string');
  }

  return errors;
}

export function validateCostsData(data: any) {
  const errors: string[] = [];

  if (typeof data.totalCost !== 'number') {
    errors.push('totalCost must be a number');
  }

  if (data.currency !== 'USD') {
    errors.push('currency must be USD');
  }

  if (!data.period || !data.period.start || !data.period.end) {
    errors.push('period must have start and end dates');
  }

  if (!Array.isArray(data.trend)) {
    errors.push('trend must be an array');
  }

  return errors;
}

export function validateMonitoringData(data: any) {
  const errors: string[] = [];

  if (!data.environments || typeof data.environments !== 'object') {
    errors.push('environments must be an object');
  }

  if (typeof data.totalInstances !== 'number') {
    errors.push('totalInstances must be a number');
  }

  if (typeof data.totalAlerts !== 'number') {
    errors.push('totalAlerts must be a number');
  }

  // Check required environments
  const requiredEnvs = ['vf-dev', 'vf-staging', 'vf-production'];
  for (const env of requiredEnvs) {
    if (!data.environments[env]) {
      errors.push(`Missing environment: ${env}`);
    } else {
      const envData = data.environments[env];
      if (!['healthy', 'warning', 'error'].includes(envData.status)) {
        errors.push(`Invalid status for ${env}: ${envData.status}`);
      }
    }
  }

  return errors;
}
