# Dictat Demo Instructions

## Overview

This guide provides step-by-step instructions for running a personal demo of the Dictat medical dictation system, including backend API and frontend (once implemented).

---

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL
- **Docker**: Docker and Docker Compose installed
- **Python**: Python 3.11+ (managed by uv)
- **Node.js**: Node.js 18+ and npm
- **uv**: Python package manager

### Check Prerequisites
```bash
# Docker
docker --version
docker-compose --version

# Python (via uv)
uv --version

# Node.js
node --version
npm --version
```

---

## Part 1: Backend Setup

### Step 1: Clone and Navigate
```bash
cd /path/to/Dictat
```

### Step 2: Environment Configuration

The `.env` file should already exist. Verify it has correct settings:

```bash
cat .env | grep -E "DB_PASSWORD|SECRET_KEY|CORS_ORIGINS"
```

Should see:
```
DB_PASSWORD=dictat_password
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars!!!
#CORS_ORIGINS=...  (commented out - uses defaults)
```

### Step 3: Start Docker Services

PostgreSQL and Redis are required:

```bash
docker-compose up -d postgres redis
```

Verify services are running:
```bash
docker-compose ps
```

Expected output:
```
NAME              IMAGE                COMMAND                  SERVICE    STATUS
dictat_postgres   postgres:15-alpine   "docker-entrypoint.s…"   postgres   Up (healthy)
dictat_redis      redis:7-alpine       "docker-entrypoint.s…"   redis      Up (healthy)
```

### Step 4: Install Python Dependencies

```bash
uv sync
```

This installs all backend dependencies (FastAPI, SQLAlchemy, etc.)

### Step 5: Run Database Migrations

```bash
uv run alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial database schema
```

### Step 6: Run Backend Tests (Optional)

Verify everything works:

```bash
uv run pytest -v
```

Expected: **81 tests passed** ✅

### Step 7: Start Backend Server

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this terminal open** - backend is now running.

### Step 8: Test Backend API

In a new terminal:

```bash
# Health check
curl http://localhost:8000/health

# API docs (open in browser)
open http://localhost:8000/docs
```

---

## Part 2: Create Demo Data

### Step 9: Create Test Users

Use the API docs at http://localhost:8000/docs or use curl:

#### Create Doctor User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "password": "DoctorPass123!",
    "full_name": "Dr. Sarah Johnson",
    "role": "doctor"
  }'
```

Save the response (contains user ID).

#### Create Secretary User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "secretary@example.com",
    "password": "SecretaryPass123!",
    "full_name": "Mary Smith",
    "role": "secretary"
  }'
```

### Step 10: Login as Doctor

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "doctor@example.com",
    "password": "DoctorPass123!"
  }'
```

Save the `access_token` from response. Example:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

Set as environment variable:
```bash
export DOCTOR_TOKEN="eyJhbGc..."
```

### Step 11: Create Sample Dictation

**Note**: Creating dictations requires audio file upload. For testing via curl:

```bash
# Create a dummy audio file
echo "Test audio content" > test-dictation.mp3

# Upload dictation
curl -X POST http://localhost:8000/api/v1/dictations/ \
  -H "Authorization: Bearer $DOCTOR_TOKEN" \
  -F "file=@test-dictation.mp3" \
  -F "title=Patient Consultation - John Doe" \
  -F "patient_reference=PAT-12345" \
  -F "notes=Follow-up visit for chronic condition" \
  -F "priority=normal"
```

Save the dictation ID from response.

### Step 12: Login as Secretary

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "secretary@example.com",
    "password": "SecretaryPass123!"
  }'
```

Save the `access_token`:
```bash
export SECRETARY_TOKEN="eyJhbGc..."
```

### Step 13: View Work Queue (Secretary)

```bash
curl -X GET http://localhost:8000/api/v1/dictations/queue \
  -H "Authorization: Bearer $SECRETARY_TOKEN"
```

Should see the dictation created in Step 11.

### Step 14: Claim Dictation (Secretary)

```bash
# Replace {dictation_id} with actual ID from Step 11
curl -X POST http://localhost:8000/api/v1/dictations/{dictation_id}/claim \
  -H "Authorization: Bearer $SECRETARY_TOKEN"
```

---

