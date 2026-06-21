"""Authentication service for user registration and credential management."""

import asyncio
from uuid import UUID
import redis.asyncio as redis
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.identity.models import AuditLog, User
from app.domains.identity.repositories.user_repository import UserRepository
from app.domains.identity.services.jwt_service import JWTService

ph = PasswordHasher()


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession, redis_client: redis.Redis | None = None):
        self.session = session
        self.user_repo = UserRepository(session)
        self.redis = redis_client
        self.jwt_service = JWTService(redis_client) if redis_client else None

    @staticmethod
    def hash_password(password: str) -> str:
        """Sync function for hashing. Must be run in threadpool."""
        return ph.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Sync function for verification. Must be run in threadpool."""
        try:
            return ph.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False

    async def register(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        normalized_email = self.user_repo.normalize_email(email)
        existing_user = await self.user_repo.get_by_email(normalized_email)
        if existing_user:
            raise ValueError(f"User with email {normalized_email} already exists")

        # Offload CPU-bound hashing to avoid blocking the async event loop
        password_hash = await asyncio.to_thread(self.hash_password, password)

        user = await self.user_repo.create_user(
            email=normalized_email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
        )

        await self.log_audit_event(
            user_id=user.id,
            event_type="USER_REGISTERED",
            metadata={
                "email": email,
                "status": user.status,
                "email_verified": user.email_verified,
            },
        )
        return user

    async def login(
        self, email: str, password: str
    ) -> tuple[str, str, int, str]:
        if not self.redis or not self.jwt_service:
            raise RuntimeError("Redis client not configured for login")
        
        normalized_email = self.user_repo.normalize_email(email)
        failed_key = f"failed_attempts:{normalized_email}"
        failed_attempts = await self.redis.get(failed_key)
        
        if failed_attempts and int(failed_attempts) >= 5:
            raise PermissionError("Account locked due to too many failed login attempts. Try again later.")
        
        user = await self.user_repo.get_by_email(normalized_email)
        if not user:
            await self._increment_failed_attempts(failed_key)
            raise ValueError("Invalid email or password")
        
        # Offload CPU-bound verification to avoid blocking the async event loop
        is_valid = await asyncio.to_thread(self.verify_password, password, user.password_hash)
        if not is_valid:
            await self._increment_failed_attempts(failed_key)
            raise ValueError("Invalid email or password")
        
        if not user.email_verified:
            raise ValueError("Email not verified. Please verify your email first.")
        
        await self.redis.delete(failed_key)
        
        role = "user"
        if user.user_roles:
            role = user.user_roles[0].role.name
        
        access_token, expires_in = self.jwt_service.create_access_token(user.id, role)
        refresh_token_uuid, _ = await self.jwt_service.create_refresh_token(user.id)
        
        await self.log_audit_event(
            user_id=user.id,
            event_type="LOGIN_SUCCESS",
            metadata={"email": normalized_email},
        )
        
        return access_token, refresh_token_uuid, expires_in, role

    async def logout(self, user_id: UUID) -> None:
        if not self.redis or not self.jwt_service:
            raise RuntimeError("Redis client not configured for logout")
        
        await self.jwt_service.revoke_all_user_tokens(user_id)
        
        await self.log_audit_event(
            user_id=user_id,
            event_type="LOGOUT",
        )

    async def _increment_failed_attempts(self, key: str) -> int:
        if not self.redis:
            raise RuntimeError("Redis client not configured")
        
        # Atomic counter + TTL refresh in Redis pipeline (Sliding window rate limit)
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, 15 * 60)
            results = await pipe.execute()
            
        return results[0]

    async def log_audit_event(
        self, user_id: UUID | None, event_type: str, metadata: dict | None = None
    ) -> AuditLog:
        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            event_metadata=metadata or {},
        )
        self.session.add(audit_log)
        await self.session.flush()
        return audit_log