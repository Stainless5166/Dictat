import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '@/test/utils';
import Login from '../Login';
import { mockTokens, mockDoctor } from '@/test/mockData';

// Mock the API
vi.mock('@/lib/api', () => ({
  default: {
    getAccessToken: vi.fn(() => null),
    auth: {
      login: vi.fn(),
      me: vi.fn(),
    },
  },
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Login Page', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('should render login form', () => {
    renderWithProviders(<Login />);

    expect(screen.getByText('Dictat')).toBeInTheDocument();
    expect(screen.getByText('Medical Dictation Service')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email address')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('should show link to registration page', () => {
    renderWithProviders(<Login />);

    const registerLink = screen.getByText(/don't have an account/i);
    expect(registerLink).toBeInTheDocument();
  });

  it('should handle successful login', async () => {
    const user = userEvent.setup();
    const api = await import('@/lib/api');

    vi.mocked(api.default.auth.login).mockResolvedValue(mockTokens);
    vi.mocked(api.default.auth.me).mockResolvedValue(mockDoctor);

    renderWithProviders(<Login />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await user.type(emailInput, 'doctor@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    await waitFor(() => {
      expect(api.default.auth.login).toHaveBeenCalledWith({
        username: 'doctor@example.com',
        password: 'password123',
      });
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('should show error message on failed login', async () => {
    const user = userEvent.setup();
    const api = await import('@/lib/api');

    vi.mocked(api.default.auth.login).mockRejectedValue({
      error: { detail: 'Invalid credentials' },
    });

    renderWithProviders(<Login />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await user.type(emailInput, 'wrong@example.com');
    await user.type(passwordInput, 'wrongpassword');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  it('should show loading state during login', async () => {
    const user = userEvent.setup();
    const api = await import('@/lib/api');

    vi.mocked(api.default.auth.login).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockTokens), 100))
    );

    renderWithProviders(<Login />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await user.type(emailInput, 'doctor@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    expect(screen.getByRole('button', { name: /logging in/i })).toBeInTheDocument();
  });

  it('should require email and password', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Login />);

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitButton);

    // HTML5 validation should prevent submission
    const emailInput = screen.getByPlaceholderText('Email address') as HTMLInputElement;
    expect(emailInput.validity.valid).toBe(false);
  });
});
