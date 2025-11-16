/**
 * Vitest Setup File
 *
 * Runs before all tests to set up the testing environment
 */
/// <reference types="vitest/globals" />

import { beforeAll, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/svelte';
import '@testing-library/jest-dom/vitest';

// Mock browser APIs
beforeAll(() => {
  // Mock localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn()
  };
  (globalThis as any).localStorage = localStorageMock;

  // Mock fetch
  (globalThis as any).fetch = vi.fn();

  // Mock window.location
  delete (window as any).location;
  window.location = {
    href: 'http://localhost:5173',
    pathname: '/',
    search: '',
    hash: ''
  } as any;
});

// Clean up after each test
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
