"""Seed coding problems from a JSON manifest.

The manifest supports either inline files or a directory tree:

{
  "slug": "friend-recommender",
  "title": "Friend Recommender",
  "difficulty": "medium",
  "description": "...",
  "entry_file": "src/main.py",
  "files_dir": "friend-recommender"
}

Every regular file below ``files_dir`` becomes a problem_file with its
relative POSIX path. Files may also be supplied as objects with ``path``,
``content``, ``language``, and ``is_entry_file`` fields.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, create_tables
from app.models.coding_problem import CodingProblem, Difficulty, ProblemFile, TestCase

LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".go": "go",
    ".rs": "rust",
    ".json": "json",
    ".md": "markdown",
}


def _safe_relative_path(value: str) -> str:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"Problem file path must be relative and safe: {value}")
    return path.as_posix()


def _language_for(path: str) -> str:
    return LANGUAGE_BY_SUFFIX.get(Path(path).suffix.lower(), "text")


def _read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as file:
        return file.read()


def _files_from_directory(
    problem: dict[str, Any], manifest_dir: Path
) -> list[dict[str, Any]]:
    files_dir = manifest_dir / problem["files_dir"]
    if not files_dir.is_dir():
        raise FileNotFoundError(f"Problem files directory not found: {files_dir}")
    files = []
    for path in sorted(file for file in files_dir.rglob("*") if file.is_file()):
        relative_path = path.relative_to(files_dir).as_posix()
        files.append(
            {
                "path": _safe_relative_path(relative_path),
                "content": _read_text(path),
                "language": _language_for(relative_path),
                "is_entry_file": relative_path == problem["entry_file"],
            }
        )
    return files


def _problem_files(problem: dict[str, Any], manifest_dir: Path) -> list[dict[str, Any]]:
    if "files_dir" in problem:
        return _files_from_directory(problem, manifest_dir)
    files = []
    for item in problem.get("files", []):
        path = _safe_relative_path(item["path"])
        files.append(
            {
                "path": path,
                "content": item.get("content", ""),
                "language": item.get("language", _language_for(path)),
                "is_entry_file": item.get("is_entry_file", path == problem["entry_file"]),
            }
        )
    return files


def seed_problem(db: Session, problem_data: dict[str, Any], manifest_dir: Path) -> CodingProblem:
    slug = problem_data.get("slug") or problem_data["id"]
    problem = db.scalar(select(CodingProblem).where(CodingProblem.slug == slug))
    if problem is None:
        problem = CodingProblem(slug=slug)
        db.add(problem)

    problem.title = problem_data.get("title") or problem_data["name"]
    problem.description = problem_data["description"]
    problem.difficulty = Difficulty(problem_data["difficulty"].lower())
    problem.entry_file = _safe_relative_path(problem_data["entry_file"])
    problem.test_command = problem_data.get("test_command", "")
    problem.test_files = [
        _safe_relative_path(path) for path in problem_data.get("test_files", [])
    ]
    files = _problem_files(problem_data, manifest_dir)
    problem.files.clear()
    db.flush()
    problem.files = [
        ProblemFile(
            path=file["path"],
            content=file["content"],
            language=file["language"],
            is_entry_file=file["is_entry_file"],
        )
        for file in files
    ]
    problem.test_cases = [
        TestCase(
            input=item.get("input", ""),
            expected_output=item.get("expected_output", ""),
            is_hidden=item.get("is_hidden", False),
        )
        for item in problem_data.get("test_cases", [])
    ]
    return problem


def seed_manifest(manifest_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems = manifest["problems"] if isinstance(manifest, dict) else manifest
    create_tables()
    with SessionLocal() as db:
        for problem in problems:
            seed_problem(db, problem, manifest_path.parent)
        db.commit()
    return len(problems)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed coding problems from JSON.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).parents[1] / "seed_data" / "problems.json",
    )
    args = parser.parse_args()
    count = seed_manifest(args.manifest.resolve())
    print(f"Seeded {count} problems.")


if __name__ == "__main__":
    main()
