import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Analysis Pages', () => {
  // We mock auth by simulating localstorage or setting auth cookies if needed,
  // but for testing accessibility, we can just load the UI state directly or mock it.
  
  test('Dashboard page renders correctly and passes accessibility', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard');
    
    // Assert dashboard elements
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    
    // Accessibility check
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('New Analysis page renders correctly and passes accessibility', async ({ page }) => {
    await page.goto('/dashboard/analysis/new');
    
    // Assert analysis form elements
    await expect(page.getByRole('heading', { name: /new analysis/i })).toBeVisible();
    
    // Accessibility check
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
