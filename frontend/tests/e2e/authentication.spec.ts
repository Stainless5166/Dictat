import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear storage before each test
    await page.context().clearCookies();
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    await page.goto('/login');

    await expect(page.locator('h2')).toContainText('Dictat');
    await expect(page.locator('text=Medical Dictation Service')).toBeVisible();
    await expect(page.getByPlaceholder('Email address')).toBeVisible();
    await expect(page.getByPlaceholder('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should show validation errors for empty form', async ({ page }) => {
    await page.goto('/login');

    await page.getByRole('button', { name: /sign in/i }).click();

    // HTML5 validation should show
    const emailInput = page.getByPlaceholder('Email address');
    await expect(emailInput).toHaveAttribute('required');
  });

  test('should navigate to registration page', async ({ page }) => {
    await page.goto('/login');

    await page.getByText(/don't have an account/i).click();

    await expect(page).toHaveURL(/.*register/);
    await expect(page.locator('h2')).toContainText('Create an account');
  });

  test('should display registration form', async ({ page }) => {
    await page.goto('/register');

    await expect(page.getByLabel('Full Name')).toBeVisible();
    await expect(page.getByLabel('Email address')).toBeVisible();
    await expect(page.getByLabel('Role')).toBeVisible();
    await expect(page.getByLabel('Password', { exact: true })).toBeVisible();
    await expect(page.getByLabel('Confirm Password')).toBeVisible();
    await expect(page.getByRole('button', { name: /create account/i })).toBeVisible();
  });

  test('should redirect unauthenticated users to login', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page).toHaveURL(/.*login/);
  });

  test('should redirect from root to login when not authenticated', async ({ page }) => {
    await page.goto('/');

    // Should redirect to dashboard which then redirects to login
    await expect(page).toHaveURL(/.*login/);
  });
});

test.describe('Authentication with Mock API', () => {
  test('should login successfully with valid credentials', async ({ page }) => {
    // Mock the API responses
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-access-token',
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

    await page.goto('/login');

    await page.getByPlaceholder('Email address').fill('doctor@example.com');
    await page.getByPlaceholder('Password').fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('should show error message on failed login', async ({ page }) => {
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Invalid credentials',
        }),
      });
    });

    await page.goto('/login');

    await page.getByPlaceholder('Email address').fill('wrong@example.com');
    await page.getByPlaceholder('Password').fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByText(/invalid credentials/i)).toBeVisible();
  });
});
