from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.session_test_result import SessionTestResultStatus


class SessionTestResultUpsertRequest(BaseModel):
    test_id: str = Field(min_length=1, max_length=500)
    test_name: str = Field(min_length=1, max_length=255)
    test_file: str = Field(min_length=1, max_length=500)
    class_name: str | None = Field(default=None, max_length=255)
    status: SessionTestResultStatus
    error_type: str | None = Field(default=None, max_length=100)
    error_message: str | None = None
    traceback: str | None = None
    execution_time_ms: int | None = Field(default=None, ge=0)


class SessionTestResultResponse(SessionTestResultUpsertRequest):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
