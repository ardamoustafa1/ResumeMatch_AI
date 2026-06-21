import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Analysis Pages', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '123e4567-e89b-12d3-a456-426614174000',
          email: 'qa@example.com',
          is_active: true,
          is_superuser: false,
          email_verified: true,
          created_at: '2026-06-21T00:00:00Z',
        }),
      });
    });
    await page.route('**/api/v1/analysis?limit=8', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], limit: 8, offset: 0 }),
      });
    });
  });

  test('Dashboard form renders correctly and passes accessibility', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByText('New analysis')).toBeVisible();
    await expect(page.getByRole('button', { name: /start ai analysis/i })).toBeVisible();

    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('Analysis validation prevents undersized content', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByLabel('CV text').fill('short');
    await page.getByLabel('Job description').fill('short');
    await page.getByRole('button', { name: /start ai analysis/i }).click();
    await expect(page.getByText(/CV must be 100\+ characters/i)).toBeVisible();
  });
});
