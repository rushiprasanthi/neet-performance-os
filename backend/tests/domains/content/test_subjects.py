"""Tests for Subject resource."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.content.schemas.subject import SubjectCreate
from app.domains.content.services.subject_service import SubjectService


@pytest.mark.asyncio
async def test_create_subject(db_session: AsyncSession):
    """Test creating a subject."""
    service = SubjectService(db_session)
    subject = await service.create_subject("Mathematics", "MATH", "Mathematics subject")
    
    assert subject.id is not None
    assert subject.name == "Mathematics"
    assert subject.code == "MATH"
    assert subject.is_active is True


@pytest.mark.asyncio
async def test_create_subject_duplicate_name(db_session: AsyncSession):
    """Test creating a subject with duplicate name."""
    service = SubjectService(db_session)
    await service.create_subject("Mathematics", "MATH")
    
    with pytest.raises(ValueError, match="already exists"):
        await service.create_subject("Mathematics", "MATH2")


@pytest.mark.asyncio
async def test_create_subject_duplicate_code(db_session: AsyncSession):
    """Test creating a subject with duplicate code."""
    service = SubjectService(db_session)
    await service.create_subject("Mathematics", "MATH")
    
    with pytest.raises(ValueError, match="already exists"):
        await service.create_subject("Math", "MATH")


@pytest.mark.asyncio
async def test_get_subject(db_session: AsyncSession):
    """Test getting a subject by ID."""
    service = SubjectService(db_session)
    created = await service.create_subject("Physics", "PHY")
    
    retrieved = await service.get_subject(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "Physics"


@pytest.mark.asyncio
async def test_list_subjects(db_session: AsyncSession):
    """Test listing subjects."""
    service = SubjectService(db_session)
    await service.create_subject("Biology", "BIO")
    await service.create_subject("Chemistry", "CHEM")
    
    subjects, total = await service.list_subjects()
    assert len(subjects) >= 2
    assert total >= 2


@pytest.mark.asyncio
async def test_update_subject(db_session: AsyncSession):
    """Test updating a subject."""
    service = SubjectService(db_session)
    created = await service.create_subject("English", "ENG")
    
    # FIX: Pass the update fields as a dictionary instead of kwargs to match the new Service contract
    updated = await service.update_subject(created.id, {"name": "English Language"})
    assert updated is not None
    assert updated.name == "English Language"


@pytest.mark.asyncio
async def test_deactivate_subject(db_session: AsyncSession):
    """Test deactivating a subject."""
    service = SubjectService(db_session)
    created = await service.create_subject("History", "HIST")
    
    deactivated = await service.deactivate_subject(created.id)
    assert deactivated is not None
    assert deactivated.is_active is False


@pytest.mark.asyncio
async def test_empty_subject_name(db_session: AsyncSession):
    """Test creating subject with empty name."""
    service = SubjectService(db_session)
    
    with pytest.raises(ValueError, match="cannot be empty"):
        await service.create_subject("", "CODE")


def test_subject_schema_whitespace_trimming():
    """Test that whitespace is cleanly stripped at the schema validation boundary."""
    subject = SubjectCreate(name="  Art  ", code="  ART  ", description="  Art class  ")
    
    assert subject.name == "Art"
    assert subject.code == "ART"
    assert subject.description == "Art class"