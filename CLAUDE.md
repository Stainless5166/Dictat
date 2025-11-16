# Claude Development Guidelines for Dictat

## Project Overview

**Dictat** is a self-hosted medical dictation service enabling healthcare professionals to record voice dictations and secretaries to transcribe them into structured markdown documents.

**Jurisdiction**: Isle of Man (UK GDPR compliance, NOT HIPAA)

**Deployment**: Single Digital Ocean droplet (~$40-50/month)

**Architecture**: Docker Compose single-server deployment with Terraform IaC

## Technology Stack

### Backend
- **FastAPI** - Async Python web framework
- **Python 3.11+** - Runtime
- **UV** - Package manager (NEVER pip)
- **PostgreSQL 15+** - Database
- **SQLAlchemy 2.0+** - Async ORM with asyncpg
- **Alembic** - Migrations
- **Redis** - Caching and message broker
- **Celery/ARQ** - Background tasks
- **Open Policy Agent (OPA)** - Authorization

### Frontend
- **Svelte** or **React** - UI framework
- **Vite** - Build tool
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Styling
- **TanStack Query** - Server state
- **CodeMirror/Monaco** - Markdown editor

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Terraform** - Infrastructure as Code (Digital Ocean)
- **Traefik** - Reverse proxy & SSL
- **Docker Volumes** - Persistent storage (NOT NFS)
- **Prometheus + Grafana + Loki** - Monitoring

### Development Tools
- **pytest** - Python testing
- **ruff** - Python linter/formatter
- **black** - Code formatter
- **mypy** - Type checker
- **pre-commit** - Git hooks
- **tflint** - Terraform linting
- **checkov** - Terraform security scanning

---

## Python Development Guidelines

### 1. Package Management - UV ONLY

**CRITICAL**: ONLY use `uv`, NEVER use `pip`

```bash
# Installation
uv add package-name

# Dev dependencies
uv add --dev package-name

# Running tools
uv run pytest
uv run uvicorn main:app --reload
uv run alembic upgrade head

# Upgrading packages
uv add --dev package-name --upgrade-package package-name

# FORBIDDEN
uv pip install package  # ❌ NEVER
pip install package     # ❌ NEVER
uv add package@latest   # ❌ NEVER
```

### 2. Code Quality Standards

**Type Hints**: Required for all code
```python
def process_dictation(dictation_id: str) -> dict[str, Any]:
    """Process a dictation and return metadata."""
    ...
```

**Docstrings**: Required for all public APIs
```python
def create_transcription(
    dictation_id: str,
    content: str,
    user_id: str
) -> Transcription:
    """
    Create a new transcription for a dictation.

    Args:
        dictation_id: UUID of the dictation
        content: Markdown content of transcription
        user_id: UUID of the transcribing user

    Returns:
        Newly created Transcription object

    Raises:
        ValueError: If dictation not found or already transcribed
    """
    ...
```

**Function Design**:
- Small, focused functions (max 20-30 lines)
- Single responsibility
- Early returns to avoid nesting
- Descriptive names (prefix handlers with `handle_`)

**Line Length**: 88 characters maximum (Black default)

### 3. Testing Requirements

**Framework**: pytest with anyio for async

```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=. --cov-report=html

# Specific test
uv run pytest tests/test_auth.py::test_login_success
```

**Requirements**:
- New features MUST have tests
- Bug fixes MUST have regression tests
- Async tests use `anyio`, not `asyncio`
- Test edge cases and error conditions
- Minimum 80% backend coverage, 70% frontend coverage

