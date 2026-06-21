"""Service for Subject operations."""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.content.repositories.subject_repository import SubjectRepository
from app.domains.content.models import Subject


class SubjectService:
    """Service for subject business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SubjectRepository(db)

    async def create_subject(self, name: str, code: str, description: str | None = None) -> Subject:
        """Create a new subject with validation."""
        if not name:
            raise ValueError("Subject name cannot be empty")
        if not code:
            raise ValueError("Subject code cannot be empty")
        
        # Check for duplicates
        existing_name = await self.repo.get_by_name(name, active_only=False)
        if existing_name:
            raise ValueError(f"Subject with name '{name}' already exists")
        
        existing_code = await self.repo.get_by_code(code, active_only=False)
        if existing_code:
            raise ValueError(f"Subject with code '{code}' already exists")
        
        return await self.repo.create(name, code, description)

    async def get_subject(self, subject_id: UUID) -> Subject | None:
        """Get subject by ID."""
        return await self.repo.get_by_id(subject_id)

    async def list_subjects(self, skip: int = 0, limit: int = 100) -> tuple[list[Subject], int]:
        """List active subjects."""
        return await self.repo.list(skip=skip, limit=limit, active_only=True)

    async def update_subject(self, subject_id: UUID, update_data: dict) -> Subject | None:
        """Update subject with validation and precise payload parsing."""
        subject = await self.repo.get_by_id(subject_id)
        if not subject:
            return None
        
        # Merge incoming partial data with current database state
        # to protect against repositories that blindly overwrite with kwargs
        name = update_data.get("name", subject.name)
        code = update_data.get("code", subject.code)
        description = update_data.get("description", subject.description)
        
        if "name" in update_data:
            if not name:
                raise ValueError("Subject name cannot be empty")
            if name != subject.name:
                existing = await self.repo.get_by_name(name, active_only=False)
                if existing and existing.id != subject_id:
                    raise ValueError(f"Subject with name '{name}' already exists")
        
        if "code" in update_data:
            if not code:
                raise ValueError("Subject code cannot be empty")
            if code != subject.code:
                existing = await self.repo.get_by_code(code, active_only=False)
                if existing and existing.id != subject_id:
                    raise ValueError(f"Subject with code '{code}' already exists")
        
        return await self.repo.update(subject_id, name, code, description)

    async def deactivate_subject(self, subject_id: UUID) -> Subject | None:
        """Deactivate subject (soft delete)."""
        return await self.repo.deactivate(subject_id)