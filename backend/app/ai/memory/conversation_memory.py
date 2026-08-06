"""
Conversation memory service.

Maintains short-term conversation history for each session.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock


@dataclass(slots=True, frozen=True)
class ConversationTurn:
    role: str
    content: str


class ConversationMemory:
    """
    Thread-safe in-memory conversation store.

    Intended for short-term conversational context.
    """

    def __init__(
        self,
        max_history: int = 10,
    ) -> None:
        self._max_history = max_history
        self._memory: dict[str, deque[ConversationTurn]] = defaultdict(
            lambda: deque(maxlen=max_history)
        )
        self._lock = Lock()

    def add_user_message(
        self,
        session_id: str,
        message: str,
    ) -> None:
        with self._lock:
            self._memory[session_id].append(
                ConversationTurn(
                    role="user",
                    content=message,
                )
            )

    def add_assistant_message(
        self,
        session_id: str,
        message: str,
    ) -> None:
        with self._lock:
            self._memory[session_id].append(
                ConversationTurn(
                    role="assistant",
                    content=message,
                )
            )

    def get_history(
        self,
        session_id: str,
    ) -> list[ConversationTurn]:
        with self._lock:
            return list(self._memory[session_id])

    def clear(
        self,
        session_id: str,
    ) -> None:
        with self._lock:
            self._memory.pop(session_id, None)