from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.problems import (
    CodingProblemDetailResponse,
    ProblemSummaryResponse,
    VisibleTestMetadataResponse,
)
from app.services.problem_service import (
    ProblemNotFoundError,
    discover_visible_tests,
    get_problem,
    list_problems,
)

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=list[ProblemSummaryResponse])
def read_problems(db: Session = Depends(get_db)) -> list[ProblemSummaryResponse]:
    return list_problems(db)


@router.get(
    "/{problem_id}",
    response_model=CodingProblemDetailResponse,
)
def read_problem(
    problem_id: UUID, db: Session = Depends(get_db)
) -> CodingProblemDetailResponse:
    try:
        problem = get_problem(db, problem_id)
        response = CodingProblemDetailResponse.model_validate(problem)
        response.tests = [
            VisibleTestMetadataResponse.model_validate(test)
            for test in discover_visible_tests(problem)
        ]
        return response
    except ProblemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding problem not found",
        ) from exc
