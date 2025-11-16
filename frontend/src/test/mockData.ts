import {
  UserRole,
  DictationStatus,
  DictationPriority,
  TranscriptionStatus,
  type CurrentUser,
  type DictationResponse,
  type DictationListItem,
  type TranscriptionResponse,
  type TokenResponse,
} from '@/types/api-types';

export const mockDoctor: CurrentUser = {
  id: 1,
  email: 'doctor@example.com',
  full_name: 'Dr. Jane Smith',
  role: UserRole.DOCTOR,
  is_active: true,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};

export const mockSecretary: CurrentUser = {
  id: 2,
  email: 'secretary@example.com',
  full_name: 'Alice Johnson',
  role: UserRole.SECRETARY,
  is_active: true,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};

export const mockAdmin: CurrentUser = {
  id: 3,
  email: 'admin@example.com',
  full_name: 'Admin User',
  role: UserRole.ADMIN,
  is_active: true,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};

export const mockTokens: TokenResponse = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'bearer',
  expires_in: 1800,
};

export const mockDictation: DictationResponse = {
  id: 1,
  doctor_id: 1,
  secretary_id: null,
  file_path: 'audio/2025/01/doctor-1/abc123.mp3',
  file_name: 'recording.mp3',
  file_size: 2048576,
  mime_type: 'audio/mpeg',
  duration: 120.5,
  title: 'Patient Visit Notes',
  patient_reference: 'PAT-12345',
  notes: 'Follow-up needed',
  priority: DictationPriority.NORMAL,
  status: DictationStatus.PENDING,
  created_at: '2025-01-15T10:00:00Z',
  updated_at: '2025-01-15T10:00:00Z',
  claimed_at: null,
  completed_at: null,
  deleted_at: null,
};

export const mockDictationList: DictationListItem[] = [
  {
    id: 1,
    title: 'Patient Visit Notes',
    patient_reference: 'PAT-12345',
    status: DictationStatus.PENDING,
    priority: DictationPriority.NORMAL,
    duration: 120.5,
    doctor_id: 1,
    secretary_id: null,
    created_at: '2025-01-15T10:00:00Z',
    claimed_at: null,
    completed_at: null,
  },
  {
    id: 2,
    title: 'Follow-up Consultation',
    patient_reference: 'PAT-67890',
    status: DictationStatus.IN_PROGRESS,
    priority: DictationPriority.URGENT,
    duration: 85.3,
    doctor_id: 1,
    secretary_id: 2,
    created_at: '2025-01-15T11:00:00Z',
    claimed_at: '2025-01-15T11:30:00Z',
    completed_at: null,
  },
  {
    id: 3,
    title: 'Procedure Notes',
    patient_reference: 'PAT-11111',
    status: DictationStatus.COMPLETED,
    priority: DictationPriority.HIGH,
    duration: 200.0,
    doctor_id: 1,
    secretary_id: 2,
    created_at: '2025-01-14T09:00:00Z',
    claimed_at: '2025-01-14T10:00:00Z',
    completed_at: '2025-01-14T12:00:00Z',
  },
];

export const mockTranscription: TranscriptionResponse = {
  id: 1,
  dictation_id: 1,
  secretary_id: 2,
  reviewer_id: null,
  content: '# Patient Visit Notes\n\nPatient presented with...',
  version: 1,
  status: TranscriptionStatus.DRAFT,
  review_notes: null,
  rejection_reason: null,
  created_at: '2025-01-15T11:30:00Z',
  updated_at: '2025-01-15T11:30:00Z',
  last_autosave_at: null,
  submitted_at: null,
  reviewed_at: null,
};

export const mockFile = new File(['audio content'], 'test.mp3', { type: 'audio/mpeg' });
