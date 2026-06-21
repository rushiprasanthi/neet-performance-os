"""Tests for profile functionality."""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.identity.models import User, Profile
from app.domains.identity.repositories.profile_repository import ProfileRepository
from app.domains.identity.services.profile_service import ProfileService
from app.domains.identity.repositories.user_repository import UserRepository


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """Create a test user with profile."""
    user_repo = UserRepository(db)
    user = await user_repo.create_user(
        email=f"testuser_{uuid4()}@neet.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
    )
    await db.commit()  # Ensure DB flush persists to the test transaction state
    return user


@pytest_asyncio.fixture
async def user_auth_headers(test_user: User) -> dict:
    """Provide authorization headers mapped explicitly to the test_user database record."""
    from unittest.mock import AsyncMock
    from app.domains.identity.services.jwt_service import JWTService
    mock_redis = AsyncMock()
    jwt_service = JWTService(mock_redis)
    token, _ = jwt_service.create_access_token(test_user.id, "student")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
class TestProfileRepository:
    """Test ProfileRepository operations."""

    async def test_get_by_user_id(self, db: AsyncSession, test_user: User):
        """Test retrieving profile by user ID."""
        repo = ProfileRepository(db)
        profile = await repo.get_by_user_id(test_user.id)
        
        assert profile is not None
        assert profile.user_id == test_user.id
        assert profile.first_name == "Test"
        assert profile.last_name == "User"

    async def test_get_by_user_id_not_found(self, db: AsyncSession):
        """Test getting profile for non-existent user."""
        repo = ProfileRepository(db)
        fake_user_id = uuid4()
        profile = await repo.get_by_user_id(fake_user_id)
        
        assert profile is None

    async def test_update(self, db: AsyncSession, test_user: User):
        """Test updating profile fields."""
        repo = ProfileRepository(db)
        
        updated_profile = await repo.update(
            test_user.id,
            bio="My bio",
            target_score=650,
            study_hours_per_day=4,
            preferred_subjects=["Physics", "Chemistry"],
        )
        
        assert updated_profile is not None
        assert updated_profile.bio == "My bio"
        assert updated_profile.target_score == 650
        assert updated_profile.study_hours_per_day == 4
        assert updated_profile.preferred_subjects == ["Physics", "Chemistry"]

    async def test_update_not_found(self, db: AsyncSession):
        """Test updating profile for non-existent user."""
        repo = ProfileRepository(db)
        fake_user_id = uuid4()
        
        result = await repo.update(fake_user_id, bio="test")
        assert result is None


@pytest.mark.asyncio
class TestProfileService:
    """Test ProfileService operations."""

    async def test_get_profile(self, db: AsyncSession, test_user: User):
        """Test getting user profile."""
        service = ProfileService(db)
        profile = await service.get_profile(test_user.id)
        
        assert profile is not None
        assert profile.user_id == test_user.id

    async def test_get_profile_not_found(self, db: AsyncSession):
        """Test getting profile for non-existent user."""
        service = ProfileService(db)
        fake_user_id = uuid4()
        
        with pytest.raises(ValueError, match="Profile for user"):
            await service.get_profile(fake_user_id)

    async def test_update_profile(self, db: AsyncSession, test_user: User):
        """Test updating user profile."""
        service = ProfileService(db)
        
        updated_profile = await service.update_profile(
            test_user.id,
            bio="Updated bio",
            target_score=700,
            study_hours_per_day=5,
            preferred_subjects=["Physics", "Chemistry", "Biology"],
            target_exam_year=2027,
        )
        
        assert updated_profile.bio == "Updated bio"
        assert updated_profile.target_score == 700
        assert updated_profile.study_hours_per_day == 5
        assert updated_profile.preferred_subjects == ["Physics", "Chemistry", "Biology"]
        assert updated_profile.target_exam_year == 2027

    async def test_update_profile_validation_first_name_length(
        self, db: AsyncSession, test_user: User
    ):
        """Test validation of first_name length."""
        service = ProfileService(db)
        
        with pytest.raises(ValueError, match="first_name must be <= 100 characters"):
            await service.update_profile(
                test_user.id,
                first_name="a" * 101,
            )

    async def test_update_profile_validation_last_name_length(
        self, db: AsyncSession, test_user: User
    ):
        """Test validation of last_name length."""
        service = ProfileService(db)
        
        with pytest.raises(ValueError, match="last_name must be <= 100 characters"):
            await service.update_profile(
                test_user.id,
                last_name="b" * 101,
            )

    async def test_update_profile_validation_bio_length(
        self, db: AsyncSession, test_user: User
    ):
        """Test validation of bio length."""
        service = ProfileService(db)
        
        with pytest.raises(ValueError, match="bio must be <= 1000 characters"):
            await service.update_profile(
                test_user.id,
                bio="c" * 1001,
            )

    async def test_update_profile_validation_target_score_range(
        self, db: AsyncSession, test_user: User
    ):
        """Test validation of target_score range."""
        service = ProfileService(db)
        
        with pytest.raises(ValueError, match="target_score must be between 0 and 720"):
            await service.update_profile(test_user.id, target_score=750)
        
        with pytest.raises(ValueError, match="target_score must be between 0 and 720"):
            await service.update_profile(test_user.id, target_score=-10)

    async def test_update_profile_validation_study_hours_range(
        self, db: AsyncSession, test_user: User
    ):
        """Test validation of study_hours_per_day range."""
        service = ProfileService(db)
        
        with pytest.raises(ValueError, match="study_hours_per_day must be between 0 and 24"):
            await service.update_profile(test_user.id, study_hours_per_day=25)
        
        with pytest.raises(ValueError, match="study_hours_per_day must be between 0 and 24"):
            await service.update_profile(test_user.id, study_hours_per_day=-1)

    async def test_update_profile_validation_subjects(
        self, db: AsyncSession, test_user: User
    ):
        """Test validation of preferred_subjects."""
        service = ProfileService(db)
        
        with pytest.raises(ValueError, match="Subjects must be Physics, Chemistry, or Biology"):
            await service.update_profile(
                test_user.id,
                preferred_subjects=["Physics", "InvalidSubject"],
            )

    async def test_update_profile_partial(
        self, db: AsyncSession, test_user: User
    ):
        """Test updating only some profile fields."""
        service = ProfileService(db)
        
        # Update only bio
        updated_profile = await service.update_profile(
            test_user.id,
            bio="Just bio update",
        )
        
        assert updated_profile.bio == "Just bio update"
        assert updated_profile.first_name == "Test"  # Should remain unchanged


