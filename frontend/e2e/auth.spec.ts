import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Auth Pages', () => {
  test('Login page renders correctly and passes accessibility', async ({ page }) => {
    await page.goto('/login');
    
    // Assert elements exist
    await expect(page.getByRole('heading', { name: /login/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    
    // Accessibility check
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('Register page renders correctly and passes accessibility', async ({ page }) => {
    await page.goto('/register');
    
    // Assert elements exist
    await expect(page.getByRole('heading', { name: /register/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /sign up/i })).toBeVisible();
    
    // Accessibility check
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
