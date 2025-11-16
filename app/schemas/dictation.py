"""
Pydantic schemas for dictation endpoints

Schemas:
- DictationCreate: Creating new dictation
- DictationUpdate: Updating existing dictation
- DictationResponse: Dictation response
- DictationListResponse: List of dictations with pagination
- DictationClaimRequest: Claim dictation request
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.dictation import DictationStatus, DictationPriority


class DictationBase(BaseModel):
    """Base dictation schema with common fields"""

    title: Optional[str] = Field(None, max_length=255, description="Dictation title")
    patient_reference: Optional[str] = Field(
        None, max_length=100, description="Patient reference ID"
    )
    notes: Optional[str] = Field(None, description="Additional notes")
    priority: DictationPriority = Field(
        default=DictationPriority.NORMAL, description="Dictation priority"
    )
    duration: Optional[float] = Field(None, gt=0, description="Audio duration in seconds")


class DictationCreate(DictationBase):
    """Schema for creating a new dictation"""

    # File information will be added during upload
    # API endpoint will handle file upload separately
    pass


class DictationUpdate(BaseModel):
    """Schema for updating an existing dictation"""

    title: Optional[str] = Field(None, max_length=255)
    patient_reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    priority: Optional[DictationPriority] = None
    status: Optional[DictationStatus] = None

    @field_validator("status")
    @classmethod
    def validate_status_transition(cls, v: Optional[DictationStatus]) -> Optional[DictationStatus]:
        """
        Validate status transitions

        Allowed transitions will be enforced in the service layer
        """
        if v is not None:
            # Valid statuses for manual updates (service layer will validate transitions)
            return v
        return None


class DictationResponse(DictationBase):
    """Schema for dictation responses"""

    id: int
    doctor_id: int
    secretary_id: Optional[int] = None
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    status: DictationStatus
    created_at: datetime
    updated_at: datetime
    claimed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DictationListItem(BaseModel):
    """Simplified schema for dictation list items"""

    id: int
    title: Optional[str]
    patient_reference: Optional[str]
    status: DictationStatus
    priority: DictationPriority
    duration: Optional[float]
    doctor_id: int
    secretary_id: Optional[int]
    created_at: datetime
    claimed_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DictationListResponse(BaseModel):
    """Schema for paginated dictation list"""

    items: list[DictationListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class DictationClaimRequest(BaseModel):
    """Schema for claiming a dictation"""

    # Empty for now - claim action doesn't require additional data
    # Could add estimated_completion_time in future
    pass


class DictationStatusUpdate(BaseModel):
    """Schema for status updates"""

    status: DictationStatus

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: DictationStatus) -> DictationStatus:
        """Validate status value"""
        if v not in DictationStatus:
            raise ValueError(f"Invalid status: {v}")
        return v
