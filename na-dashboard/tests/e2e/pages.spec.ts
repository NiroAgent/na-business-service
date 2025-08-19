import { test, expect } from '@playwright/test';

test.describe('Instances Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/instances');
    await page.waitForLoadState('networkidle');
  });

  test('should display instances table', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1')).toContainText('Instances');
    
    // Check instances table or empty state
    const instancesTable = page.locator('[data-testid="instances-table"]');
    const emptyState = page.locator('[data-testid="empty-instances"]');
    
    // Either table or empty state should be visible
    await expect(instancesTable.or(emptyState)).toBeVisible();
  });

  test('should filter instances by environment', async ({ page }) => {
    // Test environment filter
    await page.selectOption('[data-testid="environment-filter"]', 'vf-dev');
    
    // Wait for filter to apply
    await page.waitForTimeout(1000);
    
    // Check that filter is applied (URL or visible state change)
    await expect(page.locator('[data-testid="environment-filter"]')).toHaveValue('vf-dev');
  });

  test('should refresh instances data', async ({ page }) => {
    // Click refresh button
    await page.click('[data-testid="refresh-instances"]');
    
    // Check loading state appears
    await expect(page.locator('[data-testid="loading-instances"]')).toBeVisible();
    
    // Wait for loading to complete
    await page.waitForSelector('[data-testid="loading-instances"]', { state: 'hidden' });
  });

  test('should show instance details on click', async ({ page }) => {
    // Wait for any instances to load
    const instanceRow = page.locator('[data-testid^="instance-row-"]').first();
    
    if (await instanceRow.isVisible()) {
      await instanceRow.click();
      
      // Check instance details modal or panel opens
      await expect(page.locator('[data-testid="instance-details"]')).toBeVisible();
    }
  });
});

test.describe('Costs Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/costs');
    await page.waitForLoadState('networkidle');
  });

  test('should display cost breakdown', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Costs');
    
    // Check cost charts are present
    const pieChart = page.locator('[data-testid="cost-pie-chart"]');
    const lineChart = page.locator('[data-testid="cost-trend-chart"]');
    
    await expect(pieChart.or(lineChart)).toBeVisible();
  });

  test('should switch between environments', async ({ page }) => {
    // Test environment selector
    await page.selectOption('[data-testid="cost-environment-select"]', 'vf-staging');
    
    // Wait for data to update
    await page.waitForTimeout(1000);
    
    // Check environment selection is reflected
    await expect(page.locator('[data-testid="cost-environment-select"]')).toHaveValue('vf-staging');
  });

  test('should export cost data', async ({ page }) => {
    // Click export button
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-costs"]');
    
    // Wait for download to start
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/cost.*\.(csv|xlsx|pdf)$/);
  });
});

test.describe('Monitoring Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/monitoring');
    await page.waitForLoadState('networkidle');
  });

  test('should display monitoring status', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Monitoring');
    
    // Check monitoring cards
    await expect(page.locator('[data-testid="monitoring-status"]')).toBeVisible();
  });

  test('should start/stop real-time monitoring', async ({ page }) => {
    // Start monitoring
    await page.click('[data-testid="start-monitoring"]');
    
    // Check monitoring is active
    await expect(page.locator('[data-testid="monitoring-active"]')).toBeVisible();
    
    // Stop monitoring
    await page.click('[data-testid="stop-monitoring"]');
    
    // Check monitoring is stopped
    await expect(page.locator('[data-testid="monitoring-stopped"]')).toBeVisible();
  });

  test('should display alerts', async ({ page }) => {
    // Check alerts section
    const alertsSection = page.locator('[data-testid="alerts-section"]');
    await expect(alertsSection).toBeVisible();
    
    // Check for alerts or empty state
    const alertsList = page.locator('[data-testid="alerts-list"]');
    const noAlerts = page.locator('[data-testid="no-alerts"]');
    
    await expect(alertsList.or(noAlerts)).toBeVisible();
  });
});
