import { test, expect } from '@playwright/test';

const viewports = [
  { name: 'desktop', width: 1280, height: 720 },
  { name: 'mobile', width: 375, height: 667 },
];

const themes = ['light', 'dark'];

test.describe('CTA Visibility and Visual Regression', () => {
  for (const viewport of viewports) {
    for (const theme of themes) {
      test(`Hero CTA - ${viewport.name} - ${theme}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });

        // Go to home page
        await page.goto('/');

        // Force theme by evaluating script or adding class to html
        await page.evaluate((t) => {
          if (t === 'dark') {
            document.documentElement.classList.add('dark');
            document.documentElement.style.colorScheme = 'dark';
          } else {
            document.documentElement.classList.remove('dark');
            document.documentElement.style.colorScheme = 'light';
          }
        }, theme);

        // Wait for fonts to load and animations to finish
        await page.evaluate(() => document.fonts.ready);
        await page.waitForTimeout(500); // Small wait for any mounting animations

        // The CTA button should be visible
        const ctaButton = page.getByRole('link', { name: /Analiz Et|Get Started/i }).first();
        
        // Wait for it to be visible
        await expect(ctaButton).toBeVisible();

        // Take a screenshot of the hero section or full page to catch regression
        // We mask text if we only want layout, but for CTA we want the full thing.
        await expect(page).toHaveScreenshot(`home-cta-${viewport.name}-${theme}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.1,
        });
      });
    }
  }
});
