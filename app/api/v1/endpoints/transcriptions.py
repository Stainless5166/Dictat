"""
Transcription endpoints for dictation transcription workflow

Endpoints:
- POST /transcriptions - Create new transcription (secretary only)
- GET /transcriptions/{id} - Get transcription details
- PATCH /transcriptions/{id} - Update transcription content (autosave)
- POST /transcriptions/{id}/submit - Submit for review
- POST /transcriptions/{id}/review - Approve or reject (doctor only)
- GET /transcriptions/{id}/history - Get revision history (Phase 3)
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import check_resource_permission, require_role
from app.api.v1.endpoints.auth import get_current_user
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.dictation import Dictation, DictationStatus
from app.models.transcription import Transcription, TranscriptionStatus
from app.models.user import User, UserRole
from app.schemas.transcription import (
    TranscriptionCreate,
    TranscriptionResponse,
    TranscriptionReview,
    TranscriptionUpdate,
)

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=TranscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_transcription(
    data: TranscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SECRETARY)),
) -> Any:
    """
    Create new transcription for dictation

    **Permissions**: Secretaries only

    Request Body:
    - dictation_id: ID of dictation to transcribe
    - content: Initial transcription content (markdown)

    Returns:
    - Transcription object

    Raises:
    - 403: Not authorized (requires secretary role)
    - 400: Dictation not claimed by current secretary
    - 409: Transcription already exists
    - 404: Dictation not found
    """
    # Fetch dictation
    result = await db.execute(select(Dictation).where(Dictation.id == data.dictation_id))
    dictation = result.scalar_one_or_none()

    if not dictation or dictation.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictation not found")

    # Verify dictation is claimed by current secretary
    if dictation.secretary_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dictation must be claimed by you before creating transcription",
        )

    # Check if transcription already exists
    existing_result = await db.execute(
        select(Transcription).where(Transcription.dictation_id == data.dictation_id)
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transcription already exists for this dictation",
        )

    # Create transcription
    transcription = Transcription(
        dictation_id=data.dictation_id,
        secretary_id=current_user.id,
        content=data.content,
        status=TranscriptionStatus.DRAFT,
        version=1,
    )

    db.add(transcription)
    await db.commit()
    await db.refresh(transcription)

    logger.info(
        f"Transcription created: id={transcription.id}, dictation_id={data.dictation_id}, "
        f"secretary_id={current_user.id}"
    )

    return transcription


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get transcription details

    **Authorization**: Secretary who created, doctor who owns dictation, or admin

    Path Parameters:
    - transcription_id: ID of transcription

    Returns:
    - Transcription object with full details

    Raises:
    - 403: Not authorized
    - 404: Transcription not found
    """
    # Fetch transcription with dictation
    result = await db.execute(select(Transcription).where(Transcription.id == transcription_id))
    transcription = result.scalar_one_or_none()

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found"
        )

    # Fetch associated dictation for authorization check
    dictation_result = await db.execute(
        select(Dictation).where(Dictation.id == transcription.dictation_id)
    )
    dictation = dictation_result.scalar_one_or_none()

    if not dictation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictation not found")

    # Check authorization
    await check_resource_permission(
        current_user=current_user,
        action="read",
        resource_type="transcription",
        resource_id=transcription.id,
        resource_owner_id=dictation.doctor_id,
    )

    return transcription


@router.patch("/{transcription_id}", response_model=TranscriptionResponse)
async def update_transcription(
    transcription_id: int = Path(..., gt=0),
    data: TranscriptionUpdate = ...,
    is_autosave: bool = Query(False, description="Whether this is an autosave"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SECRETARY)),
) -> Any:
    """
    Update transcription content (autosave support)

    **Permissions**: Secretary who created only

    Supports autosave functionality with last_autosave_at tracking.

    Path Parameters:
    - transcription_id: ID of transcription

    Query Parameters:
    - is_autosave: Whether this is an autosave (default false)

    Request Body:
    - content: Updated transcription content (markdown)

    Returns:
    - Updated transcription object

    Raises:
    - 403: Not authorized
    - 404: Transcription not found
    - 409: Transcription already submitted/approved
    """
    # Fetch transcription
    result = await db.execute(select(Transcription).where(Transcription.id == transcription_id))
    transcription = result.scalar_one_or_none()

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found"
        )

    # Check authorization - only creator can edit
    if transcription.secretary_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only edit transcriptions you created",
        )

    # Check status - can only edit draft or rejected transcriptions
    if transcription.status not in [TranscriptionStatus.DRAFT, TranscriptionStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot edit transcription with status '{transcription.status.value}'",
        )

    # Update content
    transcription.content = data.content

    # Update timestamps
    if is_autosave:
        transcription.last_autosave_at = datetime.utcnow()
    else:
        # Manual save - increment version for revision history (Phase 3)
        # transcription.version += 1
        pass

    # If editing after rejection, update status to revised
    if transcription.status == TranscriptionStatus.REJECTED:
        transcription.status = TranscriptionStatus.REVISED

    await db.commit()
    await db.refresh(transcription)

    if not is_autosave:
        logger.info(
            f"Transcription updated: id={transcription_id}, secretary_id={current_user.id}"
        )

    return transcription


