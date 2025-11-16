"""
Audit Log model for GDPR compliance

TODO Phase 3:
- Implement tamper-proof logging (append-only)
- Add log integrity verification (hashing)
- Implement log retention policy enforcement
- Add log export for compliance reporting
- Implement log anonymization for GDPR erasure
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class AuditAction(str, Enum):
    """
    Auditable action types for GDPR compliance

    TODO Phase 3:
    - Add more granular actions
    - Implement action categories
    - Add severity levels
    """

    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"

    # User Management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"

    # Dictation
    DICTATION_CREATED = "dictation_created"
    DICTATION_VIEWED = "dictation_viewed"
    DICTATION_UPDATED = "dictation_updated"
    DICTATION_DELETED = "dictation_deleted"
    DICTATION_CLAIMED = "dictation_claimed"
    DICTATION_AUDIO_STREAMED = "dictation_audio_streamed"

    # Transcription
    TRANSCRIPTION_CREATED = "transcription_created"
    TRANSCRIPTION_VIEWED = "transcription_viewed"
    TRANSCRIPTION_UPDATED = "transcription_updated"
    TRANSCRIPTION_DELETED = "transcription_deleted"
    TRANSCRIPTION_SUBMITTED = "transcription_submitted"
    TRANSCRIPTION_APPROVED = "transcription_approved"
    TRANSCRIPTION_REJECTED = "transcription_rejected"

    # GDPR
    DATA_EXPORT_REQUESTED = "data_export_requested"
    DATA_EXPORT_COMPLETED = "data_export_completed"
    DATA_DELETION_REQUESTED = "data_deletion_requested"
    DATA_DELETION_COMPLETED = "data_deletion_completed"
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"

    # Authorization
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGED = "permission_changed"


class AuditLog(Base):
    """
    Audit log for GDPR compliance and security

    Critical for UK GDPR compliance (Isle of Man data protection)
    Must retain logs for 10 years

    TODO Phase 3:
    - Implement write-once, read-many (WORM) storage
    - Add cryptographic hash chain for tamper detection
    - Implement log signing
    - Add log archival and compression
    - Implement log querying API
    """

    __tablename__ = "audit_logs"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # User (nullable for system actions)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Action
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True, index=True)  # dictation, transcription, user
    resource_id = Column(Integer, nullable=True, index=True)

    # Context
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(36), nullable=True, index=True)  # UUID for request correlation

    # Details
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional context as JSON

    # TODO Phase 3: Add integrity verification
    # previous_log_hash = Column(String(64), nullable=True)  # Hash of previous log entry
    # log_hash = Column(String(64), nullable=False)  # Hash of this log entry
    # signature = Column(String(512), nullable=True)  # Digital signature

    # Timestamp (immutable)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    # TODO Phase 3: Define relationships
    # user = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id}, created_at={self.created_at})>"

    # TODO Phase 3: Add utility methods
    # @classmethod
    # async def log_action(
    #     cls,
    #     db: AsyncSession,
    #     action: AuditAction,
    #     user_id: int | None = None,
    #     resource_type: str | None = None,
    #     resource_id: int | None = None,
    #     metadata: dict | None = None,
    #     ip_address: str | None = None,
    #     user_agent: str | None = None,
    #     request_id: str | None = None,
    # ) -> "AuditLog":
    #     """Create and save audit log entry"""
    #     pass
    #
    # def verify_integrity(self) -> bool:
    #     """Verify log entry integrity using hash chain"""
    #     pass
