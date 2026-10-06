from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.chat import ChatMessageResponse, ChatRequest, ChatResponse
from app.services.chat_service import (
    ChatSessionNotFoundError,
    get_chat_messages,
    send_chat_message,
)

router = APIRouter(prefix="/sessions/{session_id}/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def create_chat_message(
    session_id: UUID,
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    try:
        message = send_chat_message(db, session_id, request.message)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding session not found",
        ) from exc
    return ChatResponse(message=message.content)


@router.get("", response_model=list[ChatMessageResponse])
def read_chat_messages(
    session_id: UUID, db: Session = Depends(get_db)
) -> list[ChatMessageResponse]:
    try:
        return get_chat_messages(db, session_id)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding session not found",
        ) from exc
