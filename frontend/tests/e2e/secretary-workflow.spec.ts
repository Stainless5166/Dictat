import { test, expect } from '@playwright/test';

test.describe('Secretary Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication as secretary
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 2,
          email: 'secretary@example.com',
          full_name: 'Alice Johnson',
          role: 'secretary',
          is_active: true,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
        }),
      });
    });

    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'mock-token');
    });
  });

  test('should display work queue', async ({ page }) => {
    await page.route('**/api/v1/dictations/queue*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 1,
              title: 'Patient Visit Notes',
              patient_reference: 'PAT-12345',
              status: 'pending',
              priority: 'urgent',
              duration: 120.5,
              doctor_id: 1,
              secretary_id: null,
              created_at: '2025-01-15T10:00:00Z',
              claimed_at: null,
              completed_at: null,
            },
          ],
          total: 1,
          page: 1,
          page_size: 100,
          total_pages: 1,
        }),
      });
    });

    await page.goto('/queue');

    await expect(page.locator('h1')).toContainText('Work Queue');
    await expect(page.getByText('Patient Visit Notes')).toBeVisible();
    await expect(page.getByText('urgent')).toBeVisible();
    await expect(page.getByRole('button', { name: /claim & transcribe/i })).toBeVisible();
  });

  test('should show empty queue message when no dictations available', async ({ page }) => {
    await page.route('**/api/v1/dictations/queue*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
          page: 1,
          page_size: 100,
          total_pages: 0,
        }),
      });
    });

    await page.goto('/queue');

    await expect(page.getByText('No dictations available')).toBeVisible();
    await expect(page.getByText(/check back later/i)).toBeVisible();
  });

  test('should navigate to My Work page', async ({ page }) => {
    await page.route('**/api/v1/dictations/queue*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
          page: 1,
          page_size: 100,
          total_pages: 0,
        }),
      });
    });

    await page.goto('/queue');

    await page.getByRole('link', { name: /my work/i }).click();

    await expect(page).toHaveURL(/.*my-work/);
  });

  test('should display My Work page', async ({ page }) => {
    await page.route('**/api/v1/dictations*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 2,
              title: 'In Progress Dictation',
              patient_reference: 'PAT-99999',
              status: 'in_progress',
              priority: 'normal',
              duration: 85.3,
              doctor_id: 1,
              secretary_id: 2,
              created_at: '2025-01-15T11:00:00Z',
              claimed_at: '2025-01-15T11:30:00Z',
              completed_at: null,
            },
          ],
          total: 1,
          page: 1,
          page_size: 100,
          total_pages: 1,
        }),
      });
    });

    await page.goto('/my-work');

    await expect(page.locator('h1')).toContainText('My Work');
    await expect(page.getByText('In Progress Dictation')).toBeVisible();
    await expect(page.getByText(/continue transcribing/i)).toBeVisible();
  });

  test('should show secretary navigation items', async ({ page }) => {
    await page.route('**/api/v1/dictations/queue*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
          page: 1,
          page_size: 100,
          total_pages: 0,
        }),
      });
    });

    await page.goto('/queue');

    await expect(page.getByRole('link', { name: /work queue/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /my work/i })).toBeVisible();
    await expect(page.getByText('Alice Johnson')).toBeVisible();
  });
});