## Part 3: Frontend Setup (Once Implemented)

**Current Status**: Frontend skeleton exists but needs implementation (see `FRONTEND_TODO.md`)

### Step 15: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 16: Configure Environment

Create `frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Step 17: Start Frontend Dev Server

```bash
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Keep this terminal open** - frontend is now running.

### Step 18: Open in Browser

```bash
open http://localhost:5173
```

---

## Part 4: Demo Script

### Demo Flow 1: Doctor Workflow

1. **Login**
   - Navigate to http://localhost:5173/auth/login
   - Email: `doctor@example.com`
   - Password: `DoctorPass123!`
   - Click "Login"

2. **View Dashboard**
   - See list of uploaded dictations
   - View statistics (total, pending, completed)

3. **Upload New Dictation**
   - Click "Upload Dictation"
   - Fill form:
     - **Title**: "Patient Consultation - Jane Smith"
     - **Patient Reference**: "PAT-67890"
     - **Audio File**: Upload test MP3
     - **Priority**: High
     - **Notes**: "Urgent follow-up required"
   - Click "Upload"
   - See upload progress bar
   - Redirected to dictation details

4. **View Dictation Details**
   - See all metadata
   - Play audio (if player implemented)
   - See status: "Pending"

5. **Logout**
   - Click user menu → Logout

### Demo Flow 2: Secretary Workflow

1. **Login**
   - Navigate to http://localhost:5173/auth/login
   - Email: `secretary@example.com`
   - Password: `SecretaryPass123!`
   - Click "Login"

2. **View Work Queue**
   - See "Work Queue" tab
   - List of pending dictations
   - See priority badges (High, Normal, etc.)

3. **Claim Dictation**
   - Click "Claim" on high-priority dictation
   - Dictation moves to "My Work" tab
   - Status changes to "In Progress"

4. **Create Transcription**
   - Click "Transcribe" on claimed dictation
   - Audio player loads
   - Listen to audio:
     - Play/pause
     - Adjust speed (0.5x, 1x, 1.5x, 2x)
     - Skip forward/backward
   - Type transcription in Markdown editor
   - Auto-save triggers every 30 seconds
   - Click "Save Draft"

5. **Submit Transcription**
   - Review transcription
   - Click "Submit for Review"
   - Status changes to "Submitted"
   - Redirected to dashboard

6. **Logout**

### Demo Flow 3: Doctor Review

1. **Login as Doctor** (same credentials)

2. **View Submitted Transcriptions**
   - See dictation with "Submitted" status
   - Click to view details

3. **Review Transcription**
   - Read transcription content
   - Compare with audio
   - Add review notes (if changes needed)
   - Click "Approve" or "Request Changes"

4. **Approve**
   - Transcription status → "Completed"
   - Available for export/download

---

## Part 5: API Testing with Swagger UI

### Access API Documentation

Navigate to: http://localhost:8000/docs

### Interactive Testing

1. **Authorize**
   - Click "Authorize" button (top right)
   - Enter access token (from login response)
   - Click "Authorize"

2. **Test Endpoints**
   - **GET** `/api/v1/auth/me` - Get current user
   - **GET** `/api/v1/dictations/` - List all dictations
   - **GET** `/api/v1/dictations/queue` - View work queue
   - **POST** `/api/v1/dictations/{id}/claim` - Claim dictation
   - **GET** `/api/v1/dictations/{id}/audio` - Stream audio file

3. **Try Different Filters**
   - Filter by status: `?status=pending`
   - Filter by priority: `?priority=high`
   - Pagination: `?page=1&page_size=10`

---

## Part 6: Backend Testing

### Run Full Test Suite

```bash
uv run pytest -v
```

### Run with Coverage

```bash
uv run pytest --cov=. --cov-report=html
```

Open coverage report:
```bash
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Auth tests only
uv run pytest tests/api/test_auth.py -v

# Security tests only
uv run pytest tests/unit/test_security.py -v

# User model tests
uv run pytest tests/unit/test_user_model.py -v
```

---

## Part 7: Frontend Testing (Once Implemented)

### Run Unit Tests

```bash
cd frontend
npm test
```

### Run with Coverage

```bash
npm run test:coverage
```

### Run E2E Tests

