from langchain_core.messages import HumanMessage, SystemMessage

from app.ai import graph
from app.ai.prompts import build_user_context


def test_graph_has_single_chat_node() -> None:
    nodes = set(graph.assistant_graph.get_graph().nodes)

    assert nodes == {"__start__", "chat", "__end__"}


def test_chat_node_constructs_ordered_llm_context(monkeypatch) -> None:
    captured = {}

    def fake_invoke(messages):
        captured["messages"] = messages
        return "Use a loop invariant here."

    monkeypatch.setattr(graph, "invoke_llm", fake_invoke)

    state = {
        "current_user_message": "Why does this fail?",
        "problem_description": "Find the first duplicate.",
        "current_files": [
            {"path": "main.py", "language": "python", "content": "print('x')\n"}
        ],
        "recent_history": [
            {"role": "user", "content": "What should I inspect?"},
            {"role": "assistant", "content": "Inspect the loop condition."},
        ],
        "assistant_response": "",
    }

    result = graph.chat_node(state)
    messages = captured["messages"]

    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert messages[0].content.startswith("You are an AI assistant")
    assert messages[1].content == build_user_context(
        problem_description=state["problem_description"],
        files=state["current_files"],
        history=state["recent_history"],
        current_message=state["current_user_message"],
    )
    assert result["assistant_response"] == "Use a loop invariant here."
