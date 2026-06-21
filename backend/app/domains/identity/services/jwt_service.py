"""JWT Service for token generation and validation."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, Dict, Any
from uuid import UUID

import jwt
import redis.asyncio as redis

from app.config import settings

class JWTService:
    def __init__(self, redis_client: redis.Redis | None = None):
        self.redis = redis_client
        self.secret_key = settings.SECRET_KEY
        self.algorithm = getattr(settings, "ALGORITHM", "HS256")
        self.access_token_expire_minutes = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        self.refresh_token_expire_days = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)

    def create_access_token(self, user_id: UUID, role: str) -> Tuple[str, int]:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {"sub": str(user_id), "role": role, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, self.access_token_expire_minutes * 60

    def validate_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate an access token and return its payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
        except Exception:
            return None

    async def create_refresh_token(self, user_id: UUID) -> Tuple[str, int]:
        if not self.redis:
            raise RuntimeError("Redis client is required for refresh tokens")
        
        token_uuid = str(uuid.uuid4())
        expires_in_seconds = self.refresh_token_expire_days * 24 * 60 * 60
        
        # Map refresh token to user_id
        await self.redis.setex(
            f"refresh:{token_uuid}",
            expires_in_seconds,
            str(user_id)
        )
        
        # Track active tokens per user for secure logout revocation
        await self.redis.sadd(f"user_tokens:{user_id}", token_uuid)
        await self.redis.expire(f"user_tokens:{user_id}", expires_in_seconds)
        
        return token_uuid, expires_in_seconds

    async def validate_refresh_token(self, token_uuid: str) -> Optional[UUID]:
        if not self.redis:
            return None
        user_id_str = await self.redis.get(f"refresh:{token_uuid}")
        if not user_id_str:
            return None
        return UUID(user_id_str.decode('utf-8') if isinstance(user_id_str, bytes) else user_id_str)

    async def rotate_refresh_token(self, old_token_uuid: str) -> Optional[Tuple[str, int]]:
        if not self.redis:
            return None
        
        user_id = await self.validate_refresh_token(old_token_uuid)
        if not user_id:
            return None
        
        # Revoke the old token
        await self.redis.delete(f"refresh:{old_token_uuid}")
        await self.redis.srem(f"user_tokens:{user_id}", old_token_uuid)
        
        # Issue a new token securely
        return await self.create_refresh_token(user_id)

    async def revoke_all_user_tokens(self, user_id: UUID) -> None:
        if not self.redis:
            return
        
        tokens = await self.redis.smembers(f"user_tokens:{user_id}")
        if tokens:
            pipeline = self.redis.pipeline()
            for token in tokens:
                token_str = token.decode('utf-8') if isinstance(token, bytes) else token
                pipeline.delete(f"refresh:{token_str}")
            pipeline.delete(f"user_tokens:{user_id}")
            await pipeline.execute()