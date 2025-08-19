import { test, expect } from '@playwright/test';

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the dashboard homepage', async ({ page }) => {
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check page title
    await expect(page).toHaveTitle(/Dashboard/);
    
    // Check main navigation is visible
    await expect(page.locator('nav')).toBeVisible();
    
    // Check the header title (NiroAgent Dashboard)
    await expect(page.locator('header h1')).toContainText('NiroAgent Dashboard');
    
    // Check the main page title (Dashboard)
    await expect(page.locator('main h1')).toContainText('Dashboard');
    
    // Check that we have the expected content structure
    await expect(page.locator('main')).toBeVisible();
  });

  test('should navigate to all main sections', async ({ page }) => {
    // Test Dashboard navigation
    await page.click('[data-testid="nav-dashboard"]');
    await expect(page.locator('main h1')).toContainText('Dashboard');
    
    // Test Instances navigation
    await page.click('[data-testid="nav-ec2-instances"]');
    await expect(page.locator('main h1')).toBeVisible();
    
    // Test Costs navigation
    await page.click('[data-testid="nav-cost-analysis"]');
    await expect(page.locator('main h1')).toBeVisible();
    
    // Test Monitoring navigation
    await page.click('[data-testid="nav-real-time-monitoring"]');
    await expect(page.locator('main h1')).toBeVisible();
  });

  test('should show connection status', async ({ page }) => {
    // Check WebSocket connection status is displayed
    await expect(page.locator('[data-testid="connection-status"]')).toBeVisible();
    
    // Wait for connection to establish
    await page.waitForSelector('[data-testid="connection-status"]:has-text("Open")', { timeout: 10000 });
  });
});

test.describe('Dashboard Data Loading', () => {
  test('should load and display instance metrics', async ({ page }) => {
    await page.goto('/');
    
    // Wait for API calls to complete
    await page.waitForLoadState('networkidle');
    
    // Check total instances card
    const instancesCard = page.locator('[data-testid="total-instances-card"]');
    await expect(instancesCard).toBeVisible();
    
    // Check that instance count is displayed (could be 0 in demo mode)
    const instanceCount = instancesCard.locator('[data-testid="instance-count"]');
    await expect(instanceCount).toBeVisible();
  });

  test('should load and display cost metrics', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check cost card
    const costCard = page.locator('[data-testid="total-cost-card"]');
    await expect(costCard).toBeVisible();
    
    // Check cost amount is displayed
    const costAmount = costCard.locator('[data-testid="cost-amount"]');
    await expect(costAmount).toBeVisible();
  });

  test('should show environment status', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check all three environment cards
    await expect(page.locator('[data-testid="env-vf-dev"]')).toBeVisible();
    await expect(page.locator('[data-testid="env-vf-staging"]')).toBeVisible();
    await expect(page.locator('[data-testid="env-vf-production"]')).toBeVisible();
  });
});

test.describe('Responsive Design', () => {
  test('should work on mobile devices', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check mobile navigation works
    await page.click('[data-testid="mobile-menu-button"]');
    await expect(page.locator('[data-testid="mobile-nav"]')).toBeVisible();
  });

  test('should work on tablet devices', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    
    // Check layout adapts to tablet
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('[data-testid="dashboard-grid"]')).toBeVisible();
  });
});
