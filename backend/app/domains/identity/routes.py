"""API routes for Identity domain."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import redis.asyncio as redis

from app.config import settings
from app.database import get_db, get_redis
from app.domains.identity.dependencies import get_current_user, get_current_user_optional
from app.domains.identity.models import User, UserRole, Role
from app.domains.identity.schemas import (
    LoginInput, ProfileResponseSchema, UpdateProfileSchema,
    TokenResponse, UserRegisterSchema, UserSafeSchema,
    AuthResponseSchema, UserResponseSchema
)
from app.domains.identity.services.auth_service import AuthService
from app.domains.identity.services.jwt_service import JWTService
from app.domains.identity.services.profile_service import ProfileService
from app.domains.identity.services.rbac_service import RBACService
from app.domains.identity.repositories.user_repository import UserRepository

auth_router = APIRouter()
profile_router = APIRouter()

REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
REFRESH_TOKEN_COOKIE_SECURE = getattr(settings, "environment", "production") == "production"
REFRESH_TOKEN_COOKIE_HTTPONLY = True
REFRESH_TOKEN_COOKIE_SAMESITE = "strict"

@auth_router.post("/register", response_model=AuthResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterSchema, db: AsyncSession = Depends(get_db), redis_client: redis.Redis = Depends(get_redis)):
    try:
        auth_service = AuthService(db, redis_client)
        user = await auth_service.register(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        rbac = RBACService(db)
        await rbac.assign_role(user.id, "student")
        
        # FIX: Validate and map data to Pydantic schema BEFORE committing the transaction.
        # db.commit() expires the SQLAlchemy instance, which causes a MissingGreenletException
        # if attributes are accessed asynchronously afterwards.
        response_data = AuthResponseSchema(
            user=UserResponseSchema.model_validate(user),
            message="Registration successful."
        )

        await db.commit()

        return response_data
    except ValueError as e:
        await db.rollback()
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")
    except Exception as e:
        await db.rollback()
        print(f"Registration Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed due to an internal error.")

@auth_router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginInput, response: Response, db: AsyncSession = Depends(get_db), redis_client: redis.Redis = Depends(get_redis)):
    try:
        auth_service = AuthService(db, redis_client)
        access_token, refresh_token_uuid, expires_in, _ = await auth_service.login(
            email=request.email, password=request.password
        )
        await db.commit()

        response.set_cookie(
            key=REFRESH_TOKEN_COOKIE_NAME, value=refresh_token_uuid,
            httponly=REFRESH_TOKEN_COOKIE_HTTPONLY, secure=REFRESH_TOKEN_COOKIE_SECURE,
            samesite=REFRESH_TOKEN_COOKIE_SAMESITE, max_age=7 * 86400
        )
        
        return {"access_token": access_token, "token_type": "bearer", "expires_in": expires_in}
    except ValueError as e:
        await db.rollback()
        error_msg = str(e)
        if "Email not verified" in error_msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified. Please verify your email first.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    except PermissionError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Account locked due to too many failed login attempts.")
    except Exception as e:
        await db.rollback()
        print(f"Login Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed due to an internal error.")

@auth_router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token_endpoint(request: Request, response: Response, db: AsyncSession = Depends(get_db), redis_client: redis.Redis = Depends(get_redis)):
    refresh_token_uuid = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    
    try:
        jwt_service = JWTService(redis_client)
        result = await jwt_service.rotate_refresh_token(refresh_token_uuid)
        if not result:
            response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
        
        new_token_uuid, expires_in_sec = result
        user_id = await jwt_service.validate_refresh_token(new_token_uuid)

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
        
        user = await UserRepository(db).get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        stmt = select(Role.name).join(UserRole).where(UserRole.user_id == user_id)
        role_result = await db.execute(stmt)
        role_name = role_result.scalar_one_or_none()
        role = role_name if role_name else "user"
        
        access_token, expires_in = jwt_service.create_access_token(user_id, role)
        
        response.set_cookie(
            key=REFRESH_TOKEN_COOKIE_NAME, value=new_token_uuid,
            httponly=REFRESH_TOKEN_COOKIE_HTTPONLY, secure=REFRESH_TOKEN_COOKIE_SECURE,
            samesite=REFRESH_TOKEN_COOKIE_SAMESITE, max_age=expires_in_sec
        )
        return {"access_token": access_token, "token_type": "bearer", "expires_in": expires_in}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Refresh Token Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token refresh failed due to an internal error.")

@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_endpoint(
    request: Request,
    response: Response, 
    redis_client: redis.Redis = Depends(get_redis)
):
    try:
        # Secure logout by reading cookie directly, preventing 500s from expired access tokens
        refresh_token_uuid = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
        if refresh_token_uuid:
            jwt_service = JWTService(redis_client)
            user_id = await jwt_service.validate_refresh_token(refresh_token_uuid)
            if user_id:
                await jwt_service.revoke_all_user_tokens(user_id)
    except Exception as e:
        print(f"Logout Error: {e}")
    finally:
        response.delete_cookie(
            key=REFRESH_TOKEN_COOKIE_NAME,
            httponly=REFRESH_TOKEN_COOKIE_HTTPONLY,
            secure=REFRESH_TOKEN_COOKIE_SECURE,
            samesite=REFRESH_TOKEN_COOKIE_SAMESITE
        )
        return None

@auth_router.get("/me", response_model=UserSafeSchema, status_code=status.HTTP_200_OK)
async def get_me_endpoint(current_user: User = Depends(get_current_user)):
    return UserSafeSchema.model_validate(current_user)

@auth_router.get("/health")
async def identity_health():
    return {"status": "healthy", "domain": "identity"}