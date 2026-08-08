"""Deterministic post-meeting package export."""

from __future__ import annotations

from typing import Any

from meeting_core.domain.models import PROTOCOL_VERSION, SessionState, utc_now


def build_post_meeting_package(state: SessionState) -> dict[str, Any]:
    """Stable, structured export for agents and archives."""
    return {
        "protocol_version": PROTOCOL_VERSION,
        "exported_at": utc_now().isoformat(),
        "session": state.summary(),
        "title": state.title,
        "pre_meeting": state.pre_meeting.model_dump(mode="json"),
        "participants": [p.model_dump(mode="json") for p in state.participants],
        "speakers": dict(state.speakers),
        "transcript": [s.model_dump(mode="json") for s in state.transcript],
        "translations": [t.model_dump(mode="json") for t in state.translations],
        "claims": [c.model_dump(mode="json") for c in state.claims],
        "commitments": [c.model_dump(mode="json") for c in state.commitments],
        "decisions": [d.model_dump(mode="json") for d in state.decisions],
        "questions": [q.model_dump(mode="json") for q in state.questions],
        "findings": [f.model_dump(mode="json") for f in state.findings],
        "alerts": [a.model_dump(mode="json") for a in state.alerts],
        "research": [r.model_dump(mode="json") for r in state.research],
        "primitives": [p.model_dump(mode="json") for p in state.primitives],
        "private_speech": [p.model_dump(mode="json") for p in state.private_speech],
        "actions": {
            "open_questions": [q.model_dump(mode="json") for q in state.questions if not q.answered],
            "high_severity_findings": [
                f.model_dump(mode="json") for f in state.findings if f.severity in {"high", "critical"}
            ],
            "commitments": [c.model_dump(mode="json") for c in state.commitments],
        },
    }
