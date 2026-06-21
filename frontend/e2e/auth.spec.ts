import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Auth Pages', () => {
  test('Login page renders correctly and passes accessibility', async ({ page }) => {
    await page.goto('/login');
    
    await expect(page.getByRole('heading', { name: /sign in to resumematch/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    
    // Accessibility check
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('Registration mode renders correctly and passes accessibility', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: /new here/i }).click();

    await expect(page.getByRole('heading', { name: /create your account/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /create account/i })).toBeVisible();
    await expect(page.getByRole('checkbox')).toBeVisible();
    
    // Accessibility check
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
