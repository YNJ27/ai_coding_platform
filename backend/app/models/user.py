import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from app.core.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.coding_session import CodingSession


class User(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "users"

    sessions: Mapped[list["CodingSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
