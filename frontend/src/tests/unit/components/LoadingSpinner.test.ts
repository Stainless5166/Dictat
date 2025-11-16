/**
 * LoadingSpinner Component Tests
 */

import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

describe('LoadingSpinner Component', () => {
  it('should render with default size', () => {
    const { container } = render(LoadingSpinner);
    const spinner = container.querySelector('.animate-spin');

    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('h-8', 'w-8');
  });

  it('should render with small size', () => {
    const { container } = render(LoadingSpinner, { size: 'sm' });
    const spinner = container.querySelector('.animate-spin');

    expect(spinner).toHaveClass('h-4', 'w-4');
  });

  it('should render with large size', () => {
    const { container } = render(LoadingSpinner, { size: 'lg' });
    const spinner = container.querySelector('.animate-spin');

    expect(spinner).toHaveClass('h-12', 'w-12');
  });

  it('should have correct aria attributes', () => {
    const { container } = render(LoadingSpinner);
    const spinner = container.querySelector('[role="status"]');

    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveAttribute('aria-label', 'Loading');
  });
});
