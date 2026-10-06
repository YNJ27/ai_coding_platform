from uuid import uuid4
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.coding_problem import (
    CodingProblem,
    Difficulty,
    ProblemFile,
    TestCase as ProblemTestCase,
)


def _client_with_db(db: Mock) -> TestClient:
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_list_problems_returns_selection_fields() -> None:
    problem = CodingProblem(
        id=uuid4(),
        title="Two Sum",
        slug="two-sum",
        description="Find two numbers.",
        difficulty=Difficulty.easy,
        entry_file="main.py",
    )
    db = Mock()
    db.scalars.return_value.all.return_value = [problem]

    try:
        response = _client_with_db(db).get("/api/problems")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(problem.id),
            "title": "Two Sum",
            "slug": "two-sum",
            "difficulty": "easy",
        }
    ]


def test_problem_detail_excludes_hidden_test_contents() -> None:
    problem = CodingProblem(
        id=uuid4(),
        title="Two Sum",
        slug="two-sum",
        description="Find two numbers.",
        difficulty=Difficulty.easy,
        entry_file="main.py",
        files=[
            ProblemFile(
                id=uuid4(),
                path="main.py",
                content="print('hello')",
                language="python",
                is_entry_file=True,
            )
        ],
        test_cases=[
            ProblemTestCase(
                id=uuid4(),
                input="1 2",
                expected_output="3",
                is_hidden=False,
            ),
            ProblemTestCase(
                id=uuid4(),
                input="secret input",
                expected_output="secret output",
                is_hidden=True,
            ),
        ],
    )
    db = Mock()
    db.scalar.return_value = problem

    try:
        response = _client_with_db(db).get(f"/api/problems/{problem.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["slug"] == "two-sum"
    assert payload["files"][0]["content"] == "print('hello')"
    assert payload["test_cases"] == [
        {
            "id": str(problem.test_cases[0].id),
            "is_hidden": False,
        },
        {
            "id": str(problem.test_cases[1].id),
            "is_hidden": True,
        },
    ]
    assert "input_data" not in payload["test_cases"][1]
    assert "expected_output" not in payload["test_cases"][1]


def test_problem_detail_returns_not_found_for_unknown_problem() -> None:
    db = Mock()
    db.scalar.return_value = None

    try:
        response = _client_with_db(db).get(f"/api/problems/{uuid4()}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Coding problem not found"


def test_problem_detail_discovers_visible_unittest_methods() -> None:
    problem = CodingProblem(
        id=uuid4(),
        title="Battleship",
        slug="battleship",
        description="Sink ships.",
        difficulty=Difficulty.easy,
        entry_file="src/main.py",
        test_files=["src/test_board.py"],
        files=[
            ProblemFile(
                id=uuid4(),
                path="src/test_board.py",
                content=(
                    "import unittest\n\n"
                    "class BoardTest(unittest.TestCase):\n"
                    "    def test_hit(self):\n"
                    "        pass\n\n"
                    "    def test_miss(self):\n"
                    "        pass\n"
                ),
                language="python",
                is_entry_file=False,
            )
        ],
    )
    db = Mock()
    db.scalar.return_value = problem

    try:
        response = _client_with_db(db).get(f"/api/problems/{problem.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["tests"] == [
        {
            "id": "src/test_board.py::BoardTest::test_hit",
            "name": "test_hit",
            "file": "src/test_board.py",
            "class_name": "BoardTest",
        },
        {
            "id": "src/test_board.py::BoardTest::test_miss",
            "name": "test_miss",
            "file": "src/test_board.py",
            "class_name": "BoardTest",
        },
    ]
