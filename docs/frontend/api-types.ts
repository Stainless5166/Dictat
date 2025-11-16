/**
 * TypeScript Type Definitions for Dictat API
 *
 * Auto-generated from Pydantic models
 * API Version: 1.0.0
 * Base URL: http://localhost:8000/api/v1
 */

// ============================================================================
// Enums
// ============================================================================

/**
 * User role enumeration
 */
export enum UserRole {
  DOCTOR = "doctor",
  SECRETARY = "secretary",
  ADMIN = "admin",
}

/**
 * Dictation status workflow states
 */
export enum DictationStatus {
  PENDING = "pending",           // Uploaded, waiting for assignment
  ASSIGNED = "assigned",          // Assigned to secretary but not claimed
  IN_PROGRESS = "in_progress",   // Secretary is working on it
  COMPLETED = "completed",        // Transcription submitted
  REVIEWED = "reviewed",          // Doctor has reviewed
  REJECTED = "rejected",          // Doctor rejected, needs revision
}

/**
 * Dictation priority levels
 */
export enum DictationPriority {
  LOW = "low",
  NORMAL = "normal",
  HIGH = "high",
  URGENT = "urgent",
}

/**
 * Transcription workflow states
 */
export enum TranscriptionStatus {
  DRAFT = "draft",           // Being worked on
  SUBMITTED = "submitted",   // Submitted for review
  APPROVED = "approved",     // Approved by doctor
  REJECTED = "rejected",     // Rejected, needs revision
  REVISED = "revised",       // Revised after rejection
}

// ============================================================================
// Base Types
// ============================================================================

/**
 * Standard API error response
 */
export interface APIError {
  detail: string | Record<string, any>[];
}

/**
 * Pagination metadata
 */
