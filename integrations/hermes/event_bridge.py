"""Minimal event bridge: Meeting Core → Hermes-oriented callbacks.

No Hermes SDK imports in Meeting Core. This module may later call Hermes APIs.
Includes a sim research vertical slice that does not block transcription.
"""

from __future__ import annotations

import asyncio
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
    "research.started",
    "research.completed",
}


class HermesEventBridge:
    def __init__(
        self,
        on_event: HermesHandler | None = None,
        *,
        auto_research: bool = False,
        research_delay_s: float = 0.01,
    ) -> None:
        self.on_event = on_event or (lambda _payload: None)
        self.forwarded: list[dict[str, Any]] = []
        self.auto_research = auto_research
        self.research_delay_s = research_delay_s
        self._session: MeetingSession | None = None
        self._tasks: list[asyncio.Task[Any]] = []

    def attach(self, session: MeetingSession) -> None:
        self._session = session
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
        if self.auto_research and event.type == "claim.created" and self._session is not None:
            self._schedule_research(event)

    def _schedule_research(self, event: MeetingEvent) -> None:
        session = self._session
        if session is None:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Sync demo path: run research inline without blocking caller long.
            asyncio.run(self._run_research(session, event))
            return
        self._tasks.append(loop.create_task(self._run_research(session, event)))

    async def _run_research(self, session: MeetingSession, event: MeetingEvent) -> None:
        claim_id = (event.payload or {}).get("claim_id")
        job = session.start_research(
            query=f"Verify claim: {event.text}",
            correlation_id=claim_id,
            trigger_event_type=event.type,
        )
        await asyncio.sleep(self.research_delay_s)
        # Simulated background research against pre-meeting prior facts.
        comparison = None
        if claim_id:
            comparison = session.apply_prior_comparison(claim_id)
        summary = "Claim needs verification against prior project sources."
        severity = "info"
        if comparison and comparison.get("suggested_state", "").startswith("CONTRADICTED"):
            summary = "Material claim conflicts with prior project information."
            severity = "high"
        session.complete_research(
            job.research_id,
            result_summary=summary,
            evidence=(comparison or {}).get("evidence") or [{"source": "hermes:sim", "note": summary}],
        )
        finding = session.publish_finding(
            summary,
            detail="Suggested follow-up question prepared for private alert.",
            correlation_id=job.correlation_id,
            severity=severity,
            evidence=[{"research_id": job.research_id}],
        )
        question = "Can you confirm whether this figure matches the prior specification?"
        session.record_question(question, suggested=True)
        await session.speak_private(
            f"{summary} Suggested question: {question}",
            priority=90,
            correlation_id=finding.finding_id,
        )

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
        if event.type.startswith("research"):
            return "research"
        return "context"
