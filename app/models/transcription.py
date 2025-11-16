"""
Transcription model for dictation transcriptions

TODO Phase 2:
- Implement version history tracking
- Add autosave support with timestamps
- Implement markdown validation
- Add character/word count fields
- Add estimated time tracking
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class TranscriptionStatus(str, Enum):
    """
    Transcription workflow states

    TODO Phase 2:
    - Add state transition validation
    - Track time spent in each state
    """

    DRAFT = "draft"  # Being worked on
    SUBMITTED = "submitted"  # Submitted for review
    APPROVED = "approved"  # Approved by doctor
    REJECTED = "rejected"  # Rejected, needs revision
    REVISED = "revised"  # Revised after rejection


class Transcription(Base):
    """
    Transcription model for dictation transcriptions

    Relationships:
    - dictation: One-to-one (belongs to dictation)
    - secretary: Many-to-one (created by secretary)
    - reviewer: Many-to-one (reviewed by doctor)

    TODO Phase 2:
    - Implement revision history table
    - Add autosave functionality
    - Implement collaborative editing detection
    - Add markdown formatting validation
    """

    __tablename__ = "transcriptions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Ownership
    dictation_id = Column(Integer, ForeignKey("dictations.id"), unique=True, nullable=False, index=True)
    secretary_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Content
    content = Column(Text, nullable=False)  # Markdown formatted
    version = Column(Integer, default=1, nullable=False)

    # TODO Phase 2: Add content metadata
    # word_count = Column(Integer, default=0, nullable=False)
    # character_count = Column(Integer, default=0, nullable=False)
    # estimated_duration = Column(Integer, nullable=True)  # Seconds spent transcribing

    # Workflow
    status = Column(
        SQLEnum(TranscriptionStatus),
        default=TranscriptionStatus.DRAFT,
        nullable=False,
        index=True,
    )

    # Review
    review_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_autosave_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    # TODO Phase 2: Define relationships
    # dictation = relationship("Dictation", back_populates="transcription")
    # secretary = relationship("User", back_populates="transcriptions", foreign_keys=[secretary_id])
    # reviewer = relationship("User", back_populates="reviewed_transcriptions", foreign_keys=[reviewer_id])
    # revisions = relationship("TranscriptionRevision", back_populates="transcription", order_by="TranscriptionRevision.version")

    def __repr__(self) -> str:
        return f"<Transcription(id={self.id}, dictation_id={self.dictation_id}, status='{self.status}')>"

    # TODO Phase 2: Add business logic methods
    # def increment_version(self) -> None:
    #     """Increment version number and create revision history"""
    #     pass
    #
    # def can_edit(self, user_id: int) -> bool:
    #     """Check if user can edit this transcription"""
    #     pass
    #
    # def validate_markdown(self) -> bool:
    #     """Validate markdown content"""
    #     pass


# TODO Phase 3: Implement revision history
# class TranscriptionRevision(Base):
#     """Revision history for transcriptions"""
#     __tablename__ = "transcription_revisions"
#
#     id = Column(Integer, primary_key=True)
#     transcription_id = Column(Integer, ForeignKey("transcriptions.id"), nullable=False)
#     version = Column(Integer, nullable=False)
#     content = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
