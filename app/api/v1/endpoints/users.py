"""
User management endpoints

TODO Phase 1:
- GET /users - List all users (admin only, with pagination)
- GET /users/me - Get current user profile
- GET /users/{id} - Get user by ID (admin or self)
- PUT /users/{id} - Update user profile (admin or self)
- DELETE /users/{id} - Deactivate user (admin only, soft delete)
- PUT /users/{id}/activate - Activate user (admin only)
- PUT /users/{id}/change-password - Change password (self only)
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()


@router.get("/")
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    role: str = Query(None, description="Filter by role"),
    is_active: bool = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),  # TODO: Uncomment when implemented
):
    """
    List all users with pagination and filtering

    TODO Phase 1:
    - Require admin role
    - Implement pagination
    - Add filtering by role, active status
    - Add sorting options
    - Add search by name/email
    - Return user list without passwords
    - Log access in audit log

    Query Parameters:
    - skip: Number of records to skip (default 0)
    - limit: Number of records to return (default 100, max 1000)
    - role: Filter by role (doctor, secretary, admin)
    - is_active: Filter by active status

    Returns:
    - List of users
    - Total count
    - Pagination metadata

    Raises:
    - 403: Not authorized (requires admin role)
    """
    pass


@router.get("/me")
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),  # TODO: Uncomment when implemented
):
    """
    Get current user's profile

    TODO Phase 1:
    - Return current user object
    - Include role and permissions
    - Include statistics (dictations count, transcriptions count)
    - Don't return password hash

    Returns:
    - User object with profile information

    Raises:
    - 401: Not authenticated
    """
    pass


@router.get("/{user_id}")
async def get_user(
    user_id: int = Path(..., gt=0, description="User ID"),
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),  # TODO: Uncomment when implemented
):
    """
    Get user by ID

    TODO Phase 1:
    - Check authorization (admin or self)
    - Fetch user from database
    - Return user without password
    - Log access in audit log

    Path Parameters:
    - user_id: ID of user to retrieve

    Returns:
    - User object

    Raises:
    - 403: Not authorized (must be admin or self)
    - 404: User not found
    """
    pass


@router.put("/{user_id}")
async def update_user(
    user_id: int = Path(..., gt=0, description="User ID"),
    # TODO: Add request body with updatable fields
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),  # TODO: Uncomment when implemented
):
    """
    Update user profile

    TODO Phase 1:
    - Check authorization (admin or self)
    - Validate update data
    - Only allow role change for admin
    - Update user in database
    - Log update in audit log
    - Return updated user

    Path Parameters:
    - user_id: ID of user to update

    Request Body:
    - full_name: Updated full name (optional)
    - email: Updated email (optional, must be unique)
    - role: Updated role (admin only, optional)

    Returns:
    - Updated user object

    Raises:
    - 403: Not authorized
    - 404: User not found
    - 400: Email already in use
    """
    pass


@router.delete("/{user_id}")
async def delete_user(
    user_id: int = Path(..., gt=0, description="User ID"),
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),  # TODO: Uncomment when implemented
):
    """
    Deactivate user (soft delete)

    TODO Phase 1:
    - Require admin role
    - Set is_active = False
    - Set deleted_at timestamp
    - Cannot delete self
    - Log deletion in audit log
    - Trigger GDPR data retention policy

    Path Parameters:
    - user_id: ID of user to deactivate

    Returns:
    - Success message

    Raises:
    - 403: Not authorized (requires admin)
    - 404: User not found
    - 400: Cannot delete self
    """
    pass


@router.put("/{user_id}/activate")
async def activate_user(
    user_id: int = Path(..., gt=0, description="User ID"),
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),  # TODO: Uncomment when implemented
):
    """
    Activate deactivated user

    TODO Phase 1:
    - Require admin role
    - Set is_active = True
    - Clear deleted_at timestamp
    - Log activation in audit log

    Path Parameters:
    - user_id: ID of user to activate

    Returns:
    - Success message

    Raises:
    - 403: Not authorized (requires admin)
    - 404: User not found
    """
    pass


@router.put("/me/change-password")
async def change_password(
    # TODO: Add request body with old_password and new_password
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),  # TODO: Uncomment when implemented
):
    """
    Change current user's password

    TODO Phase 1:
    - Verify old password
    - Validate new password strength
    - Hash new password
    - Update password in database
    - Invalidate all existing tokens (logout all sessions)
    - Send confirmation email
    - Log password change in audit log

    Request Body:
    - old_password: Current password
    - new_password: New password

    Returns:
    - Success message

    Raises:
    - 401: Invalid old password
    - 422: Weak new password
    """
    pass
