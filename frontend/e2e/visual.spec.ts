import { test, expect } from '@playwright/test';

test.describe('Visual Regression Testing', () => {
  test('landing page visual comparison', async ({ page }) => {
    await page.goto('/');
    
    // Wait for animations to settle
    await page.waitForTimeout(1500);
    
    // Take a screenshot and compare
    await expect(page).toHaveScreenshot('landing-page.png', {
      maxDiffPixels: 100,
      fullPage: true,
    });
  });

  test('dashboard demo visual comparison', async ({ page }) => {
    await page.goto('/dashboard/analysis/demo');
    
    // Wait for animations to settle
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('dashboard-demo.png', {
      maxDiffPixels: 100,
      fullPage: true,
    });
  });
});
