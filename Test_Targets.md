# Dictat Testing Strategy & Targets

Comprehensive testing plan for ensuring quality, security, and compliance.

## Testing Philosophy

- **Test-Driven Development (TDD)** where practical
- **Minimum 80% code coverage** for backend
- **Minimum 70% code coverage** for frontend
- **Security-first testing** - all auth/authz paths must be tested
- **UK GDPR compliance verification** through audit log testing (Isle of Man data protection)
- **Performance testing** for file streaming and database queries

---

## 1. Backend Testing

### 1.1 Unit Tests

#### Database Models (`tests/unit/models/`)

**Target Coverage**: 90%+

- [ ] **User Model**
  - Password hashing and verification
  - Email validation
  - Role assignment
  - Timestamp generation
  - User activation/deactivation

- [ ] **Dictation Model**
  - File path validation
  - Status transitions
  - Relationship with User (foreign key)
  - Relationship with Transcription
  - Duration calculation

- [ ] **Transcription Model**
  - Markdown content storage
  - Version tracking
  - Relationship with Dictation
  - Status workflow
  - Reviewer assignment

- [ ] **AuditLog Model**
  - JSON metadata storage
  - Timestamp accuracy
  - User association
  - Action type validation

#### Utilities & Helpers (`tests/unit/utils/`)

**Target Coverage**: 95%+

- [ ] **Authentication Utilities**
  - JWT token creation
  - JWT token validation
  - Token expiration handling
  - Refresh token mechanism
  - Invalid token rejection

- [ ] **Password Utilities**
  - Password hashing (bcrypt)
  - Password verification
  - Salt generation
  - Timing attack resistance

- [ ] **File Utilities**
  - Audio format detection
  - File size validation
  - MIME type verification
  - Secure filename generation

- [ ] **Validation Utilities**
  - Email format validation
  - Markdown sanitization
  - Input length restrictions
  - SQL injection prevention

### 1.2 API Endpoint Tests

#### Authentication Endpoints (`tests/api/test_auth.py`)

**Target Coverage**: 100% (critical security)

- [ ] `POST /auth/register`
  - Successful registration
  - Duplicate email rejection
  - Password strength enforcement
  - Email validation
  - Invalid input handling

- [ ] `POST /auth/login`
  - Successful login with valid credentials
  - Failed login with invalid password
  - Failed login with non-existent user
  - Inactive user rejection
  - JWT token structure validation
  - Refresh token generation

- [ ] `POST /auth/refresh`
  - Token refresh with valid refresh token
  - Rejection of expired refresh token
  - Rejection of invalid refresh token

- [ ] `POST /auth/logout`
  - Token invalidation
  - Session cleanup

#### Dictation Endpoints (`tests/api/test_dictations.py`)

**Target Coverage**: 90%+

- [ ] `POST /dictations`
  - Successful audio upload
  - File format validation (mp3, wav, m4a, ogg)
  - File size limit enforcement
  - Chunked upload handling
  - Authentication requirement
  - Doctor-only access (authorization)
  - Metadata storage

- [ ] `GET /dictations`
  - List all dictations for authenticated user
  - Pagination (limit, offset)
  - Filtering by status
  - Filtering by date range
  - Sorting options
  - Role-based filtering (doctors see own, secretaries see assigned)

- [ ] `GET /dictations/{id}`
  - Retrieve specific dictation
  - Authorization check (ownership or assigned)
  - 404 for non-existent dictation

- [ ] `GET /dictations/{id}/audio`
  - Audio file streaming
  - Range request support (HTTP 206)
  - No local caching
  - Authorization check

- [ ] `DELETE /dictations/{id}`
  - Delete dictation and associated files
  - Authorization (owner or admin only)
  - Cascade delete transcription
  - Audit log entry

- [ ] `GET /dictations/queue`
  - Work queue for secretaries
  - Only pending/assigned dictations
  - Secretary-only access
  - Sorting by priority/date

- [ ] `POST /dictations/{id}/claim`
  - Secretary claims dictation
  - Status change to in_progress
  - Assignment tracking
  - Already-claimed rejection

#### Transcription Endpoints (`tests/api/test_transcriptions.py`)

**Target Coverage**: 90%+

- [ ] `POST /transcriptions`
  - Create transcription for dictation
  - Markdown content validation
  - Secretary-only access
  - Must be assigned/claimed dictation
  - Initial version = 1

