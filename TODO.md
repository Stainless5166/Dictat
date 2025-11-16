# Dictat Development TODO

Comprehensive task list for building the Dictat medical dictation service.

## Legend
- [ ] Not started
- [x] Completed
- [~] In progress

---

## 1. Project Setup (5 tasks)

- [ ] Initialize UV project and create pyproject.toml
- [ ] Define all Python dependencies (FastAPI, SQLAlchemy, Alembic, asyncpg, etc.)
- [ ] Create .env.example with all required environment variables
- [ ] Set up Pydantic Settings for configuration management
- [ ] Configure SQLAlchemy with asyncpg for PostgreSQL

---

## 2. Database Setup (6 tasks)

- [ ] Design database schema (User, Role, Dictation, Transcription, AuditLog tables)
- [ ] Create SQLAlchemy models with proper relationships
- [ ] Set up Alembic for database migrations
- [ ] Create initial migration for all database tables
- [ ] Add database indexes for performance optimization
- [ ] Create database seed script for development data

---

## 3. Authentication (6 tasks)

- [ ] Implement JWT token generation and validation
- [ ] Create password hashing utilities (bcrypt/argon2)
- [ ] Build user registration endpoint with validation
- [ ] Build login endpoint returning JWT tokens
- [ ] Create JWT dependency for protected routes
- [ ] Implement refresh token mechanism

---

## 4. Authorization - Open Policy Agent (5 tasks)

- [ ] Set up Open Policy Agent (OPA) container in Docker Compose
- [ ] Write OPA policies for role-based access (doctor/secretary/admin)
- [ ] Create OPA client integration in FastAPI
- [ ] Build authorization dependency using OPA
- [ ] Test OPA policies for all user roles and permissions

---

## 5. File Storage - Docker Volumes (8 tasks)

- [ ] Configure Docker volume for persistent audio storage
- [ ] Create volume mount definitions in docker-compose.yml
- [ ] Implement audio file upload endpoint with streaming
- [ ] Add audio format validation (mp3, wav, m4a, ogg)
- [ ] Implement chunked upload for large audio files
- [ ] Create audio streaming endpoint (no local caching)
- [ ] Add audio playback range request support (HTTP 206)
- [ ] Implement file deletion endpoint with security checks

---

## 6. Core API - Dictations & Transcriptions (11 tasks)

- [ ] Create dictation CRUD endpoints
- [ ] Build dictation listing with pagination and filtering
- [ ] Implement dictation assignment to secretaries
- [ ] Create work queue endpoint for secretaries
- [ ] Build dictation claiming mechanism
- [ ] Implement status transitions (pending→in_progress→completed→reviewed)
- [ ] Create transcription CRUD endpoints
- [ ] Add markdown validation for transcriptions
- [ ] Implement transcription autosave functionality
- [ ] Build review/approval endpoint for doctors
- [ ] Create revision history for transcriptions

---

## 7. Background Tasks & Real-time (5 tasks)

- [ ] Set up Redis for caching and session management
- [ ] Configure Celery/ARQ for background tasks
- [ ] Implement email notification task for new dictations
- [ ] Create WebSocket endpoint for real-time updates
- [ ] Build notification system for workflow events

---

## 8. Security & Compliance - UK GDPR (11 tasks)

- [ ] Implement audit logging for all sensitive operations
- [ ] Add audit log query endpoints for compliance
- [ ] Configure data encryption at rest (PostgreSQL settings)
- [ ] Implement field-level encryption for sensitive data
- [ ] Add CORS middleware configuration
- [ ] Implement rate limiting middleware
- [ ] Add security headers (HSTS, CSP, X-Frame-Options)
- [ ] Implement GDPR Right to Erasure (data deletion) endpoint
- [ ] Implement GDPR Right to Portability (data export) endpoint
- [ ] Create data retention policy implementation
- [ ] Configure Prometheus metrics endpoint
- [ ] Add custom application metrics (dictations, transcriptions)
- [ ] Set up structured logging with Loki format
- [ ] Create health check endpoints (/health, /ready)

