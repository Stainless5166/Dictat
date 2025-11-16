"""
Dictat - Medical Dictation Service FastAPI Application

Main application entry point with configuration for:
- API routing
- CORS middleware
- OpenAPI documentation
- Error handling
- Request logging
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    **Dictat** is a self-hosted medical dictation service for healthcare professionals.

    ## Features
    - 🎤 Audio dictation upload and management
    - 📝 Transcription workflow (secretary → doctor review)
    - 🔐 Role-based access control (Doctor, Secretary, Admin)
    - 🔒 UK GDPR compliant with audit logging
    - 📊 Real-time workflow status tracking

    ## Authentication
    All endpoints (except /auth/register and /auth/login) require authentication.
    Use the /auth/login endpoint to obtain a JWT access token, then include it in the Authorization header:

    ```
    Authorization: Bearer <your_access_token>
    ```

    ## Roles
    - **Doctor**: Creates dictations, reviews transcriptions
    - **Secretary**: Claims dictations, creates transcriptions
    - **Admin**: Full access to all resources
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Dictat Support",
        "email": "support@dictat.im",
    },
    license_info={
        "name": "Proprietary",
    },
)

# CORS Configuration
# TODO: Update allowed origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "Accept-Ranges"],
)


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed error messages"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring

    Returns service status and version information
    """
    return {
        "status": "healthy",
        "service": "dictat",
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint

    Returns API information and links to documentation
    """
    return {
        "service": "Dictat API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    logger.info("Starting Dictat API server")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Version: {settings.API_V1_PREFIX}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run shutdown tasks"""
    logger.info("Shutting down Dictat API server")


# Custom OpenAPI schema
def custom_openapi():
    """Customize OpenAPI schema with additional information"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token obtained from /auth/login",
        }
    }

    # Add security requirement to all endpoints (except auth)
    for path, path_item in openapi_schema["paths"].items():
        if not path.startswith("/api/v1/auth"):
            for operation in path_item.values():
                if isinstance(operation, dict) and "security" not in operation:
                    operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
