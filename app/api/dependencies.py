"""
FastAPI dependencies for authentication and authorization
"""

from typing import Optional, Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import AuthorizationError
from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.opa import check_permission


def require_role(*allowed_roles: UserRole) -> Callable:
    """
    Dependency factory for requiring specific user roles

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
        async def admin_only_endpoint():
            ...

        @router.get("/doctors-and-admins")
        async def doctors_endpoint(user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN))):
            ...

    Args:
        *allowed_roles: One or more UserRole values that are allowed

    Returns:
        Dependency function that validates user role

    Raises:
        HTTPException 403: If user doesn't have required role
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}",
            )
        return current_user

    return role_checker


def require_permission(
    action: str,
    resource_type: str,
    resource_id_param: Optional[str] = None,
    resource_owner_id_param: Optional[str] = None,
) -> Callable:
    """
    Dependency factory for requiring specific permissions via OPA

    Usage:
        @router.get("/dictations/{dictation_id}")
        async def get_dictation(
            dictation_id: int,
            user: User = Depends(require_permission("read", "dictation", "dictation_id"))
        ):
            ...

    Args:
        action: Action to check (e.g., "read", "update", "delete")
        resource_type: Type of resource (e.g., "dictation", "transcription")
        resource_id_param: Name of path/query parameter containing resource ID
        resource_owner_id_param: Name of path/query parameter containing owner ID

    Returns:
        Dependency function that validates permission via OPA

    Raises:
        HTTPException 403: If user doesn't have required permission
    """

    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Check permission with OPA"""
        # Note: For full implementation, you'd need to extract resource_id and owner_id
        # from request context. This is a simplified version.

        allowed = await check_permission(
            user_id=current_user.id,
            user_role=current_user.role.value,
            action=action,
            resource_type=resource_type,
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action} on {resource_type}",
            )

        return current_user

    return permission_checker


async def check_resource_permission(
    current_user: User,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    resource_owner_id: Optional[int] = None,
) -> None:
    """
    Utility function to check permission for a specific resource

    Usage:
        @router.delete("/dictations/{dictation_id}")
        async def delete_dictation(
            dictation_id: int,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            dictation = await get_dictation_by_id(db, dictation_id)
            await check_resource_permission(
                current_user=current_user,
                action="delete",
                resource_type="dictation",
                resource_id=dictation.id,
                resource_owner_id=dictation.doctor_id,
            )
            # Proceed with deletion...

    Args:
        current_user: Authenticated user
        action: Action being performed
        resource_type: Type of resource
        resource_id: Optional resource ID
        resource_owner_id: Optional owner ID

    Raises:
        HTTPException 403: If permission is denied
    """
    allowed = await check_permission(
        user_id=current_user.id,
        user_role=current_user.role.value,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_owner_id=resource_owner_id,
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: cannot {action} {resource_type}",
        )
