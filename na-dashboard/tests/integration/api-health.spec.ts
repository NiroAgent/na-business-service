import { test, expect } from '@playwright/test';

test.describe('API Health Checks', () => {
  test('should have API server running', async ({ request }) => {
    const response = await request.get('http://localhost:4001/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.timestamp).toBeTruthy();
  });

  test('should return AWS instances data', async ({ request }) => {
    const response = await request.get('http://localhost:4001/api/aws/instances');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('totalInstances');
    expect(data).toHaveProperty('instancesByEnvironment');
    expect(data).toHaveProperty('instances');
    expect(data).toHaveProperty('timestamp');
    expect(Array.isArray(data.instances)).toBe(true);
  });

  test('should return cost data', async ({ request }) => {
    const response = await request.get('http://localhost:4001/api/cost/breakdown');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('totalCost');
    expect(data).toHaveProperty('currency');
    expect(data).toHaveProperty('byEnvironment');
    expect(typeof data.totalCost).toBe('number');
  });

  test('should return monitoring status', async ({ request }) => {
    const response = await request.get('http://localhost:4001/api/monitoring/status');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('environments');
    expect(data).toHaveProperty('totalInstances');
    expect(data).toHaveProperty('totalAlerts');
  });
});
