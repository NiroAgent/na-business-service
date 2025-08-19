import { Page } from '@playwright/test';

export class DashboardPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  async waitForDataLoad() {
    // Wait for all API calls to complete
    await this.page.waitForLoadState('networkidle');
    
    // Wait for specific elements to appear
    await this.page.waitForSelector('[data-testid="total-instances-card"]', { timeout: 10000 });
  }

  async getTotalInstances() {
    const element = this.page.locator('[data-testid="instance-count"]');
    const text = await element.textContent();
    return parseInt(text || '0');
  }

  async getTotalCost() {
    const element = this.page.locator('[data-testid="cost-amount"]');
    const text = await element.textContent();
    const match = text?.match(/\$?([\d,]+\.?\d*)/);
    return parseFloat(match?.[1]?.replace(',', '') || '0');
  }

  async getConnectionStatus() {
    const element = this.page.locator('[data-testid="connection-status"]');
    return await element.textContent();
  }

  async navigateToInstances() {
    await this.page.click('[data-testid="nav-instances"]');
    await this.page.waitForURL('**/instances');
  }

  async navigateToCosts() {
    await this.page.click('[data-testid="nav-costs"]');
    await this.page.waitForURL('**/costs');
  }

  async navigateToMonitoring() {
    await this.page.click('[data-testid="nav-monitoring"]');
    await this.page.waitForURL('**/monitoring');
  }
}

export class InstancesPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/instances');
    await this.page.waitForLoadState('networkidle');
  }

  async filterByEnvironment(environment: string) {
    await this.page.selectOption('[data-testid="environment-filter"]', environment);
    await this.page.waitForTimeout(1000);
  }

  async refreshInstances() {
    await this.page.click('[data-testid="refresh-instances"]');
    await this.page.waitForSelector('[data-testid="loading-instances"]', { state: 'hidden' });
  }

  async getInstanceCount() {
    const rows = this.page.locator('[data-testid^="instance-row-"]');
    return await rows.count();
  }

  async clickInstance(index: number = 0) {
    const rows = this.page.locator('[data-testid^="instance-row-"]');
    await rows.nth(index).click();
  }

  async isEmptyState() {
    return await this.page.locator('[data-testid="empty-instances"]').isVisible();
  }
}

export class CostsPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/costs');
    await this.page.waitForLoadState('networkidle');
  }

  async selectEnvironment(environment: string) {
    await this.page.selectOption('[data-testid="cost-environment-select"]', environment);
    await this.page.waitForTimeout(1000);
  }

  async exportCosts() {
    const downloadPromise = this.page.waitForEvent('download');
    await this.page.click('[data-testid="export-costs"]');
    return await downloadPromise;
  }

  async isPieChartVisible() {
    return await this.page.locator('[data-testid="cost-pie-chart"]').isVisible();
  }

  async isTrendChartVisible() {
    return await this.page.locator('[data-testid="cost-trend-chart"]').isVisible();
  }
}

export class MonitoringPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/monitoring');
    await this.page.waitForLoadState('networkidle');
  }

  async startMonitoring() {
    await this.page.click('[data-testid="start-monitoring"]');
    await this.page.waitForSelector('[data-testid="monitoring-active"]');
  }

  async stopMonitoring() {
    await this.page.click('[data-testid="stop-monitoring"]');
    await this.page.waitForSelector('[data-testid="monitoring-stopped"]');
  }

  async getAlertCount() {
    const element = this.page.locator('[data-testid="alert-count"]');
    const text = await element.textContent();
    return parseInt(text || '0');
  }

  async isMonitoringActive() {
    return await this.page.locator('[data-testid="monitoring-active"]').isVisible();
  }

  async hasAlerts() {
    return await this.page.locator('[data-testid="alerts-list"]').isVisible();
  }
}
