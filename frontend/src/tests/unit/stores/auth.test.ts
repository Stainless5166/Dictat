/**
 * Auth Store Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { authStore, isAuthenticated, currentUser } from '$stores/auth';
import { createMockApi, mockUser, mockTokens } from '../../helpers/mockApi';

// Mock the API
vi.mock('$lib/api', () => ({
  api: createMockApi()
}));

// Mock navigation
vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

describe('Auth Store', () => {
  beforeEach(() => {
    // Reset store state
    authStore.logout();
    vi.clearAllMocks();
  });

  describe('loadUser', () => {
    it('should load user when token exists', async () => {
      localStorage.setItem('access_token', 'test_token');

      await authStore.loadUser();

      const state = get(authStore);
      expect(state.user).toEqual(mockUser);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
    });

    it('should not load user when no token', async () => {
      localStorage.removeItem('access_token');

      await authStore.loadUser();

      const state = get(authStore);
      expect(state.user).toBe(null);
      expect(state.loading).toBe(false);
    });
  });

  describe('login', () => {
    it('should login successfully', async () => {
      const credentials = {
        username: 'doctor@example.com',
        password: 'password123'
      };

      await authStore.login(credentials);

      const state = get(authStore);
      expect(state.user).toEqual(mockUser);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
    });

    it('should handle login error', async () => {
      const { api } = await import('$lib/api');
      vi.mocked(api.auth.login).mockRejectedValueOnce({
        error: { detail: 'Invalid credentials' },
        status: 401
      });

      try {
        await authStore.login({
          username: 'wrong@example.com',
          password: 'wrong'
        });
      } catch (error) {
        // Expected to throw
      }

      const state = get(authStore);
      expect(state.user).toBe(null);
      expect(state.error).toBe('Invalid credentials');
    });
  });

  describe('logout', () => {
    it('should logout user', async () => {
      // First login
      await authStore.login({
        username: 'doctor@example.com',
        password: 'password123'
      });

      // Then logout
      await authStore.logout();

      const state = get(authStore);
      expect(state.user).toBe(null);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
    });
  });

  describe('derived stores', () => {
    it('isAuthenticated should be true when user exists', async () => {
      await authStore.login({
        username: 'doctor@example.com',
        password: 'password123'
      });

      expect(get(isAuthenticated)).toBe(true);
    });

    it('isAuthenticated should be false when no user', () => {
      expect(get(isAuthenticated)).toBe(false);
    });

    it('currentUser should return user', async () => {
      await authStore.login({
        username: 'doctor@example.com',
        password: 'password123'
      });

      expect(get(currentUser)).toEqual(mockUser);
    });
  });
});
