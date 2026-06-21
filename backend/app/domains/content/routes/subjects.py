"""API routes for Subject resource."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.domains.identity.dependencies import require_permission
from app.domains.content.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectListResponse,
)
from app.domains.content.services.subject_service import SubjectService

router = APIRouter(tags=["subjects"])

@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("subject", "create"))])
async def create_subject(request: SubjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new subject."""
    try:
        service = SubjectService(db)
        subject = await service.create_subject(request.name, request.code, request.description)
        await db.commit()
        return subject
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subject with this name or code already exists")
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("", response_model=SubjectListResponse, dependencies=[Depends(require_permission("subject", "read"))])
async def list_subjects(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all active subjects."""
    try:
        service = SubjectService(db)
        subjects, total = await service.list_subjects(skip=skip, limit=limit)
        return {
            "items": subjects,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{subject_id}", response_model=SubjectResponse, dependencies=[Depends(require_permission("subject", "read"))])
async def get_subject(subject_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a subject by ID."""
    try:
        service = SubjectService(db)
        subject = await service.get_subject(subject_id)
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        return subject
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.patch("/{subject_id}", response_model=SubjectResponse, dependencies=[Depends(require_permission("subject", "update"))])
async def update_subject(subject_id: UUID, request: SubjectUpdate, db: AsyncSession = Depends(get_db)):
    """Update a subject."""
    try:
        service = SubjectService(db)
        
        # Only extract fields that the client explicitly included in the request
        update_data = request.model_dump(exclude_unset=True)
        
        if not update_data:
            subject = await service.get_subject(subject_id)
            if not subject:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
            return subject
            
        subject = await service.update_subject(subject_id, update_data)
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
            
        await db.commit()
        return subject
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subject with this name or code already exists")
    except HTTPException:
        await db.rollback()
        raise
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("subject", "delete"))])
async def deactivate_subject(subject_id: UUID, db: AsyncSession = Depends(get_db)):
    """Deactivate (soft delete) a subject."""
    try:
        service = SubjectService(db)
        subject = await service.deactivate_subject(subject_id)
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        await db.commit()
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")