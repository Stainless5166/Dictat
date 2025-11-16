"""
Dictation endpoints for audio file management

Endpoints:
- POST /dictations - Upload new dictation (doctor only)
- GET /dictations - List dictations (role-based filtering)
- GET /dictations/{id} - Get dictation details
- GET /dictations/{id}/audio - Stream audio file (with range support)
- PATCH /dictations/{id} - Update dictation metadata
- DELETE /dictations/{id} - Delete dictation (soft delete)
- GET /dictations/queue - Get work queue (secretary only)
- POST /dictations/{id}/claim - Claim dictation (secretary only)
- POST /dictations/{id}/unclaim - Release claimed dictation
"""

from datetime import datetime
from typing import Any, Optional
import math
import re

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import check_resource_permission, require_role
from app.api.v1.endpoints.auth import get_current_user
from app.core.config import settings
from app.core.exceptions import FileUploadError
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.dictation import Dictation, DictationPriority, DictationStatus
from app.models.user import User, UserRole
from app.schemas.dictation import (
    DictationClaimRequest,
    DictationListResponse,
    DictationResponse,
    DictationUpdate,
)
from app.services.storage import storage_service

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=DictationResponse, status_code=status.HTTP_201_CREATED)
async def create_dictation(
    file: UploadFile = File(..., description="Audio file"),
    title: Optional[str] = Form(None, description="Dictation title"),
    patient_reference: Optional[str] = Form(None, description="Patient reference"),
    priority: str = Form("normal", description="Priority level"),
    notes: Optional[str] = Form(None, description="Additional notes"),
    duration: Optional[float] = Form(None, description="Audio duration in seconds"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
) -> Any:
    """
    Upload new dictation audio file

    **Permissions**: Doctors and admins only

    Request Body (multipart/form-data):
    - file: Audio file (required, mp3/wav/m4a/ogg/flac, max 100MB)
    - title: Dictation title (optional)
    - patient_reference: Patient reference number (optional)
    - priority: Priority level (low, normal, high, urgent)
    - notes: Additional notes (optional)
    - duration: Audio duration in seconds (optional)

    Returns:
    - Dictation object with ID and metadata

    Raises:
    - 403: Not authorized (requires doctor role)
    - 400: Invalid file format or size
    - 413: File too large
    """
    try:
        # Validate priority
        try:
            priority_enum = DictationPriority(priority.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority. Must be one of: {', '.join([p.value for p in DictationPriority])}",
            )

        # Save file to storage
        file_info = await storage_service.save_audio_file(
            file=file.file, filename=file.filename or "audio", user_id=current_user.id
        )

        # Create dictation record
        dictation = Dictation(
            doctor_id=current_user.id,
            file_path=file_info["file_path"],
            file_name=file_info["file_name"],
            file_size=file_info["file_size"],
            mime_type=file_info["mime_type"],
            duration=duration,
            title=title,
            patient_reference=patient_reference,
            priority=priority_enum,
            notes=notes,
            status=DictationStatus.PENDING,
        )

        db.add(dictation)
        await db.commit()
        await db.refresh(dictation)

        logger.info(
            f"Dictation created: id={dictation.id}, doctor_id={current_user.id}, "
            f"file_size={file_info['file_size']}, priority={priority}"
        )

        return dictation

    except FileUploadError as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Dictation creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dictation",
        )


