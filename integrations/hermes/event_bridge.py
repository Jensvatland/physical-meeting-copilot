"""Minimal event bridge: Meeting Core → Hermes-oriented callbacks.

No Hermes SDK imports in Meeting Core. This module may later call Hermes APIs.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from meeting_core.domain.models import MeetingEvent
from meeting_core.session import MeetingSession

HermesHandler = Callable[[dict[str, Any]], None]

MATERIAL_TYPES = {
    "claim.created",
    "claim.updated",
    "commitment.recorded",
    "decision.recorded",
    "question.recorded",
    "finding.published",
    "alert.pushed",
    "transcript.final",
}


class HermesEventBridge:
    def __init__(self, on_event: HermesHandler | None = None) -> None:
        self.on_event = on_event or (lambda _payload: None)
        self.forwarded: list[dict[str, Any]] = []

    def attach(self, session: MeetingSession) -> None:
        session.bus.subscribe(self._handle)

    def _handle(self, event: MeetingEvent) -> None:
        if event.type not in MATERIAL_TYPES:
            return
        payload = {
            "host": "hermes",
            "event": event.model_dump(mode="json"),
            "priority_hint": self._priority_hint(event),
        }
        self.forwarded.append(payload)
        self.on_event(payload)

    @staticmethod
    def _priority_hint(event: MeetingEvent) -> str:
        text = (event.text or "").lower()
        for needle, label in [
            ("万元", "price"),
            ("price", "price"),
            ("吨", "number"),
            ("warranty", "warranty"),
            ("质保", "warranty"),
            ("交付", "date"),
            ("september", "date"),
        ]:
            if needle in text:
                return label
        if event.type.startswith("claim"):
            return "claim"
        if event.type.startswith("alert"):
            return "alert"
        return "context"
