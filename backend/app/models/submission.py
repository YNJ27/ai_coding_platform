import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.coding_session import CodingSession


class SubmissionStatus(str, enum.Enum):
    pending = "pending"
    passed = "passed"
    failed = "failed"
    timeout = "timeout"
    file_not_found = "file_not_found"
    output_limit_exceeded = "output_limit_exceeded"
    error = "error"


class Submission(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "submissions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("coding_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status", native_enum=False),
        nullable=False,
    )
    stdout: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stderr: Mapped[str] = mapped_column(Text, nullable=False, default="")
    execution_time_ms: Mapped[int | None] = mapped_column(Integer)

    session: Mapped["CodingSession"] = relationship(back_populates="submissions")
