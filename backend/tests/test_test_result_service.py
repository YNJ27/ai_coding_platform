from uuid import uuid4

from sqlalchemy.dialects.postgresql import dialect

from app.models.session_test_result import SessionTestResultStatus
from app.schemas.test_results import SessionTestResultUpsertRequest
from app.services.test_result_service import upsert_test_result


def test_upsert_test_result_uses_session_test_conflict_key() -> None:
    captured = {}

    class FakeDb:
        def execute(self, statement):
            captured["statement"] = statement

        def commit(self):
            pass

        def scalar(self, statement):
            return "stored-result"

    result = SessionTestResultUpsertRequest(
        test_id="src/test_board.py::BoardTest::test_hit",
        test_name="test_hit",
        test_file="src/test_board.py",
        class_name="BoardTest",
        status=SessionTestResultStatus.passed,
        execution_time_ms=4,
    )

    stored = upsert_test_result(FakeDb(), uuid4(), result)

    sql = str(captured["statement"].compile(dialect=dialect()))
    assert (
        "ON CONFLICT ON CONSTRAINT uq_session_test_results_session_test DO UPDATE"
        in sql
    )
    assert stored == "stored-result"
