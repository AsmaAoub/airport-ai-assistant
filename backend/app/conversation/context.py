from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversationContext:
    """
    Stores the state of one conversation.
    """

    conversation_id: str

    history: list[dict[str, Any]] = field(default_factory=list)

    last_language: str = "unknown"

    active_languages: list[str] = field(default_factory=list)

    current_intent: str | None = None

    entities: dict[str, Any] = field(default_factory=dict)