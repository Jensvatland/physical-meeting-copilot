"""Minimal MCP-facing façade over MeetingSessionManager.

Phase 7 will wire the official MCP SDK transport. This module already exposes
resource/tool handlers for unit tests and Hermes/OpenClaw config.
"""

from __future__ import annotations

from typing import Any

from meeting_core.domain.models import ClaimState, MeetingMode
from meeting_core.session import MeetingSession, MeetingSessionManager

RESOURCE_TEMPLATES = [
    "meeting://sessions/{id}/state",
    "meeting://sessions/{id}/transcript",
    "meeting://sessions/{id}/participants",
    "meeting://sessions/{id}/claims",
    "meeting://sessions/{id}/commitments",
    "meeting://sessions/{id}/decisions",
    "meeting://sessions/{id}/questions",
    "meeting://sessions/{id}/findings",
    "meeting://sessions/{id}/alerts",
]

TOOL_NAMES = [
    "meeting.start_session",
    "meeting.stop_session",
    "meeting.get_live_state",
    "meeting.get_recent_context",
    "meeting.search_transcript",
    "meeting.list_speakers",
    "meeting.assign_speaker",
    "meeting.update_participant",
    "meeting.create_claim",
    "meeting.update_claim",
    "meeting.record_commitment",
    "meeting.record_decision",
    "meeting.record_question",
    "meeting.publish_finding",
    "meeting.push_private_alert",
    "meeting.speak_private",
    "meeting.set_mode",
    "meeting.set_language",
    "meeting.set_alert_threshold",
]


class MeetingMCPFacade:
    def __init__(self, manager: MeetingSessionManager | None = None) -> None:
        self.manager = manager or MeetingSessionManager()
        self._active_id: str | None = None

    def _require(self, session_id: str | None = None) -> MeetingSession:
        sid = session_id or self._active_id
        if not sid:
            raise ValueError("No active session")
        session = self.manager.get(sid)
        if not session:
            raise ValueError(f"Unknown session: {sid}")
        return session

    def read_resource(self, uri: str) -> Any:
        # meeting://sessions/{id}/{collection}
        parts = uri.removeprefix("meeting://sessions/").split("/")
        if len(parts) != 2:
            raise ValueError(f"Unsupported resource URI: {uri}")
        session_id, collection = parts
        session = self._require(session_id)
        mapping = {
            "state": session.state.summary(),
            "transcript": [s.model_dump(mode="json") for s in session.state.transcript],
            "participants": [p.model_dump(mode="json") for p in session.state.participants],
            "claims": [c.model_dump(mode="json") for c in session.state.claims],
            "commitments": [c.model_dump(mode="json") for c in session.state.commitments],
            "decisions": [d.model_dump(mode="json") for d in session.state.decisions],
            "questions": [q.model_dump(mode="json") for q in session.state.questions],
            "findings": [f.model_dump(mode="json") for f in session.state.findings],
            "alerts": [a.model_dump(mode="json") for a in session.state.alerts],
        }
        if collection not in mapping:
            raise ValueError(f"Unknown collection: {collection}")
        return mapping[collection]

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        args = arguments or {}
        if name == "meeting.start_session":
            session = self.manager.create(title=args.get("title"))
            session.start()
            self._active_id = session.state.session_id
            return session.state.summary()
        if name == "meeting.stop_session":
            session = self._require(args.get("session_id"))
            session.stop()
            return session.state.summary()
        if name == "meeting.get_live_state":
            return self._require(args.get("session_id")).state.summary()
        if name == "meeting.get_recent_context":
            return self._require(args.get("session_id")).get_recent_context(limit=int(args.get("limit", 20)))
        if name == "meeting.search_transcript":
            hits = self._require(args.get("session_id")).search_transcript(args["query"])
            return [h.model_dump(mode="json") for h in hits]
        if name == "meeting.list_speakers":
            session = self._require(args.get("session_id"))
            return session.state.speakers
        if name == "meeting.assign_speaker":
            session = self._require(args.get("session_id"))
            p = session.assign_speaker(
                args["speaker_id"],
                display_name=args["display_name"],
                role=args.get("role"),
                company=args.get("company"),
                seat_position=args.get("seat_position"),
                biometric_consent=bool(args.get("biometric_consent", False)),
            )
            return p.model_dump(mode="json")
        if name == "meeting.create_claim":
            session = self._require(args.get("session_id"))
            claim = session.create_claim(
                args["statement"],
                original_text=args.get("original_text"),
                speaker_id=args.get("speaker_id"),
            )
            return claim.model_dump(mode="json")
        if name == "meeting.update_claim":
            session = self._require(args.get("session_id"))
            claim = session.update_claim(
                args["claim_id"],
                state=ClaimState(args["state"]),
                evidence=args.get("evidence"),
            )
            return claim.model_dump(mode="json")
        if name == "meeting.record_commitment":
            session = self._require(args.get("session_id"))
            item = session.record_commitment(
                args["text"], speaker_id=args.get("speaker_id"), due_date=args.get("due_date")
            )
            return item.model_dump(mode="json")
        if name == "meeting.record_decision":
            session = self._require(args.get("session_id"))
            item = session.record_decision(args["text"], speaker_id=args.get("speaker_id"))
            return item.model_dump(mode="json")
        if name == "meeting.record_question":
            session = self._require(args.get("session_id"))
            item = session.record_question(
                args["text"], suggested=bool(args.get("suggested", False)), speaker_id=args.get("speaker_id")
            )
            return item.model_dump(mode="json")
        if name == "meeting.publish_finding":
            session = self._require(args.get("session_id"))
            finding = session.publish_finding(
                args["summary"],
                detail=args.get("detail"),
                correlation_id=args.get("correlation_id"),
                evidence=args.get("evidence"),
                severity=args.get("severity", "info"),
            )
            return finding.model_dump(mode="json")
        if name == "meeting.push_private_alert":
            session = self._require(args.get("session_id"))
            alert = session.push_private_alert(
                args["text"],
                priority=int(args.get("priority", 50)),
                correlation_id=args.get("correlation_id"),
            )
            return alert.model_dump(mode="json")
        if name == "meeting.speak_private":
            session = self._require(args.get("session_id"))
            # Phase 9 wires TTS; for now queue as alert with spoken flag path via event.
            alert = session.push_private_alert(args["text"], priority=int(args.get("priority", 80)))
            return {"queued": True, "alert": alert.model_dump(mode="json")}
        if name == "meeting.set_mode":
            session = self._require(args.get("session_id"))
            session.set_mode(MeetingMode(args["mode"]))
            return session.state.summary()
        if name == "meeting.set_language":
            session = self._require(args.get("session_id"))
            session.set_language(
                target_language=args.get("target_language"),
                source_languages=args.get("source_languages"),
            )
            return session.state.summary()
        if name == "meeting.set_alert_threshold":
            session = self._require(args.get("session_id"))
            session.state.config.alert_threshold = int(args["threshold"])
            return session.state.summary()
        if name == "meeting.update_participant":
            session = self._require(args.get("session_id"))
            participant_id = args["participant_id"]
            p = next(x for x in session.state.participants if x.participant_id == participant_id)
            for key in ("display_name", "role", "company", "seat_position"):
                if key in args:
                    setattr(p, key, args[key])
            if "biometric_consent" in args:
                p.biometric_consent = bool(args["biometric_consent"])
            session.storage.save_session(session.state)
            return p.model_dump(mode="json")
        raise ValueError(f"Unknown tool: {name}")
