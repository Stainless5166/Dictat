import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useToast } from '../useToast';

describe('useToast', () => {
  it('should initialize with empty toasts', () => {
    const { result } = renderHook(() => useToast());

    const { ToastContainer } = result.current;
    const { container } = render(<ToastContainer />);

    expect(container.querySelector('.fixed')).toBeInTheDocument();
  });

  it('should add a toast when showToast is called', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.showToast('Test message', 'info');
    });

    const { ToastContainer } = result.current;
    const { getByText } = render(<ToastContainer />);

    expect(getByText('Test message')).toBeInTheDocument();
  });

  it('should add multiple toasts', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.showToast('First message', 'info');
      result.current.showToast('Second message', 'success');
    });

    const { ToastContainer } = result.current;
    const { getByText } = render(<ToastContainer />);

    expect(getByText('First message')).toBeInTheDocument();
    expect(getByText('Second message')).toBeInTheDocument();
  });

  it('should show success toast', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.showToast('Success!', 'success');
    });

    const { ToastContainer } = result.current;
    const { container } = render(<ToastContainer />);

    const toast = container.querySelector('.bg-green-50');
    expect(toast).toBeInTheDocument();
  });

  it('should show error toast', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.showToast('Error!', 'error');
    });

    const { ToastContainer } = result.current;
    const { container } = render(<ToastContainer />);

    const toast = container.querySelector('.bg-red-50');
    expect(toast).toBeInTheDocument();
  });

  it('should default to info type when not specified', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.showToast('Info message');
    });

    const { ToastContainer } = result.current;
    const { container } = render(<ToastContainer />);

    const toast = container.querySelector('.bg-blue-50');
    expect(toast).toBeInTheDocument();
  });
});
