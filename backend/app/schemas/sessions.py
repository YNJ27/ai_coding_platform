from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.coding_session import SessionStatus


class CreateSessionRequest(BaseModel):
    user_id: UUID
    problem_id: UUID


class SessionFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    path: str
    content: str
    language: str


class CodingSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID = Field(validation_alias="id", serialization_alias="session_id")
    user_id: UUID
    problem_id: UUID
    status: SessionStatus
    files: list[SessionFileResponse] = Field(default_factory=list)


class UpdateSessionFileRequest(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str
