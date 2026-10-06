from typing import TypedDict


class AssistantState(TypedDict):
    current_user_message: str
    problem_description: str
    current_files: list[dict[str, str]]
    recent_history: list[dict[str, str]]
    assistant_response: str
