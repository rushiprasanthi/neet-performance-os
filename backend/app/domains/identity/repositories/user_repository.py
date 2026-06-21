"""Repository pattern for User model."""

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.identity.models import Profile, User, UserRole


class UserRepository:
    """User repository for database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def normalize_email(email: str) -> str:
        """Canonicalize email addresses for consistent lookups and writes."""
        return email.strip().lower()

    def _base_query(self):
        """Base query with eager loaded relationships to prevent MissingGreenletException."""
        return select(User).options(
            selectinload(User.profile),
            selectinload(User.user_roles).selectinload(UserRole.role)
        )

    async def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        normalized_email = self.normalize_email(email)

        existing = await self.get_by_email(normalized_email)
        if existing:
            raise ValueError(f"User with email {normalized_email} already exists")

        user = User(
            email=normalized_email, 
            password_hash=password_hash, 
            status="active",
            email_verified=True 
        )
        self.session.add(user)
        await self.session.flush() 

        profile = Profile(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            notification_prefs={"email_notifications": True, "sms_notifications": False},
        )
        self.session.add(profile)
        await self.session.flush()
        
        # Load the fully attached entity (with relationships) safely.
        loaded_user = await self.get_by_id(user.id)
        if not loaded_user:
            raise RuntimeError("Failed to retrieve user after creation")
        
        return loaded_user

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = self._base_query().where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        normalized_email = self.normalize_email(email)
        stmt = self._base_query().where(User.email == normalized_email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: UUID, **kwargs) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.flush()
        return True

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = self._base_query().offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def log_audit(self, user_id: UUID, event_type: str, metadata: dict | None = None):
        from app.domains.identity.models import AuditLog
        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            event_metadata=metadata or {},
        )
        self.session.add(audit_log)
        await self.session.flush()