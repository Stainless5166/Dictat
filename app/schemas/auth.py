"""
Authentication schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import UserRole


class UserRegister(BaseModel):
    """Schema for user registration"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    full_name: str = Field(..., min_length=1, max_length=255, description="User full name")
    role: UserRole = Field(..., description="User role (doctor, secretary, admin)")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "dr.smith@dictat.im",
                "password": "SecurePass123",
                "full_name": "Dr. John Smith",
                "role": "doctor",
            }
        }


class UserLogin(BaseModel):
    """Schema for user login (OAuth2 compatible)"""

    username: EmailStr = Field(..., description="User email (OAuth2 uses 'username')")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "dr.smith@dictat.im",
                "password": "SecurePass123",
            }
        }


class TokenResponse(BaseModel):
    """Schema for authentication token response"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: "UserResponse" = Field(..., description="User information")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "dr.smith@dictat.im",
                    "full_name": "Dr. John Smith",
                    "role": "doctor",
                    "is_active": True,
                    "is_verified": True,
                },
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""

    refresh_token: str = Field(..., description="Refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class UserResponse(BaseModel):
    """Schema for user response (no sensitive data)"""

    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Is user active")
    is_verified: bool = Field(..., description="Is email verified")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "dr.smith@dictat.im",
                "full_name": "Dr. John Smith",
                "role": "doctor",
                "is_active": True,
                "is_verified": True,
            }
        }


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request"""

    email: EmailStr = Field(..., description="User email address")

    class Config:
        json_schema_extra = {"example": {"email": "dr.smith@dictat.im"}}


class ResetPasswordRequest(BaseModel):
    """Schema for password reset request"""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="New password"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456",
                "new_password": "NewSecurePass123",
            }
        }


class VerifyEmailRequest(BaseModel):
    """Schema for email verification request"""

    token: str = Field(..., description="Email verification token")

    class Config:
        json_schema_extra = {"example": {"token": "abc123def456"}}
