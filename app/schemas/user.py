"""
User schemas for request/response validation
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="User full name")
    role: UserRole = Field(..., description="User role")


class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str = Field(..., min_length=8, max_length=100, description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "dr.smith@dictat.im",
                "full_name": "Dr. John Smith",
                "role": "doctor",
                "password": "SecurePass123",
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="User full name"
    )
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Is user active")
    is_verified: Optional[bool] = Field(None, description="Is email verified")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Dr. John Smith Jr.",
                "is_verified": True,
            }
        }


class UserInDB(UserBase):
    """Schema for user in database (includes ID and timestamps)"""

    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Is user active")
    is_verified: bool = Field(..., description="Is email verified")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp (soft delete)")

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user schema (safe for external API responses)"""

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
