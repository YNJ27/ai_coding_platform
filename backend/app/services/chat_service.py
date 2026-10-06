from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.ai.graph import generate_response
from app.core.config import get_settings
from app.models.coding_session import ChatMessage, CodingSession


class ChatSessionNotFoundError(LookupError):
    pass


def _load_session(db: Session, session_id: UUID) -> CodingSession:
    statement = (
        select(CodingSession)
        .options(
            selectinload(CodingSession.files),
            selectinload(CodingSession.problem),
        )
        .where(CodingSession.id == session_id)
    )
    session = db.scalar(statement)
    if session is None:
        raise ChatSessionNotFoundError(session_id)
    return session


def _complete_turns(messages: list[ChatMessage]) -> list[list[ChatMessage]]:
    turns: list[list[ChatMessage]] = []
    index = 0
    while index < len(messages) - 1:
        user_message = messages[index]
        assistant_message = messages[index + 1]
        if user_message.role == "user" and assistant_message.role == "assistant":
            turns.append([user_message, assistant_message])
            index += 2
        else:
            index += 1
    return turns


def _history_for_context(db: Session, session_id: UUID) -> list[dict[str, str]]:
    messages = list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at, ChatMessage.id)
        ).all()
    )
    turns = _complete_turns(messages)
    turn_limit = get_settings().chat_history_turns
    latest_turns = turns[-turn_limit:] if turn_limit > 0 else []
    return [
        {"role": message.role, "content": message.content}
        for turn in latest_turns
        for message in turn
    ]


def get_chat_messages(db: Session, session_id: UUID) -> list[ChatMessage]:
    _load_session(db, session_id)
    return list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at, ChatMessage.id)
        ).all()
    )


def send_chat_message(db: Session, session_id: UUID, content: str) -> ChatMessage:
    session = _load_session(db, session_id)
    history = _history_for_context(db, session_id)

    response = generate_response(
        message=content,
        problem_description=session.problem.description,
        files=[
            {
                "path": file.path,
                "language": file.language,
                "content": file.content,
            }
            for file in session.files
        ],
        history=history,
    )
    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=content,
    )
    assistant_message = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=response,
    )
    db.add(user_message)
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    return assistant_message
