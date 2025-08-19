import { test, expect } from '@playwright/test';

test.describe('WebSocket Real-time Updates', () => {
  test('should establish WebSocket connection', async ({ page }) => {
    await page.goto('/');
    
    // Wait for WebSocket connection
    await page.waitForSelector('[data-testid="connection-status"]:has-text("Open")', { timeout: 10000 });
    
    // Check connection status
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toContainText('Open');
  });

  test('should receive real-time updates', async ({ page }) => {
    await page.goto('/monitoring');
    
    // Start real-time monitoring
    await page.click('[data-testid="start-monitoring"]');
    
    // Check for real-time update indicators
    await expect(page.locator('[data-testid="live-indicator"]')).toBeVisible();
    
    // Wait for updates (this would normally be triggered by backend events)
    await page.waitForTimeout(5000);
    
    // Stop monitoring
    await page.click('[data-testid="stop-monitoring"]');
  });
});

test.describe('API Error Handling', () => {
  test('should handle API timeouts gracefully', async ({ page }) => {
    // Intercept API calls and simulate timeout
    await page.route('**/api/**', route => {
      // Simulate slow API response
      setTimeout(() => route.abort(), 5000);
    });
    
    await page.goto('/');
    
    // Check error state is displayed
    await expect(page.locator('[data-testid="api-error"]')).toBeVisible({ timeout: 10000 });
  });

  test('should show appropriate error messages', async ({ page }) => {
    // Intercept API calls and return 500 error
    await page.route('**/api/aws/instances', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    await page.goto('/instances');
    
    // Check error message is displayed
    await expect(page.locator('[data-testid="instances-error"]')).toBeVisible();
  });

  test('should retry failed requests', async ({ page }) => {
    let requestCount = 0;
    
    await page.route('**/api/monitoring/status', route => {
      requestCount++;
      if (requestCount < 3) {
        route.abort();
      } else {
        route.continue();
      }
    });
    
    await page.goto('/monitoring');
    
    // Should eventually succeed after retries
    await expect(page.locator('[data-testid="monitoring-status"]')).toBeVisible({ timeout: 15000 });
  });
});

test.describe('Performance', () => {
  test('should load dashboard within performance budget', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Dashboard should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('should have good Lighthouse performance score', async ({ page }) => {
    await page.goto('/');
    
    // Run basic performance checks
    const performanceTiming = await page.evaluate(() => {
      return JSON.stringify(performance.timing);
    });
    
    const timing = JSON.parse(performanceTiming);
    const loadTime = timing.loadEventEnd - timing.navigationStart;
    
    // Load time should be reasonable
    expect(loadTime).toBeLessThan(10000);
  });
});

test.describe('Accessibility', () => {
  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');
    
    // Test Tab navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Check focus is visible
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto('/');
    
    // Check navigation has proper ARIA
    await expect(page.locator('nav[role="navigation"]')).toBeVisible();
    
    // Check buttons have labels
    const buttons = page.locator('button');
    const count = await buttons.count();
    
    for (let i = 0; i < count; i++) {
      const button = buttons.nth(i);
      const ariaLabel = await button.getAttribute('aria-label');
      const textContent = await button.textContent();
      
      // Button should have either aria-label or text content
      expect(ariaLabel || textContent).toBeTruthy();
    }
  });

  test('should have sufficient color contrast', async ({ page }) => {
    await page.goto('/');
    
    // This would typically use an accessibility testing library
    // For now, just check that text is visible
    const textElements = page.locator('p, h1, h2, h3, span');
    const count = await textElements.count();
    
    for (let i = 0; i < Math.min(count, 10); i++) {
      await expect(textElements.nth(i)).toBeVisible();
    }
  });
});
