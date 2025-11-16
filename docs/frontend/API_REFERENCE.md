# Dictat API Reference for Frontend Developers

Complete API reference for building the Dictat frontend application.

**Base URL**: `http://localhost:8000/api/v1`

**OpenAPI Documentation**: `http://localhost:8000/docs` (Swagger UI)

**Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

---

## Table of Contents

- [Authentication](#authentication)
- [Dictations](#dictations)
- [Transcriptions](#transcriptions)
- [Users](#users)
- [GDPR](#gdpr)
- [Audit Logs](#audit-logs)
- [Error Handling](#error-handling)
- [File Uploads](#file-uploads)
- [Audio Streaming](#audio-streaming)

---

## Quick Start

### 1. Install Dependencies

```bash
# Install TypeScript types
npm install --save-dev @types/node

# Or copy the provided type definitions
cp docs/frontend/api-types.ts src/types/
cp docs/frontend/api-client.ts src/lib/
```

### 2. Initialize API Client

```typescript
import { createAPIClient } from './lib/api-client';

const api = createAPIClient({
  baseURL: 'http://localhost:8000/api/v1',
  onAuthError: () => {
    // Redirect to login
    window.location.href = '/login';
  },
  onNetworkError: (error) => {
    console.error('Network error:', error);
  },
});

export default api;
```

### 3. Login and Make Requests

```typescript
// Login
const { access_token, refresh_token } = await api.auth.login({
  username: 'doctor@example.com',
  password: 'securepassword123',
});

// Get current user
const user = await api.auth.me();

// List dictations
const dictations = await api.dictations.list({
  limit: 20,
  status: 'pending',
});

// Upload dictation
const dictation = await api.dictations.create(
  {
    file: audioFile,
    title: 'Patient Visit Notes',
    priority: 'normal',
  },
  (progress) => console.log(`Upload: ${progress}%`)
);
```

---

## Authentication

### POST /auth/register

Register a new user account.

**Permissions**: Public

**Request Body**:
```json
{
  "email": "doctor@example.com",
  "password": "SecurePass123",
  "full_name": "Dr. Jane Smith",
  "role": "doctor"
}
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "doctor@example.com",
  "full_name": "Dr. Jane Smith",
  "role": "doctor",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

**TypeScript**:
```typescript
const user = await api.auth.register({
  email: 'doctor@example.com',
  password: 'SecurePass123',
  full_name: 'Dr. Jane Smith',
  role: UserRole.DOCTOR,
});
```

---

### POST /auth/login

Login with email and password, receive JWT tokens.

**Permissions**: Public

**Request Body** (form-urlencoded):
```
username=doctor@example.com&password=SecurePass123
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**TypeScript**:
```typescript
const tokens = await api.auth.login({
  username: 'doctor@example.com',
  password: 'SecurePass123',
});

// Tokens are automatically stored and sent with future requests
```

---

### POST /auth/refresh

Refresh access token using refresh token.

**Permissions**: Public

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**TypeScript**:
```typescript
const tokens = await api.auth.refresh(refreshToken);
// New tokens are automatically stored
```

---

### POST /auth/logout

Logout (invalidate tokens on client side).

**Permissions**: Authenticated users

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

**TypeScript**:
```typescript
await api.auth.logout();
// Tokens are automatically cleared
```

---

### GET /auth/me

Get current authenticated user profile.

**Permissions**: Authenticated users

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "doctor@example.com",
  "full_name": "Dr. Jane Smith",
  "role": "doctor",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

**TypeScript**:
```typescript
const user = await api.auth.me();
console.log(`Logged in as: ${user.full_name} (${user.role})`);
```

---

## Dictations

### POST /dictations

Upload a new dictation audio file.

**Permissions**: Doctors and Admins only

**Request** (multipart/form-data):
```
file: <audio-file>             (required)
title: "Patient Visit Notes"   (optional)
patient_reference: "PAT-12345" (optional)
priority: "normal"              (optional: low|normal|high|urgent)
notes: "Follow-up needed"       (optional)
duration: 120.5                 (optional, seconds)
```

**Supported Audio Formats**: mp3, wav, m4a, ogg, flac

**Max File Size**: 100 MB

**Response** (201 Created):
```json
{
  "id": 1,
  "doctor_id": 1,
  "secretary_id": null,
  "file_path": "audio/2025/01/doctor-1/abc123.mp3",
  "file_name": "recording.mp3",
  "file_size": 2048576,
  "mime_type": "audio/mpeg",
  "duration": 120.5,
  "title": "Patient Visit Notes",
  "patient_reference": "PAT-12345",
  "notes": "Follow-up needed",
  "priority": "normal",
  "status": "pending",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z",
  "claimed_at": null,
  "completed_at": null,
  "deleted_at": null
}
```

**TypeScript**:
```typescript
// With progress tracking
const dictation = await api.dictations.create(
  {
    file: audioFile,
    title: 'Patient Visit Notes',
    patient_reference: 'PAT-12345',
    priority: DictationPriority.NORMAL,
    notes: 'Follow-up needed',
  },
  (progress) => {
    console.log(`Upload: ${progress.toFixed(1)}%`);
  }
);
```

---

### GET /dictations

List dictations with pagination and filtering.

**Permissions**:
- **Doctors**: See only their own dictations
- **Secretaries**: See pending/assigned dictations and those claimed by them
- **Admins**: See all dictations

**Query Parameters**:
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 100, max: 1000) - Results per page
- `status` (string) - Filter by status: `pending|assigned|in_progress|completed|reviewed|rejected`
- `priority` (string) - Filter by priority: `low|normal|high|urgent`
- `from_date` (ISO 8601) - Filter from date
- `to_date` (ISO 8601) - Filter to date

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "title": "Patient Visit Notes",
      "patient_reference": "PAT-12345",
      "status": "pending",
      "priority": "normal",
      "duration": 120.5,
      "doctor_id": 1,
      "secretary_id": null,
      "created_at": "2025-01-15T10:00:00Z",
      "claimed_at": null,
      "completed_at": null
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 100,
  "total_pages": 1
}
```

**TypeScript**:
```typescript
// List all dictations
const dictations = await api.dictations.list();

// With filtering
const urgentDictations = await api.dictations.list({
  priority: DictationPriority.URGENT,
  status: DictationStatus.PENDING,
  limit: 20,
});

// Pagination
const page2 = await api.dictations.list({
  skip: 20,
  limit: 20,
});
```

---

### GET /dictations/queue

Get work queue for secretaries (unclaimed dictations).

**Permissions**: Secretaries only

**Query Parameters**:
- `skip` (int) - Pagination offset
- `limit` (int) - Results per page
- `priority` (string) - Filter by priority

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "title": "Patient Visit Notes",
      "patient_reference": "PAT-12345",
      "status": "pending",
      "priority": "urgent",
      "duration": 120.5,
      "doctor_id": 1,
      "secretary_id": null,
      "created_at": "2025-01-15T10:00:00Z",
      "claimed_at": null,
      "completed_at": null
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 100,
  "total_pages": 1
}
```

**Sorting**: By priority (urgent first) then by age (oldest first)

**TypeScript**:
```typescript
const queue = await api.dictations.queue({
  limit: 50,
});

// Filter by priority
const urgentQueue = await api.dictations.queue({
  priority: DictationPriority.URGENT,
});
```

---

### GET /dictations/{id}

Get dictation details by ID.

**Permissions**: Owner (doctor), assigned secretary, or admin

**Response** (200 OK):
```json
{
  "id": 1,
  "doctor_id": 1,
  "secretary_id": null,
  "file_path": "audio/2025/01/doctor-1/abc123.mp3",
  "file_name": "recording.mp3",
  "file_size": 2048576,
  "mime_type": "audio/mpeg",
  "duration": 120.5,
  "title": "Patient Visit Notes",
  "patient_reference": "PAT-12345",
  "notes": "Follow-up needed",
  "priority": "normal",
  "status": "pending",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z",
  "claimed_at": null,
  "completed_at": null,
  "deleted_at": null
}
```

**TypeScript**:
```typescript
const dictation = await api.dictations.get(1);
```

---

### GET /dictations/{id}/audio

Stream audio file with range request support.

**Permissions**: Owner (doctor), assigned secretary, or admin

**Headers**:
- `Range` (optional) - Byte range for partial content (e.g., "bytes=0-1023")

**Response** (200 OK or 206 Partial Content):
- Binary audio stream
- Headers:
  - `Content-Type`: audio/mpeg (or appropriate MIME type)
  - `Accept-Ranges`: bytes
  - `Content-Length`: file size
  - `Content-Disposition`: inline; filename="recording.mp3"
  - `Content-Range` (if 206): bytes 0-1023/2048576

**TypeScript/HTML**:
```typescript
// Get audio URL with token
const audioURL = api.dictations.getAudioURL(dictation.id);

// Use in HTML5 audio player
<audio controls src={audioURL}>
  Your browser does not support the audio element.
</audio>

// Or use Audio API
const audio = new Audio(audioURL);
audio.play();
```

**Range Requests** (for seeking):
```typescript
// Fetch specific byte range
const response = await fetch(audioURL, {
  headers: {
    'Range': 'bytes=0-1023',
  },
});
// Returns 206 Partial Content
```

---

### POST /dictations/{id}/claim

Claim a dictation for transcription (secretaries).

**Permissions**: Secretaries only

**Response** (200 OK):
```json
{
  "id": 1,
  "doctor_id": 1,
  "secretary_id": 2,
  "status": "in_progress",
  "claimed_at": "2025-01-15T11:00:00Z",
  ...
}
```

**TypeScript**:
```typescript
const dictation = await api.dictations.claim(1);
console.log(`Claimed by secretary ${dictation.secretary_id}`);
```

**Errors**:
- `409 Conflict` - Dictation already claimed by another secretary
- `409 Conflict` - Invalid status (must be pending or assigned)

---

### POST /dictations/{id}/unclaim

Release a claimed dictation back to the queue.

**Permissions**: Secretary who claimed it, or admin

**Response** (200 OK):
```json
{
  "message": "Dictation unclaimed successfully"
}
```

**TypeScript**:
```typescript
await api.dictations.unclaim(1);
```

---

### PATCH /dictations/{id}

Update dictation metadata.

**Permissions**: Owner (doctor) or admin

**Request Body**:
```json
{
  "title": "Updated Title",
  "patient_reference": "PAT-67890",
  "notes": "Updated notes",
  "priority": "high",
  "status": "pending"
}
```

**Note**: Only admins can update `status` directly.

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Updated Title",
  "patient_reference": "PAT-67890",
  ...
}
```

**TypeScript**:
```typescript
const updated = await api.dictations.update(1, {
  title: 'Updated Title',
  priority: DictationPriority.HIGH,
});
```

---

### DELETE /dictations/{id}

Soft delete a dictation (sets `deleted_at` timestamp).

**Permissions**: Owner (doctor) or admin

**Response** (200 OK):
```json
{
  "message": "Dictation deleted successfully"
}
```

**TypeScript**:
```typescript
await api.dictations.delete(1);
```

**Errors**:
- `409 Conflict` - Cannot delete if transcription is in progress

---

## Transcriptions

### POST /transcriptions

Create a new transcription for a dictation.

**Permissions**: Secretaries only

**Request Body**:
```json
{
  "dictation_id": 1,
  "content": "# Patient Visit Notes\n\nPatient presented with..."
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "dictation_id": 1,
  "secretary_id": 2,
  "reviewer_id": null,
  "content": "# Patient Visit Notes\n\nPatient presented with...",
  "version": 1,
  "status": "draft",
  "review_notes": null,
  "rejection_reason": null,
  "created_at": "2025-01-15T11:30:00Z",
  "updated_at": "2025-01-15T11:30:00Z",
  "last_autosave_at": null,
  "submitted_at": null,
  "reviewed_at": null
}
```

**TypeScript**:
```typescript
const transcription = await api.transcriptions.create({
  dictation_id: 1,
  content: '# Patient Visit Notes\n\nPatient presented with...',
});
```

**Errors**:
- `400 Bad Request` - Dictation not claimed by current secretary
- `409 Conflict` - Transcription already exists for this dictation

---

### GET /transcriptions/{id}

Get transcription details by ID.

**Permissions**: Secretary who created it, doctor who owns dictation, or admin

**Response** (200 OK):
```json
{
  "id": 1,
  "dictation_id": 1,
  "secretary_id": 2,
  "reviewer_id": null,
  "content": "# Patient Visit Notes\n\nPatient presented with...",
  "version": 1,
  "status": "draft",
  "review_notes": null,
  "rejection_reason": null,
  "created_at": "2025-01-15T11:30:00Z",
  "updated_at": "2025-01-15T11:30:00Z",
  "last_autosave_at": null,
  "submitted_at": null,
  "reviewed_at": null
}
```

**TypeScript**:
```typescript
const transcription = await api.transcriptions.get(1);
```

---

### PATCH /transcriptions/{id}

Update transcription content (supports autosave).

**Permissions**: Secretary who created it

**Query Parameters**:
- `is_autosave` (bool, default: false) - Whether this is an autosave

**Request Body**:
```json
{
  "content": "# Patient Visit Notes\n\nUpdated content..."
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "content": "# Patient Visit Notes\n\nUpdated content...",
  "last_autosave_at": "2025-01-15T11:35:00Z",
  ...
}
```

**TypeScript**:
```typescript
// Manual save
const transcription = await api.transcriptions.update(1, {
  content: updatedContent,
});

// Autosave (doesn't log)
const transcription = await api.transcriptions.update(
  1,
  { content: updatedContent },
  true // isAutosave
);

// Implement autosave in editor
let autosaveTimer;
const handleContentChange = (newContent: string) => {
  clearTimeout(autosaveTimer);
  autosaveTimer = setTimeout(async () => {
    await api.transcriptions.update(
      transcriptionId,
      { content: newContent },
      true
    );
  }, 2000); // Autosave after 2 seconds of inactivity
};
```

**Errors**:
- `403 Forbidden` - Can only edit transcriptions you created
- `409 Conflict` - Cannot edit after submission (unless rejected)

**Note**: If transcription was rejected and you edit it, status automatically changes to "revised".

---

### POST /transcriptions/{id}/submit

Submit transcription for doctor review.

**Permissions**: Secretary who created it

**Response** (200 OK):
```json
{
  "id": 1,
  "status": "submitted",
  "submitted_at": "2025-01-15T12:00:00Z",
  ...
}
```

**Side Effects**:
- Transcription status → `submitted`
- Dictation status → `completed`

**TypeScript**:
```typescript
await api.transcriptions.submit(1);
```

**Errors**:
- `400 Bad Request` - Already submitted
- `422 Unprocessable Entity` - Content is empty

---

### POST /transcriptions/{id}/review

Approve or reject a transcription (doctors).

**Permissions**: Doctor who owns the dictation, or admin

**Request Body** (Approve):
```json
{
  "action": "approve",
  "review_notes": "Excellent work, well documented."
}
```

**Request Body** (Reject):
```json
{
  "action": "reject",
  "rejection_reason": "Missing patient history section",
  "review_notes": "Please add patient medical history."
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "status": "approved",
  "reviewer_id": 1,
  "review_notes": "Excellent work, well documented.",
  "reviewed_at": "2025-01-15T14:00:00Z",
  ...
}
```

**Side Effects** (Approve):
- Transcription status → `approved`
- Dictation status → `reviewed`

**Side Effects** (Reject):
- Transcription status → `rejected`
- Dictation status → `rejected`
- Secretary can edit and resubmit

**TypeScript**:
```typescript
// Approve
await api.transcriptions.review(1, {
  action: 'approve',
  review_notes: 'Excellent work',
});

// Reject
await api.transcriptions.review(1, {
  action: 'reject',
  rejection_reason: 'Missing patient history',
  review_notes: 'Please add patient medical history.',
});
```

**Errors**:
- `403 Forbidden` - Can only review transcriptions for your own dictations
- `400 Bad Request` - Transcription not submitted
- `422 Unprocessable Entity` - Rejection reason required when rejecting

---

## GDPR

### GET /gdpr/export

Export all user data (GDPR Right to Data Portability).

**Permissions**: Authenticated users (exports their own data)

**Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "email": "doctor@example.com",
    ...
  },
  "dictations": [ ... ],
  "transcriptions": [ ... ],
  "audit_logs": [ ... ],
  "exported_at": "2025-01-15T15:00:00Z"
}
```

**TypeScript**:
```typescript
const data = await api.gdpr.exportData();

// Download as JSON
const blob = new Blob([JSON.stringify(data, null, 2)], {
  type: 'application/json',
});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `dictat-data-export-${new Date().toISOString()}.json`;
a.click();
```

---

### DELETE /gdpr/account

Delete user account (GDPR Right to Erasure).

**Permissions**: Authenticated users (delete their own account)

**Request Body**:
```json
{
  "confirm_email": "doctor@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "Account deleted successfully"
}
```

**TypeScript**:
```typescript
await api.gdpr.deleteAccount(user.email);
```

**Note**:
- Deletes user account and all associated data
- Anonymizes audit logs (retains structure, removes PII)
- Cannot delete if active transcriptions are assigned

---

## Audit Logs

### GET /audit

List audit log entries (compliance).

**Permissions**: Admins only

**Query Parameters**:
- `skip` (int) - Pagination offset
- `limit` (int) - Results per page
- `user_id` (int) - Filter by user
- `action` (string) - Filter by action
- `resource_type` (string) - Filter by resource type
- `from_date` (ISO 8601) - Filter from date
- `to_date` (ISO 8601) - Filter to date

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "action": "dictation.create",
      "resource_type": "dictation",
      "resource_id": 1,
      "details": { "file_size": 2048576 },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 1234,
  "page": 1,
  "page_size": 100,
  "total_pages": 13
}
```

**TypeScript**:
```typescript
const logs = await api.audit.list({
  user_id: 1,
  action: 'dictation.create',
  from_date: '2025-01-01T00:00:00Z',
  to_date: '2025-01-31T23:59:59Z',
});
```

---

## Error Handling

All API errors follow a consistent format:

### Error Response Format

```json
{
  "detail": "Error message"
}
```

Or for validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `204 No Content` - Success with no response body
- `206 Partial Content` - Partial content (range request)
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., already claimed)
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `501 Not Implemented` - Feature not yet implemented

### TypeScript Error Handling

```typescript
import type { APIErrorResponse } from './types';

try {
  const dictation = await api.dictations.get(123);
} catch (error) {
  const apiError = error as APIErrorResponse;

  if (apiError.status === 404) {
    console.error('Dictation not found');
  } else if (apiError.status === 403) {
    console.error('You do not have permission to view this dictation');
  } else if (apiError.status === 401) {
    console.error('Please log in again');
    // Redirect to login
  } else {
    console.error('Unexpected error:', apiError.error.detail);
  }
}
```

---

## File Uploads

### Uploading Audio Files

Audio files are uploaded using `multipart/form-data`.

**TypeScript Example**:

```typescript
// From file input
const fileInput = document.getElementById('audio') as HTMLInputElement;
const file = fileInput.files?.[0];

if (file) {
  const dictation = await api.dictations.create(
    {
      file,
      title: 'Patient Visit',
      priority: DictationPriority.NORMAL,
    },
    (progress) => {
      // Update progress bar
      progressBar.style.width = `${progress}%`;
      progressText.textContent = `${progress.toFixed(1)}%`;
    }
  );

  console.log('Upload complete:', dictation);
}
```

**React Example**:

```tsx
const [uploadProgress, setUploadProgress] = useState(0);
const [uploading, setUploading] = useState(false);

const handleFileUpload = async (file: File) => {
  setUploading(true);
  try {
    const dictation = await api.dictations.create(
      {
        file,
        title: 'Patient Visit',
        priority: DictationPriority.NORMAL,
      },
      (progress) => setUploadProgress(progress)
    );

    console.log('Upload complete:', dictation);
  } catch (error) {
    console.error('Upload failed:', error);
  } finally {
    setUploading(false);
    setUploadProgress(0);
  }
};

return (
  <div>
    <input
      type="file"
      accept="audio/*"
      onChange={(e) => {
        const file = e.target.files?.[0];
        if (file) handleFileUpload(file);
      }}
    />
    {uploading && (
      <div className="progress-bar">
        <div style={{ width: `${uploadProgress}%` }} />
        <span>{uploadProgress.toFixed(1)}%</span>
      </div>
    )}
  </div>
);
```

---

## Audio Streaming

### HTML5 Audio Player

```tsx
const AudioPlayer: React.FC<{ dictationId: number }> = ({ dictationId }) => {
  const audioURL = api.dictations.getAudioURL(dictationId);

  return (
    <audio controls preload="metadata">
      <source src={audioURL} type="audio/mpeg" />
      Your browser does not support the audio element.
    </audio>
  );
};
```

### Custom Audio Player with Seeking

```tsx
import { useRef, useState } from 'react';

const CustomAudioPlayer: React.FC<{ dictationId: number }> = ({
  dictationId,
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const audioURL = api.dictations.getAudioURL(dictationId);

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (playing) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setPlaying(!playing);
    }
  };

  const handleSeek = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={audioURL}
        onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
        onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
        onEnded={() => setPlaying(false)}
      />

      <button onClick={togglePlayPause}>
        {playing ? 'Pause' : 'Play'}
      </button>

      <input
        type="range"
        min={0}
        max={duration}
        value={currentTime}
        onChange={(e) => handleSeek(Number(e.target.value))}
      />

      <span>
        {formatTime(currentTime)} / {formatTime(duration)}
      </span>
    </div>
  );
};

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
```

---

## Best Practices

### 1. Token Management

```typescript
// Tokens are automatically managed by the API client
// But you can manually handle them if needed:

const { access_token, refresh_token } = await api.auth.login({
  username: 'user@example.com',
  password: 'password',
});

// Tokens are automatically stored in localStorage
// and sent with all subsequent requests

// Check if user is authenticated
const token = api.getAccessToken();
if (!token) {
  // Redirect to login
}
```

### 2. Auto-Refresh on 401

The API client automatically refreshes tokens when receiving a 401 response:

```typescript
// This happens automatically:
// 1. Request fails with 401
// 2. Client tries to refresh token
// 3. If refresh succeeds, retries original request
// 4. If refresh fails, calls onAuthError callback
```

### 3. Pagination

```typescript
// Load all pages
async function loadAllDictations(): Promise<DictationListItem[]> {
  const allDictations: DictationListItem[] = [];
  let page = 0;
  const pageSize = 100;

  while (true) {
    const response = await api.dictations.list({
      skip: page * pageSize,
      limit: pageSize,
    });

    allDictations.push(...response.items);

    if (response.items.length < pageSize) {
      break; // Last page
    }

    page++;
  }

  return allDictations;
}
```

### 4. Optimistic Updates

```typescript
// Update UI immediately, rollback on error
const [dictations, setDictations] = useState<DictationResponse[]>([]);

const handleClaim = async (id: number) => {
  // Optimistic update
  setDictations((prev) =>
    prev.map((d) =>
      d.id === id
        ? { ...d, status: DictationStatus.IN_PROGRESS, secretary_id: currentUserId }
        : d
    )
  );

  try {
    const updated = await api.dictations.claim(id);
    // Update with server response
    setDictations((prev) => prev.map((d) => (d.id === id ? updated : d)));
  } catch (error) {
    // Rollback on error
    setDictations((prev) =>
      prev.map((d) =>
        d.id === id
          ? { ...d, status: DictationStatus.PENDING, secretary_id: null }
          : d
      )
    );
    console.error('Failed to claim dictation:', error);
  }
};
```

### 5. Real-Time Updates (Polling)

```typescript
// Poll for updates every 30 seconds
useEffect(() => {
  const interval = setInterval(async () => {
    const response = await api.dictations.list();
    setDictations(response.items);
  }, 30000);

  return () => clearInterval(interval);
}, []);
```

---

## Complete React Example

```tsx
import { useState, useEffect } from 'react';
import api from './lib/api-client';
import type {
  DictationListItem,
  DictationPriority,
  DictationStatus,
} from './types/api-types';

function DictationList() {
  const [dictations, setDictations] = useState<DictationListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load dictations
  useEffect(() => {
    loadDictations();
  }, []);

  const loadDictations = async () => {
    try {
      setLoading(true);
      const response = await api.dictations.list({
        limit: 50,
      });
      setDictations(response.items);
    } catch (err) {
      setError('Failed to load dictations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = async (id: number) => {
    try {
      await api.dictations.claim(id);
      await loadDictations(); // Reload list
    } catch (err) {
      console.error('Failed to claim:', err);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Dictations</h1>
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {dictations.map((dictation) => (
            <tr key={dictation.id}>
              <td>{dictation.title || 'Untitled'}</td>
              <td>{dictation.priority}</td>
              <td>{dictation.status}</td>
              <td>{dictation.duration}s</td>
              <td>
                {dictation.status === 'pending' && (
                  <button onClick={() => handleClaim(dictation.id)}>
                    Claim
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DictationList;
```

---

## Resources

- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

---

## Support

For questions or issues, please open a GitHub issue or contact support@dictat.im.
