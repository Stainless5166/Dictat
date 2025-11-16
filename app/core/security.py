"""
Security utilities for authentication and authorization

TODO Phase 1:
- Implement JWT token generation and validation
- Add password hashing with Argon2/bcrypt
- Create token refresh mechanism
- Implement secure random token generation
- Add timing attack protection
"""

from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context configured from settings
# Uses the algorithm specified in settings.PASSWORD_HASH_ALGORITHM (argon2 or bcrypt)
# Both algorithms are supported for backwards compatibility (can verify old hashes)
# but new hashes will use the configured algorithm (first in list)
_schemes = [settings.PASSWORD_HASH_ALGORITHM]
if settings.PASSWORD_HASH_ALGORITHM != "bcrypt":
    _schemes.append("bcrypt")
if settings.PASSWORD_HASH_ALGORITHM != "argon2":
    _schemes.append("argon2")

pwd_context = CryptContext(schemes=_schemes, deprecated="auto")


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Data to encode in token (typically user_id, email, role)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    TODO:
    - Add token type claim (access vs refresh)
    - Include permissions in token
    - Add token jti (JWT ID) for revocation
    - Implement token blacklisting
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    # TODO: Add issuer (iss) and audience (aud) claims
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create JWT refresh token with longer expiration

    Args:
        data: Data to encode in token

    Returns:
        Encoded refresh token

    TODO:
    - Use separate secret for refresh tokens
    - Store refresh token hash in database
    - Implement refresh token rotation
    - Add device/session tracking
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any] | None:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid

    TODO:
    - Verify token type (access vs refresh)
    - Check token revocation status
    - Validate issuer and audience
    - Add rate limiting for token validation
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """
    Hash password using Argon2/bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string

    TODO:
    - Add password strength validation
    - Implement pepper (server-side secret)
    - Add timing attack protection
    - Log password hash operations for audit
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored password hash

    Returns:
        True if password matches, False otherwise

    TODO:
    - Add brute force protection
    - Implement account lockout after failed attempts
    - Log failed verification attempts
    - Add timing attack protection
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Invalid hash format or other errors should return False
        return False


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token

    Args:
        length: Length of token in bytes

    Returns:
        Hex-encoded random token

    TODO:
    - Use for password reset tokens
    - Use for email verification tokens
    - Add token expiration tracking
    - Store token hashes in database
    """
    import secrets

    return secrets.token_urlsafe(length)
