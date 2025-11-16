"""
Database seeding script for development

Creates initial users and sample data for testing

Usage:
    uv run python scripts/seed_database.py
"""

import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, engine
from app.models import User, Dictation, Transcription, AuditLog
from app.models.user import UserRole
from app.models.dictation import DictationStatus, DictationPriority
from app.models.transcription import TranscriptionStatus
from app.models.audit_log import AuditAction


async def create_users(db: AsyncSession) -> dict[str, User]:
    """Create initial users for testing"""
    print("Creating users...")

    # Create admin user
    admin = User(
        email="admin@dictat.im",
        hashed_password=hash_password("admin123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db.add(admin)

    # Create doctors
    doctor1 = User(
        email="dr.smith@dictat.im",
        hashed_password=hash_password("doctor123"),
        full_name="Dr. John Smith",
        role=UserRole.DOCTOR,
        is_active=True,
        is_verified=True,
    )
    db.add(doctor1)

    doctor2 = User(
        email="dr.jones@dictat.im",
        hashed_password=hash_password("doctor123"),
        full_name="Dr. Sarah Jones",
        role=UserRole.DOCTOR,
        is_active=True,
        is_verified=True,
    )
    db.add(doctor2)

    # Create secretaries
    secretary1 = User(
        email="secretary1@dictat.im",
        hashed_password=hash_password("secretary123"),
        full_name="Alice Johnson",
        role=UserRole.SECRETARY,
        is_active=True,
        is_verified=True,
    )
    db.add(secretary1)

    secretary2 = User(
        email="secretary2@dictat.im",
        hashed_password=hash_password("secretary123"),
        full_name="Bob Williams",
        role=UserRole.SECRETARY,
        is_active=True,
        is_verified=True,
    )
    db.add(secretary2)

    await db.commit()
    await db.refresh(admin)
    await db.refresh(doctor1)
    await db.refresh(doctor2)
    await db.refresh(secretary1)
    await db.refresh(secretary2)

    print(f"Created {5} users")

    return {
        "admin": admin,
        "doctor1": doctor1,
        "doctor2": doctor2,
        "secretary1": secretary1,
        "secretary2": secretary2,
    }


async def create_sample_dictations(db: AsyncSession, users: dict[str, User]) -> list[Dictation]:
    """Create sample dictations"""
    print("Creating sample dictations...")

    dictations = []

    # Pending dictation
    dictation1 = Dictation(
        doctor_id=users["doctor1"].id,
        file_path="/app/storage/audio/sample1.mp3",
        file_name="consultation_20241116_001.mp3",
        file_size=2048000,
        mime_type="audio/mpeg",
        duration=120.5,
        status=DictationStatus.PENDING,
        priority=DictationPriority.NORMAL,
        title="Patient Consultation - John Doe",
        patient_reference="P12345",
        notes="Regular checkup, no major issues",
    )
    db.add(dictation1)
    dictations.append(dictation1)

    # Assigned dictation
    dictation2 = Dictation(
        doctor_id=users["doctor1"].id,
        secretary_id=users["secretary1"].id,
        file_path="/app/storage/audio/sample2.mp3",
        file_name="surgery_notes_20241116_002.mp3",
        file_size=5120000,
        mime_type="audio/mpeg",
        duration=300.0,
        status=DictationStatus.ASSIGNED,
        priority=DictationPriority.HIGH,
        title="Post-Surgery Notes - Jane Smith",
        patient_reference="P67890",
        notes="Appendectomy, successful procedure",
        claimed_at=datetime.utcnow() - timedelta(hours=2),
    )
    db.add(dictation2)
    dictations.append(dictation2)

    # In progress dictation
    dictation3 = Dictation(
        doctor_id=users["doctor2"].id,
        secretary_id=users["secretary1"].id,
        file_path="/app/storage/audio/sample3.mp3",
        file_name="emergency_notes_20241116_003.mp3",
        file_size=3072000,
        mime_type="audio/mpeg",
        duration=180.0,
        status=DictationStatus.IN_PROGRESS,
        priority=DictationPriority.URGENT,
        title="Emergency Visit - Robert Brown",
        patient_reference="P11111",
        notes="Chest pain, cardiac evaluation",
        claimed_at=datetime.utcnow() - timedelta(hours=4),
    )
    db.add(dictation3)
    dictations.append(dictation3)

    # Completed dictation
    dictation4 = Dictation(
        doctor_id=users["doctor2"].id,
        secretary_id=users["secretary2"].id,
        file_path="/app/storage/audio/sample4.mp3",
        file_name="followup_20241116_004.mp3",
        file_size=1536000,
        mime_type="audio/mpeg",
        duration=90.0,
        status=DictationStatus.COMPLETED,
        priority=DictationPriority.NORMAL,
        title="Follow-up Visit - Mary Davis",
        patient_reference="P22222",
        notes="Diabetes management follow-up",
        claimed_at=datetime.utcnow() - timedelta(days=1),
        completed_at=datetime.utcnow() - timedelta(hours=12),
    )
    db.add(dictation4)
    dictations.append(dictation4)

    await db.commit()
    for d in dictations:
        await db.refresh(d)

    print(f"Created {len(dictations)} dictations")
    return dictations


async def create_sample_transcriptions(
    db: AsyncSession, users: dict[str, User], dictations: list[Dictation]
) -> list[Transcription]:
    """Create sample transcriptions"""
    print("Creating sample transcriptions...")

    transcriptions = []

    # Draft transcription for in-progress dictation
    trans1 = Transcription(
        dictation_id=dictations[2].id,
        secretary_id=users["secretary1"].id,
        content="""# Emergency Visit - Robert Brown

**Patient ID:** P11111
**Visit Date:** 2024-11-16
**Chief Complaint:** Chest pain

## Assessment
Patient presented with acute chest pain. Cardiac evaluation performed.
ECG shows normal sinus rhythm. Troponin levels pending.

## Plan
- Monitor cardiac enzymes
- Schedule stress test
- Follow-up in 1 week
""",
        status=TranscriptionStatus.DRAFT,
        last_autosave_at=datetime.utcnow() - timedelta(minutes=5),
    )
    db.add(trans1)
    transcriptions.append(trans1)

    # Submitted transcription
    trans2 = Transcription(
        dictation_id=dictations[3].id,
        secretary_id=users["secretary2"].id,
        content="""# Follow-up Visit - Mary Davis

**Patient ID:** P22222
**Visit Date:** 2024-11-15
**Chief Complaint:** Diabetes management

## Current Status
Patient reports good glucose control. HbA1c: 6.8%

## Medications
- Metformin 1000mg BID
- Lisinopril 10mg daily

## Plan
- Continue current medications
- Repeat labs in 3 months
- Dietitian referral scheduled
""",
        status=TranscriptionStatus.SUBMITTED,
        submitted_at=datetime.utcnow() - timedelta(hours=12),
    )
    db.add(trans2)
    transcriptions.append(trans2)

    await db.commit()
    for t in transcriptions:
        await db.refresh(t)

    print(f"Created {len(transcriptions)} transcriptions")
    return transcriptions


async def create_audit_logs(db: AsyncSession, users: dict[str, User]) -> None:
    """Create sample audit logs"""
    print("Creating audit logs...")

    logs = [
        AuditLog(
            user_id=users["doctor1"].id,
            action=AuditAction.LOGIN,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            created_at=datetime.utcnow() - timedelta(hours=3),
        ),
        AuditLog(
            user_id=users["doctor1"].id,
            action=AuditAction.DICTATION_CREATED,
            resource_type="dictation",
            resource_id=1,
            ip_address="192.168.1.100",
            created_at=datetime.utcnow() - timedelta(hours=2, minutes=30),
        ),
        AuditLog(
            user_id=users["secretary1"].id,
            action=AuditAction.LOGIN,
            ip_address="192.168.1.101",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            created_at=datetime.utcnow() - timedelta(hours=2),
        ),
        AuditLog(
            user_id=users["secretary1"].id,
            action=AuditAction.DICTATION_CLAIMED,
            resource_type="dictation",
            resource_id=2,
            ip_address="192.168.1.101",
            created_at=datetime.utcnow() - timedelta(hours=2),
        ),
    ]

    for log in logs:
        db.add(log)

    await db.commit()
    print(f"Created {len(logs)} audit log entries")


async def seed_database() -> None:
    """Main seeding function"""
    print("=" * 60)
    print("Starting database seeding...")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            # Create users
            users = await create_users(db)

            # Create sample dictations
            dictations = await create_sample_dictations(db, users)

            # Create sample transcriptions
            await create_sample_transcriptions(db, users, dictations)

            # Create audit logs
            await create_audit_logs(db, users)

            print("=" * 60)
            print("Database seeding completed successfully!")
            print("=" * 60)
            print("\nTest credentials:")
            print("  Admin:      admin@dictat.im / admin123")
            print("  Doctor 1:   dr.smith@dictat.im / doctor123")
            print("  Doctor 2:   dr.jones@dictat.im / doctor123")
            print("  Secretary 1: secretary1@dictat.im / secretary123")
            print("  Secretary 2: secretary2@dictat.im / secretary123")
            print("=" * 60)

        except Exception as e:
            print(f"Error seeding database: {e}")
            raise


async def main() -> None:
    """Entry point"""
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
