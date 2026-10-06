from uuid import uuid4
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.coding_session import CodingSession, SessionFile, SessionStatus
from app.schemas.sessions import CodingSessionResponse


def test_get_session_files_returns_exact_content() -> None:
    session_id = uuid4()
    session_file = SessionFile(
        id=uuid4(),
        session_id=session_id,
        path="src/main.py",
        content="def main():\n\treturn 1\n",
        language="python",
    )
    db = Mock()
    db.scalar.return_value = CodingSession(
        id=session_id,
        user_id=uuid4(),
        problem_id=uuid4(),
        status=SessionStatus.active,
        files=[session_file],
    )

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get(f"/api/sessions/{session_id}/files")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["content"] == "def main():\n\treturn 1\n"


def test_session_file_update_returns_not_found_for_missing_file() -> None:
    db = Mock()
    db.scalar.return_value = CodingSession(
        id=uuid4(),
        user_id=uuid4(),
        problem_id=uuid4(),
        status=SessionStatus.active,
        files=[],
    )
    session_id = db.scalar.return_value.id

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).put(
            f"/api/sessions/{session_id}/files",
            json={"path": "missing.py", "content": "unchanged\n"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Session file not found"


def test_session_response_exposes_session_id() -> None:
    session = CodingSession(
        id=uuid4(),
        user_id=uuid4(),
        problem_id=uuid4(),
        status=SessionStatus.active,
        files=[],
    )

    response = CodingSessionResponse.model_validate(session)

    assert response.session_id == session.id
    assert response.model_dump(by_alias=True)["session_id"] == session.id
