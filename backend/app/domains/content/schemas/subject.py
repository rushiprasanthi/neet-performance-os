"""Schemas for Subject resource."""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SubjectCreate(BaseModel):
    """Schema for creating a subject."""

    name: str = Field(..., min_length=1, max_length=255, description="Subject name")
    code: str = Field(..., min_length=1, max_length=50, description="Subject code")
    description: str | None = Field(None, max_length=1000, description="Subject description")

    model_config = ConfigDict(str_strip_whitespace=True)


class SubjectUpdate(BaseModel):
    """Schema for updating a subject."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Subject name")
    code: str | None = Field(None, min_length=1, max_length=50, description="Subject code")
    description: str | None = Field(None, max_length=1000, description="Subject description")

    model_config = ConfigDict(str_strip_whitespace=True)


class SubjectResponse(BaseModel):
    """Schema for subject response."""

    id: UUID
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubjectListResponse(BaseModel):
    """Schema for subject list response."""

    items: list[SubjectResponse]
    total: int
    skip: int
    limit: int