- [ ] `PUT /transcriptions/{id}`
  - Update transcription content
  - Version increment
  - Autosave support (partial updates)
  - Authorization (creator only)

- [ ] `GET /transcriptions/{id}`
  - Retrieve transcription
  - Authorization check
  - Include version history

- [ ] `POST /transcriptions/{id}/submit`
  - Submit for review
  - Status change to completed
  - Notification to doctor

- [ ] `POST /transcriptions/{id}/review`
  - Doctor reviews transcription
  - Approval or rejection
  - Status change to reviewed
  - Feedback/comments

#### User Management Endpoints (`tests/api/test_users.py`)

**Target Coverage**: 85%+

- [ ] `GET /users` (admin only)
  - List all users
  - Pagination
  - Role filtering

- [ ] `GET /users/{id}`
  - Get user details
  - Self or admin access

- [ ] `PUT /users/{id}`
  - Update user profile
  - Self or admin access
  - Role change (admin only)

- [ ] `DELETE /users/{id}`
  - Deactivate user (soft delete)
  - Admin only

#### GDPR Compliance Endpoints (`tests/api/test_gdpr.py`)

**Target Coverage**: 100% (compliance critical)

- [ ] `GET /user/data-export` (Right to Portability - GDPR Article 20)
  - Export all user data in machine-readable format
  - Include dictations, transcriptions, audit logs
  - JSON format with proper structure
  - Authentication required
  - Only own data accessible

- [ ] `DELETE /user/account` (Right to Erasure - GDPR Article 17)
  - Delete all user data
  - Cascade delete dictations and transcriptions
  - Anonymize audit logs (retain structure, remove PII)
  - Cannot delete if active transcriptions assigned
  - Confirmation required
  - Audit trail of deletion

- [ ] `GET /user/consent`
  - Retrieve current consent settings
  - Data processing purposes listed

- [ ] `PUT /user/consent`
  - Update consent preferences
  - Audit consent changes

#### Audit Log Endpoints (`tests/api/test_audit.py`)

**Target Coverage**: 95%+ (compliance critical)

- [ ] `GET /audit-logs`
  - Admin-only access
  - Filter by user
  - Filter by action type
  - Filter by date range
  - Filter by resource
  - Pagination

### 1.3 Integration Tests

#### Complete Workflows (`tests/integration/`)

**Target Coverage**: Key user journeys

- [ ] **Doctor Dictation Workflow**
  1. Doctor registers
  2. Doctor logs in
  3. Doctor uploads dictation
  4. Doctor views dictation status
  5. Doctor receives notification when transcription complete
  6. Doctor reviews and approves transcription

- [ ] **Secretary Transcription Workflow**
  1. Secretary logs in
  2. Secretary views work queue
  3. Secretary claims dictation
  4. Secretary streams audio
  5. Secretary creates transcription
  6. Secretary autosaves progress
  7. Secretary submits for review

- [ ] **Authorization Workflow**
  1. User attempts access without token (401)
  2. User attempts access to unauthorized resource (403)
  3. Doctor cannot access secretary endpoints
  4. Secretary cannot access other secretary's claimed work
  5. Admin can access all resources

- [ ] **Audit Trail Workflow**
  1. Perform sensitive operations
  2. Verify audit log entries created
  3. Query audit logs
  4. Verify log immutability

### 1.4 OPA Policy Tests

#### Authorization Policies (`tests/opa/`)

**Target Coverage**: 100% (security critical)

- [ ] **Role-Based Access**
  - Doctor can create dictations
  - Secretary cannot create dictations
  - Secretary can claim dictations
  - Doctor cannot claim dictations
  - Admin can access all resources

- [ ] **Resource Ownership**
  - User can access own dictations
  - User cannot access others' dictations
  - Secretaries can access assigned dictations

- [ ] **State Transitions**
  - Only secretaries can mark as in_progress
  - Only doctors can mark as reviewed
  - Cannot skip states in workflow

- [ ] **Data Access**
  - Users cannot view other users' data
  - Admin can view all data
  - Secretaries can only view assigned work

### 1.5 Performance Tests

#### Load Testing (`tests/performance/`)

- [ ] **Concurrent Users**
  - 100 concurrent authenticated sessions
  - 50 concurrent audio uploads
  - 100 concurrent audio streams

- [ ] **Response Times**
  - API endpoints < 200ms (p95)
  - Audio streaming start < 500ms
  - Database queries < 100ms (p95)