---

## 9. Frontend Setup (5 tasks)

- [ ] Initialize frontend project (Svelte/React with Vite)
- [ ] Set up TypeScript configuration
- [ ] Configure Tailwind CSS or UI component library
- [ ] Create authentication context/store
- [ ] Set up API client with axios/fetch wrapper

---

## 10. Frontend - Authentication (3 tasks)

- [ ] Build login page with form validation
- [ ] Build registration page
- [ ] Create protected route wrapper/guard

---

## 11. Frontend - Doctor Interface (4 tasks)

- [ ] Build doctor dashboard with dictation list
- [ ] Create audio recording component (MediaRecorder API)
- [ ] Build dictation upload component with progress
- [ ] Create dictation status tracking view

---

## 12. Frontend - Secretary Interface (9 tasks)

- [ ] Build secretary dashboard with work queue
- [ ] Create audio playback component with controls
- [ ] Implement playback speed control (0.5x - 2x)
- [ ] Add rewind/forward skip buttons (5s, 10s)
- [ ] Build markdown editor with preview
- [ ] Implement autosave for transcription
- [ ] Create transcription submission interface
- [ ] Build review interface for doctors
- [ ] Add keyboard shortcuts for efficiency

---

## 13. Frontend - Shared Features (4 tasks)

- [ ] Add search and filter components
- [ ] Create notification toast/banner system
- [ ] Implement real-time updates via WebSocket
- [ ] Build user profile and settings page

---

## 14. Testing - Backend (10 tasks)

- [ ] Write pytest configuration and fixtures
- [ ] Create test database setup/teardown
- [ ] Write unit tests for database models
- [ ] Write unit tests for authentication utilities
- [ ] Write API endpoint tests for authentication
- [ ] Write API endpoint tests for dictations
- [ ] Write API endpoint tests for transcriptions
- [ ] Write integration tests for complete workflows
- [ ] Write OPA policy tests
- [ ] Set up test coverage reporting (>80% target)

---

## 15. Testing - Frontend (2 tasks)

- [ ] Write frontend unit tests (components)
- [ ] Write frontend integration tests (Playwright/Cypress)

---

## 16. Docker & Containerization (4 tasks)

- [ ] Create Dockerfile for FastAPI backend
- [ ] Create Dockerfile for frontend (Nginx serving static files)
- [ ] Create multi-stage builds for optimization
- [ ] Write docker-compose.yml for local development
- [ ] Write docker-compose.prod.yml for production deployment

---

## 17. Terraform & Digital Ocean Infrastructure (12 tasks)

- [ ] Create Terraform configuration directory structure
- [ ] Define Digital Ocean provider and variables (terraform.tfvars)
- [ ] Create Droplet resource configuration (4GB RAM minimum)
- [ ] Configure block storage volume (100GB for Docker volumes)
- [ ] Set up firewall rules (ports 80, 443, 22)
- [ ] Configure SSH key provisioning
- [ ] Create DNS records (if using Digital Ocean DNS)
- [ ] Add provisioner scripts for Docker installation
- [ ] Create Terraform outputs (droplet IP, volume ID)
- [ ] Write Terraform backend configuration (state management)
- [ ] Document Terraform variable requirements
- [ ] Create infrastructure teardown procedures

---

## 18. Production Deployment (13 tasks)

