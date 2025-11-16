# CLAUDE.md - AI Assistant Guide for Dictat

## Project Overview

**Dictat** is a minimal FastAPI web application that serves as a starter template. The project demonstrates basic FastAPI routing with a simple "Hello World" style API.

### Key Information
- **Framework**: FastAPI (Python web framework)
- **License**: GNU General Public License v3.0 (GPL-3.0)
- **Project Type**: Web API / REST API
- **Current State**: Initial setup with basic endpoints

## Repository Structure

```
Dictat/
├── .git/                 # Git version control
├── .idea/                # JetBrains IDE configuration
├── .gitignore           # Git ignore rules (Python, IDEs, venv, etc.)
├── LICENSE              # GPL-3.0 License text
├── main.py              # Main FastAPI application
├── test_main.http       # HTTP request tests
└── CLAUDE.md            # This file - AI assistant documentation
```

### File Descriptions

#### main.py (217 bytes)
The core application file containing:
- FastAPI app initialization
- Root endpoint (`/`) - Returns `{"message": "Hello World"}`
- Parameterized greeting endpoint (`/hello/{name}`) - Returns personalized greeting

#### test_main.http (156 bytes)
HTTP test file for manual endpoint testing:
- Test for root endpoint: `GET http://127.0.0.1:8000/`
- Test for hello endpoint: `GET http://127.0.0.1:8000/hello/User`

#### .gitignore (3,205 bytes)
Comprehensive ignore rules covering:
- Python artifacts (`__pycache__/`, `*.pyc`, `*.pyo`)
- Virtual environments (`venv/`, `env/`, `.venv/`)
- IDE files (`.idea/`, `.vscode/`)
- Testing and coverage (`pytest_cache/`, `.coverage`)
- Build artifacts (`dist/`, `build/`, `*.egg-info/`)

## Technology Stack

### Current Dependencies
- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Python 3.x**: Required (specific version not pinned)

### Missing Configuration Files
**Important**: This project currently lacks dependency management files. Consider adding:
- `requirements.txt` or `pyproject.toml` for dependency management
- `README.md` for project documentation
- Test files (e.g., `test_main.py` using pytest)
- Configuration management (environment variables, settings)

## Development Workflows

### Running the Application

Since there's no dependency file yet, the recommended workflow is:

```bash
# Install FastAPI and ASGI server
pip install fastapi uvicorn[standard]

# Run the development server
uvicorn main:app --reload

# Server will start at http://127.0.0.1:8000
```

### Testing Endpoints

1. **Using the HTTP test file**: Open `test_main.http` in a compatible IDE (JetBrains IDEs, VS Code with REST Client extension)
2. **Using curl**:
   ```bash
   curl http://127.0.0.1:8000/
   curl http://127.0.0.1:8000/hello/Claude
   ```
3. **Using browser**: Navigate to `http://127.0.0.1:8000` or `http://127.0.0.1:8000/docs` for auto-generated API docs

### Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn[standard]

# Run application
uvicorn main:app --reload
```

## Code Conventions and Standards

### Current Code Style
- **Async/await**: All endpoints use `async def` for asynchronous request handling
- **Type hints**: Function parameters include type hints (`name: str`)
- **FastAPI decorators**: Standard decorator pattern (`@app.get("/path")`)

### Recommended Conventions for AI Assistants

When modifying or extending this codebase:

1. **Maintain async/await pattern**: Continue using `async def` for route handlers
2. **Use type hints**: Always include type hints for parameters and return types
3. **Follow FastAPI best practices**:
   - Use Pydantic models for request/response validation
   - Implement proper error handling with HTTPException
   - Document endpoints with docstrings
4. **Code organization**:
   - Keep route handlers in `main.py` for now (small project)
   - Consider splitting into modules when adding more endpoints (e.g., `routers/`, `models/`, `services/`)
5. **Testing**: When adding tests, use pytest with FastAPI's TestClient
6. **Dependencies**: When adding new dependencies, create `requirements.txt` or `pyproject.toml`

## Git Workflow

### Branch Structure
- **Main branch**: Default branch for stable code
- **Feature branches**: Should follow pattern `feature/description` or `claude/session-id`

### Commit Conventions
The repository uses standard commit messages. When committing:
- Use clear, descriptive messages
- Focus on the "why" rather than the "what"
- Follow format: `<type>: <description>` (e.g., "feat: add user authentication endpoint")

### Current Git Status
- Clean working tree
- Recent commits show project initialization with default setup

## Common Development Tasks

### Adding a New Endpoint

```python
@app.get("/new-endpoint")
async def new_endpoint():
    return {"message": "Response data"}
