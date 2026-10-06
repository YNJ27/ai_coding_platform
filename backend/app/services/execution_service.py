from __future__ import annotations

import os
import subprocess
import tempfile
import time
from uuid import UUID, uuid4
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models.coding_problem import CodingProblem
from app.models.coding_session import CodingSession
from app.models.submission import Submission, SubmissionStatus


class ExecutionError(LookupError):
    """Expected execution failure that can be returned through the API."""

    def __init__(self, message: str, status: SubmissionStatus = SubmissionStatus.error):
        super().__init__(message)
        self.status = status


def _load_session(db: Session, session_id: UUID) -> CodingSession:
    statement = (
        select(CodingSession)
        .options(
            selectinload(CodingSession.files),
            selectinload(CodingSession.problem),
        )
        .where(CodingSession.id == session_id)
    )
    session = db.scalar(statement)
    if session is None:
        raise ExecutionError("Coding session not found")
    return session


def _write_session_files(session: CodingSession, workdir: Path) -> None:
    for session_file in session.files:
        relative_path = Path(session_file.path)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ExecutionError(f"Invalid session file path: {session_file.path}")
        target = (workdir / relative_path).resolve()
        if workdir.resolve() not in target.parents:
            raise ExecutionError(f"Invalid session file path: {session_file.path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="") as file:
            file.write(session_file.content)


def _decode_output(value: bytes) -> str:
    if isinstance(value, str):
        return value
    return value.decode("utf-8", errors="replace")


def run_session(db: Session, session_id: UUID) -> Submission:
    session = _load_session(db, session_id)
    settings = get_settings()
    started_at = time.monotonic()
    status = SubmissionStatus.error
    stdout = ""
    stderr = ""

    try:
        with tempfile.TemporaryDirectory(prefix="coding-session-") as temporary_dir:
            workdir = Path(temporary_dir)
            _write_session_files(session, workdir)

            entry_path = Path(session.problem.entry_file)
            if entry_path.is_absolute() or ".." in entry_path.parts:
                raise ExecutionError(
                    "Configured problem entry file is invalid",
                    SubmissionStatus.file_not_found,
                )
            entry_file = (workdir / entry_path).resolve()
            if workdir.resolve() not in entry_file.parents or not entry_file.is_file():
                raise ExecutionError(
                    "Configured problem entry file was not found",
                    SubmissionStatus.file_not_found,
                )

            try:
                completed = subprocess.run(
                    [settings.python_executable, str(entry_path)],
                    cwd=workdir,
                    shell=False,
                    capture_output=True,
                    timeout=settings.max_execution_time,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                stdout = _decode_output(exc.stdout or b"")
                stderr = _decode_output(exc.stderr or b"")
                status = SubmissionStatus.timeout
            except FileNotFoundError as exc:
                raise ExecutionError(
                    "Configured Python executable was not found"
                ) from exc
            else:
                stdout = _decode_output(completed.stdout)
                stderr = _decode_output(completed.stderr)
                if (
                    len(completed.stdout) > settings.max_output_size
                    or len(completed.stderr) > settings.max_output_size
                ):
                    status = SubmissionStatus.output_limit_exceeded
                    stderr = "Execution output exceeded the configured size limit."
                else:
                    status = (
                        SubmissionStatus.passed
                        if completed.returncode == 0
                        else SubmissionStatus.failed
                    )
    except ExecutionError as exc:
        status = exc.status
        stderr = str(exc)
    except Exception as exc:
        status = SubmissionStatus.error
        stderr = f"Unexpected execution error: {exc}"

    execution_time_ms = int((time.monotonic() - started_at) * 1000)
    submission = Submission(
        id=uuid4(),
        session_id=session.id,
        status=status,
        stdout=stdout,
        stderr=stderr,
        execution_time_ms=execution_time_ms,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
