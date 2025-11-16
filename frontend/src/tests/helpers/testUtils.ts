/**
 * Test Utilities
 */

import { render, type RenderResult } from '@testing-library/svelte';
import type { ComponentType, SvelteComponent } from 'svelte';
import { vi } from 'vitest';

/**
 * Render a Svelte component with default props
 */
export function renderComponent<T extends SvelteComponent>(
  component: ComponentType<T>,
  props?: Record<string, any>
): RenderResult<T> {
  return render(component, props ? { props } : {});
}

/**
 * Wait for a condition to be true
 */
export async function waitFor(
  condition: () => boolean,
  timeout = 1000,
  interval = 50
): Promise<void> {
  const startTime = Date.now();

  while (!condition()) {
    if (Date.now() - startTime > timeout) {
      throw new Error('Timeout waiting for condition');
    }
    await new Promise((resolve) => setTimeout(resolve, interval));
  }
}

/**
 * Create a mock file
 */
export function createMockFile(
  name: string,
  size: number,
  type: string = 'audio/mp3'
): File {
  const blob = new Blob(['a'.repeat(size)], { type });
  return new File([blob], name, { type });
}

/**
 * Mock fetch response
 */
export function mockFetchResponse(data: any, status = 200): void {
  (globalThis as any).fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    statusText: 'OK',
    json: async () => data,
    headers: new Headers(),
    redirected: false,
    type: 'basic',
    url: ''
  } as Response);
}

/**
 * Mock fetch error
 */
export function mockFetchError(error: any, status = 500): void {
  (globalThis as any).fetch = vi.fn().mockResolvedValue({
    ok: false,
    status,
    statusText: 'Error',
    json: async () => ({ detail: error }),
    headers: new Headers(),
    redirected: false,
    type: 'basic',
    url: ''
  } as Response);
}
