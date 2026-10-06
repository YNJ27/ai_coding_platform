from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.execution import ExecutionResponse
from app.schemas.sessions import (
    CodingSessionResponse,
    CreateSessionRequest,
    SessionFileResponse,
    UpdateSessionFileRequest,
)
from app.services.session_service import (
    ProblemNotFoundError,
    SessionFileNotFoundError,
    SessionNotFoundError,
    create_session,
    get_session,
    get_session_files,
    update_session_file,
)
from app.services.execution_service import ExecutionError, run_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _session_not_found(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Coding session not found",
    )


@router.post("", response_model=CodingSessionResponse, status_code=status.HTTP_201_CREATED)
def create_coding_session(
    request: CreateSessionRequest, db: Session = Depends(get_db)
) -> CodingSessionResponse:
    try:
        return create_session(db, request.user_id, request.problem_id)
    except ProblemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding problem not found",
        ) from exc


@router.get("/{session_id}", response_model=CodingSessionResponse)
def read_coding_session(
    session_id: UUID, db: Session = Depends(get_db)
) -> CodingSessionResponse:
    try:
        return get_session(db, session_id)
    except SessionNotFoundError as exc:
        raise _session_not_found(exc) from exc


@router.get("/{session_id}/files", response_model=list[SessionFileResponse])
def read_session_files(
    session_id: UUID, db: Session = Depends(get_db)
) -> list[SessionFileResponse]:
    try:
        return get_session_files(db, session_id)
    except SessionNotFoundError as exc:
        raise _session_not_found(exc) from exc


@router.put("/{session_id}/files", response_model=SessionFileResponse)
def save_session_file(
    session_id: UUID,
    request: UpdateSessionFileRequest,
    db: Session = Depends(get_db),
) -> SessionFileResponse:
    try:
        return update_session_file(db, session_id, request.path, request.content)
    except SessionNotFoundError as exc:
        raise _session_not_found(exc) from exc
    except SessionFileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session file not found",
        ) from exc


@router.post("/{session_id}/run", response_model=ExecutionResponse)
def run_coding_session(
    session_id: UUID, db: Session = Depends(get_db)
) -> ExecutionResponse:
    try:
        submission = run_session(db, session_id)
    except ExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(exc) == "Coding session not found"
            else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return ExecutionResponse(
        submission_id=submission.id,
        status=submission.status,
        stdout=submission.stdout,
        stderr=submission.stderr,
        execution_time_ms=submission.execution_time_ms or 0,
    )
