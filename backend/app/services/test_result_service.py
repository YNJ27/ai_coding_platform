from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.session_test_result import SessionTestResult
from app.schemas.test_results import SessionTestResultUpsertRequest


def upsert_test_result(
    db: Session,
    session_id: UUID,
    result: SessionTestResultUpsertRequest,
) -> SessionTestResult:
    values = result.model_dump()
    values["session_id"] = session_id
    statement = insert(SessionTestResult).values(**values)
    update_values = {
        key: statement.excluded[key]
        for key in values
        if key not in {"session_id", "test_id"}
    }
    update_values["updated_at"] = func.now()
    statement = statement.on_conflict_do_update(
        constraint="uq_session_test_results_session_test",
        set_=update_values,
    )
    db.execute(statement)
    db.commit()
    return db.scalar(
        select(SessionTestResult).where(
            SessionTestResult.session_id == session_id,
            SessionTestResult.test_id == result.test_id,
        )
    )
