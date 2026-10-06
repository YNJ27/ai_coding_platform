import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, UpdatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.coding_session import CodingSession


class SessionTestResultStatus(str, enum.Enum):
    pending = "pending"
    passed = "passed"
    failed = "failed"
    error = "error"
    skipped = "skipped"


class SessionTestResult(UUIDPrimaryKeyMixin, UpdatedAtMixin, Base):
    __tablename__ = "session_test_results"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "test_id",
            name="uq_session_test_results_session_test",
        ),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("coding_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_id: Mapped[str] = mapped_column(String(500), nullable=False)
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_file: Mapped[str] = mapped_column(String(500), nullable=False)
    class_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[SessionTestResultStatus] = mapped_column(
        Enum(
            SessionTestResultStatus,
            name="session_test_result_status",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )
    error_type: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    traceback: Mapped[str | None] = mapped_column(Text)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer)

    session: Mapped["CodingSession"] = relationship(
        back_populates="test_results"
    )
