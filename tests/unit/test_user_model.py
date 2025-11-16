"""
Unit tests for User model

Tests cover:
- User creation and basic attributes
- Email validation and uniqueness
- Password hashing integration
- User roles (doctor, secretary, admin)
- Timestamps (created_at, updated_at)
- Soft delete functionality
- User activation/deactivation
"""

import pytest
import pytest_asyncio
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password


@pytest.mark.unit
class TestUserModelBasics:
    """Test basic User model functionality"""

    @pytest.mark.asyncio
    async def test_create_user_basic(self, test_db: AsyncSession) -> None:
        """Test creating a basic user"""
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == UserRole.DOCTOR

    @pytest.mark.asyncio
    async def test_create_user_all_fields(self, test_db: AsyncSession) -> None:
        """Test creating user with all fields"""
        user = User(
            email="complete@example.com",
            hashed_password=hash_password("password123"),
            full_name="Complete User",
            role=UserRole.SECRETARY,
            is_active=True,
            is_verified=True,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.id is not None
        assert user.email == "complete@example.com"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.role == UserRole.SECRETARY

    @pytest.mark.asyncio
    async def test_user_repr(self, test_db: AsyncSession) -> None:
        """Test user string representation"""
        user = User(
            email="repr@example.com",
            hashed_password=hash_password("password123"),
            full_name="Repr User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        repr_str = repr(user)
        assert "User" in repr_str
        assert str(user.id) in repr_str
        assert "repr@example.com" in repr_str
        assert "doctor" in repr_str


@pytest.mark.unit
class TestUserEmail:
    """Test user email functionality"""

    @pytest.mark.asyncio
    async def test_email_unique_constraint(self, test_db: AsyncSession) -> None:
        """Test that email must be unique"""
        # Create first user
        user1 = User(
            email="unique@example.com",
            hashed_password=hash_password("password123"),
            full_name="First User",
            role=UserRole.DOCTOR,
        )
        test_db.add(user1)
        await test_db.commit()

        # Try to create second user with same email
        user2 = User(
            email="unique@example.com",
            hashed_password=hash_password("password456"),
            full_name="Second User",
            role=UserRole.SECRETARY,
        )
        test_db.add(user2)

        with pytest.raises(IntegrityError):
            await test_db.commit()

    @pytest.mark.asyncio
    async def test_email_case_sensitive(self, test_db: AsyncSession) -> None:
        """Test email storage (case preservation)"""
        user = User(
            email="MixedCase@Example.COM",
            hashed_password=hash_password("password123"),
            full_name="Test User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Email should be stored as provided
        assert user.email == "MixedCase@Example.COM"

    @pytest.mark.asyncio
    async def test_email_required(self, test_db: AsyncSession) -> None:
        """Test that email is required"""
        user = User(
            hashed_password=hash_password("password123"),
            full_name="No Email User",
            role=UserRole.DOCTOR,
        )
        test_db.add(user)

        with pytest.raises(IntegrityError):
            await test_db.commit()


@pytest.mark.unit
class TestUserPassword:
    """Test user password functionality"""

    @pytest.mark.asyncio
    async def test_password_hashing(self, test_db: AsyncSession) -> None:
        """Test that password is hashed before storage"""
        plain_password = "SecurePassword123!"
        user = User(
            email="password@example.com",
            hashed_password=hash_password(plain_password),
            full_name="Password User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Password should be hashed
        assert user.hashed_password != plain_password
        # But should verify correctly
        assert verify_password(plain_password, user.hashed_password)

    @pytest.mark.asyncio
    async def test_password_verification(self, test_db: AsyncSession) -> None:
        """Test password verification for stored user"""
        plain_password = "CorrectPassword123"
        user = User(
            email="verify@example.com",
            hashed_password=hash_password(plain_password),
            full_name="Verify User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()

        # Correct password should verify
        assert verify_password(plain_password, user.hashed_password)

        # Wrong password should not verify
        assert not verify_password("WrongPassword", user.hashed_password)


@pytest.mark.unit
class TestUserRoles:
    """Test user role functionality"""

    @pytest.mark.asyncio
    async def test_create_doctor(self, test_db: AsyncSession) -> None:
        """Test creating a doctor user"""
        user = User(
            email="doctor@example.com",
            hashed_password=hash_password("password123"),
            full_name="Dr. Test",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.role == UserRole.DOCTOR
        assert user.role.value == "doctor"

    @pytest.mark.asyncio
    async def test_create_secretary(self, test_db: AsyncSession) -> None:
        """Test creating a secretary user"""
        user = User(
            email="secretary@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test Secretary",
            role=UserRole.SECRETARY,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.role == UserRole.SECRETARY
        assert user.role.value == "secretary"

    @pytest.mark.asyncio
    async def test_create_admin(self, test_db: AsyncSession) -> None:
        """Test creating an admin user"""
        user = User(
            email="admin@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test Admin",
            role=UserRole.ADMIN,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.role == UserRole.ADMIN
        assert user.role.value == "admin"

    @pytest.mark.asyncio
    async def test_role_required(self, test_db: AsyncSession) -> None:
        """Test that role is required"""
        user = User(
            email="norole@example.com",
            hashed_password=hash_password("password123"),
            full_name="No Role User",
        )
        test_db.add(user)

        with pytest.raises(IntegrityError):
            await test_db.commit()


@pytest.mark.unit
class TestUserTimestamps:
    """Test user timestamp functionality"""

    @pytest.mark.asyncio
    async def test_created_at_auto_set(self, test_db: AsyncSession) -> None:
        """Test that created_at is automatically set"""
        before = datetime.utcnow()

        user = User(
            email="timestamp@example.com",
            hashed_password=hash_password("password123"),
            full_name="Timestamp User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        after = datetime.utcnow()

        assert user.created_at is not None
        assert before <= user.created_at <= after

    @pytest.mark.asyncio
    async def test_updated_at_auto_set(self, test_db: AsyncSession) -> None:
        """Test that updated_at is automatically set"""
        user = User(
            email="updatetime@example.com",
            hashed_password=hash_password("password123"),
            full_name="Update User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.updated_at is not None
        assert user.created_at is not None
        # Should be approximately equal at creation
        assert abs((user.updated_at - user.created_at).total_seconds()) < 1

    @pytest.mark.asyncio
    async def test_updated_at_changes_on_update(self, test_db: AsyncSession) -> None:
        """Test that updated_at changes when user is updated"""
        import asyncio

        user = User(
            email="update@example.com",
            hashed_password=hash_password("password123"),
            full_name="Update User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        original_updated_at = user.updated_at

        # Wait a bit to ensure timestamp difference
        await asyncio.sleep(0.1)

        # Update user
        user.full_name = "Updated Name"
        await test_db.commit()
        await test_db.refresh(user)

        # updated_at should have changed
        assert user.updated_at > original_updated_at


@pytest.mark.unit
class TestUserActiveStatus:
    """Test user active/inactive status"""

    @pytest.mark.asyncio
    async def test_user_active_by_default(self, test_db: AsyncSession) -> None:
        """Test that users are active by default"""
        user = User(
            email="active@example.com",
            hashed_password=hash_password("password123"),
            full_name="Active User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_inactive_user(self, test_db: AsyncSession) -> None:
        """Test creating an inactive user"""
        user = User(
            email="inactive@example.com",
            hashed_password=hash_password("password123"),
            full_name="Inactive User",
            role=UserRole.DOCTOR,
            is_active=False,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.is_active is False

    @pytest.mark.asyncio
    async def test_deactivate_user(self, test_db: AsyncSession) -> None:
        """Test deactivating a user"""
        user = User(
            email="deactivate@example.com",
            hashed_password=hash_password("password123"),
            full_name="Deactivate User",
            role=UserRole.DOCTOR,
            is_active=True,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.is_active is True

        # Deactivate
        user.is_active = False
        await test_db.commit()
        await test_db.refresh(user)

        assert user.is_active is False


@pytest.mark.unit
class TestUserVerification:
    """Test user verification status"""

    @pytest.mark.asyncio
    async def test_user_unverified_by_default(self, test_db: AsyncSession) -> None:
        """Test that users are unverified by default"""
        user = User(
            email="unverified@example.com",
            hashed_password=hash_password("password123"),
            full_name="Unverified User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.is_verified is False

    @pytest.mark.asyncio
    async def test_verify_user(self, test_db: AsyncSession) -> None:
        """Test verifying a user"""
        user = User(
            email="verify@example.com",
            hashed_password=hash_password("password123"),
            full_name="Verify User",
            role=UserRole.DOCTOR,
            is_verified=False,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.is_verified is False

        # Verify user
        user.is_verified = True
        await test_db.commit()
        await test_db.refresh(user)

        assert user.is_verified is True


@pytest.mark.unit
class TestUserSoftDelete:
    """Test user soft delete functionality"""

    @pytest.mark.asyncio
    async def test_deleted_at_null_by_default(self, test_db: AsyncSession) -> None:
        """Test that deleted_at is null for active users"""
        user = User(
            email="notdeleted@example.com",
            hashed_password=hash_password("password123"),
            full_name="Not Deleted User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.deleted_at is None

    @pytest.mark.asyncio
    async def test_soft_delete_user(self, test_db: AsyncSession) -> None:
        """Test soft deleting a user"""
        user = User(
            email="delete@example.com",
            hashed_password=hash_password("password123"),
            full_name="Delete User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Soft delete
        user.deleted_at = datetime.utcnow()
        await test_db.commit()
        await test_db.refresh(user)

        assert user.deleted_at is not None
        assert isinstance(user.deleted_at, datetime)


@pytest.mark.unit
class TestUserQueries:
    """Test querying users from database"""

    @pytest.mark.asyncio
    async def test_query_user_by_email(self, test_db: AsyncSession) -> None:
        """Test querying user by email"""
        user = User(
            email="query@example.com",
            hashed_password=hash_password("password123"),
            full_name="Query User",
            role=UserRole.DOCTOR,
        )

        test_db.add(user)
        await test_db.commit()

        # Query by email
        result = await test_db.execute(select(User).where(User.email == "query@example.com"))
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.email == "query@example.com"

    @pytest.mark.asyncio
    async def test_query_users_by_role(self, test_db: AsyncSession) -> None:
        """Test querying users by role"""
        # Create users with different roles
        doctor1 = User(
            email="doctor1@example.com",
            hashed_password=hash_password("password123"),
            full_name="Doctor 1",
            role=UserRole.DOCTOR,
        )
        doctor2 = User(
            email="doctor2@example.com",
            hashed_password=hash_password("password123"),
            full_name="Doctor 2",
            role=UserRole.DOCTOR,
        )
        secretary = User(
            email="secretary@example.com",
            hashed_password=hash_password("password123"),
            full_name="Secretary",
            role=UserRole.SECRETARY,
        )

        test_db.add_all([doctor1, doctor2, secretary])
        await test_db.commit()

        # Query doctors
        result = await test_db.execute(select(User).where(User.role == UserRole.DOCTOR))
        doctors = result.scalars().all()

        assert len(doctors) == 2
        assert all(user.role == UserRole.DOCTOR for user in doctors)

    @pytest.mark.asyncio
    async def test_query_active_users(self, test_db: AsyncSession) -> None:
        """Test querying only active users"""
        active_user = User(
            email="active@example.com",
            hashed_password=hash_password("password123"),
            full_name="Active",
            role=UserRole.DOCTOR,
            is_active=True,
        )
        inactive_user = User(
            email="inactive@example.com",
            hashed_password=hash_password("password123"),
            full_name="Inactive",
            role=UserRole.DOCTOR,
            is_active=False,
        )

        test_db.add_all([active_user, inactive_user])
        await test_db.commit()

        # Query active users
        result = await test_db.execute(select(User).where(User.is_active == True))
        active_users = result.scalars().all()

        assert len(active_users) >= 1
        assert all(user.is_active for user in active_users)
