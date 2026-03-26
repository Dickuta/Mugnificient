import { test, expect } from '@playwright/test';

test.describe('Forecasting (Staff Only)', () => {
  test.beforeEach(async ({ page }) => {
    // Login as warehouse staff
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'warehouse');
    await page.fill('input[label="Password"]', 'warehouse123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');
  });

  test('should access forecasting page', async ({ page }) => {
    await page.goto('/forecasting');
    await expect(page.locator('.text-h4')).toContainText(/Forecasting/i);
  });

  test('should display product forecasts', async ({ page }) => {
    await page.goto('/forecasting');
    await expect(page.locator('.q-tab')).toContainText(/Product Forecasts/i);
  });

  test('should view seasonal patterns', async ({ page }) => {
    await page.goto('/forecasting');
    await page.click('.q-tab:has-text("Seasonal Patterns")');
    await expect(page.locator('.text-h6')).toContainText(/Monthly Demand/i);
  });

  test('should view auto-order settings', async ({ page }) => {
    await page.goto('/forecasting');
    await page.click('.q-tab:has-text("Auto-Order Settings")');
    await expect(page.locator('.q-table')).toBeVisible();
  });

  test('should view purchase orders', async ({ page }) => {
    await page.goto('/forecasting');
    await page.click('.q-tab:has-text("Purchase Orders")');
    await expect(page.locator('.q-table')).toBeVisible();
  });
});

test.describe('Inventory ML (Staff Only)', () => {
  test.beforeEach(async ({ page }) => {
    // Login as warehouse staff
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'warehouse');
    await page.fill('input[label="Password"]', 'warehouse123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');
  });

  test('should access inventory ML page', async ({ page }) => {
    await page.goto('/inventory-ml');
    await expect(page.locator('.text-h4')).toContainText(/Inventory ML/i);
  });

  test('should display predictions', async ({ page }) => {
    await page.goto('/inventory-ml');
    await expect(page.locator('.q-tab')).toContainText(/Predictions/i);
  });

  test('should view refill requests', async ({ page }) => {
    await page.goto('/inventory-ml');
    await page.click('.q-tab:has-text("Refill Requests")');
    await expect(page.locator('.q-table')).toBeVisible();
  });
});

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'admin');
    await page.fill('input[label="Password"]', 'admin123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');
  });

  test('should access admin dashboard', async ({ page }) => {
    await page.goto('/admin');
    await expect(page.locator('.text-h4')).toContainText(/Dashboard/i);
  });

  test('should access RBAC management', async ({ page }) => {
    await page.goto('/admin/rbac');
    await expect(page.locator('.text-h4')).toContainText(/RBAC/i);
  });
});

test.describe('Access Control', () => {
  test('customer should not access forecasting', async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'student1');
    await page.fill('input[label="Password"]', 'student123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');
    
    await page.goto('/forecasting');
    await expect(page.locator('text=Staff access required')).toBeVisible();
  });

  test('unauthenticated user should be redirected', async ({ page }) => {
    await page.goto('/forecasting');
    await expect(page).toHaveURL(/.*login/);
  });
});