@router.get("/", response_model=DictationListResponse)
async def list_dictations(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    priority_filter: Optional[str] = Query(None, alias="priority", description="Filter by priority"),
    from_date: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    to_date: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    List dictations with role-based filtering

    **Authorization**:
    - Doctors see only their own dictations
    - Secretaries see pending/assigned/in_progress dictations
    - Admins see all dictations

    Query Parameters:
    - skip: Pagination offset (default: 0)
    - limit: Number of results (default: 100, max: 1000)
    - status: Filter by status
    - priority: Filter by priority
    - from_date: Filter from date (ISO format)
    - to_date: Filter to date (ISO format)

    Returns:
    - List of dictations with pagination metadata
    """
    # Build base query
    query = select(Dictation).where(Dictation.deleted_at.is_(None))

    # Role-based filtering
    if current_user.role == UserRole.DOCTOR:
        # Doctors see only their own dictations
        query = query.where(Dictation.doctor_id == current_user.id)
    elif current_user.role == UserRole.SECRETARY:
        # Secretaries see available dictations (pending, assigned to them, or claimed by them)
        query = query.where(
            (Dictation.status.in_([DictationStatus.PENDING, DictationStatus.ASSIGNED]))
            | (Dictation.secretary_id == current_user.id)
        )
    # Admins see all dictations (no additional filter)

    # Apply filters
    if status_filter:
        try:
            status_enum = DictationStatus(status_filter.lower())
            query = query.where(Dictation.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join([s.value for s in DictationStatus])}",
            )

    if priority_filter:
        try:
            priority_enum = DictationPriority(priority_filter.lower())
            query = query.where(Dictation.priority == priority_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority. Must be one of: {', '.join([p.value for p in DictationPriority])}",
            )

    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date)
            query = query.where(Dictation.created_at >= from_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid from_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
            )

    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date)
            query = query.where(Dictation.created_at <= to_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid to_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
            )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting (priority DESC, created_at DESC)
    query = query.order_by(Dictation.priority.desc(), Dictation.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    dictations = result.scalars().all()

    # Calculate pagination metadata
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1

    return DictationListResponse(
        items=dictations, total=total, page=current_page, page_size=limit, total_pages=total_pages
    )


@router.get("/queue", response_model=DictationListResponse)
async def get_work_queue(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    priority_filter: Optional[str] = Query(None, alias="priority", description="Filter by priority"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SECRETARY)),
) -> Any:
    """
    Get work queue for secretaries

    **Permissions**: Secretaries only

    Returns pending and assigned (but not claimed) dictations,
    sorted by priority and creation date.

    Query Parameters:
    - skip: Pagination offset
    - limit: Number of results
    - priority: Filter by priority

    Returns:
    - List of available dictations
    """
    # Query for pending dictations (not claimed by anyone)
    query = select(Dictation).where(
        Dictation.deleted_at.is_(None),
        Dictation.status.in_([DictationStatus.PENDING, DictationStatus.ASSIGNED]),
        Dictation.secretary_id.is_(None),  # Not yet claimed
    )

    # Apply priority filter
    if priority_filter:
        try:
            priority_enum = DictationPriority(priority_filter.lower())
            query = query.where(Dictation.priority == priority_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority. Must be one of: {', '.join([p.value for p in DictationPriority])}",
            )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sort by priority (urgent first) and created_at (oldest first)
    # Priority order: urgent > high > normal > low
    query = query.order_by(Dictation.priority.desc(), Dictation.created_at.asc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    dictations = result.scalars().all()

    # Calculate pagination metadata
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1

    return DictationListResponse(
        items=dictations, total=total, page=current_page, page_size=limit, total_pages=total_pages
    )


@router.get("/{dictation_id}", response_model=DictationResponse)
async def get_dictation(
    dictation_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get dictation details

    **Authorization**: Owner, assigned secretary, or admin

    Path Parameters:
    - dictation_id: ID of dictation

    Returns:
    - Dictation object with full details

    Raises:
    - 403: Not authorized
    - 404: Dictation not found
    """
    # Fetch dictation
    result = await db.execute(select(Dictation).where(Dictation.id == dictation_id))
    dictation = result.scalar_one_or_none()

    if not dictation or dictation.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictation not found")

    # Check authorization
    await check_resource_permission(
        current_user=current_user,
        action="read",
        resource_type="dictation",
        resource_id=dictation.id,
        resource_owner_id=dictation.doctor_id,
    )

    return dictation


@router.get("/{dictation_id}/audio")
async def stream_audio(
    dictation_id: int = Path(..., gt=0),
    range_header: Optional[str] = Header(None, alias="Range"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Stream audio file with range support (HTTP 206)

    **Authorization**: Owner, assigned secretary, or admin

    Supports HTTP Range requests for seeking in audio player.

    Path Parameters:
    - dictation_id: ID of dictation

    Headers:
    - Range: Byte range for partial content (e.g., "bytes=0-1023")

    Returns:
    - StreamingResponse with audio data
    - Status 200 for full content
    - Status 206 for partial content

    Raises:
    - 403: Not authorized
    - 404: Dictation or audio file not found
    - 416: Range not satisfiable
    """
    # Fetch dictation
    result = await db.execute(select(Dictation).where(Dictation.id == dictation_id))
    dictation = result.scalar_one_or_none()

    if not dictation or dictation.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictation not found")

    # Check authorization
    await check_resource_permission(
        current_user=current_user,
        action="read",
        resource_type="dictation",
        resource_id=dictation.id,
        resource_owner_id=dictation.doctor_id,
    )

    # Get file info
    try:
        file_info = await storage_service.get_file_info(dictation.file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")

    file_size = file_info["size"]
    start_byte = 0
    end_byte = file_size - 1

    # Parse Range header
    if range_header:
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if not range_match:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail="Invalid range format",
            )

        start_byte = int(range_match.group(1))
        if range_match.group(2):
            end_byte = int(range_match.group(2))

        # Validate range
        if start_byte >= file_size or end_byte >= file_size or start_byte > end_byte:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail=f"Range not satisfiable. File size: {file_size} bytes",
            )

    # Stream file
    try:
        stream = storage_service.stream_audio_file(dictation.file_path, start_byte, end_byte)

        headers = {
            "Content-Type": dictation.mime_type,
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'inline; filename="{dictation.file_name}"',
        }

        if range_header:
            # Partial content (HTTP 206)
            content_length = end_byte - start_byte + 1
            headers["Content-Range"] = f"bytes {start_byte}-{end_byte}/{file_size}"
            headers["Content-Length"] = str(content_length)

            return StreamingResponse(
                stream, status_code=status.HTTP_206_PARTIAL_CONTENT, headers=headers
            )
        else:
            # Full content (HTTP 200)
            headers["Content-Length"] = str(file_size)
            return StreamingResponse(stream, status_code=status.HTTP_200_OK, headers=headers)

    except Exception as e:
        logger.error(f"Audio streaming failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stream audio file",
        )


@router.post("/{dictation_id}/claim", response_model=DictationResponse)
async def claim_dictation(
    dictation_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SECRETARY)),
) -> Any:
    """
    Claim dictation for transcription

    **Permissions**: Secretaries only

    Assigns the dictation to the current secretary and updates status to in_progress.

    Path Parameters:
    - dictation_id: ID of dictation to claim

    Returns:
    - Updated dictation object

    Raises:
    - 403: Not authorized (requires secretary role)
    - 404: Dictation not found
    - 409: Dictation already claimed or invalid status
    """
    # Fetch dictation
    result = await db.execute(select(Dictation).where(Dictation.id == dictation_id))
    dictation = result.scalar_one_or_none()

    if not dictation or dictation.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictation not found")

    # Check if dictation can be claimed
    if dictation.status not in [DictationStatus.PENDING, DictationStatus.ASSIGNED]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot claim dictation with status '{dictation.status.value}'",
        )

    if dictation.secretary_id is not None and dictation.secretary_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dictation already claimed by another secretary",
        )

    # Claim dictation
    dictation.secretary_id = current_user.id
    dictation.status = DictationStatus.IN_PROGRESS
    dictation.claimed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(dictation)

    logger.info(f"Dictation claimed: id={dictation_id}, secretary_id={current_user.id}")

    return dictation


@router.post("/{dictation_id}/unclaim")
async def unclaim_dictation(
    dictation_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SECRETARY)),
) -> dict[str, str]:
    """
    Release claimed dictation back to queue

    **Permissions**: Secretary who claimed it, or admin

    Path Parameters:
    - dictation_id: ID of dictation to unclaim

    Returns:
    - Success message

    Raises:
    - 403: Not authorized (must be assigned secretary)
    - 404: Dictation not found
    - 400: Dictation not claimed by current user
    """
    # Fetch dictation
    result = await db.execute(select(Dictation).where(Dictation.id == dictation_id))
    dictation = result.scalar_one_or_none()

    if not dictation or dictation.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictation not found")

    # Check if current user can unclaim
    if dictation.secretary_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only unclaim dictations assigned to you",
        )

    if dictation.secretary_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dictation is not currently claimed",
        )

    # Unclaim dictation
    dictation.secretary_id = None
    dictation.status = DictationStatus.PENDING
    dictation.claimed_at = None

    await db.commit()

    logger.info(f"Dictation unclaimed: id={dictation_id}, secretary_id={current_user.id}")

    return {"message": "Dictation unclaimed successfully"}


@router.patch("/{dictation_id}", response_model=DictationResponse)
async def update_dictation(
    dictation_id: int = Path(..., gt=0),
    update_data: DictationUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update dictation metadata

    **Authorization**: Owner (doctor) or admin only

    Path Parameters:
    - dictation_id: ID of dictation

    Request Body:
    - title: Updated title (optional)
    - priority: Updated priority (optional)
    - notes: Updated notes (optional)
    - patient_reference: Updated patient reference (optional)
    - status: Updated status (optional, admins only)

    Returns:
    - Updated dictation object

    Raises:
    - 403: Not authorized
    - 404: Dictation not found
    """
    # Fetch dictation
    result = await db.execute(select(Dictation).where(Dictation.id == dictation_id))
    dictation = result.scalar_one_or_none()

    if not dictation or dictation.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictation not found")

    # Check authorization
    await check_resource_permission(
        current_user=current_user,
        action="update",
        resource_type="dictation",
        resource_id=dictation.id,
        resource_owner_id=dictation.doctor_id,
    )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        if field == "status" and current_user.role != UserRole.ADMIN:
            # Only admins can change status directly
            continue
        if hasattr(dictation, field):
            setattr(dictation, field, value)

    await db.commit()
    await db.refresh(dictation)

    logger.info(f"Dictation updated: id={dictation_id}, user_id={current_user.id}")

    return dictation


@router.delete("/{dictation_id}")
async def delete_dictation(
    dictation_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Delete dictation (soft delete)

    **Authorization**: Owner (doctor) or admin only

    Sets deleted_at timestamp. Audio file is retained for audit purposes.

    Path Parameters:
    - dictation_id: ID of dictation

    Returns:
    - Success message

    Raises:
    - 403: Not authorized
    - 404: Dictation not found
    - 409: Cannot delete if transcription in progress
    """
    # Fetch dictation
    result = await db.execute(select(Dictation).where(Dictation.id == dictation_id))
    dictation = result.scalar_one_or_none()

    if not dictation or dictation.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictation not found")

    # Check authorization
    await check_resource_permission(
        current_user=current_user,
        action="delete",
        resource_type="dictation",
        resource_id=dictation.id,
        resource_owner_id=dictation.doctor_id,
    )

    # Check if transcription is in progress
    if dictation.status == DictationStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete dictation while transcription is in progress",
        )

    # Soft delete
    dictation.deleted_at = datetime.utcnow()

    await db.commit()

    logger.info(f"Dictation deleted: id={dictation_id}, user_id={current_user.id}")

    return {"message": "Dictation deleted successfully"}