@pytest.mark.asyncio
class TestProfileEndpoints:
    """Test profile API endpoints."""

    async def test_get_profile_unauthorized(self, client):
        """Test GET /profile without authorization."""
        response = await client.get("/api/v1/profile")
        assert response.status_code == 401

    async def test_patch_profile_unauthorized(self, client):
        """Test PATCH /profile without authorization."""
        response = await client.patch(
            "/api/v1/profile",
            json={"bio": "test"},
        )
        assert response.status_code == 401

    async def test_get_profile_authorized(self, client, user_auth_headers, test_user):
        """Test GET /profile with valid token."""
        response = await client.get(
            "/api/v1/profile",
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(test_user.id)
        assert data["first_name"] == "Test"

    async def test_patch_profile_authorized(self, client, user_auth_headers, test_user):
        """Test PATCH /profile with valid token."""
        response = await client.patch(
            "/api/v1/profile",
            headers=user_auth_headers,
            json={
                "bio": "Updated bio",
                "target_score": 680,
                "study_hours_per_day": 5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Updated bio"
        assert data["target_score"] == 680
        assert data["study_hours_per_day"] == 5

    async def test_patch_profile_validation_error(
        self, client, user_auth_headers
    ):
        """Test PATCH /profile with invalid data."""
        response = await client.patch(
            "/api/v1/profile",
            headers=user_auth_headers,
            json={"target_score": 750},  # Invalid: > 720
        )
        
        # Handle both Service Layer custom exceptions (400) and Pydantic field validation (422)
        assert response.status_code in [400, 422]
        
        if response.status_code == 422:
            detail = response.json()["detail"]
            assert isinstance(detail, list)
            assert detail[0]["loc"][-1] == "target_score"
        else:
            assert "target_score must be between 0 and 720" in response.json()["detail"]

    async def test_patch_profile_invalid_subjects(
        self, client, user_auth_headers
    ):
        """Test PATCH /profile with invalid subjects."""
        response = await client.patch(
            "/api/v1/profile",
            headers=user_auth_headers,
            json={"preferred_subjects": ["Physics", "Invalid"]},
        )
        
        assert response.status_code in [400, 422]
        
        if response.status_code == 422:
            detail = response.json()["detail"]
            assert "preferred_subjects" in str(detail)


@pytest.mark.asyncio
class TestProfileAuditEvents:
    """Test audit event logging."""

    async def test_profile_viewed_audit_event(self, db: AsyncSession, test_user: User):
        """Test that PROFILE_VIEWED event is logged."""
        from app.domains.identity.models import AuditLog
        from sqlalchemy import select
        
        service = ProfileService(db)
        await service.get_profile(test_user.id)
        
        # Check audit log
        stmt = select(AuditLog).where(
            AuditLog.event_type == "PROFILE_VIEWED"
        ).where(
            AuditLog.user_id == test_user.id
        )
        result = await db.execute(stmt)
        audit_log = result.scalar_one_or_none()
        
        assert audit_log is not None
        assert audit_log.event_type == "PROFILE_VIEWED"

    async def test_profile_updated_audit_event(self, db: AsyncSession, test_user: User):
        """Test that PROFILE_UPDATED event is logged."""
        from app.domains.identity.models import AuditLog
        from sqlalchemy import select
        
        service = ProfileService(db)
        await service.update_profile(test_user.id, bio="New bio")
        
        # Check audit log
        stmt = select(AuditLog).where(
            AuditLog.event_type == "PROFILE_UPDATED"
        ).where(
            AuditLog.user_id == test_user.id
        )
        result = await db.execute(stmt)
        audit_log = result.scalar_one_or_none()
        
        assert audit_log is not None
        assert audit_log.event_type == "PROFILE_UPDATED"