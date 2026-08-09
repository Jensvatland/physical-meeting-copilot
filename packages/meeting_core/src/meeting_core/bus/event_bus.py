"""In-process event bus for Meeting Core."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from meeting_core.domain.models import MeetingEvent

EventHandler = Callable[[MeetingEvent], Any]

logger = logging.getLogger(__name__)


class EventBus:
    """Simple synchronous pub/sub; adapters/agents subscribe without owning media."""

    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []
        self._history: list[MeetingEvent] = []
        self.handler_errors: list[str] = []

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    def publish(self, event: MeetingEvent) -> MeetingEvent:
        self._history.append(event)
        for handler in list(self._handlers):
            try:
                handler(event)
            except Exception as exc:  # noqa: BLE001 — isolate subscriber failures
                detail = f"{handler!r}: {exc}"
                self.handler_errors.append(detail)
                logger.exception("EventBus handler failed for %s", event.type)
        return event

    @property
    def history(self) -> list[MeetingEvent]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()
