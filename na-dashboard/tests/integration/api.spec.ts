import { test, expect } from '@playwright/test';

const API_BASE_URL = 'http://localhost:4000';

test.describe('API Health Checks', () => {
  test('should return healthy status', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/health`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.service).toBe('dashboard-api');
    expect(data.version).toBe('1.0.0');
  });

  test('should have proper response headers', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/health`);
    
    expect(response.headers()['content-type']).toContain('application/json');
    expect(response.headers()['access-control-allow-origin']).toBeDefined();
  });
});

test.describe('AWS Instances API', () => {
  test('should return instances data structure', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/aws/instances`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('totalInstances');
    expect(data).toHaveProperty('instancesByEnvironment');
    expect(data).toHaveProperty('instances');
    expect(data).toHaveProperty('timestamp');
    
    // Check data types
    expect(typeof data.totalInstances).toBe('number');
    expect(Array.isArray(data.instances)).toBe(true);
    expect(typeof data.instancesByEnvironment).toBe('object');
  });

  test('should include AWS access information in development', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/aws/instances`);
    const data = await response.json();
    
    // In development mode, should include error information
    if (data.totalInstances === 0) {
      expect(data).toHaveProperty('errors');
      expect(data).toHaveProperty('note');
      expect(data.note).toContain('AWS access not configured');
    }
  });

  test('should handle environment filtering', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/aws/instances`);
    const data = await response.json();
    
    // Check environment breakdown
    expect(data.instancesByEnvironment).toHaveProperty('vf-dev');
    expect(data.instancesByEnvironment).toHaveProperty('vf-staging');
    expect(data.instancesByEnvironment).toHaveProperty('vf-production');
  });
});

test.describe('Cost Breakdown API', () => {
  test('should return cost data structure', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/cost/breakdown`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('totalCost');
    expect(data).toHaveProperty('currency');
    expect(data).toHaveProperty('period');
    expect(data).toHaveProperty('byEnvironment');
    expect(data).toHaveProperty('byService');
    expect(data).toHaveProperty('trend');
    expect(data).toHaveProperty('timestamp');
    
    // Check data types
    expect(typeof data.totalCost).toBe('number');
    expect(data.currency).toBe('USD');
    expect(typeof data.period).toBe('object');
    expect(Array.isArray(data.trend)).toBe(true);
  });

  test('should have valid cost calculations', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/cost/breakdown`);
    const data = await response.json();
    
    // Total cost should be non-negative
    expect(data.totalCost).toBeGreaterThanOrEqual(0);
    
    // Period should have start and end dates
    expect(data.period).toHaveProperty('start');
    expect(data.period).toHaveProperty('end');
    
    // Trend data should have proper structure
    if (data.trend.length > 0) {
      const trendItem = data.trend[0];
      expect(trendItem).toHaveProperty('date');
      expect(trendItem).toHaveProperty('cost');
      expect(typeof trendItem.cost).toBe('number');
    }
  });
});

test.describe('Monitoring Status API', () => {
  test('should return monitoring data structure', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/monitoring/status`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('environments');
    expect(data).toHaveProperty('totalInstances');
    expect(data).toHaveProperty('totalAlerts');
    expect(data).toHaveProperty('timestamp');
    
    // Check environment data structure
    expect(data.environments).toHaveProperty('vf-dev');
    expect(data.environments).toHaveProperty('vf-staging');
    expect(data.environments).toHaveProperty('vf-production');
    
    // Check environment properties
    const envData = data.environments['vf-dev'];
    expect(envData).toHaveProperty('status');
    expect(envData).toHaveProperty('instances');
    expect(envData).toHaveProperty('alerts');
    expect(envData).toHaveProperty('lastUpdate');
  });

  test('should have valid monitoring status values', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/monitoring/status`);
    const data = await response.json();
    
    // Check total values are non-negative
    expect(data.totalInstances).toBeGreaterThanOrEqual(0);
    expect(data.totalAlerts).toBeGreaterThanOrEqual(0);
    
    // Check environment status values are valid
    Object.values(data.environments).forEach((env: any) => {
      expect(['healthy', 'warning', 'error']).toContain(env.status);
      expect(env.instances).toBeGreaterThanOrEqual(0);
      expect(env.alerts).toBeGreaterThanOrEqual(0);
    });
  });
});

test.describe('API Error Handling', () => {
  test('should return 404 for unknown endpoints', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/unknown/endpoint`);
    
    expect(response.status()).toBe(404);
    
    const data = await response.json();
    expect(data).toHaveProperty('error');
    expect(data.error).toBe('Not Found');
  });

  test('should handle malformed requests gracefully', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/aws/instances`, {
      data: { invalid: 'data' }
    });
    
    // Should return method not allowed or bad request
    expect([400, 405]).toContain(response.status());
  });

  test('should have CORS headers', async ({ request }) => {
    const response = await request.options(`${API_BASE_URL}/api/aws/instances`);
    
    const headers = response.headers();
    expect(headers['access-control-allow-origin']).toBeDefined();
    expect(headers['access-control-allow-methods']).toBeDefined();
  });
});

test.describe('API Performance', () => {
  test('should respond within reasonable time', async ({ request }) => {
    const startTime = Date.now();
    
    const response = await request.get(`${API_BASE_URL}/health`);
    
    const responseTime = Date.now() - startTime;
    
    expect(response.status()).toBe(200);
    expect(responseTime).toBeLessThan(1000); // Should respond within 1 second
  });

  test('should handle concurrent requests', async ({ request }) => {
    const requests = Array(10).fill(null).map(() => 
      request.get(`${API_BASE_URL}/health`)
    );
    
    const responses = await Promise.all(requests);
    
    responses.forEach(response => {
      expect(response.status()).toBe(200);
    });
  });
});

test.describe('API Data Consistency', () => {
  test('should maintain data consistency across endpoints', async ({ request }) => {
    // Get data from both instances and monitoring endpoints
    const [instancesResponse, monitoringResponse] = await Promise.all([
      request.get(`${API_BASE_URL}/api/aws/instances`),
      request.get(`${API_BASE_URL}/api/monitoring/status`)
    ]);
    
    const instancesData = await instancesResponse.json();
    const monitoringData = await monitoringResponse.json();
    
    // Total instances should match between endpoints
    expect(instancesData.totalInstances).toBe(monitoringData.totalInstances);
    
    // Environment instance counts should match
    expect(instancesData.instancesByEnvironment['vf-dev'])
      .toBe(monitoringData.environments['vf-dev'].instances);
    expect(instancesData.instancesByEnvironment['vf-staging'])
      .toBe(monitoringData.environments['vf-staging'].instances);
    expect(instancesData.instancesByEnvironment['vf-production'])
      .toBe(monitoringData.environments['vf-production'].instances);
  });
});