```bash
npm run test:e2e
```

### Run E2E in UI Mode

```bash
npm run test:e2e:ui
```

---

## Troubleshooting

### Backend Issues

#### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart if needed
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

#### Port 8000 Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process or use different port
uv run uvicorn main:app --reload --port 8001
```

#### Migration Errors
```bash
# Check current migration version
uv run alembic current

# Rollback to previous version
uv run alembic downgrade -1

# Re-apply migrations
uv run alembic upgrade head
```

### Frontend Issues

#### Port 5173 Already in Use
```bash
# Frontend will auto-increment to 5174, 5175, etc.
# Or specify custom port:
npm run dev -- --port 3000
```

#### API Connection Error (CORS)
Ensure backend `.env` has correct CORS origins:
```bash
# Should be commented out to use defaults
#CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Or add your custom port if using different one.

#### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .svelte-kit node_modules/.vite
npm run dev
```

---

## Stopping Services

### Stop Backend

In the terminal running uvicorn:
```
Ctrl+C
```

### Stop Docker Services

```bash
docker-compose down
```

To keep data:
```bash
docker-compose stop
```

### Stop Frontend

In the terminal running `npm run dev`:
```
Ctrl+C
```

---

## Clean Shutdown

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -r {} +

# Clean frontend build
cd frontend
rm -rf .svelte-kit node_modules/.vite
```

---

## Performance Tips

### Backend

1. **Use production DB settings** for larger datasets:
   ```env
   DB_POOL_SIZE=50
   DB_MAX_OVERFLOW=20
   ```

2. **Enable Redis caching**:
   ```env
   REDIS_CACHE_TTL=3600
   ```

3. **Increase workers** for production:
   ```bash
   uv run uvicorn main:app --workers 4
   ```

### Frontend

1. **Build for production**:
   ```bash
   npm run build
   npm run preview
   ```

2. **Enable compression** in production

3. **Use environment-specific API URLs**

---

## Demo Data Suggestions

### Users
- **Doctor**: "Dr. Sarah Johnson" (doctor@example.com)
- **Secretary**: "Mary Smith" (secretary@example.com)
- **Admin**: "Admin User" (admin@example.com)

### Dictations
- **Routine Check-up** (Priority: Normal)
- **Emergency Consultation** (Priority: Urgent)
- **Follow-up Visit** (Priority: Low)
- **Surgical Procedure Notes** (Priority: High)

### Patient References
- PAT-12345 (John Doe)
- PAT-67890 (Jane Smith)
- PAT-11111 (Bob Johnson)

---

## Recording the Demo

### Screen Recording Tools
- **macOS**: QuickTime, ScreenFlow
- **Linux**: SimpleScreenRecorder, OBS Studio
- **Windows**: OBS Studio, Camtasia

### Demo Recording Tips
1. Close unnecessary browser tabs
2. Use incognito mode for clean UI
3. Prepare test data beforehand
4. Have script open on second monitor
5. Test audio/video before recording
6. Use 1920x1080 resolution
7. Record in segments (easier to edit)

### Demo Segments
1. **Intro** (30s) - Overview of Dictat
2. **Doctor Upload** (2min) - Upload dictation
3. **Secretary Transcribe** (3min) - Claim and transcribe
4. **Doctor Review** (1min) - Review and approve
5. **Admin/API** (1min) - Show API docs
6. **Outro** (30s) - Summary and next steps

**Total**: ~8 minutes

---

## Next Steps After Demo

1. **Implement Frontend** (see `FRONTEND_TODO.md`)
2. **Add Real Audio Processing** (transcription API integration)
3. **Implement GDPR Features** (data export, deletion)
4. **Add Email Notifications**
5. **Deploy to Production** (Digital Ocean)
6. **Set Up Monitoring** (Prometheus, Grafana)
7. **Add Backup Strategy**
8. **Write User Documentation**

---

## Support

For issues or questions:
- Check `README.md` for project overview
- See `CLAUDE.md` for development guidelines
- Review `TODO.md` for roadmap
- Create GitHub issue for bugs

---

**Last Updated**: 2025-11-16
**Status**: Backend Ready ✅ | Frontend Pending ⏳
**Demo Duration**: ~30 minutes (with setup)
**Difficulty**: Intermediate
