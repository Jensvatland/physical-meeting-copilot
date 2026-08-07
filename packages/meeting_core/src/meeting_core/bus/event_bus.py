"""In-process event bus for Meeting Core."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from meeting_core.domain.models import MeetingEvent

EventHandler = Callable[[MeetingEvent], Any]


class EventBus:
    """Simple synchronous pub/sub; adapters/agents subscribe without owning media."""

    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []
        self._history: list[MeetingEvent] = []

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    def publish(self, event: MeetingEvent) -> MeetingEvent:
        self._history.append(event)
        for handler in list(self._handlers):
            handler(event)
        return event

    @property
    def history(self) -> list[MeetingEvent]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()