**Test Structure**:
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_dictation_success(client: AsyncClient, auth_headers):
    """Test successful dictation creation."""
    response = await client.post(
        "/dictations",
        json={"title": "Test", "audio_file": "path.mp3"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test"
```

### 4. Code Style

**Naming Conventions**:
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

**String Formatting**: Use f-strings
```python
# Good
message = f"User {user.email} created dictation {dictation.id}"

# Bad
message = "User %s created dictation %s" % (user.email, dictation.id)
message = "User {} created dictation {}".format(user.email, dictation.id)
```

**Imports**: Organized in groups
```python
# Standard library
import os
from datetime import datetime

# Third-party
from fastapi import FastAPI, Depends
from sqlalchemy import select

# Local
from app.models import User, Dictation
from app.config import settings
```

### 5. Code Formatting Tools

**Ruff** (primary linter and formatter):
```bash
# Format code
uv run ruff format .

# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix
```

**Black** (code formatter):
```bash
uv run black .
```

**Type Checking** (Pyright/mypy):
```bash
uv run pyright
uv run mypy .
```

**Security Scanning** (Bandit):
```bash
uv run bandit -r .
```

### 6. Pre-commit Hooks

**Setup** (one-time):
```bash
./scripts/setup-hooks.sh
```

**Hooks automatically run**:
- Black (formatting)
- Ruff (linting)
- mypy (type checking)
- Bandit (security)
- YAML/JSON validation
- Markdown linting

**Manual execution**:
```bash
pre-commit run --all-files
```

### 7. Development Philosophy

**Simplicity**: Write simple, straightforward code
- Avoid clever tricks
- Prefer explicit over implicit
- Clear is better than concise

**Readability**: Make code easy to understand
- Self-documenting code
- Comments for "why", not "what"
- Consistent patterns

**Build Iteratively**:
- Start with minimal functionality
- Verify it works before adding complexity
- Test frequently with realistic inputs

**Functional Code**:
- Prefer immutable data structures where practical
- Pure functions when possible
- Push side effects to edges

**Clean Logic**:
- Keep core business logic clean
- Push I/O and implementation details to boundaries
- Separate concerns

**File Organization**:
- Balance organization with simplicity
- Don't over-engineer file structure
- Group related functionality

### 8. Error Handling

**Explicit Error Handling**:
```python
from fastapi import HTTPException

async def get_dictation(dictation_id: str) -> Dictation:
    """Retrieve a dictation by ID."""
    dictation = await db.get(Dictation, dictation_id)
    if dictation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dictation {dictation_id} not found"
        )
    return dictation
```

**Validation**:
```python
from pydantic import BaseModel, validator

class DictationCreate(BaseModel):
    title: str
    audio_format: str

    @validator("audio_format")
    def validate_audio_format(cls, v):
        allowed = ["mp3", "wav", "m4a", "ogg"]
        if v not in allowed:
            raise ValueError(f"Format must be one of {allowed}")
        return v
```

### 9. Async Best Practices

**Always await async functions**:
```python
# Good
result = await async_function()

# Bad
result = async_function()  # Returns coroutine, not result
```

**Use async context managers**:
```python
async with AsyncClient() as client:
    response = await client.get("/endpoint")
```

**Database sessions**:
```python
from app.database import get_db

async def create_user(user_data: dict, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

### 10. Test-Driven Development (TDD)

**CRITICAL**: Follow TDD practices for all new features and bug fixes

#### TDD Cycle: Red-Green-Refactor

```
1. RED:    Write a failing test first
2. GREEN:  Write minimal code to pass the test
3. REFACTOR: Improve code while keeping tests green
4. COMMIT: Commit working code with tests
5. DOCUMENT: Update docs when feature is complete
```

#### When to Use TDD

**ALWAYS use TDD for**:
- ✅ New features (API endpoints, models, services)
- ✅ Bug fixes (write test that reproduces bug first)
- ✅ Security-critical code (authentication, authorization, GDPR)
- ✅ Complex business logic
- ✅ Public APIs and utilities

**TDD is OPTIONAL for**:
- 🟡 Simple data models with no logic
- 🟡 Configuration files
- 🟡 Documentation-only changes

#### TDD Workflow

**Step 1: Write the Test First (RED)**

```python
# tests/unit/test_dictation_service.py
import pytest
from app.services.dictation import create_dictation
from app.models.user import UserRole

@pytest.mark.asyncio
async def test_create_dictation_success(test_db, test_doctor):
    """Test creating a dictation as a doctor"""
    # Arrange
    dictation_data = {
        "title": "Patient Visit Notes",
        "audio_file": "recording.mp3",
        "duration": 120,
    }

    # Act
    dictation = await create_dictation(
        db=test_db,
        user=test_doctor,
        data=dictation_data
    )

    # Assert
    assert dictation.id is not None
    assert dictation.title == "Patient Visit Notes"
    assert dictation.doctor_id == test_doctor.id
    assert dictation.status == "pending"
```

**Run the test - it should FAIL**:
```bash
uv run pytest tests/unit/test_dictation_service.py::test_create_dictation_success -v
# Expected: FAILED (function doesn't exist yet)
```

**Commit the failing test**:
```bash
git add tests/unit/test_dictation_service.py
git commit -m "test: add failing test for dictation creation

RED phase of TDD - test currently fails as create_dictation
service function has not been implemented yet."
```

**Step 2: Write Minimal Code (GREEN)**

```python
# app/services/dictation.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dictation import Dictation
from app.models.user import User

async def create_dictation(
    db: AsyncSession,
    user: User,
    data: dict
) -> Dictation:
    """
    Create a new dictation

    Args:
        db: Database session
        user: User creating the dictation (must be doctor)
        data: Dictation data (title, audio_file, duration)

    Returns:
        Created Dictation object
    """
    dictation = Dictation(
        title=data["title"],
        audio_file=data["audio_file"],
        duration=data["duration"],
        doctor_id=user.id,
        status="pending",
    )

    db.add(dictation)
    await db.commit()
    await db.refresh(dictation)

    return dictation
```

**Run the test - it should PASS**:
```bash
uv run pytest tests/unit/test_dictation_service.py::test_create_dictation_success -v
# Expected: PASSED
```

**Commit the passing implementation**:
```bash
git add app/services/dictation.py
git commit -m "feat: implement create_dictation service function

GREEN phase of TDD - minimal implementation to pass test.
Creates dictation with pending status and associates with doctor."
```

**Step 3: Add Edge Cases and Error Handling**

Write more tests for edge cases:
```python
@pytest.mark.asyncio
async def test_create_dictation_secretary_forbidden(test_db, test_secretary):
    """Test that secretaries cannot create dictations"""
    dictation_data = {
        "title": "Test",
        "audio_file": "test.mp3",
        "duration": 60,
    }

    with pytest.raises(PermissionError):
        await create_dictation(
            db=test_db,
            user=test_secretary,  # Secretary, not doctor
            data=dictation_data
        )

@pytest.mark.asyncio
async def test_create_dictation_missing_title(test_db, test_doctor):
    """Test validation for missing title"""
    dictation_data = {
        "audio_file": "test.mp3",
        "duration": 60,
    }

    with pytest.raises(ValueError, match="Title is required"):
        await create_dictation(
            db=test_db,
            user=test_doctor,
            data=dictation_data
        )
```

**Run tests - they should FAIL**:
```bash
uv run pytest tests/unit/test_dictation_service.py -v
# Expected: 1 passed, 2 failed
```

**Commit the new failing tests**:
```bash
git add tests/unit/test_dictation_service.py
git commit -m "test: add edge case tests for dictation creation

RED phase - tests for:
- Permission check (only doctors can create)
- Validation (title is required)

Both tests currently fail."
```

**Step 4: Implement Edge Cases (GREEN)**

```python
# app/services/dictation.py
from app.models.user import UserRole

async def create_dictation(
    db: AsyncSession,
    user: User,
    data: dict
) -> Dictation:
    """Create a new dictation"""

    # Validation
    if user.role != UserRole.DOCTOR:
        raise PermissionError("Only doctors can create dictations")

    if "title" not in data or not data["title"]:
        raise ValueError("Title is required")

    dictation = Dictation(
        title=data["title"],
        audio_file=data["audio_file"],
        duration=data["duration"],
        doctor_id=user.id,
        status="pending",
    )

    db.add(dictation)
    await db.commit()
    await db.refresh(dictation)

    return dictation
```

**Run all tests - they should ALL PASS**:
```bash
uv run pytest tests/unit/test_dictation_service.py -v
# Expected: 3 passed
```

**Commit the complete implementation**:
```bash
git add app/services/dictation.py
git commit -m "feat: add validation and permission checks to create_dictation

GREEN phase - all tests passing.

Changes:
- Add role check (only doctors can create dictations)
- Add title validation (title is required)
- Raise appropriate exceptions for violations"
```

**Step 5: Refactor (REFACTOR)**

Improve code quality while keeping tests green:

```python
# app/services/dictation.py
from typing import TypedDict

class DictationCreateData(TypedDict):
    """Type definition for dictation creation data"""
    title: str
    audio_file: str
    duration: int

async def create_dictation(
    db: AsyncSession,
    user: User,
    data: DictationCreateData
) -> Dictation:
    """
    Create a new dictation

    Args:
        db: Database session
        user: User creating the dictation (must be doctor)
        data: Dictation creation data

    Returns:
        Created Dictation object

    Raises:
        PermissionError: If user is not a doctor
        ValueError: If required fields are missing
    """
    _validate_user_can_create(user)
    _validate_dictation_data(data)

    dictation = Dictation(
        title=data["title"],
        audio_file=data["audio_file"],
        duration=data["duration"],
        doctor_id=user.id,
        status="pending",
    )

    db.add(dictation)
    await db.commit()
    await db.refresh(dictation)

    return dictation


def _validate_user_can_create(user: User) -> None:
    """Validate that user has permission to create dictations"""
    if user.role != UserRole.DOCTOR:
        raise PermissionError("Only doctors can create dictations")


def _validate_dictation_data(data: dict) -> None:
    """Validate dictation creation data"""
    if "title" not in data or not data["title"]:
        raise ValueError("Title is required")
```

**Run all tests - they should STILL PASS**:
```bash
uv run pytest tests/unit/test_dictation_service.py -v
# Expected: 3 passed (no changes in behavior)
```

**Commit the refactoring**:
```bash
git add app/services/dictation.py
git commit -m "refactor: extract validation helpers in dictation service

REFACTOR phase - improve code organization while keeping tests green.

Changes:
- Extract validation into separate functions
- Add TypedDict for better type safety
- Improve docstrings with Raises section
- Better separation of concerns

All tests still passing, no behavior changes."
```

**Step 6: Update Documentation**

Once ALL tests are passing and code is refactored:

```bash
# Update TODO.md to mark task as complete
# Update Test_Targets.md to update coverage
# Add API documentation if needed
```

**Commit documentation updates**:
```bash
git add TODO.md Test_Targets.md
git commit -m "docs: update TODO and test targets for dictation creation

Mark dictation creation feature as complete:
- TODO.md: Mark task as [x] completed
- Test_Targets.md: Update coverage (90%+ for dictation service)

All tests passing (3/3), feature complete."
```

#### Git Commit Strategy During TDD

**Commit FREQUENTLY** during TDD cycle:

1. **RED commits**: Commit failing tests
   ```bash
   git commit -m "test: add failing test for <feature>"
   ```

2. **GREEN commits**: Commit when tests pass
   ```bash
   git commit -m "feat: implement <feature> to pass tests"
   ```

3. **REFACTOR commits**: Commit improvements
   ```bash
   git commit -m "refactor: improve <aspect> while keeping tests green"
   ```

4. **FIX commits**: Commit bug fixes with tests
   ```bash
   git commit -m "fix: resolve <bug> - add regression test"
   ```

5. **DOCS commits**: Commit documentation after feature complete
   ```bash
   git commit -m "docs: update documentation for <feature>"
   ```

**Commit Message Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `test`: Adding or modifying tests (RED phase)
- `feat`: New feature implementation (GREEN phase)
- `fix`: Bug fix with test
- `refactor`: Code improvement without behavior change
- `docs`: Documentation updates
- `chore`: Maintenance tasks

**Example TDD commit sequence**:
```bash
# 1. RED phase
git commit -m "test: add failing test for user authentication"

# 2. GREEN phase
git commit -m "feat: implement basic user authentication"

# 3. More RED
git commit -m "test: add edge case tests for invalid credentials"

# 4. More GREEN
git commit -m "feat: add validation for authentication credentials"

# 5. REFACTOR
git commit -m "refactor: extract token generation to separate function"

# 6. DOCS
git commit -m "docs: update TODO.md - authentication feature complete"
```

#### Testing Best Practices

**Coverage Requirements**:
- **Minimum 80%** overall backend coverage
- **100%** coverage for security-critical code
- **90%+** coverage for business logic
- **70%+** coverage for frontend

**Test Organization**:
```
tests/
├── unit/              # Fast, isolated tests (no DB, no network)
│   ├── test_security_password.py
│   ├── test_security_jwt.py
│   └── test_user_model.py
├── api/               # API endpoint tests (with DB)
│   ├── test_auth_endpoints.py
│   └── test_dictation_endpoints.py
├── integration/       # Full workflow tests
│   └── test_dictation_workflow.py
└── conftest.py       # Shared fixtures
```

**Running Tests During Development**:

```bash
# Run specific test file
uv run pytest tests/unit/test_dictation_service.py -v

# Run specific test
uv run pytest tests/unit/test_dictation_service.py::test_create_dictation_success -v

# Run with coverage
uv run pytest tests/unit/ --cov=app --cov-report=term-missing

# Run fast tests only (exclude slow integration tests)
uv run pytest tests/unit/ -v

# Watch mode (re-run on file changes) - requires pytest-watch
uv run ptw tests/unit/ -- -v
```

**Test Naming Convention**:
- `test_<function_name>_<scenario>_<expected_result>`
- Examples:
  - `test_create_dictation_success`
  - `test_create_dictation_invalid_user_raises_error`
  - `test_verify_password_wrong_password_returns_false`

#### Documentation Updates After Tests Pass

**Once ALL tests are GREEN**, update these files:

**1. Update TODO.md**:
```markdown
- [x] Implement dictation creation endpoint
```

**2. Update Test_Targets.md** (if applicable):
```markdown
✅ Dictation Service (3/3 tests, 95% coverage)
- Create dictation
- Validation
- Permission checks
```

**3. Add API Documentation** (if new endpoint):
```python
@router.post("/dictations", response_model=DictationResponse, status_code=201)
async def create_dictation(
    data: DictationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dictation:
    """
    Create a new dictation

    **Permissions**: Doctors only

    **GDPR**: Creates audit log entry

    Args:
        data: Dictation creation data
        current_user: Authenticated user (must be doctor)
        db: Database session

    Returns:
        Created dictation

    Raises:
        403: If user is not a doctor
        400: If validation fails
    """
    return await create_dictation(db, current_user, data.dict())
```

**4. Update README.md** (if major feature):
Add to features list, update examples

**5. Commit documentation**:
```bash
git add TODO.md Test_Targets.md README.md app/api/v1/endpoints/dictations.py
git commit -m "docs: update documentation for dictation creation feature

Updates:
- TODO.md: Mark dictation creation as complete
- Test_Targets.md: Add coverage metrics (95%)
- README.md: Add dictation creation to features
- Add comprehensive docstring to API endpoint

All tests passing (68/68)"
```

#### TDD Anti-Patterns to AVOID

**❌ Don't write all tests first**:
```python
# BAD - Writing 50 tests before any implementation
def test_feature_1(): ...
def test_feature_2(): ...
# ... 48 more tests
def test_feature_50(): ...
```

**✅ Do write tests incrementally**:
```python
# GOOD - One test, implement, one test, implement
def test_basic_feature():
    # Write test, implement, commit

# After basic works:
def test_edge_case():
    # Write test, implement, commit
```

**❌ Don't skip the RED phase**:
```python
# BAD - Writing implementation first
def create_user(...):
    # Implementation without test

# Then writing test
def test_create_user():
    # Test that might not fail
```

**✅ Do write failing test first**:
```python
# GOOD - Test first (will fail)
def test_create_user():
    user = create_user(...)  # Doesn't exist yet
    assert user.id is not None

# Then implement to make it pass
def create_user(...):
    # Minimal implementation
```

**❌ Don't commit broken code**:
```bash
# BAD - Code doesn't compile
git commit -m "feat: half-implemented feature"
```

**✅ Do commit working code (even if incomplete)**:
```bash
# GOOD - Tests pass, feature incomplete
git commit -m "feat: implement basic user creation

GREEN phase - basic functionality working.
TODO: Add validation and edge cases."
```

#### TDD for Bug Fixes

**ALWAYS write regression test first**:

```python
# 1. Write test that reproduces the bug (RED)
@pytest.mark.asyncio
async def test_dictation_claim_race_condition():
    """
    Regression test for bug #42

    Bug: Two secretaries could claim same dictation simultaneously
    Expected: Second claim should fail with 409 Conflict
    """
    # Test that currently fails due to bug
    ...

# 2. Fix the bug (GREEN)
# ... implement fix ...

# 3. Verify test passes
# 4. Commit with reference to bug
git commit -m "fix: prevent race condition in dictation claiming

Fixes bug where two secretaries could claim same dictation.

Solution: Add database-level unique constraint and handle
concurrent claims with optimistic locking.

Closes #42" \
  --trailer "Reported-by: Dr. Smith"
```

---

## Terraform Development Guidelines

### 1. Multi-File Awareness

**CRITICAL**: Always scan the entire module directory before making changes

- Check for dependencies across files
- Variables, outputs, data sources may be referenced anywhere
- When modifying a resource, search for ALL references
- Consider module boundaries

**Search for references**:
```bash
# Before changing a resource
grep -r "aws_instance.web" --include="*.tf"
grep -r "instance_id" --include="*.tf"

# Check variable usage
grep -r "var.environment" --include="*.tf"
```

### 2. File Organization

Follow standard Terraform conventions:

```
terraform/
├── main.tf           # Primary resources
├── variables.tf      # Variable declarations
├── outputs.tf        # Output definitions
├── providers.tf      # Provider configurations
├── versions.tf       # Version constraints
├── data.tf           # Data sources (if numerous)
├── locals.tf         # Local values (if numerous)
├── security.tf       # Security groups, IAM (optional)
└── networking.tf     # VPC, subnets (optional)
```

### 3. Standard Workflow

**Before making changes**:
```bash
# Initialize
terraform init

# Validate syntax
terraform validate

# Lint with tflint
tflint --init
tflint --recursive

# Security scan with checkov
checkov -d .

# Review structure
find . -name "*.tf" -type f
grep -r "resource\|module\|data" --include="*.tf" | head -20
```

**After making changes**:
```bash
# Format
terraform fmt -recursive

# Validate
terraform validate

# Lint
tflint --recursive

# Security scan
checkov -d . --compact

# Plan
terraform plan -out=plan.out
```

### 4. Linting with tflint

**Configuration** (.tflint.hcl):
```hcl
plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "aws" {
  enabled = true
  version = "0.21.1"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}
```

**Usage**:
```bash
# Initialize plugins
tflint --init

# Run linting
tflint

# Recursive (all modules)
tflint --recursive

# Detailed output
tflint --format compact
```

**Fix common issues**:
- Deprecated syntax
- Invalid instance types
- Hardcoded credentials
- Missing required providers
- Unused declarations

### 5. Security Scanning with checkov

**Usage**:
```bash
# Basic scan
checkov -d .

# Terraform-specific
checkov -d . --framework terraform

# Skip specific checks
checkov -d . --skip-check CKV_AWS_20,CKV_AWS_23

# JSON output
checkov -d . -o json
```

**Critical checks to pass**:
- Encryption at rest enabled
- Encryption in transit enabled
- No public access (unless required)
- IAM least privilege
- Logging enabled
- Backup configured
- No hardcoded secrets

### 6. Terraform Best Practices

**Resource naming**:
```hcl
# Good - consistent naming
resource "digitalocean_droplet" "dictat_app" {
  name   = "dictat-app-${var.environment}"
  region = var.region
  size   = var.droplet_size
}

# Bad - inconsistent
resource "digitalocean_droplet" "my-server" {
  name = "server1"
}
```

**Variable declarations**:
```hcl
variable "droplet_size" {
  description = "Size of the Digital Ocean droplet"
  type        = string
  default     = "s-2vcpu-4gb"

  validation {
    condition     = contains(["s-2vcpu-4gb", "s-4vcpu-8gb"], var.droplet_size)
    error_message = "Droplet size must be s-2vcpu-4gb or s-4vcpu-8gb"
  }
}
```

**Outputs with descriptions**:
```hcl
output "droplet_ip" {
  description = "Public IP address of the Dictat application droplet"
  value       = digitalocean_droplet.dictat_app.ipv4_address
}
```

**Use locals for computed values**:
```hcl
locals {
  common_tags = {
    Project     = "Dictat"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  droplet_name = "dictat-${var.environment}-app"
}
```

### 7. Multi-File Change Process

**Example: Adding a new variable**

1. **Add to variables.tf**:
```hcl
variable "enable_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}
```

2. **Search for usage locations**:
```bash
grep -r "backup" --include="*.tf"
```

3. **Update main.tf**:
```hcl
resource "digitalocean_droplet" "dictat_app" {
  # ...
  backups = var.enable_backups
}
```

4. **Verify no broken references**:
```bash
terraform validate
tflint
```

### 8. CRITICAL RULE: No Live Changes

**Claude MUST NOT ever make changes to live systems**

- ❌ `terraform apply`
- ❌ `terraform destroy`
- ❌ Any state-modifying commands

**ONLY allowed**:
- ✅ `terraform validate`
- ✅ `terraform fmt`
- ✅ `terraform plan`
- ✅ `tflint`
- ✅ `checkov`

### 9. Testing Checklist

Before considering Terraform changes complete:

- [ ] `terraform fmt -recursive` passes
- [ ] `terraform validate` passes
- [ ] `tflint --recursive` shows no errors
- [ ] `checkov -d .` critical issues resolved
- [ ] All variable references resolved
- [ ] All output consumers checked
- [ ] Documentation updated
- [ ] Tested with `terraform plan`

---

## Architecture Decisions

### 1. Single-Server Deployment

**Choice**: Docker Compose on single Digital Ocean droplet
**NOT**: Docker Swarm, Kubernetes, multi-server

**Rationale**:
- Cost-effective (~$40-50/month)
- Simpler operations
- Sufficient for expected load
- Easy to understand and maintain

**Scale-up path**: Upgrade droplet size before going multi-server

### 2. Docker Volumes (NOT NFS)

**Storage**: Docker volumes on block storage
**NOT**: NFS, network file systems

**Rationale**:
- Simpler configuration
- Better performance for single server
- No network overhead
- Easier backup with Digital Ocean snapshots

### 3. Terraform for Infrastructure

**Tool**: Terraform with Digital Ocean provider
**NOT**: Manual setup, ClickOps, other IaC tools

**Rationale**:
- Infrastructure as Code
- Version controlled
- Reproducible deployments
- Easy disaster recovery

### 4. Streaming-Only File Access

**Pattern**: Stream audio files directly from volumes
**NOT**: Load into memory, cache locally

**Rationale**:
- Memory efficiency
- Support for large files
- Predictable resource usage
- Better for concurrent users

### 5. Open Policy Agent for AuthZ

**Tool**: OPA for authorization decisions
**NOT**: Hard-coded permissions, database-based authz

**Rationale**:
- Centralized policy management
- Complex rules without code changes
- Audit trail of policy decisions
- Testable policies (Rego tests)

---

## Compliance Requirements - UK GDPR

### Isle of Man Data Protection

**Jurisdiction**: Isle of Man (aligned with UK GDPR)
**NOT**: HIPAA (US healthcare regulation)

### Required Features

**1. Right to Erasure (GDPR Article 17)**:
```python
@router.delete("/user/account")
async def delete_user_account(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user account and all associated data.

    Implements GDPR Right to Erasure (Article 17).
    - Deletes dictations and transcriptions
    - Anonymizes audit logs (retain structure, remove PII)
    - Cannot delete if active transcriptions assigned
    """
    # Implementation
```

**2. Right to Portability (GDPR Article 20)**:
```python
@router.get("/user/data-export")
async def export_user_data(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export all user data in machine-readable format.

    Implements GDPR Right to Data Portability (Article 20).
    Returns JSON with all user data including:
    - Profile information
    - Dictations
    - Transcriptions
    - Audit logs
    """
    # Implementation
```

**3. Audit Logging**:
- Log all sensitive operations
- Immutable audit trail
- Retain for 7 years (medical records)
- Include: user, action, resource, timestamp, metadata

**4. Data Retention**:
- Configurable retention policies
- Automated deletion of expired data
- Medical records: 7 years recommended
- Audit logs: 7 years required

**5. Encryption**:
- At rest: PostgreSQL encryption, encrypted volumes
- In transit: TLS/SSL via Traefik with Let's Encrypt
- Field-level encryption for sensitive data

### Testing Requirements

All GDPR endpoints require 100% test coverage:
- Data export completeness
- Data deletion verification
- Audit log anonymization
- Consent management

---

## Git Commit Conventions

### Commit Message Format

```
<type>: <subject>

<body>

<trailers>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat: add GDPR data export endpoint

Implements Right to Data Portability (GDPR Article 20).
Returns JSON with all user data including dictations,
transcriptions, and audit logs."

# Bug fix with reporter
git commit -m "fix: prevent duplicate transcription claims" \
  --trailer "Reported-by: Dr. Smith"

# Feature with GitHub issue
git commit -m "feat: add audio playback speed control" \
  --trailer "Github-Issue: #42"
```

### Trailers

**For bug fixes/features from user reports**:
```bash
git commit --trailer "Reported-by: User Name"
```

**For GitHub issues**:
```bash
git commit --trailer "Github-Issue: #123"
```

**NEVER mention**:
- `Co-authored-by`
- AI tool used
- Assistant/Claude in commit messages

---

## Project Structure

```
Dictat/
├── main.py                  # FastAPI application entry point
├── pyproject.toml           # UV dependencies and tool config
├── .env.example             # Environment variables template
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── docker-compose.yml       # Local development
├── docker-compose.prod.yml  # Production deployment
├── Dockerfile               # Backend container
├── alembic.ini              # Database migration config
│
├── app/
│   ├── __init__.py
│   ├── config.py            # Pydantic settings
│   ├── database.py          # SQLAlchemy setup
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── dictation.py
│   │   └── transcription.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   └── dictation.py
│   ├── api/                 # API routes
│   │   ├── auth.py
│   │   ├── dictations.py
│   │   ├── transcriptions.py
│   │   └── gdpr.py          # GDPR endpoints
│   ├── core/                # Core functionality
│   │   ├── security.py      # JWT, hashing
│   │   └── opa.py           # OPA integration
│   └── services/            # Business logic
│       ├── dictation.py
│       └── transcription.py
│
├── alembic/
│   └── versions/            # Database migrations
│
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── unit/
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── api/
│   │   ├── test_auth.py
│   │   ├── test_dictations.py
│   │   └── test_gdpr.py
│   └── integration/
│       └── test_workflows.py
│
├── frontend/                # Svelte/React app
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── terraform/               # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── versions.tf
│   └── .tflint.hcl
│
├── scripts/
│   └── setup-hooks.sh       # Git hooks installation
│
└── docs/
    ├── README.md            # Project overview
    ├── TODO.md              # Development roadmap
    ├── Test_Targets.md      # Testing strategy
    └── claude.md            # This file
```

---

## Common Tasks Reference

### Development Workflow

```bash
# Setup
git clone <repo>
cd Dictat
cp .env.example .env
./scripts/setup-hooks.sh

# Install dependencies
uv sync

# Start database
docker-compose up -d postgres redis

# Run migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn main:app --reload

# Run tests
uv run pytest

# Format and lint
uv run ruff format .
uv run ruff check . --fix
uv run mypy .
```

### Database Operations

```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Show current version
uv run alembic current

# Show migration history
uv run alembic history
```

### Docker Operations

```bash
# Local development
docker-compose up -d

# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f backend

# Rebuild container
docker-compose build backend

# Shell into container
docker-compose exec backend bash
```

### Terraform Operations

```bash
# Initialize
cd terraform
terraform init

# Format
terraform fmt -recursive

# Validate
terraform validate

# Lint
tflint --init
tflint --recursive

# Security scan
checkov -d .

# Plan (safe, read-only)
terraform plan -out=plan.out

# NEVER run apply without explicit approval
```

---

## Troubleshooting

### UV Issues

**Problem**: `uv: command not found`
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

**Problem**: Package conflicts
```bash
# Clear cache
uv cache clean

# Reinstall dependencies
rm -rf .venv
uv sync
```

### Database Issues

**Problem**: Migration conflicts
```bash
# Check current version
uv run alembic current

# Show history
uv run alembic history

# Stamp to specific version
uv run alembic stamp <revision>
```

**Problem**: Connection refused
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL
```

### Docker Issues

**Problem**: Port already in use
```bash
# Find process using port
lsof -i :8000

# Stop all containers
docker-compose down
```

**Problem**: Volume permission issues
```bash
# Fix volume permissions
docker-compose exec backend chown -R app:app /app/storage
```

### Test Failures

**Problem**: Database state
```bash
# Use separate test database
export DATABASE_URL=postgresql://user:pass@localhost/dictat_test

# Clear test database
docker-compose exec postgres dropdb dictat_test
docker-compose exec postgres createdb dictat_test
```

---

## Important Reminders

### NEVER
- ❌ Use `pip` instead of `uv`
- ❌ Run `terraform apply` or `terraform destroy`
- ❌ Commit secrets or credentials
- ❌ Mention HIPAA (use UK GDPR)
- ❌ Reference Docker Swarm or NFS
- ❌ Mention AI/Claude in commits
- ❌ Skip tests for new features
- ❌ Ignore type errors

### ALWAYS
- ✅ Use `uv` for all Python packages
- ✅ Add type hints to all code
- ✅ Write tests for new features
- ✅ Run pre-commit hooks before committing
- ✅ Document GDPR-related endpoints
- ✅ Use Mermaid for diagrams
- ✅ Check cross-file dependencies in Terraform
- ✅ Run `tflint` and `checkov` on Terraform
- ✅ Stream audio files, never cache
- ✅ Use OPA for authorization decisions
- ✅ Update the TODO.md list before commiting

---

## Quick Reference

### Python Commands
```bash
uv add package              # Add dependency
uv add --dev package        # Add dev dependency
uv sync                     # Install dependencies
uv run pytest               # Run tests
uv run ruff format .        # Format code
uv run ruff check . --fix   # Lint and fix
uv run mypy .               # Type check
```

### Git Commands
```bash
git add -A                              # Stage all
git commit -m "type: message"           # Commit
git commit --trailer "Reported-by:name" # With trailer
git push origin branch-name             # Push
```

### Docker Commands
```bash
docker-compose up -d             # Start services
docker-compose down              # Stop services
docker-compose logs -f service   # View logs
docker-compose exec service bash # Shell
```

### Terraform Commands
```bash
terraform fmt -recursive    # Format
terraform validate          # Validate
terraform plan             # Plan (safe)
tflint --recursive         # Lint
checkov -d .               # Security scan
```

---

## Contact & Support

- **Issues**: Create GitHub issue with `claude/` branch prefix
- **Documentation**: See README.md, TODO.md, Test_Targets.md

---

Last Updated: 2025-11-16
