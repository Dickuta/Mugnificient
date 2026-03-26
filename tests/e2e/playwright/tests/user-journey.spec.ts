import { test, expect } from '@playwright/test';

/**
 * Complete user journey E2E tests
 * Tests the full workflow from registration to checkout
 */

test.describe('Complete Customer Journey', () => {
  test('should complete full shopping flow', async ({ page }) => {
    // Step 1: Visit homepage
    await page.goto('/');
    await expect(page.locator('.text-h4')).toContainText(/Welcome/i);

    // Step 2: Navigate to products
    await page.click('a[href="/products"]');
    await page.waitForURL('/products');
    await expect(page.locator('.text-h4')).toBeVisible();

    // Step 3: View product details
    await page.waitForSelector('.product-card', { timeout: 10000 });
    await page.click('.product-card >> nth=0');
    
    // Step 4: Register new user
    await page.goto('/auth/register');
    await page.fill('input[label="Username"]', `testuser${Date.now()}`);
    await page.fill('input[label="Email"]', `test${Date.now()}@example.com`);
    await page.fill('input[label="Password"]', 'testpass123');
    await page.fill('input[label="Confirm Password"]', 'testpass123');
    await page.click('button:has-text("Register")');

    // Step 5: Login
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', `testuser${Date.now()}`);
    await page.fill('input[label="Password"]', 'testpass123');
    await page.click('button:has-text("Login")');
    
    // Step 6: Go to cart
    await page.goto('/cart');
    await expect(page.locator('.text-h4')).toContainText(/Cart/i);
  });
});

test.describe('Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'student1');
    await page.fill('input[label="Password"]', 'student123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');
  });

  test('should display checkout page', async ({ page }) => {
    await page.goto('/checkout');
    await expect(page.locator('.text-h4')).toContainText(/Checkout/i);
  });
});

test.describe('Order History', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'student1');
    await page.fill('input[label="Password"]', 'student123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');
  });

  test('should display orders page', async ({ page }) => {
    await page.goto('/orders');
    await expect(page.locator('.text-h4')).toContainText(/Orders/i);
  });
});

test.describe('Profile Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'student1');
    await page.fill('input[label="Password"]', 'student123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');
  });

  test('should display profile page', async ({ page }) => {
    await page.goto('/profile');
    await expect(page.locator('.text-h4')).toContainText(/Profile/i);
  });
});

test.describe('Delivery Tracking', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'warehouse');
    await page.fill('input[label="Password"]', 'warehouse123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');
  });

  test('should display delivery tracking page', async ({ page }) => {
    await page.goto('/delivery');
    await expect(page.locator('.text-h4')).toContainText(/Delivery/i);
  });
});
