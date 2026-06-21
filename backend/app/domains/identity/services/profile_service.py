"""Profile service for profile management operations."""

from uuid import UUID
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.identity.models import AuditLog, Profile
from app.domains.identity.repositories.profile_repository import ProfileRepository


class ProfileService:
    def __init__(self, session: AsyncSession, redis_client: redis.Redis | None = None):
        self.session = session
        self.profile_repo = ProfileRepository(session)
        self.redis = redis_client

    async def get_profile(self, user_id: UUID) -> Profile | None:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Profile for user {user_id} not found")

        await self.log_audit_event(
            user_id=user_id,
            event_type="PROFILE_VIEWED",
            metadata={"profile_id": str(profile.id)},
        )
        return profile

    async def update_profile(self, user_id: UUID, **kwargs) -> Profile:
        if "first_name" in kwargs and kwargs["first_name"] and len(kwargs["first_name"]) > 100:
            raise ValueError("first_name must be <= 100 characters")
        if "last_name" in kwargs and kwargs["last_name"] and len(kwargs["last_name"]) > 100:
            raise ValueError("last_name must be <= 100 characters")
        if "bio" in kwargs and kwargs["bio"] and len(kwargs["bio"]) > 1000:
            raise ValueError("bio must be <= 1000 characters")
        if "target_score" in kwargs and kwargs["target_score"]:
            if not (0 <= kwargs["target_score"] <= 720):
                raise ValueError("target_score must be between 0 and 720")
        if "study_hours_per_day" in kwargs and kwargs["study_hours_per_day"] is not None:
            if not (0 <= kwargs["study_hours_per_day"] <= 24):
                raise ValueError("study_hours_per_day must be between 0 and 24")
        if "preferred_subjects" in kwargs and kwargs["preferred_subjects"]:
            allowed = {"Physics", "Chemistry", "Biology"}
            if not all(s in allowed for s in kwargs["preferred_subjects"]):
                raise ValueError("Subjects must be Physics, Chemistry, or Biology")

        profile = await self.profile_repo.update(user_id, **kwargs)
        if not profile:
            raise ValueError(f"Profile for user {user_id} not found")

        await self.log_audit_event(
            user_id=user_id,
            event_type="PROFILE_UPDATED",
            metadata={"profile_id": str(profile.id), "updated_fields": list(kwargs.keys())},
        )
        return profile

    async def log_audit_event(self, user_id: UUID, event_type: str, metadata: dict | None = None) -> None:
        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            event_metadata=metadata or {},
        )
        self.session.add(audit_log)
        await self.session.flush()