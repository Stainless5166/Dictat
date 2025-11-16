"""
Unit tests for JWT token generation and validation

Tests cover:
- Access token creation and validation
- Refresh token creation and validation
- Token expiration handling
- Invalid token handling
- Token payload verification
- Token type differentiation
"""

import pytest
from datetime import timedelta, datetime
from jose import jwt
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.config import settings


class TestAccessTokenCreation:
    """Test JWT access token creation"""

    def test_create_access_token_basic(self) -> None:
        """Test basic access token creation"""
        data = {"sub": "123", "email": "test@example.com", "role": "doctor"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_payload(self) -> None:
        """Test that access token contains correct payload"""
        data = {
            "sub": "user_id_123",
            "email": "doctor@test.com",
            "role": "doctor",
        }
        token = create_access_token(data)

        # Decode without verification for testing
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["sub"] == "user_id_123"
        assert payload["email"] == "doctor@test.com"
        assert payload["role"] == "doctor"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_access_token_expiration(self) -> None:
        """Test that access token has correct expiration"""
        data = {"sub": "123"}
        token = create_access_token(data)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)

        # Should expire in approximately ACCESS_TOKEN_EXPIRE_MINUTES
        now = datetime.utcnow()
        expected_exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Allow 5 second tolerance
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 5

    def test_create_access_token_custom_expiration(self) -> None:
        """Test access token with custom expiration"""
        data = {"sub": "123"}
        custom_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_delta)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)

        now = datetime.utcnow()
        expected_exp = now + custom_delta

        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 5

    def test_create_access_token_preserves_custom_claims(self) -> None:
        """Test that custom claims are preserved in token"""
        data = {
            "sub": "123",
            "email": "test@example.com",
            "role": "doctor",
            "custom_field": "custom_value",
            "permissions": ["read", "write"],
        }
        token = create_access_token(data)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["custom_field"] == "custom_value"
        assert payload["permissions"] == ["read", "write"]


class TestRefreshTokenCreation:
    """Test JWT refresh token creation"""

    def test_create_refresh_token_basic(self) -> None:
        """Test basic refresh token creation"""
        data = {"sub": "123"}
        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_type(self) -> None:
        """Test that refresh token has correct type"""
        data = {"sub": "123"}
        token = create_refresh_token(data)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["type"] == "refresh"

    def test_create_refresh_token_longer_expiration(self) -> None:
        """Test that refresh token has longer expiration than access token"""
        data = {"sub": "123"}

        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        access_payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        refresh_payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert refresh_payload["exp"] > access_payload["exp"]

    def test_create_refresh_token_expiration(self) -> None:
        """Test that refresh token has correct expiration"""
        data = {"sub": "123"}
        token = create_refresh_token(data)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)

        now = datetime.utcnow()
        expected_exp = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # Allow 5 second tolerance
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 5


class TestTokenVerification:
    """Test JWT token verification"""

    def test_verify_token_valid_access(self) -> None:
        """Test verification of valid access token"""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_verify_token_valid_refresh(self) -> None:
        """Test verification of valid refresh token"""
        data = {"sub": "123"}
        token = create_refresh_token(data)

        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["type"] == "refresh"

    def test_verify_token_invalid_signature(self) -> None:
        """Test verification of token with invalid signature"""
        data = {"sub": "123"}
        token = create_access_token(data)

        # Tamper with token
        tampered_token = token[:-5] + "xxxxx"

        payload = verify_token(tampered_token)

        assert payload is None

    def test_verify_token_invalid_format(self) -> None:
        """Test verification of invalid token format"""
        invalid_tokens = [
            "not.a.token",
            "invalid",
            "",
            "a.b",  # Too few parts
            "a.b.c.d",  # Too many parts
        ]

        for invalid_token in invalid_tokens:
            payload = verify_token(invalid_token)
            assert payload is None, f"Should reject invalid token: {invalid_token}"

    def test_verify_token_expired(self) -> None:
        """Test verification of expired token"""
        data = {"sub": "123"}
        # Create token with very short expiration
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        payload = verify_token(token)

        assert payload is None

    def test_verify_token_wrong_algorithm(self) -> None:
        """Test verification of token signed with wrong algorithm"""
        data = {"sub": "123", "exp": datetime.utcnow() + timedelta(minutes=30)}

        # Create token with different algorithm
        token = jwt.encode(data, settings.SECRET_KEY, algorithm="HS512")

        payload = verify_token(token)

        # Should fail verification because algorithm doesn't match
        assert payload is None

    def test_verify_token_wrong_secret(self) -> None:
        """Test that token signed with wrong secret fails verification"""
        data = {"sub": "123", "exp": datetime.utcnow() + timedelta(minutes=30)}

        # Create token with different secret
        wrong_secret = "wrong-secret-key-that-is-different"
        token = jwt.encode(data, wrong_secret, algorithm=settings.ALGORITHM)

        payload = verify_token(token)

        assert payload is None


