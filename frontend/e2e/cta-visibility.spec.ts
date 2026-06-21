import { test, expect } from '@playwright/test';

const viewports = [
  { name: 'desktop', width: 1280, height: 720 },
  { name: 'mobile', width: 375, height: 667 },
];

test.describe('CTA Visibility', () => {
  for (const viewport of viewports) {
    test(`Hero CTA - ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');

      const ctaButton = page.getByRole('link', { name: /Get Started/i }).first();
      await expect(ctaButton).toBeVisible();
      await expect(page.getByRole('link', { name: /View Demo/i })).toBeVisible();
    });
  }
});
