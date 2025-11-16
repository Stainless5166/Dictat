import { test, expect } from '@playwright/test';

test.describe('Doctor Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          email: 'doctor@example.com',
          full_name: 'Dr. Jane Smith',
          role: 'doctor',
          is_active: true,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
        }),
      });
    });

    // Mock token
    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'mock-token');
    });
  });

  test('should display doctor dashboard', async ({ page }) => {
    await page.route('**/api/v1/dictations*', async (route) => {
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
              priority: 'normal',
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

    await page.goto('/doctor/dashboard');

    await expect(page.locator('h1')).toContainText('My Dictations');
    await expect(page.getByText('Patient Visit Notes')).toBeVisible();
    await expect(page.getByText('PAT-12345')).toBeVisible();
  });

  test('should navigate to upload page', async ({ page }) => {
    await page.route('**/api/v1/dictations*', async (route) => {
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

    await page.goto('/doctor/dashboard');

    await page.getByText('Upload New Dictation').click();

    await expect(page).toHaveURL(/.*upload/);
    await expect(page.locator('h1')).toContainText('Upload Dictation');
  });

  test('should display upload form', async ({ page }) => {
    await page.goto('/upload');

    await expect(page.getByLabel('Audio File *')).toBeVisible();
    await expect(page.getByLabel('Title')).toBeVisible();
    await expect(page.getByLabel('Patient Reference')).toBeVisible();
    await expect(page.getByLabel('Priority')).toBeVisible();
    await expect(page.getByLabel('Notes')).toBeVisible();
    await expect(page.getByRole('button', { name: /upload dictation/i })).toBeVisible();
  });

  test('should filter dictations by status', async ({ page }) => {
    let requestedStatus = '';

    await page.route('**/api/v1/dictations*', async (route) => {
      const url = new URL(route.request().url());
      requestedStatus = url.searchParams.get('status') || '';

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

    await page.goto('/doctor/dashboard');

    await page.getByRole('button', { name: 'Pending' }).click();

    // Wait for API call
    await page.waitForTimeout(500);

    expect(requestedStatus).toBe('pending');
  });

  test('should show logout button in navigation', async ({ page }) => {
    await page.route('**/api/v1/dictations*', async (route) => {
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

    await page.goto('/doctor/dashboard');

    await expect(page.getByText('Dr. Jane Smith')).toBeVisible();
    await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
  });
});