export interface PaginationMeta {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ============================================================================
// Authentication & Users
// ============================================================================

/**
 * User registration request
 */
export interface UserRegister {
  email: string;
  password: string;         // Min 8 chars, must contain uppercase, lowercase, and digit
  full_name: string;
  role: UserRole;
}

/**
 * User login request
 */
export interface LoginRequest {
  username: string;  // Email address
  password: string;
}

/**
 * JWT token response
 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;  // Seconds
}

/**
 * Refresh token request
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * User profile response
 */
export interface UserResponse {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;  // ISO 8601 datetime
  updated_at: string;  // ISO 8601 datetime
}

/**
 * Current user profile (includes additional fields)
 */
export interface CurrentUser extends UserResponse {
  // Add any additional fields specific to current user
}

// ============================================================================
// Dictations
// ============================================================================

/**
 * Create dictation request (multipart/form-data)
 */
export interface DictationCreate {
  file: File;                        // Audio file (required)
  title?: string;                    // Dictation title
  patient_reference?: string;        // Patient reference ID
  priority?: DictationPriority;      // Default: normal
  notes?: string;                    // Additional notes
  duration?: number;                 // Audio duration in seconds
}

/**
 * Update dictation request
 */
export interface DictationUpdate {
  title?: string;
  patient_reference?: string;
  notes?: string;
  priority?: DictationPriority;
  status?: DictationStatus;  // Admins only
}

/**
 * Dictation response (full details)
 */
export interface DictationResponse {
  id: number;
  doctor_id: number;
  secretary_id: number | null;
  file_path: string;
  file_name: string;
  file_size: number;             // Bytes
  mime_type: string;
  duration: number | null;       // Seconds
  title: string | null;
  patient_reference: string | null;
  notes: string | null;
  priority: DictationPriority;
  status: DictationStatus;
  created_at: string;            // ISO 8601 datetime
  updated_at: string;            // ISO 8601 datetime
  claimed_at: string | null;     // ISO 8601 datetime
  completed_at: string | null;   // ISO 8601 datetime
  deleted_at: string | null;     // ISO 8601 datetime
}

/**
 * Simplified dictation list item
 */
export interface DictationListItem {
  id: number;
  title: string | null;
  patient_reference: string | null;
  status: DictationStatus;
  priority: DictationPriority;
  duration: number | null;
  doctor_id: number;
  secretary_id: number | null;
  created_at: string;
  claimed_at: string | null;
  completed_at: string | null;
}

/**
 * Paginated dictation list response
 */
export interface DictationListResponse extends PaginationMeta {
  items: DictationListItem[];
}

/**
 * Dictation list query parameters
 */
export interface DictationListParams {
  skip?: number;                  // Pagination offset (default: 0)
  limit?: number;                 // Results per page (default: 100, max: 1000)
  status?: DictationStatus;       // Filter by status
  priority?: DictationPriority;   // Filter by priority
  from_date?: string;             // ISO 8601 date
  to_date?: string;               // ISO 8601 date
}

/**
 * Work queue query parameters
 */
export interface WorkQueueParams {
  skip?: number;
  limit?: number;
  priority?: DictationPriority;
}

// ============================================================================
// Transcriptions
// ============================================================================

/**
 * Create transcription request
 */
export interface TranscriptionCreate {
  dictation_id: number;
  content: string;  // Markdown formatted
}

/**
 * Update transcription request (autosave)
 */
export interface TranscriptionUpdate {
  content: string;  // Markdown formatted
}

/**
 * Submit transcription for review
 * (Empty request body)
 */
export interface TranscriptionSubmit {
  // No fields - submit uses current content
}

/**
 * Review transcription request
 */
export interface TranscriptionReview {
  action: "approve" | "reject";
  review_notes?: string;
  rejection_reason?: string;  // Required if action is "reject"
}

/**
 * Transcription response (full details)
 */
export interface TranscriptionResponse {
  id: number;
  dictation_id: number;
  secretary_id: number;
  reviewer_id: number | null;
  content: string;                    // Markdown formatted
  version: number;
  status: TranscriptionStatus;
  review_notes: string | null;
  rejection_reason: string | null;
  created_at: string;                 // ISO 8601 datetime
  updated_at: string;                 // ISO 8601 datetime
  last_autosave_at: string | null;    // ISO 8601 datetime
  submitted_at: string | null;        // ISO 8601 datetime
  reviewed_at: string | null;         // ISO 8601 datetime
}

/**
 * Simplified transcription list item
 */
export interface TranscriptionListItem {
  id: number;
  dictation_id: number;
  status: TranscriptionStatus;
  version: number;
  created_at: string;
  updated_at: string;
  submitted_at: string | null;
}

// ============================================================================
// GDPR
// ============================================================================

/**
 * Data export request
 */
export interface DataExportRequest {
  // Empty request - exports all user data
}

/**
 * Data export response
 */
export interface DataExportResponse {
  user: UserResponse;
  dictations: DictationResponse[];
  transcriptions: TranscriptionResponse[];
  audit_logs: AuditLogResponse[];
  exported_at: string;  // ISO 8601 datetime
}

/**
 * Account deletion request
 */
export interface AccountDeletionRequest {
  confirm_email: string;  // Must match current user email
}

// ============================================================================
// Audit Logs
// ============================================================================

/**
 * Audit log entry
 */
export interface AuditLogResponse {
  id: number;
  user_id: number | null;
  action: string;
  resource_type: string;
  resource_id: number | null;
  details: Record<string, any> | null;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;  // ISO 8601 datetime
}

/**
 * Audit log query parameters
 */
export interface AuditLogParams {
  skip?: number;
  limit?: number;
  user_id?: number;
  action?: string;
  resource_type?: string;
  from_date?: string;  // ISO 8601 date
  to_date?: string;    // ISO 8601 date
}

/**
 * Paginated audit log response
 */
export interface AuditLogListResponse extends PaginationMeta {
  items: AuditLogResponse[];
}

// ============================================================================
// API Client Configuration
// ============================================================================

/**
 * API client configuration
 */
export interface APIConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

/**
 * Authentication state
 */
export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: CurrentUser | null;
  isAuthenticated: boolean;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * API response wrapper
 */
export type APIResponse<T> = {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
};

/**
 * API error wrapper
 */
export type APIErrorResponse = {
  error: APIError;
  status: number;
  statusText: string;
};

/**
 * Success message response
 */
export interface SuccessMessage {
  message: string;
}

/**
 * Health check response
 */
export interface HealthCheckResponse {
  status: "healthy" | "unhealthy";
  service: string;
  version: string;
}

// ============================================================================
// WebSocket Types (Future)
// ============================================================================

/**
 * WebSocket message types
 */
export enum WSMessageType {
  DICTATION_CLAIMED = "dictation_claimed",
  DICTATION_COMPLETED = "dictation_completed",
  TRANSCRIPTION_SUBMITTED = "transcription_submitted",
  TRANSCRIPTION_REVIEWED = "transcription_reviewed",
  NOTIFICATION = "notification",
}

/**
 * WebSocket message
 */
export interface WSMessage {
  type: WSMessageType;
  data: any;
  timestamp: string;
}
