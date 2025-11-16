"""
User model for authentication and authorization

TODO Phase 1:
- Implement password hashing on save
- Add email verification status
- Implement soft delete (deactivation)
- Add last login tracking
- Add failed login attempt tracking for security
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.session import Base


class UserRole(str, Enum):
    """
    User roles for RBAC

    TODO Phase 2:
    - Add permissions mapping for each role
    - Implement hierarchical roles (admin > doctor > secretary)
    - Add custom role support
    """

    DOCTOR = "doctor"
    SECRETARY = "secretary"
    ADMIN = "admin"


class User(Base):
    """
    User model for authentication and role-based access

    Relationships:
    - dictations: One-to-many (doctor creates dictations)
    - transcriptions: One-to-many (secretary creates transcriptions)
    - reviewed_transcriptions: One-to-many (doctor reviews transcriptions)
    - audit_logs: One-to-many (user actions logged)

    TODO Phase 1:
    - Add unique constraint on email
    - Add check constraint for email format
    - Implement password hashing in setter
    - Add created_by and updated_by tracking
    - Add timezone support for timestamps
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # User Profile
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)

    # TODO Phase 2: Add additional profile fields
    # phone_number = Column(String(20), nullable=True)
    # department = Column(String(100), nullable=True)
    # license_number = Column(String(50), nullable=True)  # For doctors

    # Security
    # TODO Phase 2: Implement these fields
    # failed_login_attempts = Column(Integer, default=0)
    # account_locked_until = Column(DateTime, nullable=True)
    # last_login_at = Column(DateTime, nullable=True)
    # last_login_ip = Column(String(45), nullable=True)  # IPv6 support

    # GDPR Consent
    # TODO Phase 3: Implement consent tracking
    # consent_given_at = Column(DateTime, nullable=True)
    # consent_version = Column(String(10), nullable=True)
    # data_processing_consent = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    # TODO Phase 2: Define all relationships
    # dictations = relationship("Dictation", back_populates="doctor", foreign_keys="Dictation.doctor_id")
    # assigned_dictations = relationship("Dictation", back_populates="secretary", foreign_keys="Dictation.secretary_id")
    # transcriptions = relationship("Transcription", back_populates="secretary", foreign_keys="Transcription.secretary_id")
    # reviewed_transcriptions = relationship("Transcription", back_populates="reviewer", foreign_keys="Transcription.reviewer_id")
    # audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    # TODO Phase 1: Add property methods
    # @property
    # def is_doctor(self) -> bool:
    #     return self.role == UserRole.DOCTOR
    #
    # @property
    # def is_secretary(self) -> bool:
    #     return self.role == UserRole.SECRETARY
    #
    # @property
    # def is_admin(self) -> bool:
    #     return self.role == UserRole.ADMIN

    # TODO Phase 2: Add password validation
    # def set_password(self, password: str) -> None:
    #     """Hash and set password"""
    #     from app.core.security import hash_password
    #     self.hashed_password = hash_password(password)
    #
    # def verify_password(self, password: str) -> bool:
    #     """Verify password against hash"""
    #     from app.core.security import verify_password
    #     return verify_password(password, self.hashed_password)