- [ ] **Throughput**
  - 1000 requests/second
  - 50 concurrent file uploads (5MB each)
  - 100 concurrent audio streams

### 1.6 Security Tests

#### Vulnerability Testing (`tests/security/`)

**Target Coverage**: OWASP Top 10

- [ ] **Authentication**
  - Brute force protection
  - Session fixation prevention
  - Token expiration enforcement

- [ ] **Authorization**
  - Vertical privilege escalation (prevented)
  - Horizontal privilege escalation (prevented)
  - Insecure direct object references (prevented)

- [ ] **Input Validation**
  - SQL injection prevention
  - NoSQL injection prevention
  - Command injection prevention
  - Path traversal prevention
  - XSS prevention

- [ ] **File Upload**
  - Malicious file rejection
  - File size limits
  - MIME type validation
  - Virus scanning (if implemented)

- [ ] **API Security**
  - Rate limiting
  - CORS configuration
  - Security headers (HSTS, CSP, etc.)

---

## 2. Frontend Testing

### 2.1 Unit Tests

#### Components (`frontend/tests/unit/components/`)

**Target Coverage**: 75%+

- [ ] **Login Component**
  - Form validation
  - Submit handler
  - Error display
  - Loading states

- [ ] **Audio Recorder Component**
  - Start/stop recording
  - Audio preview
  - Format selection
  - Error handling (no microphone)

- [ ] **Audio Player Component**
  - Play/pause
  - Seek controls
  - Speed adjustment
  - Skip forward/backward

- [ ] **Markdown Editor Component**
  - Text input
  - Preview rendering
  - Autosave trigger
  - Keyboard shortcuts

- [ ] **Dictation List Component**
  - Rendering dictations
  - Filtering
  - Sorting
  - Pagination

- [ ] **Work Queue Component**
  - Rendering queue
  - Claim action
  - Status updates

#### State Management (`frontend/tests/unit/stores/`)

**Target Coverage**: 85%+

- [ ] **Auth Store**
  - Login action
  - Logout action
  - Token storage
  - Token refresh
  - User state management

- [ ] **Dictation Store**
  - Fetch dictations
  - Create dictation
  - Update dictation
  - Delete dictation
  - Filter/sort state

- [ ] **Transcription Store**
  - Fetch transcription
  - Update transcription
  - Submit transcription
  - Autosave logic

#### Utilities (`frontend/tests/unit/utils/`)

**Target Coverage**: 90%+

- [ ] **API Client**
  - Request interceptors (auth headers)
  - Response interceptors (error handling)
  - Token refresh on 401

- [ ] **Validation Functions**
  - Email validation
  - Password strength
  - Form validation

- [ ] **Formatting Functions**
  - Date/time formatting
  - Duration formatting
  - File size formatting

### 2.2 Integration Tests

#### User Flows (`frontend/tests/e2e/`)

**Target Coverage**: Critical user paths

- [ ] **Doctor Registration & Login**
  1. Navigate to registration
  2. Fill registration form
  3. Submit and verify account created
  4. Login with credentials
  5. Verify redirect to dashboard

- [ ] **Upload Dictation**
  1. Login as doctor
  2. Navigate to upload
  3. Record audio or select file
  4. Submit upload
  5. Verify dictation appears in list

- [ ] **Secretary Claim & Transcribe**
  1. Login as secretary
  2. View work queue
  3. Claim dictation
  4. Play audio
  5. Type transcription
  6. Verify autosave
  7. Submit transcription

- [ ] **Doctor Review**
  1. Login as doctor
  2. View completed transcriptions
  3. Review transcription
  4. Approve or request changes

- [ ] **Real-time Updates**
  1. Open app in two browsers
  2. Perform action in one (upload dictation)
  3. Verify update appears in other (WebSocket)

### 2.3 Accessibility Tests

#### WCAG Compliance (`frontend/tests/a11y/`)

**Target**: WCAG 2.1 Level AA

- [ ] **Keyboard Navigation**
  - All interactive elements accessible via keyboard
  - Logical tab order
  - Skip links for main content

- [ ] **Screen Reader**
  - Proper ARIA labels
  - Form labels associated with inputs
  - Error messages announced

- [ ] **Visual**
  - Sufficient color contrast (4.5:1)
  - Text resizable to 200%
  - No information conveyed by color alone

- [ ] **Audio Player**
  - Controls accessible via keyboard
  - Playback rate announced
  - Current time announced

### 2.4 Visual Regression Tests

