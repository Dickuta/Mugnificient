import { test, expect } from '@playwright/test';

test.describe('Products', () => {
  test('should display product list', async ({ page }) => {
    await page.goto('/products');
    await expect(page.locator('.text-h4')).toContainText(/Products/i);
  });

  test('should display product details', async ({ page }) => {
    await page.goto('/products');
    // Wait for products to load
    await page.waitForSelector('.product-card', { timeout: 10000 });
    await page.click('.product-card >> nth=0');
    await expect(page.locator('.text-h4')).toBeVisible();
  });

  test('should add product to cart', async ({ page }) => {
    // Login first
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'student1');
    await page.fill('input[label="Password"]', 'student123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');

    // Go to products
    await page.goto('/products');
    await page.waitForSelector('.product-card', { timeout: 10000 });
    
    // Add to cart
    await page.click('.product-card >> nth=0 .q-btn');
    
    // Verify notification
    await expect(page.locator('.q-notification')).toContainText(/cart/i);
  });
});

test.describe('Cart', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'student1');
    await page.fill('input[label="Password"]', 'student123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('/');
  });

  test('should display cart page', async ({ page }) => {
    await page.goto('/cart');
    await expect(page.locator('.text-h4')).toContainText(/Cart/i);
  });
});
