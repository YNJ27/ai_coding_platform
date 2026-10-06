from unittest.mock import Mock

from scripts.seed_problems import _problem_files, _safe_relative_path, seed_problem


def test_safe_relative_paths_and_recursive_file_loading(tmp_path) -> None:
    files_root = tmp_path / "friend"
    (files_root / "data").mkdir(parents=True)
    (files_root / "src").mkdir()
    (files_root / "data" / "users.txt").write_text("a\tb\n", encoding="utf-8", newline="")
    (files_root / "src" / "main.py").write_text("print(1)\n", encoding="utf-8", newline="")

    problem = {
        "entry_file": "src/main.py",
        "files_dir": "friend",
    }
    files = _problem_files(problem, tmp_path)

    assert [item["path"] for item in files] == ["data/users.txt", "src/main.py"]
    assert files[0]["content"] == "a\tb\n"
    assert files[1]["is_entry_file"] is True


def test_unsafe_seed_path_is_rejected() -> None:
    try:
        _safe_relative_path("../outside.py")
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe paths must be rejected")


def test_reseeding_flushes_old_files_before_replacing_same_path() -> None:
    existing_problem = Mock()
    existing_problem.slug = "friend-recommender"
    existing_problem.files = [Mock(path="data/users_huge.txt")]
    existing_problem.test_cases = []
    db = Mock()
    db.scalar.return_value = existing_problem

    seed_problem(
        db,
        {
            "slug": "friend-recommender",
            "title": "Friend Recommender",
            "difficulty": "medium",
            "description": "Rank friends.",
            "entry_file": "src/main.py",
            "files": [
                {
                    "path": "data/users_huge.txt",
                    "content": "updated\n",
                    "language": "text",
                }
            ],
        },
        __import__("pathlib").Path("."),
    )

    db.flush.assert_called_once()
    assert existing_problem.files[0].content == "updated\n"


def test_seed_problem_stores_trusted_test_file_configuration() -> None:
    problem = Mock()
    problem.slug = "battleship"
    problem.files = []
    problem.test_cases = []
    db = Mock()
    db.scalar.return_value = problem

    seed_problem(
        db,
        {
            "id": "battleship",
            "name": "Battleship",
            "difficulty": "easy",
            "language": "python",
            "description": "Sink ships.",
            "entry_file": "src/main.py",
            "test_command": "python -m unittest",
            "test_files": ["src/test_board.py"],
            "files": [],
        },
        __import__("pathlib").Path("."),
    )

    assert problem.test_command == "python -m unittest"
    assert problem.test_files == ["src/test_board.py"]