class TestTokenSecurity:
    """Test security aspects of token handling"""

    def test_tokens_are_unique(self) -> None:
        """Test that same data produces different tokens (due to exp timestamp)"""
        import time

        data = {"sub": "123"}

        token1 = create_access_token(data)
        time.sleep(1.1)  # Sleep 1.1 seconds to ensure different timestamp (datetime.utcnow() has second precision)
        token2 = create_access_token(data)

        # Tokens should be different due to different exp timestamps
        assert token1 != token2

        # But both should verify correctly
        assert verify_token(token1) is not None
        assert verify_token(token2) is not None

    def test_token_contains_no_sensitive_data(self) -> None:
        """Test that token doesn't expose sensitive data in plain text"""
        data = {
            "sub": "123",
            "email": "test@example.com",
            # Password should NEVER be in token
        }
        token = create_access_token(data)

        # Token should not contain password or password hash
        assert "password" not in token.lower()
        assert "hashed_password" not in token.lower()

    def test_token_modification_detected(self) -> None:
        """Test that any modification to token is detected"""
        data = {"sub": "123", "role": "secretary"}
        token = create_access_token(data)

        # Try to decode and modify role
        parts = token.split(".")
        assert len(parts) == 3

        # Tamper with payload (middle part)
        import base64
        import json

        # Decode payload
        payload_part = parts[1]
        # Add padding if needed
        missing_padding = len(payload_part) % 4
        if missing_padding:
            payload_part += "=" * (4 - missing_padding)

        decoded_payload = base64.urlsafe_b64decode(payload_part)
        payload_dict = json.loads(decoded_payload)

        # Change role
        payload_dict["role"] = "admin"

        # Re-encode
        modified_payload = base64.urlsafe_b64encode(
            json.dumps(payload_dict).encode()
        ).decode().rstrip("=")

        # Create tampered token
        tampered_token = f"{parts[0]}.{modified_payload}.{parts[2]}"

        # Verification should fail
        assert verify_token(tampered_token) is None


class TestTokenWorkflow:
    """Integration tests for token workflow"""

    def test_complete_auth_workflow(self) -> None:
        """Test complete authentication workflow with tokens"""
        # User logs in
        user_data = {
            "sub": "user_123",
            "email": "doctor@test.com",
            "role": "doctor",
        }

        # Create tokens
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)

        # Verify access token
        access_payload = verify_token(access_token)
        assert access_payload is not None
        assert access_payload["sub"] == "user_123"
        assert access_payload["type"] == "access"

        # Verify refresh token
        refresh_payload = verify_token(refresh_token)
        assert refresh_payload is not None
        assert refresh_payload["sub"] == "user_123"
        assert refresh_payload["type"] == "refresh"

    def test_token_refresh_workflow(self) -> None:
        """Test token refresh workflow"""
        user_data = {"sub": "user_123"}

        # Original access token with short expiration
        old_access_token = create_access_token(
            user_data, expires_delta=timedelta(seconds=-1)
        )

        # Access token expired
        assert verify_token(old_access_token) is None

        # But refresh token is still valid
        refresh_token = create_refresh_token(user_data)
        refresh_payload = verify_token(refresh_token)
        assert refresh_payload is not None

        # Use refresh token to create new access token
        new_access_token = create_access_token({"sub": refresh_payload["sub"]})

        # New access token should work
        new_payload = verify_token(new_access_token)
        assert new_payload is not None
        assert new_payload["sub"] == "user_123"
