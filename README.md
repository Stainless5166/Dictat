# Dictat

A self-hosted medical dictation service enabling healthcare professionals to record voice dictations and secretaries to transcribe them into structured markdown documents.

## Overview

Dictat provides a complete workflow for medical dictation management:

- **Doctors** record voice dictations via browser or upload audio files
- **Secretaries** access a work queue, claim dictations, and transcribe using an integrated markdown editor
- **Doctors** review and approve completed transcriptions
- **Administrators** manage users, monitor system health, and ensure compliance

## Technology Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **Python 3.11+** - Runtime environment
- **UV** - Fast Python package manager and dependency resolver
- **PostgreSQL 15+** - Primary relational database
- **SQLAlchemy 2.0+** - Async ORM with asyncpg driver
- **Alembic** - Database migration management
- **Redis** - Caching, session storage, and message broker
- **Celery/ARQ** - Distributed task queue for background jobs
- **Open Policy Agent (OPA)** - Policy-based authorization engine
- **python-jose** - JWT token generation and validation
- **passlib[bcrypt]** - Secure password hashing

### Frontend
- **Svelte** or **React** - Modern UI framework
- **Vite** - Lightning-fast build tool
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **TanStack Query** - Server state management
- **Zod** - Schema validation
- **CodeMirror/Monaco** - Markdown editor
- **MediaRecorder API** - Browser-based audio recording

### Infrastructure
- **Docker** - Containerization
- **Docker Swarm** - Container orchestration
- **Traefik** - Reverse proxy, load balancer, SSL termination
- **NFS** - Network file storage for audio files (streaming only, no local caching)
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization and dashboards
- **Loki** - Log aggregation
- **Promtail** - Log collection and shipping

### Development Tools
- **pytest** - Python testing framework
- **Vitest** - Frontend unit testing
- **Playwright/Cypress** - E2E testing
- **ruff** - Fast Python linter
- **black** - Code formatter
- **mypy** - Static type checker
- **ESLint** - JavaScript/TypeScript linter

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Traefik (SSL/Load Balancer)               │
└────────────┬──────────────────────────┬─────────────────────┘
             │                          │
    ┌────────▼────────┐        ┌────────▼────────┐
    │  Frontend       │        │  FastAPI        │
    │  (Nginx/Svelte) │◄──────►│  Backend        │
    └─────────────────┘        └───┬────┬────┬───┘
                                   │    │    │
                    ┌──────────────┘    │    └──────────┐
                    │                   │               │
            ┌───────▼────────┐   ┌──────▼──────┐  ┌────▼─────┐
            │  PostgreSQL    │   │   Redis     │  │   OPA    │
            │  (Database)    │   │   (Cache)   │  │ (AuthZ)  │
            └────────────────┘   └─────────────┘  └──────────┘
                    │
            ┌───────▼────────┐
            │  NFS Storage   │
            │  (Audio Files) │
            └────────────────┘

         Monitoring & Logging:
    ┌──────────────────────────────┐
    │ Prometheus → Grafana         │
    │ Loki ← Promtail              │
    └──────────────────────────────┘
```

### Key Architecture Decisions

1. **Streaming-Only File Access** - Audio files are streamed directly from NFS, never cached locally
2. **Docker Swarm** - Self-hosted orchestration for high availability and scaling
3. **Policy-Based Authorization** - OPA handles complex role-based access control
4. **Async Architecture** - FastAPI with async/await for high concurrency
5. **Monitoring-First** - Prometheus/Grafana/Loki integrated from the start
6. **Security-Focused** - HIPAA-compliant audit logging, encryption, JWT authentication

## Data Model

### Core Entities

- **User** - Doctors, secretaries, and administrators
  - id, email, hashed_password, role, is_active, created_at
- **Dictation** - Audio recording metadata
  - id, user_id, file_path, duration, status, created_at, assigned_to
- **Transcription** - Markdown transcriptions linked to dictations
  - id, dictation_id, content, status, created_by, reviewed_by, version
- **AuditLog** - Compliance and security audit trail
  - id, user_id, action, resource_type, resource_id, timestamp, metadata

### Workflow States

**Dictation Status**: `pending` → `assigned` → `in_progress` → `completed` → `reviewed`

**User Roles**: `doctor`, `secretary`, `admin`

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- UV (Python package manager)
- pnpm or npm

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Dictat
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Backend setup**
   ```bash
   # Install UV if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv sync

   # Run migrations
   uv run alembic upgrade head

   # Start development server
   uv run uvicorn main:app --reload
   ```

5. **Frontend setup**
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Code Quality & Git Hooks

We use pre-commit hooks to ensure code quality and consistency. Install them once:

```bash
# Install pre-commit hooks
./scripts/setup-hooks.sh
```

This will set up automatic checks that run before each commit:

**Python:**
- **Black** - Code formatting (100 char line length)
- **Ruff** - Fast linting and import sorting
- **mypy** - Static type checking
- **Bandit** - Security vulnerability scanning

**General:**
- **Hadolint** - Dockerfile linting
- **ShellCheck** - Shell script linting
- **Markdownlint** - Markdown formatting
- **YAML/JSON validators** - Configuration file validation

**Frontend (when available):**
- **ESLint** - JavaScript/TypeScript linting
- **Prettier** - Code formatting
- **TypeScript** - Type checking

**Manual commands:**
```bash
# Run all hooks manually
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate

