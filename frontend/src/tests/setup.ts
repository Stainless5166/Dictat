/**
 * Vitest Setup File
 *
 * Runs before all tests to set up the testing environment
 */

import { beforeAll, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/svelte';

// Mock browser APIs
beforeAll(() => {
  // Mock localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn()
  };
  global.localStorage = localStorageMock as any;

  // Mock fetch
  global.fetch = vi.fn();

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
