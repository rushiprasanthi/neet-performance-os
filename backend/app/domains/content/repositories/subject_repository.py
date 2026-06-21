"""Repository pattern for Subject model."""

from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.content.models import Subject


class SubjectRepository:
    """Subject repository for database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, subject_id: UUID) -> Subject | None:
        stmt = select(Subject).where(Subject.id == subject_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, active_only: bool = True) -> Subject | None:
        stmt = select(Subject).where(Subject.name == name)
        if active_only:
            stmt = stmt.where(Subject.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str, active_only: bool = True) -> Subject | None:
        stmt = select(Subject).where(Subject.code == code)
        if active_only:
            stmt = stmt.where(Subject.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> tuple[list[Subject], int]:
        stmt = select(Subject)
        count_stmt = select(func.count(Subject.id))
        
        if active_only:
            stmt = stmt.where(Subject.is_active == True)
            count_stmt = count_stmt.where(Subject.is_active == True)
            
        total = await self.session.scalar(count_stmt)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        
        return list(result.scalars().all()), total or 0

    async def create(self, name: str, code: str, description: str | None = None) -> Subject:
        subject = Subject(
            name=name,
            code=code,
            description=description,
            is_active=True
        )
        self.session.add(subject)
        await self.session.flush()
        await self.session.refresh(subject)
        return subject

    async def update(self, subject_id: UUID, name: str | None = None, code: str | None = None, description: str | None = None) -> Subject | None:
        subject = await self.get_by_id(subject_id)
        if not subject:
            return None
            
        if name is not None:
            subject.name = name
        if code is not None:
            subject.code = code
        if description is not None:
            subject.description = description
            
        await self.session.flush()
        await self.session.refresh(subject)
        return subject

    async def deactivate(self, subject_id: UUID) -> Subject | None:
        subject = await self.get_by_id(subject_id)
        if not subject:
            return None
            
        subject.is_active = False
        await self.session.flush()
        await self.session.refresh(subject)
        return subject