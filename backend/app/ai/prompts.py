SYSTEM_PROMPT = """You are an AI assistant helping a candidate solve a coding problem.
Assist the candidate while they work. Explain code, identify bugs, suggest improvements,
answer questions about the current code, provide hints when appropriate, and help the
candidate understand the problem. Use the supplied files as your primary code context.
Do not execute code, use tools, browse the web, or make changes autonomously. Prefer
clear explanations and hints over simply giving away a complete solution."""


def format_files(files: list[dict[str, str]]) -> str:
    if not files:
        return "(No session files are currently available.)"
    return "\n\n".join(
        f"--- {file['path']} ({file.get('language', 'text')}) ---\n{file['content']}"
        for file in files
    )


def format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return "(No previous complete conversation turns.)"
    return "\n".join(
        f"{message['role'].upper()}: {message['content']}" for message in history
    )


def build_user_context(
    *,
    problem_description: str,
    files: list[dict[str, str]],
    history: list[dict[str, str]],
    current_message: str,
) -> str:
    return (
        f"PROBLEM DESCRIPTION:\n{problem_description}\n\n"
        f"CURRENT SESSION FILES:\n{format_files(files)}\n\n"
        f"RECENT CONVERSATION:\n{format_history(history)}\n\n"
        f"CURRENT USER MESSAGE:\n{current_message}"
    )
