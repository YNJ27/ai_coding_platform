from app.core.base import Base
from app.models import (
    ChatMessage,
    CodingProblem,
    CodingSession,
    ProblemFile,
    SessionFile,
    Submission,
    SessionTestResult,
    TestCase as ProblemTestCase,
    User,
)


def test_core_models_have_uuid_primary_keys() -> None:
    for model in (User, CodingProblem, CodingSession, Submission, SessionTestResult):
        assert model.__table__.c.id.primary_key
        assert str(model.__table__.c.id.type) == "UUID"


def test_expected_tables_are_registered() -> None:
    assert {
        "users",
        "problems",
        "problem_files",
        "test_cases",
        "coding_sessions",
        "session_files",
        "submissions",
        "chat_messages",
        "session_test_results",
    } <= set(Base.metadata.tables)


def test_coding_problem_has_unique_slug() -> None:
    slug = CodingProblem.__table__.c.slug

    assert not slug.nullable
    assert slug.unique


def test_database_columns_match_requested_schema() -> None:
    assert {"language", "is_entry_file"} <= set(ProblemFile.__table__.c.keys())
    assert {"input", "expected_output", "is_hidden"} <= set(ProblemTestCase.__table__.c.keys())
    assert {"language", "updated_at"} <= set(SessionFile.__table__.c.keys())
    assert "created_at" not in SessionFile.__table__.c
    assert {"stdout", "stderr", "execution_time_ms"} <= set(Submission.__table__.c.keys())
    assert {"role", "content", "created_at"} <= set(ChatMessage.__table__.c.keys())
    assert CodingSession.__table__.c.status.nullable is False


def test_session_test_result_schema_has_unique_latest_result_key() -> None:
    columns = SessionTestResult.__table__.c
    assert {
        "session_id",
        "test_id",
        "test_name",
        "test_file",
        "class_name",
        "status",
        "error_type",
        "error_message",
        "traceback",
        "execution_time_ms",
        "updated_at",
    } <= set(columns.keys())
    assert any(
        constraint.name == "uq_session_test_results_session_test"
        for constraint in SessionTestResult.__table__.constraints
    )
    assert any(
        constraint.name == "session_test_result_status"
        for constraint in SessionTestResult.__table__.constraints
    )
