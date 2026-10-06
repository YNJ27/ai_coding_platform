from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.submission import SubmissionStatus


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    submission_id: UUID
    status: SubmissionStatus
    stdout: str
    stderr: str
    execution_time_ms: int
