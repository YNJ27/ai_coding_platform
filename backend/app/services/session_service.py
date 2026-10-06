from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.coding_problem import CodingProblem
from app.models.coding_session import CodingSession, SessionFile
from app.models.user import User


class ProblemNotFoundError(LookupError):
    pass


class SessionNotFoundError(LookupError):
    pass


class SessionFileNotFoundError(LookupError):
    pass


def _get_session(db: Session, session_id: UUID) -> CodingSession:
    statement = (
        select(CodingSession)
        .options(selectinload(CodingSession.files))
        .where(CodingSession.id == session_id)
    )
    session = db.scalar(statement)
    if session is None:
        raise SessionNotFoundError(session_id)
    return session


def create_session(db: Session, user_id: UUID, problem_id: UUID) -> CodingSession:
    problem = db.scalar(
        select(CodingProblem)
        .options(selectinload(CodingProblem.files))
        .where(CodingProblem.id == problem_id)
    )
    if problem is None:
        raise ProblemNotFoundError(problem_id)

    user = db.get(User, user_id)
    if user is None:
        user = User(id=user_id)
        db.add(user)

    coding_session = CodingSession(user=user, problem=problem)
    trusted_test_files = set(problem.test_files or [])
    coding_session.files = [
        SessionFile(
            path=problem_file.path,
            content=problem_file.content,
            language=problem_file.language,
        )
        for problem_file in problem.files
        if problem_file.path not in trusted_test_files
    ]
    db.add(coding_session)
    db.commit()
    return _get_session(db, coding_session.id)


def get_session(db: Session, session_id: UUID) -> CodingSession:
    return _get_session(db, session_id)


def get_session_files(db: Session, session_id: UUID) -> list[SessionFile]:
    coding_session = _get_session(db, session_id)
    return coding_session.files


def update_session_file(
    db: Session, session_id: UUID, path: str, content: str
) -> SessionFile:
    coding_session = _get_session(db, session_id)
    session_file = next(
        (file for file in coding_session.files if file.path == path), None
    )
    if session_file is None:
        raise SessionFileNotFoundError(path)

    session_file.content = content
    db.commit()
    db.refresh(session_file)
    return session_file
