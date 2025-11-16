"""
Unit tests for security utilities

TODO Phase 4:
- Test password hashing
- Test password verification
- Test JWT token creation
- Test JWT token validation
- Test token expiration
"""

import pytest
from datetime import datetime, timedelta

# from app.core.security import (
#     hash_password,
#     verify_password,
#     create_access_token,
#     create_refresh_token,
#     verify_token,
# )


class TestPasswordHashing:
    """Tests for password hashing and verification"""

    def test_hash_password(self):
        """
        Test password hashing

        TODO Phase 4:
        - Hash a password
        - Verify hash is different from password
        - Verify hash is consistent format
        """
        pass

    def test_verify_password_success(self):
        """
        Test password verification with correct password

        TODO Phase 4:
        - Hash a password
        - Verify with correct password
        - Assert returns True
        """
        pass

    def test_verify_password_failure(self):
        """
        Test password verification with incorrect password

        TODO Phase 4:
        - Hash a password
        - Verify with incorrect password
        - Assert returns False
        """
        pass

    def test_password_hash_uniqueness(self):
        """
        Test that same password produces different hashes (salt)

        TODO Phase 4:
        - Hash same password twice
        - Verify hashes are different (salted)
        """
        pass


class TestJWTTokens:
    """Tests for JWT token creation and validation"""

    def test_create_access_token(self):
        """
        Test JWT access token creation

        TODO Phase 4:
        - Create token with user data
        - Verify token is string
        - Decode and verify contents
        - Verify expiration is set
        """
        pass

    def test_create_refresh_token(self):
        """
        Test JWT refresh token creation

        TODO Phase 4:
        - Create refresh token
        - Verify longer expiration
        - Verify token type
        """
        pass

    def test_verify_token_success(self):
        """
        Test token verification with valid token

        TODO Phase 4:
        - Create token
        - Verify token
        - Assert payload matches
        """
        pass

    def test_verify_token_expired(self):
        """
        Test token verification with expired token

        TODO Phase 4:
        - Create token with past expiration
        - Verify token
        - Assert returns None or raises exception
        """
        pass

    def test_verify_token_invalid(self):
        """
        Test token verification with invalid token

        TODO Phase 4:
        - Create invalid token
        - Verify token
        - Assert returns None or raises exception
        """
        pass
