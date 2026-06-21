"""FastAPI dependencies for authentication and authorization."""

from uuid import UUID
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.database import get_db, get_redis
from app.domains.identity.models import User
from app.domains.identity.repositories.user_repository import UserRepository
from app.domains.identity.services.jwt_service import JWTService
from app.domains.identity.services.rbac_service import RBACService

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> User:
    """Get current authenticated user from JWT token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    jwt_service = JWTService(redis_client)
    
    payload = jwt_service.validate_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> User | None:
    """Get current user if provided, otherwise None."""
    if not credentials or not credentials.credentials:
        return None
    
    token = credentials.credentials
    jwt_service = JWTService(redis_client)
    
    payload = jwt_service.validate_access_token(token)
    if not payload:
        return None
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return None
    
    user_repo = UserRepository(db)
    return await user_repo.get_by_id(user_id)


def require_permission(resource: str, action: str):
    """Dependency factory for RBAC endpoint protection."""
    async def wrapper(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        rbac = RBACService(db)
        allowed = await rbac.has_permission(current_user.id, resource, action)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return True

    return wrapper