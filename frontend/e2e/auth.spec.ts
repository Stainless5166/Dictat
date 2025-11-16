/**
 * E2E Tests: Authentication Flow
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should redirect to login page when not authenticated', async ({ page }) => {
    await expect(page).toHaveURL(/.*login/);
    await expect(page.locator('h2')).toContainText('Sign in to Dictat');
  });

  test('should show validation errors for empty login form', async ({ page }) => {
    await page.goto('/auth/login');

    // Try to submit empty form
    await page.getByRole('button', { name: 'Sign in' }).click();

    // Browser validation should prevent submission
    const emailInput = page.getByLabel('Email address');
    const isInvalid = await emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
    expect(isInvalid).toBe(true);
  });

  test('should navigate to registration page', async ({ page }) => {
    await page.goto('/auth/login');

    await page.getByRole('link', { name: 'Register here' }).click();

    await expect(page).toHaveURL(/.*register/);
    await expect(page.locator('h2')).toContainText('Create your account');
  });

  test('should show password requirements on registration page', async ({ page }) => {
    await page.goto('/auth/register');

    const requirements = page.getByText(/Min 8 characters/);
    await expect(requirements).toBeVisible();
  });

  test('should validate password confirmation', async ({ page }) => {
    await page.goto('/auth/register');

    await page.getByLabel('Full Name').fill('Test User');
    await page.getByLabel('Email address').fill('test@example.com');
    await page.getByLabel('Password', { exact: true }).fill('Password123');
    await page.getByLabel('Confirm Password').fill('DifferentPassword123');

    await page.getByRole('button', { name: 'Register' }).click();

    await expect(page.getByText('Passwords do not match')).toBeVisible();
  });

  test('should validate password strength', async ({ page }) => {
    await page.goto('/auth/register');

    await page.getByLabel('Full Name').fill('Test User');
    await page.getByLabel('Email address').fill('test@example.com');
    await page.getByLabel('Password', { exact: true }).fill('weak');
    await page.getByLabel('Confirm Password').fill('weak');

    await page.getByRole('button', { name: 'Register' }).click();

    await expect(page.getByText(/Password must/)).toBeVisible();
  });

  test('should navigate back to login from registration', async ({ page }) => {
    await page.goto('/auth/register');

    await page.getByRole('link', { name: 'Sign in here' }).click();

    await expect(page).toHaveURL(/.*login/);
  });
});
