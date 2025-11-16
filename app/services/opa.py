"""
Open Policy Agent (OPA) integration for authorization

TODO Phase 2:
- Implement OPA client
- Create policy evaluation functions
- Define policy input structure
- Add caching for policy decisions
- Implement fallback authorization
"""

import httpx
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import OPAError, AuthorizationError

logger = get_logger(__name__)


class OPAClient:
    """
    Client for interacting with Open Policy Agent

    TODO Phase 2:
    - Implement connection pooling
    - Add retry logic with exponential backoff
    - Implement circuit breaker pattern
    - Add metrics for policy evaluation latency
    - Implement policy decision caching with Redis
    """

    def __init__(self):
        self.base_url = settings.OPA_URL
        self.policy_path = settings.OPA_POLICY_PATH
        self.timeout = settings.OPA_TIMEOUT

    async def evaluate_policy(
        self,
        user_id: int,
        user_role: str,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        resource_owner_id: Optional[int] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Evaluate authorization policy with OPA

        Args:
            user_id: ID of user performing action
            user_role: Role of user (doctor, secretary, admin)
            action: Action being performed (create, read, update, delete, claim, etc.)
            resource_type: Type of resource (dictation, transcription, user)
            resource_id: Optional ID of specific resource
            resource_owner_id: Optional ID of resource owner
            additional_context: Optional additional context for policy

        Returns:
            True if action is allowed, False otherwise

        TODO Phase 2:
        - Build proper OPA input document
        - Send POST request to OPA
        - Parse and validate response
        - Handle OPA errors gracefully
        - Log policy decisions
        - Cache decisions when appropriate
        - Implement timeout handling

        Raises:
            OPAError: If policy evaluation fails
            AuthorizationError: If action is explicitly denied
        """
        # Build OPA input document
        input_doc = {
            "input": {
                "user": {
                    "id": user_id,
                    "role": user_role,
                },
                "action": action,
                "resource": {
                    "type": resource_type,
                    "id": resource_id,
                    "owner_id": resource_owner_id,
                },
                "context": additional_context or {},
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{self.policy_path}",
                    json=input_doc,
                )
                response.raise_for_status()
                result = response.json()
                allowed = result.get("result", False)

                logger.info(
                    f"OPA policy evaluation: user={user_id}, role={user_role}, "
                    f"action={action}, resource={resource_type}, allowed={allowed}"
                )

                return allowed

        except httpx.HTTPError as e:
            logger.error(f"OPA connection error: {e}. Using fallback authorization.")
            # Fallback to basic RBAC if OPA is unavailable
            return self._fallback_authorization(
                user_role, action, resource_type, user_id, resource_owner_id
            )
        except Exception as e:
            logger.error(f"OPA policy evaluation error: {e}")
            raise OPAError(f"Failed to evaluate authorization policy: {str(e)}")

    def _fallback_authorization(
        self,
        user_role: str,
        action: str,
        resource_type: str,
        user_id: int,
        resource_owner_id: Optional[int],
    ) -> bool:
        """
        Fallback authorization when OPA is unavailable

        TODO Phase 2:
        - Implement basic RBAC rules
        - Log when fallback is used
        - Alert ops team if OPA is down
        - This should mirror OPA policies
        """
        # Admin can do everything
        if user_role == "admin":
            return True

        # Doctors can manage their own dictations
        if resource_type == "dictation":
            if action in ["create", "read", "update", "delete"] and user_role == "doctor":
                return resource_owner_id is None or resource_owner_id == user_id
            if action in ["read", "claim"] and user_role == "secretary":
                return True

        # Secretaries can manage their own transcriptions
        if resource_type == "transcription":
            if action in ["create", "read", "update", "submit"] and user_role == "secretary":
                return resource_owner_id is None or resource_owner_id == user_id
            if action in ["read", "approve", "reject"] and user_role == "doctor":
                return True

        # Default deny
        return False


# Singleton OPA client instance
opa_client = OPAClient()


async def check_permission(
    user_id: int,
    user_role: str,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    resource_owner_id: Optional[int] = None,
) -> bool:
    """
    Convenience function for checking permissions

    Args:
        user_id: ID of user
        user_role: Role of user
        action: Action to check
        resource_type: Type of resource
        resource_id: Optional resource ID
        resource_owner_id: Optional owner ID

    Returns:
        True if allowed, False otherwise

    TODO Phase 2:
    - Add permission caching
    - Log permission checks
    - Add metrics
    """
    return await opa_client.evaluate_policy(
        user_id=user_id,
        user_role=user_role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_owner_id=resource_owner_id,
    )


async def require_permission(
    user_id: int,
    user_role: str,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    resource_owner_id: Optional[int] = None,
) -> None:
    """
    Raise exception if permission is denied

    Args:
        user_id: ID of user
        user_role: Role of user
        action: Action to check
        resource_type: Type of resource
        resource_id: Optional resource ID
        resource_owner_id: Optional owner ID

    Raises:
        AuthorizationError: If permission is denied

    TODO Phase 2:
    - Add detailed error messages
    - Log authorization failures
    - Include required permissions in error
    """
    allowed = await check_permission(
        user_id, user_role, action, resource_type, resource_id, resource_owner_id
    )
    if not allowed:
        raise AuthorizationError(
            f"User {user_id} with role {user_role} not authorized to {action} {resource_type}"
        )
