/**
 * Mock API Client for Testing
 */

import { vi } from 'vitest';
import type { APIClient } from '$lib/api-client';
import type {
  TokenResponse,
  CurrentUser,
  DictationListResponse,
  DictationResponse,
  TranscriptionResponse
} from '$lib/types/api-types';
import { UserRole, DictationStatus, DictationPriority } from '$lib/types/api-types';

export const mockUser: CurrentUser = {
  id: 1,
  email: 'doctor@example.com',
  full_name: 'Dr. John Doe',
  role: UserRole.DOCTOR,
  is_active: true,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z'
};

export const mockTokens: TokenResponse = {
  access_token: 'mock_access_token',
  refresh_token: 'mock_refresh_token',
  token_type: 'bearer',
  expires_in: 1800
};

export const mockDictation: DictationResponse = {
  id: 1,
  doctor_id: 1,
  secretary_id: null,
  file_path: 'audio/test.mp3',
  file_name: 'test.mp3',
  file_size: 1024000,
  mime_type: 'audio/mpeg',
  duration: 120,
  title: 'Test Dictation',
  patient_reference: 'PAT-001',
  notes: 'Test notes',
  priority: DictationPriority.NORMAL,
  status: DictationStatus.PENDING,
  created_at: '2025-01-01T10:00:00Z',
  updated_at: '2025-01-01T10:00:00Z',
  claimed_at: null,
  completed_at: null,
  deleted_at: null
};

export const mockDictationList: DictationListResponse = {
  items: [
    {
      id: 1,
      title: 'Test Dictation 1',
      patient_reference: 'PAT-001',
      status: DictationStatus.PENDING,
      priority: DictationPriority.NORMAL,
      duration: 120,
      doctor_id: 1,
      secretary_id: null,
      created_at: '2025-01-01T10:00:00Z',
      claimed_at: null,
      completed_at: null
    },
    {
      id: 2,
      title: 'Test Dictation 2',
      patient_reference: 'PAT-002',
      status: DictationStatus.IN_PROGRESS,
      priority: DictationPriority.HIGH,
      duration: 90,
      doctor_id: 1,
      secretary_id: 2,
      created_at: '2025-01-01T11:00:00Z',
      claimed_at: '2025-01-01T12:00:00Z',
      completed_at: null
    }
  ],
  total: 2,
  page: 1,
  page_size: 20,
  total_pages: 1
};

export const mockTranscription: TranscriptionResponse = {
  id: 1,
  dictation_id: 1,
  secretary_id: 2,
  reviewer_id: null,
  content: '# Test Transcription\n\nThis is a test.',
  version: 1,
  status: 'draft',
  review_notes: null,
  rejection_reason: null,
  created_at: '2025-01-01T12:00:00Z',
  updated_at: '2025-01-01T12:00:00Z',
  last_autosave_at: null,
  submitted_at: null,
  reviewed_at: null
};

/**
 * Create a mock API client with vitest mocks
 */
export function createMockApi(): Partial<APIClient> {
  return {
    auth: {
      login: vi.fn().mockResolvedValue(mockTokens),
      register: vi.fn().mockResolvedValue(mockUser),
      refresh: vi.fn().mockResolvedValue(mockTokens),
      logout: vi.fn().mockResolvedValue({ message: 'Logged out' }),
      me: vi.fn().mockResolvedValue(mockUser)
    },
    dictations: {
      list: vi.fn().mockResolvedValue(mockDictationList),
      queue: vi.fn().mockResolvedValue(mockDictationList),
      get: vi.fn().mockResolvedValue(mockDictation),
      create: vi.fn().mockResolvedValue(mockDictation),
      update: vi.fn().mockResolvedValue(mockDictation),
      claim: vi.fn().mockResolvedValue(mockDictation),
      unclaim: vi.fn().mockResolvedValue({ message: 'Unclaimed' }),
      delete: vi.fn().mockResolvedValue({ message: 'Deleted' }),
      getAudioURL: vi.fn().mockReturnValue('http://localhost:8000/api/v1/dictations/1/audio')
    },
    transcriptions: {
      create: vi.fn().mockResolvedValue(mockTranscription),
      get: vi.fn().mockResolvedValue(mockTranscription),
      update: vi.fn().mockResolvedValue(mockTranscription),
      submit: vi.fn().mockResolvedValue({ ...mockTranscription, status: 'submitted' }),
      review: vi.fn().mockResolvedValue({ ...mockTranscription, status: 'approved' })
    },
    setTokens: vi.fn(),
    clearTokens: vi.fn(),
    getAccessToken: vi.fn().mockReturnValue('mock_access_token'),
    getRefreshToken: vi.fn().mockReturnValue('mock_refresh_token')
  } as any;
}
