import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from '../ProtectedRoute';
import { AuthProvider } from '@/contexts/AuthContext';
import { UserRole } from '@/types/api-types';

// Mock the API client
vi.mock('@/lib/api', () => ({
  default: {
    getAccessToken: vi.fn(),
    auth: {
      me: vi.fn(),
    },
  },
}));

describe('ProtectedRoute', () => {
  const mockAuthenticatedUser = {
    id: 1,
    email: 'doctor@example.com',
    full_name: 'Dr. Jane Smith',
    role: UserRole.DOCTOR,
    is_active: true,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  };

  it('should show loading state while checking authentication', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should redirect to login when not authenticated', async () => {
    const api = await import('@/lib/api');
    vi.mocked(api.default.getAccessToken).mockReturnValue(null);

    render(
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <div>Protected Content</div>
                </ProtectedRoute>
              }
            />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    );

    // Should eventually redirect to login
    await screen.findByText('Login Page');
  });

  it('should show access denied for unauthorized role', async () => {
    const api = await import('@/lib/api');
    vi.mocked(api.default.getAccessToken).mockReturnValue('mock-token');
    vi.mocked(api.default.auth.me).mockResolvedValue({
      ...mockAuthenticatedUser,
      role: UserRole.SECRETARY,
    });

    render(
      <BrowserRouter>
        <AuthProvider>
          <ProtectedRoute allowedRoles={[UserRole.DOCTOR]}>
            <div>Doctor Only Content</div>
          </ProtectedRoute>
        </AuthProvider>
      </BrowserRouter>
    );

    // Wait for auth check
    await screen.findByText(/Access Denied/i);
    expect(screen.getByText(/do not have permission/i)).toBeInTheDocument();
  });
});
