/**
 * Toast Store Tests
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { get } from 'svelte/store';
import { toastStore } from '$stores/toast';

describe('Toast Store', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    toastStore.clear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should add success toast', () => {
    toastStore.success('Success message');

    const toasts = get(toastStore);
    expect(toasts).toHaveLength(1);
    expect(toasts[0].type).toBe('success');
    expect(toasts[0].message).toBe('Success message');
  });

  it('should add error toast', () => {
    toastStore.error('Error message');

    const toasts = get(toastStore);
    expect(toasts).toHaveLength(1);
    expect(toasts[0].type).toBe('error');
    expect(toasts[0].message).toBe('Error message');
  });

  it('should auto-remove toast after duration', () => {
    toastStore.success('Temp message', 1000);

    let toasts = get(toastStore);
    expect(toasts).toHaveLength(1);

    // Fast-forward time
    vi.advanceTimersByTime(1000);

    toasts = get(toastStore);
    expect(toasts).toHaveLength(0);
  });

  it('should manually remove toast', () => {
    const id = toastStore.success('Message');

    let toasts = get(toastStore);
    expect(toasts).toHaveLength(1);

    toastStore.remove(id);

    toasts = get(toastStore);
    expect(toasts).toHaveLength(0);
  });

  it('should add multiple toasts', () => {
    toastStore.success('Message 1');
    toastStore.error('Message 2');
    toastStore.warning('Message 3');

    const toasts = get(toastStore);
    expect(toasts).toHaveLength(3);
  });

  it('should clear all toasts', () => {
    toastStore.success('Message 1');
    toastStore.error('Message 2');

    let toasts = get(toastStore);
    expect(toasts).toHaveLength(2);

    toastStore.clear();

    toasts = get(toastStore);
    expect(toasts).toHaveLength(0);
  });
});