- [ ] Create production docker-compose.yml
- [ ] Configure Traefik as reverse proxy and load balancer
- [ ] Set up Traefik SSL/TLS certificates (Let's Encrypt)
- [ ] Configure PostgreSQL service with persistence
- [ ] Configure Redis service
- [ ] Configure OPA service
- [ ] Set up Prometheus service
- [ ] Set up Grafana service
- [ ] Set up Loki service
- [ ] Configure Promtail for log collection
- [ ] Create Grafana dashboards for application metrics
- [ ] Create database backup strategy and scripts (Digital Ocean Spaces)
- [ ] Implement health checks for all services
- [ ] Create deployment scripts and documentation

---

## 19. CI/CD Pipeline (8 tasks)

- [ ] Create CI pipeline (GitHub Actions/GitLab CI)
- [ ] Add linting to CI (ruff/black for Python, ESLint for frontend)
- [ ] Add type checking to CI (mypy for Python)
- [ ] Add automated tests to CI pipeline
- [ ] Add security scanning to CI (bandit, safety, npm audit)
- [ ] Create CD pipeline for Docker image building
- [ ] Set up container registry (Docker Hub/private registry)
- [ ] Create deployment automation (SSH deploy to Digital Ocean)

---

## 20. Documentation (10 tasks)

- [x] Write comprehensive README.md
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Create deployment documentation
- [ ] Write developer setup guide
- [ ] Create user manual for doctors
- [ ] Create user manual for secretaries
- [ ] Document OPA policies and authorization rules
- [x] Create architecture diagrams (Mermaid)
- [ ] Document monitoring and alerting setup
- [ ] Create disaster recovery documentation
- [ ] Create GDPR compliance documentation

---

## Progress Summary

**Total Tasks**: 139

**Completed**: 2 / 139 (1.4%)

### By Category
- Project Setup: 0/5
- Database: 0/6
- Authentication: 0/6
- Authorization (OPA): 0/5
- File Storage (Docker Volumes): 0/8
- Core API: 0/11
- Background Tasks: 0/5
- Security & Compliance (GDPR): 0/14
- Frontend Setup: 0/5
- Frontend Auth: 0/3
- Frontend Doctor: 0/4
- Frontend Secretary: 0/9
- Frontend Shared: 0/4
- Backend Testing: 0/10
- Frontend Testing: 0/2
- Docker: 0/5
- Terraform & Infrastructure: 0/12
- Production Deployment: 0/13
- CI/CD: 0/8
- Documentation: 2/11

---

## Development Phases

### Phase 1: Foundation (Weeks 1-2)
- Project Setup
- Database Setup
- Authentication
- Basic Docker setup

### Phase 2: Core Backend (Weeks 3-4)
- Authorization (OPA)
- File Storage (Docker Volumes)
- Core API endpoints
- Background tasks

### Phase 3: Frontend (Weeks 5-6)
- Frontend setup
- Authentication UI
- Doctor interface
- Secretary interface

### Phase 4: Testing & Security (Week 7)
- Backend tests
- Frontend tests
- Security hardening
- GDPR compliance features

### Phase 5: Infrastructure & Deployment (Week 8)
- Terraform infrastructure setup
- Digital Ocean deployment
- CI/CD pipeline
- Monitoring & logging

### Phase 6: Polish & Launch (Week 9-10)
- Bug fixes
- Performance optimization
- User testing
- Production deployment
- Final documentation

---

## Notes

- **Prioritize UK GDPR compliance** throughout development (Isle of Man data protection)
- Implement audit logging early for all sensitive operations
- Test OPA policies thoroughly - authorization is critical
- Ensure Docker volume streaming works properly before building frontend audio components
- Set up monitoring and alerting before production deployment
- Consider disaster recovery and backup strategies from the start
- **Digital Ocean costs**: Plan for ~$40-50/month (4GB droplet + 100GB storage + backups)
- **Data retention**: Medical records typically retained for 7 years
- **Terraform state**: Store in Digital Ocean Spaces or S3 for team collaboration

---

## Cost Optimization Tips

- Start with 4GB droplet, scale to 8GB if >50 concurrent users
- Use Digital Ocean Spaces for database backups ($5/250GB)
- Enable automated backups only if needed ($4.80/month)
- Consider reserved instances for 15% discount (annual commitment)
- Monitor bandwidth usage (1TB included, $0.01/GB after)

---

Last Updated: 2025-11-16