@router.post("/{transcription_id}/submit", response_model=TranscriptionResponse)
async def submit_transcription(
    transcription_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SECRETARY)),
) -> Any:
    """
    Submit transcription for doctor review

    **Permissions**: Secretary who created only

    Updates transcription status to submitted and dictation status to completed.

    Path Parameters:
    - transcription_id: ID of transcription

    Returns:
    - Updated transcription object

    Raises:
    - 403: Not authorized
    - 404: Transcription not found
    - 400: Transcription already submitted
    - 422: Content is empty or invalid
    """
    # Fetch transcription
    result = await db.execute(select(Transcription).where(Transcription.id == transcription_id))
    transcription = result.scalar_one_or_none()

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found"
        )

    # Check authorization
    if transcription.secretary_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only submit transcriptions you created",
        )

    # Validate status
    if transcription.status not in [TranscriptionStatus.DRAFT, TranscriptionStatus.REVISED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit transcription with status '{transcription.status.value}'",
        )

    # Validate content
    if not transcription.content or len(transcription.content.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Transcription content cannot be empty",
        )

    # Update transcription status
    transcription.status = TranscriptionStatus.SUBMITTED
    transcription.submitted_at = datetime.utcnow()

    # Update dictation status
    dictation_result = await db.execute(
        select(Dictation).where(Dictation.id == transcription.dictation_id)
    )
    dictation = dictation_result.scalar_one_or_none()

    if dictation:
        dictation.status = DictationStatus.COMPLETED
        dictation.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(transcription)

    logger.info(
        f"Transcription submitted: id={transcription_id}, dictation_id={transcription.dictation_id}"
    )

    return transcription


@router.post("/{transcription_id}/review", response_model=TranscriptionResponse)
async def review_transcription(
    transcription_id: int = Path(..., gt=0),
    review_data: TranscriptionReview = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
) -> Any:
    """
    Approve or reject transcription

    **Permissions**: Doctor who owns dictation, or admin

    Action can be 'approve' or 'reject'.
    If rejecting, rejection_reason is required.

    Path Parameters:
    - transcription_id: ID of transcription

    Request Body:
    - action: 'approve' or 'reject' (required)
    - review_notes: Optional notes from doctor
    - rejection_reason: Required if rejecting

    Returns:
    - Updated transcription object

    Raises:
    - 403: Not authorized (requires doctor role)
    - 404: Transcription not found
    - 400: Transcription not submitted
    - 422: Rejection reason required when rejecting
    """
    # Fetch transcription
    result = await db.execute(select(Transcription).where(Transcription.id == transcription_id))
    transcription = result.scalar_one_or_none()

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found"
        )

    # Fetch dictation for authorization
    dictation_result = await db.execute(
        select(Dictation).where(Dictation.id == transcription.dictation_id)
    )
    dictation = dictation_result.scalar_one_or_none()

    if not dictation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictation not found")

    # Check authorization - must be the doctor who owns the dictation, or admin
    if current_user.role != UserRole.ADMIN and dictation.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only review transcriptions for your own dictations",
        )

    # Validate status
    if transcription.status != TranscriptionStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot review transcription with status '{transcription.status.value}'",
        )

    # Set reviewer and timestamp
    transcription.reviewer_id = current_user.id
    transcription.reviewed_at = datetime.utcnow()

    if review_data.action == "approve":
        # Approve transcription
        transcription.status = TranscriptionStatus.APPROVED
        transcription.review_notes = review_data.review_notes

        # Update dictation status
        dictation.status = DictationStatus.REVIEWED

        logger.info(
            f"Transcription approved: id={transcription_id}, "
            f"dictation_id={transcription.dictation_id}, reviewer_id={current_user.id}"
        )

    elif review_data.action == "reject":
        # Reject transcription
        transcription.status = TranscriptionStatus.REJECTED
        transcription.rejection_reason = review_data.rejection_reason
        transcription.review_notes = review_data.review_notes

        # Update dictation status
        dictation.status = DictationStatus.REJECTED

        logger.info(
            f"Transcription rejected: id={transcription_id}, "
            f"dictation_id={transcription.dictation_id}, reviewer_id={current_user.id}, "
            f"reason={review_data.rejection_reason}"
        )

    await db.commit()
    await db.refresh(transcription)

    return transcription


@router.get("/{transcription_id}/history")
async def get_revision_history(
    transcription_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Get revision history for transcription

    **TODO Phase 3**: Implement revision history tracking

    Currently returns placeholder message.

    Path Parameters:
    - transcription_id: ID of transcription

    Returns:
    - Placeholder message

    Raises:
    - 501: Not implemented
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Revision history feature is planned for Phase 3",
    )
