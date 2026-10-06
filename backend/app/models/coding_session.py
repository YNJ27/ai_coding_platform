import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import (
    Base,
    CreatedAtMixin,
    TimestampMixin,
    UpdatedAtMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from app.models.coding_problem import CodingProblem
    from app.models.submission import Submission
    from app.models.session_test_result import SessionTestResult
    from app.models.user import User


class SessionStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    abandoned = "abandoned"


class CodingSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "coding_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("problems.id"), nullable=False, index=True
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status", native_enum=False),
        nullable=False,
        default=SessionStatus.active,
    )

    user: Mapped["User"] = relationship(back_populates="sessions")
    problem: Mapped["CodingProblem"] = relationship(back_populates="sessions")
    files: Mapped[list["SessionFile"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    test_results: Mapped[list["SessionTestResult"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class SessionFile(UUIDPrimaryKeyMixin, UpdatedAtMixin, Base):
    __tablename__ = "session_files"
    __table_args__ = (UniqueConstraint("session_id", "path"),)

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("coding_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="text")

    session: Mapped[CodingSession] = relationship(back_populates="files")


class ChatMessage(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("coding_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    session: Mapped[CodingSession] = relationship(back_populates="chat_messages")
