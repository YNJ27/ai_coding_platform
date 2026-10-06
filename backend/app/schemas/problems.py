from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.coding_problem import Difficulty


class ProblemFileBase(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str = ""
    language: str = Field(min_length=1, max_length=50)
    is_entry_file: bool = False


class ProblemFileResponse(ProblemFileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class TestCaseMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_hidden: bool = False


class VisibleTestMetadataResponse(BaseModel):
    id: str
    name: str
    file: str
    class_name: str


class ProblemSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    difficulty: Difficulty


class CodingProblemDetailResponse(ProblemSummaryResponse):
    model_config = ConfigDict(from_attributes=True)

    description: str
    entry_file: str
    files: list[ProblemFileResponse] = Field(default_factory=list)
    test_cases: list[TestCaseMetadataResponse] = Field(default_factory=list)
    tests: list[VisibleTestMetadataResponse] = Field(default_factory=list)
