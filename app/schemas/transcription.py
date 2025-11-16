"""
Pydantic schemas for transcription endpoints

Schemas:
- TranscriptionCreate: Creating new transcription
- TranscriptionUpdate: Updating existing transcription (autosave)
- TranscriptionResponse: Transcription response
- TranscriptionSubmit: Submit for review
- TranscriptionReview: Review/approve/reject
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.transcription import TranscriptionStatus


class TranscriptionBase(BaseModel):
    """Base transcription schema with common fields"""

    content: str = Field(..., min_length=1, description="Markdown formatted content")


class TranscriptionCreate(TranscriptionBase):
    """Schema for creating a new transcription"""

    dictation_id: int = Field(..., description="ID of dictation being transcribed")


class TranscriptionUpdate(BaseModel):
    """Schema for updating a transcription (autosave)"""

    content: str = Field(..., min_length=1, description="Updated markdown content")


class TranscriptionResponse(TranscriptionBase):
    """Schema for transcription responses"""

    id: int
    dictation_id: int
    secretary_id: int
    reviewer_id: Optional[int] = None
    version: int
    status: TranscriptionStatus
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_autosave_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TranscriptionSubmit(BaseModel):
    """Schema for submitting transcription for review"""

    # Empty for now - submit action uses current content
    # Could add submission notes in future
    pass


class TranscriptionReview(BaseModel):
    """Schema for reviewing a transcription"""

    action: str = Field(..., description="Action: 'approve' or 'reject'")
    review_notes: Optional[str] = Field(None, description="Review notes from doctor")
    rejection_reason: Optional[str] = Field(
        None, description="Reason for rejection (required if rejecting)"
    )

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate review action"""
        if v not in ["approve", "reject"]:
            raise ValueError("Action must be 'approve' or 'reject'")
        return v

    @field_validator("rejection_reason")
    @classmethod
    def validate_rejection_reason(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure rejection_reason is provided when rejecting"""
        # Note: In Pydantic v2, we use info.data to access other fields
        data = info.data
        if data.get("action") == "reject" and not v:
            raise ValueError("Rejection reason is required when rejecting")
        return v


class TranscriptionListItem(BaseModel):
    """Simplified schema for transcription list items"""

    id: int
    dictation_id: int
    status: TranscriptionStatus
    version: int
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]

    class Config:
        from_attributes = True
