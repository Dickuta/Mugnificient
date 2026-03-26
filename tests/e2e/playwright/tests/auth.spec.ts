import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/auth/login');
    await expect(page.locator('text=Login')).toBeVisible();
  });

  test('should display register page', async ({ page }) => {
    await page.goto('/auth/register');
    await expect(page.locator('text=Register')).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'admin');
    await page.fill('input[label="Password"]', 'admin123');
    await page.click('button:has-text("Login")');
    await expect(page).toHaveURL('/');
  });

  test('should fail login with invalid credentials', async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[label="Username"]', 'invalid');
    await page.fill('input[label="Password"]', 'wrong');
    await page.click('button:has-text("Login")');
    await expect(page.locator('.q-notification')).toContainText('failed');
  });
});
