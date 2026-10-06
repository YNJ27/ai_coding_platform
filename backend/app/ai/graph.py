from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app.ai.llm import invoke_llm, system_prompt
from app.ai.prompts import build_user_context
from app.ai.state import AssistantState


def chat_node(state: AssistantState) -> AssistantState:
    messages = [
        SystemMessage(content=system_prompt()),
        HumanMessage(
            content=build_user_context(
                problem_description=state["problem_description"],
                files=state["current_files"],
                history=state["recent_history"],
                current_message=state["current_user_message"],
            )
        ),
    ]
    return {**state, "assistant_response": invoke_llm(messages)}


def build_graph():
    graph = StateGraph(AssistantState)
    graph.add_node("chat", chat_node)
    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)
    return graph.compile()


assistant_graph = build_graph()


def generate_response(
    *,
    message: str,
    problem_description: str,
    files: list[dict[str, str]],
    history: list[dict[str, str]],
) -> str:
    result = assistant_graph.invoke(
        {
            "current_user_message": message,
            "problem_description": problem_description,
            "current_files": files,
            "recent_history": history,
            "assistant_response": "",
        }
    )
    return result["assistant_response"]
