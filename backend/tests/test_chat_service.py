from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.models.coding_problem import CodingProblem, Difficulty
from app.models.coding_session import ChatMessage, CodingSession, SessionFile, SessionStatus
from app.services import chat_service


def _session() -> CodingSession:
    problem = CodingProblem(
        id=uuid4(),
        slug="chat-test",
        title="Chat test",
        description="Explain a simple function.",
        difficulty=Difficulty.easy,
        entry_file="main.py",
    )
    return CodingSession(
        id=uuid4(),
        user_id=uuid4(),
        problem_id=problem.id,
        status=SessionStatus.active,
        problem=problem,
        files=[
            SessionFile(
                id=uuid4(),
                path="main.py",
                content="print('hello')\n",
                language="python",
            )
        ],
    )


def test_send_chat_message_stores_both_messages_and_uses_session_context(monkeypatch):
    session = _session()
    existing_messages = [
        ChatMessage(
            id=uuid4(),
            session_id=session.id,
            role=role,
            content=f"{role}-{index}",
            created_at=datetime(2026, 1, index + 1, tzinfo=timezone.utc),
        )
        for index, role in enumerate(
            ["user", "assistant", "user", "assistant", "user", "assistant"]
        )
    ]
    db = Mock()
    db.scalar.return_value = session
    db.scalars.return_value.all.return_value = existing_messages
    captured = {}

    def fake_generate_response(**kwargs):
        captured.update(kwargs)
        return "Try checking the loop invariant."

    monkeypatch.setattr(chat_service, "generate_response", fake_generate_response)
    monkeypatch.setattr(
        chat_service,
        "get_settings",
        lambda: SimpleNamespace(chat_history_turns=1),
    )

    response = chat_service.send_chat_message(db, session.id, "How do I debug this?")

    assert response.content == "Try checking the loop invariant."
    assert captured["problem_description"] == session.problem.description
    assert captured["files"][0]["content"] == "print('hello')\n"
    assert captured["history"] == [
        {"role": "user", "content": "user-4"},
        {"role": "assistant", "content": "assistant-5"},
    ]
    assert db.add.call_count == 2
    assert db.commit.call_count == 1


def test_incomplete_turn_is_not_sent_as_context(monkeypatch):
    session = _session()
    messages = [
        ChatMessage(
            id=uuid4(),
            session_id=session.id,
            role="user",
            content="unfinished",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    ]
    db = Mock()
    db.scalar.return_value = session
    db.scalars.return_value.all.return_value = messages
    captured = {}
    monkeypatch.setattr(
        chat_service,
        "generate_response",
        lambda **kwargs: captured.update(kwargs) or "response",
    )

    chat_service.send_chat_message(db, session.id, "new message")

    assert captured["history"] == []


def test_only_adjacent_user_assistant_pairs_form_turns(monkeypatch):
    session = _session()
    messages = [
        ChatMessage(
            id=uuid4(),
            session_id=session.id,
            role="user",
            content="incomplete",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ),
        ChatMessage(
            id=uuid4(),
            session_id=session.id,
            role="user",
            content="complete user",
            created_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        ),
        ChatMessage(
            id=uuid4(),
            session_id=session.id,
            role="assistant",
            content="complete assistant",
            created_at=datetime(2026, 1, 3, tzinfo=timezone.utc),
        ),
    ]
    db = Mock()
    db.scalar.return_value = session
    db.scalars.return_value.all.return_value = messages
    captured = {}
    monkeypatch.setattr(
        chat_service,
        "get_settings",
        lambda: SimpleNamespace(chat_history_turns=5),
    )
    monkeypatch.setattr(
        chat_service,
        "generate_response",
        lambda **kwargs: captured.update(kwargs) or "response",
    )

    chat_service.send_chat_message(db, session.id, "current")

    assert captured["history"] == [
        {"role": "user", "content": "complete user"},
        {"role": "assistant", "content": "complete assistant"},
    ]


def test_failed_generation_does_not_persist_an_incomplete_turn(monkeypatch):
    session = _session()
    db = Mock()
    db.scalar.return_value = session
    db.scalars.return_value.all.return_value = []

    def fail_generation(**kwargs):
        raise RuntimeError("model unavailable")

    monkeypatch.setattr(chat_service, "generate_response", fail_generation)

    try:
        chat_service.send_chat_message(db, session.id, "Please help.")
    except RuntimeError:
        pass
    else:
        raise AssertionError("generation failure should be propagated")

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_context_contains_only_latest_configured_complete_turns(monkeypatch):
    session = _session()
    messages = []
    for index in range(6):
        for role in ("user", "assistant"):
            messages.append(
                ChatMessage(
                    id=uuid4(),
                    session_id=session.id,
                    role=role,
                    content=f"{role}-{index}",
                    created_at=datetime(2026, 1, index + 1, tzinfo=timezone.utc),
                )
            )
    db = Mock()
    db.scalar.return_value = session
    db.scalars.return_value.all.return_value = messages
    captured = {}
    monkeypatch.setattr(
        chat_service,
        "get_settings",
        lambda: SimpleNamespace(chat_history_turns=5),
    )
    monkeypatch.setattr(
        chat_service,
        "generate_response",
        lambda **kwargs: captured.update(kwargs) or "response",
    )

    chat_service.send_chat_message(db, session.id, "current")

    assert captured["history"] == [
        {"role": role, "content": f"{role}-{index}"}
        for index in range(1, 6)
        for role in ("user", "assistant")
    ]
    assert len(messages) == 12
