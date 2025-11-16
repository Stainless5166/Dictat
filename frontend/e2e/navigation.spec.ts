/**
 * E2E Tests: Navigation and Layout
 */

import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should not show navigation on auth pages', async ({ page }) => {
    await page.goto('/auth/login');

    const nav = page.locator('nav');
    await expect(nav).not.toBeVisible();
  });

  test('should show Dictat branding on login page', async ({ page }) => {
    await page.goto('/auth/login');

    await expect(page.getByText('Sign in to Dictat')).toBeVisible();
    await expect(page.getByText('Medical dictation transcription service')).toBeVisible();
  });

  test('should have responsive layout', async ({ page }) => {
    await page.goto('/auth/login');

    // Check that the form is visible
    const form = page.locator('form');
    await expect(form).toBeVisible();

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(form).toBeVisible();
  });

  test('should have proper form accessibility', async ({ page }) => {
    await page.goto('/auth/login');

    // Check for labels
    await expect(page.getByLabel('Email address')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();

    // Check for required fields
    const emailInput = page.getByLabel('Email address');
    expect(await emailInput.getAttribute('required')).not.toBeNull();
  });
});
