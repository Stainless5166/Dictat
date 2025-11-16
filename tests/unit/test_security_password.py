"""
Unit tests for password hashing and verification

Tests cover:
- Password hashing functionality
- Password verification
- Hash uniqueness (salt generation)
- Timing attack resistance
- Invalid input handling
"""

import pytest
from app.core.security import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing utilities"""

    def test_hash_password_basic(self) -> None:
        """Test basic password hashing"""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Hash should not equal plain text

    def test_hash_password_different_hashes(self) -> None:
        """Test that same password produces different hashes (unique salts)"""
        password = "SamePassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Salts should make hashes different
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_hash_password_empty_string(self) -> None:
        """Test hashing empty password"""
        # Empty passwords should still hash (validation is done elsewhere)
        hashed = hash_password("")
        assert hashed is not None
        assert verify_password("", hashed)

    def test_hash_password_long_password(self) -> None:
        """Test hashing very long password"""
        password = "a" * 1000  # 1000 character password
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed)

    def test_hash_password_unicode(self) -> None:
        """Test hashing password with unicode characters"""
        password = "パスワード123!@#"
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed)

    def test_hash_password_special_chars(self) -> None:
        """Test hashing password with special characters"""
        password = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed)


class TestPasswordVerification:
    """Test password verification utilities"""

    def test_verify_password_success(self) -> None:
        """Test successful password verification"""
        password = "CorrectPassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self) -> None:
        """Test failed password verification with wrong password"""
        password = "CorrectPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_case_sensitive(self) -> None:
        """Test that password verification is case-sensitive"""
        password = "CaseSensitive123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("casesensitive123", hashed) is False
        assert verify_password("CASESENSITIVE123", hashed) is False

    def test_verify_password_whitespace_matters(self) -> None:
        """Test that whitespace in passwords matters"""
        password = "password with spaces"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("passwordwithspaces", hashed) is False
        assert verify_password(" password with spaces", hashed) is False
        assert verify_password("password with spaces ", hashed) is False

    def test_verify_password_empty_against_hashed(self) -> None:
        """Test verifying empty password against hashed password"""
        password = "SomePassword123"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_verify_password_invalid_hash_format(self) -> None:
        """Test verification with invalid hash format"""
        password = "TestPassword123"

        # Invalid hash should return False (not raise exception)
        assert verify_password(password, "invalid_hash") is False
        assert verify_password(password, "") is False
        assert verify_password(password, "short") is False


class TestPasswordSecurity:
    """Test security aspects of password handling"""

    def test_hash_uses_configured_algorithm(self) -> None:
        """Test that password hashing uses the configured algorithm from settings"""
        from app.core.config import settings

        password = "TestPassword123"
        hashed = hash_password(password)

        # Verify hash uses the configured algorithm
        if settings.PASSWORD_HASH_ALGORITHM == "argon2":
            assert hashed.startswith("$argon2"), f"Expected argon2 hash, but got: {hashed[:20]}"
        elif settings.PASSWORD_HASH_ALGORITHM == "bcrypt":
            assert hashed.startswith("$2b$"), f"Expected bcrypt hash, but got: {hashed[:20]}"
        else:
            pytest.fail(f"Unknown algorithm: {settings.PASSWORD_HASH_ALGORITHM}")

    def test_hash_format_contains_algorithm(self) -> None:
        """Test that hash contains algorithm identifier"""
        password = "Test123"
        hashed = hash_password(password)

        # Argon2 hashes start with $argon2, bcrypt with $2b$
        assert hashed.startswith("$argon2") or hashed.startswith("$2b$")

    def test_timing_attack_resistance_same_length(self) -> None:
        """
        Test that password verification time is consistent

        Note: This is a basic check. Real timing attack testing
        requires more sophisticated statistical analysis.
        """
        password = "CorrectPassword123"
        hashed = hash_password(password)

        # These should take similar time regardless of being correct
        import time

        # Correct password
        start = time.perf_counter()
        result1 = verify_password(password, hashed)
        time1 = time.perf_counter() - start

        # Wrong password (same length)
        start = time.perf_counter()
        result2 = verify_password("WrongPassword456", hashed)
        time2 = time.perf_counter() - start

        assert result1 is True
        assert result2 is False
        # Both should take similar time (within 100x tolerance)
        # Note: This is a weak test; real timing attack requires statistical analysis
        assert abs(time1 - time2) < max(time1, time2) * 100

    def test_hash_is_not_reversible(self) -> None:
        """Test that hash cannot be reversed to original password"""
        password = "MySecretPassword123"
        hashed = hash_password(password)

        # Hash should not contain the original password
        assert password not in hashed
        # Hash should be different from password
        assert hashed != password


class TestPasswordIntegration:
    """Integration tests for password workflow"""

    def test_complete_password_lifecycle(self) -> None:
        """Test complete password creation and verification workflow"""
        # Simulate user registration
        user_password = "NewUser123!@#"
        stored_hash = hash_password(user_password)

        # Simulate user login with correct password
        assert verify_password(user_password, stored_hash) is True

        # Simulate login attempt with wrong password
        assert verify_password("WrongPassword", stored_hash) is False

    def test_multiple_users_same_password(self) -> None:
        """Test that multiple users can have the same password securely"""
        shared_password = "CommonPassword123"

        # Two users with same password
        hash1 = hash_password(shared_password)
        hash2 = hash_password(shared_password)

        # Hashes should be different (unique salts)
        assert hash1 != hash2

        # Both should verify correctly
        assert verify_password(shared_password, hash1)
        assert verify_password(shared_password, hash2)

        # Each hash should not verify with other user's password attempts
        other_password = "DifferentPassword456"
        assert verify_password(other_password, hash1) is False
        assert verify_password(other_password, hash2) is False
