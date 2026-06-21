"""Pydantic schemas for Identity domain."""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class ProfileSchema(BaseModel):
    """Profile data."""
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    target_score: int | None = Field(None, ge=0, le=720)
    target_exam_year: int | None = None
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=1000)
    preferred_subjects: list[str] | None = None
    study_hours_per_day: float | None = Field(None, ge=0, le=24)

    @field_validator('preferred_subjects')
    @classmethod
    def validate_subjects(cls, v):
        if v:
            allowed = {'Physics', 'Chemistry', 'Biology'}
            if not all(s in allowed for s in v):
                raise ValueError('Subjects must be Physics, Chemistry, or Biology')
        return v

    model_config = ConfigDict(from_attributes=True)


class UpdateProfileSchema(BaseModel):
    """Profile update request."""
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    target_score: int | None = Field(None, ge=0, le=720)
    target_exam_year: int | None = None
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=1000)
    preferred_subjects: list[str] | None = None
    study_hours_per_day: float | None = Field(None, ge=0, le=24)

    @field_validator('preferred_subjects')
    @classmethod
    def validate_subjects(cls, v):
        if v:
            allowed = {'Physics', 'Chemistry', 'Biology'}
            if not all(s in allowed for s in v):
                raise ValueError('Subjects must be Physics, Chemistry, or Biology')
        return v

    model_config = ConfigDict(from_attributes=True)


class ProfileResponseSchema(ProfileSchema):
    """Profile response."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRegisterSchema(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str | None = None
    last_name: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@neet.com",
                "password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe",
            }
        }
    )


class UserResponseSchema(BaseModel):
    """User response (without sensitive data)."""
    id: UUID
    email: str
    status: str
    email_verified: bool
    profile: ProfileResponseSchema | None = None

    model_config = ConfigDict(from_attributes=True)


class AuthResponseSchema(BaseModel):
    """Authentication response."""
    user: UserResponseSchema
    message: str = "Registration successful. Please verify your email."

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "student@neet.com",
                    "status": "pending",
                    "email_verified": False,
                    "profile": {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "first_name": "John",
                        "last_name": "Doe",
                        "target_score": None,
                        "target_year": None,
                        "avatar_url": None,
                    },
                },
                "message": "Registration successful. Please verify your email.",
            }
        }
    )


class LoginInput(BaseModel):
    """Login request."""
    email: EmailStr
    password: str = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@neet.com",
                "password": "SecurePassword123!",
            }
        }
    )


class TokenResponse(BaseModel):
    """Token response after successful login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
            }
        }
    )


class UserSafeSchema(BaseModel):
    """Safe user data (no sensitive fields)."""
    id: UUID
    email: str
    status: str
    email_verified: bool
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)