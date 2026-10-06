import sys
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.models.coding_problem import CodingProblem, Difficulty, ProblemFile
from app.models.coding_session import CodingSession, SessionFile, SessionStatus
from app.models.submission import SubmissionStatus
from app.services import execution_service


def _session(source: str, entry_file: str = "src/main.py") -> CodingSession:
    problem = CodingProblem(
        id=uuid4(),
        slug="execution-test",
        title="Execution test",
        description="Test",
        difficulty=Difficulty.easy,
        entry_file=entry_file,
        files=[
            ProblemFile(
                id=uuid4(),
                path="src/main.py",
                content=source,
                language="python",
            )
        ],
    )
    session = CodingSession(
        id=uuid4(),
        user_id=uuid4(),
        problem_id=problem.id,
        status=SessionStatus.active,
        problem=problem,
        files=[
            SessionFile(
                id=uuid4(),
                path="src/main.py",
                content=source,
                language="python",
            )
        ],
    )
    return session


def _db_for(session: CodingSession) -> Mock:
    db = Mock()
    db.scalar.return_value = session
    return db


def test_run_session_executes_entry_file_and_persists_submission(monkeypatch) -> None:
    session = _session("print('line 1\\nline 2')\n")
    db = _db_for(session)
    monkeypatch.setattr(
        execution_service,
        "get_settings",
        lambda: SimpleNamespace(
            python_executable=sys.executable,
            max_execution_time=5,
            max_output_size=1000,
        ),
    )

    submission = execution_service.run_session(db, session.id)

    assert submission.status is SubmissionStatus.passed
    assert submission.stdout.replace("\r\n", "\n") == "line 1\nline 2\n"
    assert submission.stderr == ""
    db.add.assert_called_once_with(submission)
    db.commit.assert_called_once()


def test_run_session_handles_missing_entry_file(monkeypatch) -> None:
    session = _session("print('not used')\n", entry_file="src/missing.py")
    db = _db_for(session)
    monkeypatch.setattr(
        execution_service,
        "get_settings",
        lambda: SimpleNamespace(
            python_executable=sys.executable,
            max_execution_time=5,
            max_output_size=1000,
        ),
    )

    submission = execution_service.run_session(db, session.id)

    assert submission.status is SubmissionStatus.file_not_found
    assert "not found" in submission.stderr


def test_run_session_handles_timeout(monkeypatch) -> None:
    session = _session("while True:\n    pass\n")
    db = _db_for(session)
    monkeypatch.setattr(
        execution_service,
        "get_settings",
        lambda: SimpleNamespace(
            python_executable=sys.executable,
            max_execution_time=0.1,
            max_output_size=1000,
        ),
    )

    submission = execution_service.run_session(db, session.id)

    assert submission.status is SubmissionStatus.timeout


def test_run_session_handles_output_limit(monkeypatch) -> None:
    session = _session("print('0123456789')\n")
    db = _db_for(session)
    monkeypatch.setattr(
        execution_service,
        "get_settings",
        lambda: SimpleNamespace(
            python_executable=sys.executable,
            max_execution_time=5,
            max_output_size=5,
        ),
    )

    submission = execution_service.run_session(db, session.id)

    assert submission.status is SubmissionStatus.output_limit_exceeded
    assert "size limit" in submission.stderr