#### UI Consistency (`frontend/tests/visual/`)

- [ ] **Login Page**
- [ ] **Dashboard (Doctor)**
- [ ] **Dashboard (Secretary)**
- [ ] **Audio Player**
- [ ] **Markdown Editor**
- [ ] **Modals & Dialogs**

---

## 3. Testing Infrastructure

### 3.1 Test Database

- [ ] Separate test database configuration
- [ ] Automatic schema creation/teardown
- [ ] Test data fixtures
- [ ] Database rollback after each test

### 3.2 Mock Services

- [ ] Mock NFS storage (local filesystem)
- [ ] Mock OPA service
- [ ] Mock Redis
- [ ] Mock email service
- [ ] Mock WebSocket connections

### 3.3 CI/CD Integration

- [ ] Run all tests on every commit
- [ ] Fail builds on test failure
- [ ] Generate coverage reports
- [ ] Upload coverage to dashboard (Codecov/Coveralls)
- [ ] Run security scans
- [ ] Run linting and type checking

### 3.4 Test Data Management

- [ ] Factory functions for models
- [ ] Faker integration for realistic data
- [ ] GDPR-compliant test data (no real personal/medical data)
- [ ] Seed scripts for development database

---

## 4. Coverage Targets

### Backend
| Module | Target | Priority |
|--------|--------|----------|
| Models | 90% | High |
| Auth | 100% | Critical |
| API Endpoints | 90% | High |
| OPA Integration | 100% | Critical |
| File Streaming | 85% | High |
| Background Tasks | 80% | Medium |
| Utilities | 95% | High |

### Frontend
| Module | Target | Priority |
|--------|--------|----------|
| Components | 75% | Medium |
| State Management | 85% | High |
| API Client | 90% | High |
| Auth Flow | 100% | Critical |
| Utilities | 90% | High |

### Overall Targets
- **Backend**: Minimum 80% coverage, target 90%
- **Frontend**: Minimum 70% coverage, target 80%
- **Critical Paths**: 100% coverage (auth, authz, audit)

---

## 5. Test Execution Plan

### Daily (Developer)
```bash
# Backend
uv run pytest tests/unit/
uv run mypy .
uv run ruff check .

# Frontend
pnpm test:unit
pnpm lint
pnpm type-check
```

### Pre-Commit
```bash
# Automated via pre-commit hooks
- Code formatting (black, prettier)
- Linting (ruff, eslint)
- Unit tests (fast tests only)
```

### CI Pipeline (Every Push)
```bash
# Backend
uv run pytest --cov --cov-report=xml
uv run bandit -r .
uv run safety check

# Frontend
pnpm test:coverage
pnpm test:e2e
npm audit
```

### Weekly (Full Suite)
```bash
# Performance tests
locust -f tests/performance/load_test.py

# Security tests
zap-cli scan

# Integration tests
pytest tests/integration/ --slow
```

---

## 6. Test Metrics & Reporting

### Required Metrics
- [ ] Code coverage percentage
- [ ] Test execution time
- [ ] Flaky test identification
- [ ] Test failure rate
- [ ] Security vulnerability count

### Dashboards
- [ ] Coverage trends over time
- [ ] Test performance trends
- [ ] Failure analysis
- [ ] Security scan results

---

## 7. Testing Tools

### Backend
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting
- **httpx** - HTTP client for API testing
- **faker** - Test data generation
- **factory_boy** - Model factories
- **pytest-mock** - Mocking library
- **locust** - Load testing

### Frontend
- **Vitest** - Unit testing
- **Testing Library** - Component testing
- **Playwright** or **Cypress** - E2E testing
- **axe-core** - Accessibility testing
- **Percy** or **Chromatic** - Visual regression testing
- **MSW (Mock Service Worker)** - API mocking

### Security
- **bandit** - Python security linter
- **safety** - Dependency vulnerability scanner
- **OWASP ZAP** - Web application security scanner
- **npm audit** - Node.js security scanner

---

## 8. Definition of Done

A feature is considered complete when:

- [ ] Unit tests written (minimum coverage met)
- [ ] Integration tests written (if applicable)
- [ ] All tests passing
- [ ] Code coverage meets target
- [ ] Security tests passing
- [ ] OPA policies tested (if auth/authz changes)
- [ ] Manual testing completed
- [ ] Accessibility verified
- [ ] Documentation updated
- [ ] Code reviewed and approved

---

Last Updated: 2025-11-16
