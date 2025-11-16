/**
 * Dictat API Client
 *
 * TypeScript/JavaScript client for the Dictat medical dictation service API
 * Supports both axios and fetch
 *
 * Usage:
 *   import { DictatAPI } from './api-client';
 *
 *   const api = new DictatAPI({ baseURL: 'http://localhost:8000/api/v1' });
 *   await api.auth.login({ username: 'user@example.com', password: 'pass' });
 *   const dictations = await api.dictations.list();
 */

import type {
  // Auth
  UserRegister,
  LoginRequest,
  TokenResponse,
  RefreshTokenRequest,
  CurrentUser,

  // Dictations
  DictationCreate,
  DictationUpdate,
  DictationResponse,
  DictationListResponse,
  DictationListParams,
  WorkQueueParams,

  // Transcriptions
  TranscriptionCreate,
  TranscriptionUpdate,
  TranscriptionResponse,
  TranscriptionReview,

  // GDPR
  DataExportResponse,

  // Audit
  AuditLogListResponse,
  AuditLogParams,

  // Utility
  SuccessMessage,
  HealthCheckResponse,
  APIError,
} from './api-types';

// ============================================================================
// Configuration & Helpers
// ============================================================================

export interface APIClientConfig {
  baseURL: string;
  timeout?: number;
  onAuthError?: () => void;
  onNetworkError?: (error: Error) => void;
}

export class APIClient {
  private baseURL: string;
  private timeout: number;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private onAuthError?: () => void;
  private onNetworkError?: (error: Error) => void;

  constructor(config: APIClientConfig) {
    this.baseURL = config.baseURL;
    this.timeout = config.timeout || 30000;
    this.onAuthError = config.onAuthError;
    this.onNetworkError = config.onNetworkError;
  }

  /**
   * Set authentication tokens
   */
  setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;

    // Store in localStorage for persistence
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  /**
   * Clear authentication tokens
   */
  clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;

    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  /**
   * Get access token from storage
   */
  getAccessToken(): string | null {
    if (this.accessToken) return this.accessToken;

    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }

