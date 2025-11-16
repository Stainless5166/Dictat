import { Page } from '@playwright/test';

export async function loginAsDoctor(page: Page) {
  await page.route('**/api/v1/auth/login', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: 'mock-doctor-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        expires_in: 1800,
      }),
    });
  });

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

  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'mock-doctor-token');
    localStorage.setItem('refresh_token', 'mock-refresh-token');
  });
}

export async function loginAsSecretary(page: Page) {
  await page.route('**/api/v1/auth/login', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: 'mock-secretary-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        expires_in: 1800,
      }),
    });
  });

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
    localStorage.setItem('access_token', 'mock-secretary-token');
    localStorage.setItem('refresh_token', 'mock-refresh-token');
  });
}
