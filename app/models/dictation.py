"""
Dictation model for audio file management

TODO Phase 2:
- Add file metadata (size, format, duration)
- Implement file path encryption
- Add checksum/hash for file integrity
- Add support for multiple audio formats
- Implement file retention policy
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class DictationStatus(str, Enum):
    """
    Dictation workflow states

    TODO Phase 2:
    - Add state transition validation
    - Implement state machine for workflow
    - Add timestamps for each state transition
    """

    PENDING = "pending"  # Uploaded, waiting for assignment
    ASSIGNED = "assigned"  # Assigned to secretary but not claimed
    IN_PROGRESS = "in_progress"  # Secretary is working on it
    COMPLETED = "completed"  # Transcription submitted
    REVIEWED = "reviewed"  # Doctor has reviewed
    REJECTED = "rejected"  # Doctor rejected, needs revision


class DictationPriority(str, Enum):
    """Dictation priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Dictation(Base):
    """
    Dictation model representing uploaded audio files

    Relationships:
    - doctor: Many-to-one (created by doctor)
    - secretary: Many-to-one (assigned to secretary)
    - transcription: One-to-one (has one transcription)

    TODO Phase 2:
    - Add file encryption at rest
    - Implement versioning for re-uploads
    - Add support for metadata extraction from audio
    - Implement automatic cleanup for deleted dictations
    """

    __tablename__ = "dictations"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Ownership
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    secretary_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # File Information
    file_path = Column(String(500), nullable=False)  # TODO: Encrypt this field
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Bytes
    mime_type = Column(String(100), nullable=False)
    duration = Column(Float, nullable=True)  # Duration in seconds

    # TODO Phase 2: Add file integrity
    # file_hash = Column(String(64), nullable=False)  # SHA-256 hash
    # checksum = Column(String(32), nullable=False)  # MD5 checksum

    # Workflow
    status = Column(
        SQLEnum(DictationStatus),
        default=DictationStatus.PENDING,
        nullable=False,
        index=True,
    )
    priority = Column(
        SQLEnum(DictationPriority),
        default=DictationPriority.NORMAL,
        nullable=False,
        index=True,
    )

    # Metadata
    title = Column(String(255), nullable=True)
    patient_reference = Column(String(100), nullable=True)  # TODO: Encrypt
    notes = Column(Text, nullable=True)

    # TODO Phase 3: Add patient information (encrypted)
    # patient_id = Column(String(100), nullable=True)  # Encrypted
    # patient_name = Column(String(255), nullable=True)  # Encrypted
    # procedure_type = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    claimed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    # TODO Phase 2: Define relationships
    # doctor = relationship("User", back_populates="dictations", foreign_keys=[doctor_id])
    # secretary = relationship("User", back_populates="assigned_dictations", foreign_keys=[secretary_id])
    # transcription = relationship("Transcription", back_populates="dictation", uselist=False)

    def __repr__(self) -> str:
        return f"<Dictation(id={self.id}, status='{self.status}', doctor_id={self.doctor_id})>"

    # TODO Phase 2: Add business logic methods
    # def can_claim(self, user_id: int, user_role: str) -> bool:
    #     """Check if user can claim this dictation"""
    #     pass
    #
    # def can_edit(self, user_id: int) -> bool:
    #     """Check if user can edit this dictation"""
    #     pass
    #
    # def transition_status(self, new_status: DictationStatus) -> bool:
    #     """Validate and transition to new status"""
    #     pass