# Bypass hooks (not recommended)
git commit --no-verify
```

### Running Tests

```bash
# Backend tests
uv run pytest

# Backend tests with coverage
uv run pytest --cov=. --cov-report=html

# Frontend tests
cd frontend
pnpm test

# E2E tests
pnpm test:e2e
```

## Production Deployment

### Docker Swarm Setup

1. **Initialize Swarm (on manager node)**
   ```bash
   docker swarm init
   ```

2. **Configure NFS mount**
   - Mount NFS share on all nodes at `/mnt/dictat-storage`

3. **Set up secrets**
   ```bash
   echo "your-secret-key" | docker secret create jwt_secret -
   echo "db-password" | docker secret create db_password -
   ```

4. **Deploy the stack**
   ```bash
   docker stack deploy -c docker-stack.yml dictat
   ```

5. **Access Grafana**
   - URL: https://monitoring.yourdomain.com
   - Set up dashboards for application metrics

### Environment Variables

Key environment variables (see `.env.example` for complete list):

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - Secret for JWT token signing
- `NFS_MOUNT_PATH` - Path to NFS storage
- `OPA_URL` - Open Policy Agent endpoint
- `PROMETHEUS_URL` - Prometheus endpoint
- `LOKI_URL` - Loki endpoint

## Security & Compliance

### HIPAA Considerations

- **Audit Logging** - All data access and modifications are logged
- **Encryption at Rest** - PostgreSQL encryption, encrypted NFS volumes
- **Encryption in Transit** - TLS/SSL via Traefik with Let's Encrypt
- **Access Control** - Role-based access via OPA policies
- **Data Retention** - Configurable retention policies
- **Session Management** - Secure JWT tokens with refresh mechanism

### Authentication Flow

1. User submits credentials to `/auth/login`
2. Backend validates credentials and generates JWT access + refresh tokens
3. Frontend stores tokens securely (httpOnly cookies or memory)
4. Requests include JWT in Authorization header
5. Backend validates JWT and checks OPA for authorization
6. Refresh tokens used to obtain new access tokens

### Authorization (OPA)

Policies are defined in Rego and enforce:
- Role-based access (doctor/secretary/admin)
- Resource ownership (users can only access their own dictations)
- State transitions (only secretaries can mark as in_progress)
- Administrative actions (only admins can manage users)

## Monitoring & Observability

### Metrics (Prometheus + Grafana)

- Request rate, latency, error rate (RED metrics)
- Custom metrics: dictations uploaded, transcriptions completed
- Database connection pool statistics
- NFS I/O performance
- Service health checks

### Logs (Loki + Promtail)

- Structured JSON logging
- Centralized log aggregation
- Query logs by service, level, user, or request ID
- Audit log retention for compliance

### Alerting

Configure Grafana alerts for:
- Service downtime
- High error rates
- Database connection failures
- Disk space on NFS volumes
- Unusual access patterns

## API Documentation

Once running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Key endpoints:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /dictations` - Upload dictation
- `GET /dictations/queue` - Get work queue (secretaries)
- `POST /dictations/{id}/claim` - Claim dictation
- `POST /transcriptions` - Submit transcription
- `PUT /transcriptions/{id}` - Update transcription
- `POST /dictations/{id}/review` - Review and approve

## Contributing

1. Create a feature branch from `main`
2. Set up git hooks (if not already done): `./scripts/setup-hooks.sh`
3. Make your changes
4. Git hooks will automatically run on commit (formatting, linting, type checking)
5. Run tests: `uv run pytest`
6. Submit a pull request

### Code Quality

Pre-commit hooks will automatically run these checks, but you can also run them manually:

```bash
# All hooks
pre-commit run --all-files

# Individual tools
uv run black .              # Format code
uv run ruff check --fix .   # Lint and fix
uv run mypy .               # Type checking
uv run bandit -r .          # Security scanning
uv run safety check         # Dependency vulnerabilities
```

## License

GNU General Public License v3.0 - see [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Contact the development team

## Roadmap

See [TODO.md](TODO.md) for detailed development tasks and project roadmap.

## Testing

See [Test_Targets.md](Test_Targets.md) for comprehensive testing strategy and targets.
