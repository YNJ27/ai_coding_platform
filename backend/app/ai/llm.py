from functools import lru_cache

from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.ai.prompts import SYSTEM_PROMPT
from app.core.config import get_settings


@lru_cache
def get_chat_model() -> ChatGoogleGenerativeAI:
    settings = get_settings()
    if not settings.google_api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured. Add it to the backend environment."
        )
    return ChatGoogleGenerativeAI(
        model=settings.google_model,
        google_api_key=settings.google_api_key,
        temperature=settings.google_temperature,
    )


def invoke_llm(messages: list[BaseMessage]) -> str:
    response = get_chat_model().invoke(messages)
    content = response.content
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") for block in content if isinstance(block, dict)
    )


def system_prompt() -> str:
    return SYSTEM_PROMPT
