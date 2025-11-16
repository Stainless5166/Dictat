"""
Main API router combining all endpoint routers

TODO Phase 1:
- Include all routers with proper prefixes
- Add API versioning strategy
- Configure rate limiting per endpoint
- Add OpenAPI documentation tags
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, dictations, transcriptions, audit, gdpr

api_router = APIRouter()

# TODO: Configure rate limiting and authentication requirements
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(dictations.router, prefix="/dictations", tags=["Dictations"])
api_router.include_router(transcriptions.router, prefix="/transcriptions", tags=["Transcriptions"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Logs"])
api_router.include_router(gdpr.router, prefix="/gdpr", tags=["GDPR Compliance"])