    return null;
  }

  /**
   * Get refresh token from storage
   */
  getRefreshToken(): string | null {
    if (this.refreshToken) return this.refreshToken;

    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token');
    }

    return null;
  }

  /**
   * Make HTTP request with automatic token refresh
   */
  private async request<T>(
    method: string,
    path: string,
    options: {
      body?: any;
      params?: Record<string, any>;
      headers?: Record<string, string>;
      requiresAuth?: boolean;
    } = {}
  ): Promise<T> {
    const { body, params, headers = {}, requiresAuth = true } = options;

    // Build URL with query params
    const url = new URL(path, this.baseURL);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    // Build headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    };

    // Add auth token if required
    if (requiresAuth) {
      const token = this.getAccessToken();
      if (token) {
        requestHeaders['Authorization'] = `Bearer ${token}`;
      }
    }

    // Build request options
    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
    };

    if (body && method !== 'GET') {
      if (body instanceof FormData) {
        // Remove Content-Type header for FormData (browser sets it with boundary)
        delete requestHeaders['Content-Type'];
        requestOptions.body = body;
      } else {
        requestOptions.body = JSON.stringify(body);
      }
    }

    try {
      const response = await fetch(url.toString(), requestOptions);

      // Handle 401 Unauthorized - try to refresh token
      if (response.status === 401 && requiresAuth) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry request with new token
          return this.request<T>(method, path, options);
        } else {
          // Refresh failed - trigger auth error handler
          this.clearTokens();
          if (this.onAuthError) {
            this.onAuthError();
          }
          throw new Error('Authentication failed');
        }
      }

      // Handle error responses
      if (!response.ok) {
        const error: APIError = await response.json();
        throw {
          status: response.status,
          statusText: response.statusText,
          error,
        };
      }

      // Parse response
      return await response.json();
    } catch (error) {
      // Handle network errors
      if (error instanceof TypeError) {
        if (this.onNetworkError) {
          this.onNetworkError(error);
        }
      }
      throw error;
    }
  }

  /**
   * Refresh access token using refresh token
   */
  private async refreshAccessToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const response = await this.request<TokenResponse>(
        'POST',
        '/auth/refresh',
        {
          body: { refresh_token: refreshToken },
          requiresAuth: false,
        }
      );

      this.setTokens(response.access_token, response.refresh_token);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Upload file with progress tracking
   */
  private async uploadFile<T>(
    path: string,
    formData: FormData,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const url = new URL(path, this.baseURL);
    const token = this.getAccessToken();

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Track upload progress
      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = (event.loaded / event.total) * 100;
            onProgress(progress);
          }
        });
      }

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            resolve(data);
          } catch (error) {
            reject(new Error('Invalid JSON response'));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject({
              status: xhr.status,
              statusText: xhr.statusText,
              error,
            });
          } catch (e) {
            reject({
              status: xhr.status,
              statusText: xhr.statusText,
              error: { detail: 'Upload failed' },
            });
          }
        }
      });

      // Handle errors
      xhr.addEventListener('error', () => {
        reject(new Error('Network error'));
      });

      xhr.addEventListener('abort', () => {
        reject(new Error('Upload aborted'));
      });

      // Send request
      xhr.open('POST', url.toString());
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
      xhr.send(formData);
    });
  }

  // ============================================================================
  // Authentication API
  // ============================================================================

  auth = {
    /**
     * Register new user
     */
    register: async (data: UserRegister): Promise<CurrentUser> => {
      return this.request<CurrentUser>('POST', '/auth/register', {
        body: data,
        requiresAuth: false,
      });
    },

    /**
     * Login with email and password
     */
    login: async (credentials: LoginRequest): Promise<TokenResponse> => {
      // OAuth2 password flow uses form data
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await this.request<TokenResponse>('POST', '/auth/login', {
        body: formData.toString(),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        requiresAuth: false,
      });

      // Store tokens
      this.setTokens(response.access_token, response.refresh_token);

      return response;
    },

    /**
     * Refresh access token
     */
    refresh: async (refreshToken: string): Promise<TokenResponse> => {
      const response = await this.request<TokenResponse>('POST', '/auth/refresh', {
        body: { refresh_token: refreshToken },
        requiresAuth: false,
      });

      this.setTokens(response.access_token, response.refresh_token);

      return response;
    },

    /**
     * Logout (clear tokens)
     */
    logout: async (): Promise<SuccessMessage> => {
      const response = await this.request<SuccessMessage>('POST', '/auth/logout');
      this.clearTokens();
      return response;
    },

    /**
     * Get current user profile
     */
    me: async (): Promise<CurrentUser> => {
      return this.request<CurrentUser>('GET', '/auth/me');
    },
  };

  // ============================================================================
  // Dictations API
  // ============================================================================

  dictations = {
    /**
     * Upload new dictation
     */
    create: async (
      data: DictationCreate,
      onProgress?: (progress: number) => void
    ): Promise<DictationResponse> => {
      const formData = new FormData();
      formData.append('file', data.file);
      if (data.title) formData.append('title', data.title);
      if (data.patient_reference) formData.append('patient_reference', data.patient_reference);
      if (data.priority) formData.append('priority', data.priority);
      if (data.notes) formData.append('notes', data.notes);
      if (data.duration) formData.append('duration', String(data.duration));

      return this.uploadFile<DictationResponse>('/dictations', formData, onProgress);
    },

    /**
     * List dictations with pagination and filtering
     */
    list: async (params?: DictationListParams): Promise<DictationListResponse> => {
      return this.request<DictationListResponse>('GET', '/dictations', { params });
    },

    /**
     * Get work queue for secretaries
     */
    queue: async (params?: WorkQueueParams): Promise<DictationListResponse> => {
      return this.request<DictationListResponse>('GET', '/dictations/queue', { params });
    },

    /**
     * Get dictation by ID
     */
    get: async (id: number): Promise<DictationResponse> => {
      return this.request<DictationResponse>('GET', `/dictations/${id}`);
    },

    /**
     * Get audio stream URL
     */
    getAudioURL: (id: number): string => {
      const token = this.getAccessToken();
      return `${this.baseURL}/dictations/${id}/audio?token=${token}`;
    },

    /**
     * Update dictation metadata
     */
    update: async (id: number, data: DictationUpdate): Promise<DictationResponse> => {
      return this.request<DictationResponse>('PATCH', `/dictations/${id}`, { body: data });
    },

    /**
     * Claim dictation
     */
    claim: async (id: number): Promise<DictationResponse> => {
      return this.request<DictationResponse>('POST', `/dictations/${id}/claim`);
    },

    /**
     * Unclaim dictation
     */
    unclaim: async (id: number): Promise<SuccessMessage> => {
      return this.request<SuccessMessage>('POST', `/dictations/${id}/unclaim`);
    },

    /**
     * Delete dictation
     */
    delete: async (id: number): Promise<SuccessMessage> => {
      return this.request<SuccessMessage>('DELETE', `/dictations/${id}`);
    },
  };

  // ============================================================================
  // Transcriptions API
  // ============================================================================

  transcriptions = {
    /**
     * Create new transcription
     */
    create: async (data: TranscriptionCreate): Promise<TranscriptionResponse> => {
      return this.request<TranscriptionResponse>('POST', '/transcriptions', { body: data });
    },

    /**
     * Get transcription by ID
     */
    get: async (id: number): Promise<TranscriptionResponse> => {
      return this.request<TranscriptionResponse>('GET', `/transcriptions/${id}`);
    },

    /**
     * Update transcription content (autosave)
     */
    update: async (
      id: number,
      data: TranscriptionUpdate,
      isAutosave = false
    ): Promise<TranscriptionResponse> => {
      return this.request<TranscriptionResponse>('PATCH', `/transcriptions/${id}`, {
        body: data,
        params: { is_autosave: isAutosave },
      });
    },

    /**
     * Submit transcription for review
     */
    submit: async (id: number): Promise<TranscriptionResponse> => {
      return this.request<TranscriptionResponse>('POST', `/transcriptions/${id}/submit`);
    },

    /**
     * Review transcription (approve or reject)
     */
    review: async (id: number, review: TranscriptionReview): Promise<TranscriptionResponse> => {
      return this.request<TranscriptionResponse>('POST', `/transcriptions/${id}/review`, {
        body: review,
      });
    },
  };

  // ============================================================================
  // GDPR API
  // ============================================================================

  gdpr = {
    /**
     * Export all user data
     */
    exportData: async (): Promise<DataExportResponse> => {
      return this.request<DataExportResponse>('GET', '/gdpr/export');
    },

    /**
     * Delete user account
     */
    deleteAccount: async (confirmEmail: string): Promise<SuccessMessage> => {
      return this.request<SuccessMessage>('DELETE', '/gdpr/account', {
        body: { confirm_email: confirmEmail },
      });
    },
  };

  // ============================================================================
  // Audit Logs API
  // ============================================================================

  audit = {
    /**
     * List audit logs
     */
    list: async (params?: AuditLogParams): Promise<AuditLogListResponse> => {
      return this.request<AuditLogListResponse>('GET', '/audit', { params });
    },
  };

  // ============================================================================
  // Health Check
  // ============================================================================

  /**
   * Health check
   */
  health = async (): Promise<HealthCheckResponse> => {
    return this.request<HealthCheckResponse>('GET', '/health', { requiresAuth: false });
  };
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

/**
 * Create API client instance
 */
export function createAPIClient(config: APIClientConfig): APIClient {
  return new APIClient(config);
}

/**
 * Default API client (configure before use)
 */
export const api = new APIClient({
  baseURL: 'http://localhost:8000/api/v1',
});
