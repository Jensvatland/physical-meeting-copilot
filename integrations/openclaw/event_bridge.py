"""OpenClaw event bridge — second reference host, same Meeting Core surface."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from meeting_core.domain.models import MeetingEvent
from meeting_core.session import MeetingSession

OpenClawHandler = Callable[[dict[str, Any]], None]

MATERIAL_TYPES = {
    "claim.created",
    "claim.updated",
    "commitment.recorded",
    "decision.recorded",
    "question.recorded",
    "finding.published",
    "alert.pushed",
    "transcript.final",
    "research.started",
    "research.completed",
    "meeting.exported",
}


class OpenClawEventBridge:
    def __init__(self, on_event: OpenClawHandler | None = None) -> None:
        self.on_event = on_event or (lambda _payload: None)
        self.forwarded: list[dict[str, Any]] = []

    def attach(self, session: MeetingSession) -> None:
        session.bus.subscribe(self._handle)

    def _handle(self, event: MeetingEvent) -> None:
        if event.type not in MATERIAL_TYPES:
            return
        payload = {
            "host": "openclaw",
            "event": event.model_dump(mode="json"),
        }
        self.forwarded.append(payload)
        self.on_event(payload)