```

### Adding Request Parameters

```python
from fastapi import Query

@app.get("/items")
async def get_items(skip: int = Query(0), limit: int = Query(10)):
    return {"skip": skip, "limit": limit}
```

### Adding Request Body with Pydantic

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
async def create_item(item: Item):
    return {"item": item}
```

## Important Notes for AI Assistants

### Project State
- **Early stage**: This is a minimal starter project
- **No database**: No database integration or ORM configured
- **No authentication**: No auth/security implemented
- **No environment configuration**: No `.env` or config management

### Before Making Changes
1. Check if dependencies need to be added to a requirements file
2. Ensure FastAPI best practices are followed
3. Consider backward compatibility with existing endpoints
4. Test changes locally before committing

### Security Considerations
- When adding new features, watch for:
  - Input validation (use Pydantic models)
  - SQL injection risks (if adding database)
  - XSS vulnerabilities (sanitize user inputs)
  - Authentication/authorization requirements
  - CORS configuration if frontend will consume the API

### Suggested Improvements
When asked to enhance the project, consider:
1. Adding `requirements.txt` with pinned versions
2. Creating a `README.md` with setup instructions
3. Adding proper testing with pytest
4. Implementing logging
5. Adding environment-based configuration
6. Creating API documentation
7. Adding database integration (SQLAlchemy/Tortoise ORM)
8. Implementing authentication (OAuth2, JWT)
9. Adding error handling middleware
10. Structuring code into modules (routers, models, schemas, services)

## API Documentation

### Endpoints

#### GET /
Returns a hello world message.

**Response**:
```json
{
  "message": "Hello World"
}
```

#### GET /hello/{name}
Returns a personalized greeting.

**Parameters**:
- `name` (path parameter, string): The name to greet

**Response**:
```json
{
  "message": "Hello {name}"
}
```

### Auto-generated Documentation
FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Environment Information

### Platform
- **OS**: Linux (kernel 4.4.0)
- **Working Directory**: `/home/user/Dictat`
- **Git**: Repository initialized

### IDE Configuration
- JetBrains IDE configuration present (`.idea/` directory)
- HTTP test file compatible with JetBrains HTTP Client

## FAQs for AI Assistants

**Q: Should I create a requirements.txt file?**
A: Yes, when adding or modifying dependencies, create a `requirements.txt` file with all dependencies listed.

**Q: How should I structure database models?**
A: Create a `models.py` file for SQLAlchemy models or use Pydantic models in a `schemas.py` file for request/response validation.

**Q: Where should I add configuration?**
A: Create a `config.py` file using Pydantic's `BaseSettings` for environment-based configuration.

**Q: Should I modify main.py or create new files?**
A: For small changes, modify `main.py`. For larger features, create a modular structure with `routers/`, `models/`, `schemas/`, and `services/` directories.

**Q: How do I handle errors?**
A: Use FastAPI's `HTTPException` for API errors and consider adding custom exception handlers.

## Version History

- **Initial Commit**: Project created with GPL-3.0 license
- **Second Commit**: Default FastAPI hello world implementation
- **Third Commit**: Added comprehensive .gitignore

---

**Last Updated**: 2025-11-16
**Project Version**: 0.1.0 (Initial Development)
