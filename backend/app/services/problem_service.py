import ast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.coding_problem import CodingProblem


def discover_visible_tests(problem: CodingProblem) -> list[dict[str, str]]:
    files_by_path = {problem_file.path: problem_file for problem_file in problem.files}
    tests: list[dict[str, str]] = []
    for file_path in problem.test_files or []:
        problem_file = files_by_path.get(file_path)
        if problem_file is None or not file_path.endswith(".py"):
            continue
        tree = ast.parse(problem_file.content, filename=file_path)
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or not _is_test_case_class(node):
                continue
            for method in node.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if method.name.startswith("test_"):
                        tests.append(
                            {
                                "id": f"{file_path}::{node.name}::{method.name}",
                                "name": method.name,
                                "file": file_path,
                                "class_name": node.name,
                            }
                        )
    return tests


def _is_test_case_class(node: ast.ClassDef) -> bool:
    return any(
        isinstance(base, ast.Name) and base.id == "TestCase"
        or isinstance(base, ast.Attribute) and base.attr == "TestCase"
        for base in node.bases
    )


class ProblemNotFoundError(LookupError):
    """Raised when a requested coding problem does not exist."""


def list_problems(db: Session) -> list[CodingProblem]:
    statement = select(CodingProblem).order_by(CodingProblem.title)
    return list(db.scalars(statement).all())


def get_problem_by_slug(db: Session, slug: str) -> CodingProblem:
    statement = select(CodingProblem).where(CodingProblem.slug == slug)
    problem = db.scalar(statement)
    if problem is None:
        raise ProblemNotFoundError(slug)
    return problem


def get_problem(db: Session, problem_id: UUID) -> CodingProblem:
    statement = (
        select(CodingProblem)
        .options(
            selectinload(CodingProblem.files),
            selectinload(CodingProblem.test_cases),
        )
        .where(CodingProblem.id == problem_id)
    )
    problem = db.scalar(statement)
    if problem is None:
        raise ProblemNotFoundError(problem_id)
    return problem
