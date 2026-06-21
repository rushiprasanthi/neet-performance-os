"""Content domain models."""

from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, TimestampMixin


class Subject(Base, TimestampMixin):
    """Subject model for course content."""

    __tablename__ = "subjects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index('ix_subjects_name_active', 'name', postgresql_where=text("is_active = true")),
        Index('ix_subjects_code_active', 'code', postgresql_where=text("is_active = true")),
    )

    def __repr__(self) -> str:
        return f"<Subject id={self.id} name={self.name} code={self.code}>"