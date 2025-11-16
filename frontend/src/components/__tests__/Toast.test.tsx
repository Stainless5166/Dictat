import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Toast from '../Toast';

describe('Toast', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should render success toast with message', () => {
    render(<Toast message="Success message" type="success" onClose={mockOnClose} />);
    expect(screen.getByText('Success message')).toBeInTheDocument();
  });

  it('should render error toast with message', () => {
    render(<Toast message="Error message" type="error" onClose={mockOnClose} />);
    expect(screen.getByText('Error message')).toBeInTheDocument();
  });

  it('should render info toast with message', () => {
    render(<Toast message="Info message" type="info" onClose={mockOnClose} />);
    expect(screen.getByText('Info message')).toBeInTheDocument();
  });

  it('should render warning toast with message', () => {
    render(<Toast message="Warning message" type="warning" onClose={mockOnClose} />);
    expect(screen.getByText('Warning message')).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', async () => {
    const user = userEvent.setup({ delay: null });
    render(<Toast message="Test message" type="info" onClose={mockOnClose} />);

    const closeButton = screen.getByRole('button', { hidden: true });
    await user.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should auto-close after default duration', () => {
    render(<Toast message="Test message" type="info" onClose={mockOnClose} />);

    // Fast-forward time by 5 seconds (default duration)
    vi.advanceTimersByTime(5000);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should auto-close after custom duration', () => {
    render(<Toast message="Test message" type="info" onClose={mockOnClose} duration={3000} />);

    // Fast-forward time by 3 seconds
    vi.advanceTimersByTime(3000);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should not auto-close before duration expires', () => {
    render(<Toast message="Test message" type="info" onClose={mockOnClose} duration={5000} />);

    // Fast-forward time by 3 seconds (less than duration)
    vi.advanceTimersByTime(3000);

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('should apply correct styling for success type', () => {
    const { container } = render(
      <Toast message="Success" type="success" onClose={mockOnClose} />
    );
    const toast = container.firstChild as HTMLElement;
    expect(toast.className).toContain('bg-green-50');
  });

  it('should apply correct styling for error type', () => {
    const { container } = render(<Toast message="Error" type="error" onClose={mockOnClose} />);
    const toast = container.firstChild as HTMLElement;
    expect(toast.className).toContain('bg-red-50');
  });
});
