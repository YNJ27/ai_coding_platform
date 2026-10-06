import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.coding_session import CodingSession


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class CodingProblem(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "problems"

    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, name="difficulty", native_enum=False), nullable=False
    )
    entry_file: Mapped[str] = mapped_column(String(500), nullable=False)
    test_command: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    test_files: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    files: Mapped[list["ProblemFile"]] = relationship(
        back_populates="problem", cascade="all, delete-orphan"
    )
    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="problem", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["CodingSession"]] = relationship(back_populates="problem")


class ProblemFile(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "problem_files"
    __table_args__ = (UniqueConstraint("problem_id", "path"),)

    problem_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True
    )
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="text")
    is_entry_file: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    problem: Mapped[CodingProblem] = relationship(back_populates="files")


class TestCase(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "test_cases"

    problem_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True
    )
    input: Mapped[str] = mapped_column(Text, nullable=False, default="")
    expected_output: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    problem: Mapped[CodingProblem] = relationship(back_populates="test_cases")
