/**
 * Toast Component Tests
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Toast from '$components/shared/Toast.svelte';
import { toastStore } from '$stores/toast';

describe('Toast Component', () => {
  beforeEach(() => {
    toastStore.clear();
  });

  it('should render success toast', () => {
    toastStore.success('Success message');
    render(Toast);

    expect(screen.getByText('Success message')).toBeInTheDocument();
    expect(screen.getByText('✓')).toBeInTheDocument();
  });

  it('should render error toast', () => {
    toastStore.error('Error message');
    render(Toast);

    expect(screen.getByText('Error message')).toBeInTheDocument();
    expect(screen.getByText('✕')).toBeInTheDocument();
  });

  it('should render multiple toasts', () => {
    toastStore.success('Message 1');
    toastStore.error('Message 2');
    render(Toast);

    expect(screen.getByText('Message 1')).toBeInTheDocument();
    expect(screen.getByText('Message 2')).toBeInTheDocument();
  });

  it('should render with correct styling', () => {
    toastStore.success('Success');
    const { container } = render(Toast);

    const toast = container.querySelector('.bg-green-50');
    expect(toast).toBeInTheDocument();
  });
});
