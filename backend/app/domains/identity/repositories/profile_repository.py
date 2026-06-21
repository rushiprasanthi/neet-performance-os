"""Repository pattern for Profile model."""

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.identity.models import Profile


class ProfileRepository:
    """Profile repository for database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, profile_id: UUID) -> Profile | None:
        stmt = select(Profile).where(Profile.id == profile_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, user_id: UUID, **kwargs) -> Profile | None:
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return None

        for key, value in kwargs.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)

        await self.session.flush()
        await self.session.refresh(profile)
        return profile