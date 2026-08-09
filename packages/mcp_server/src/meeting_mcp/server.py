"""MCP-facing façade over MeetingSessionManager + stdio transport."""

from __future__ import annotations

import json
import os
from typing import Any

from meeting_core.domain.models import ClaimState, MeetingMode
from meeting_core.session import MeetingSession, MeetingSessionManager
from meeting_core.storage.sqlite import SqliteStorageAdapter

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
    "meeting://sessions/{id}/research",
    "meeting://sessions/{id}/primitives",
    "meeting://sessions/{id}/export",
    "meeting://sessions/{id}/pre_meeting",
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
    "meeting.set_pre_meeting_context",
    "meeting.start_research",
    "meeting.complete_research",
    "meeting.export_package",
    "meeting.list_sessions",
    "meeting.search_sessions",
    "meeting.delete_session",
    "meeting.record_consent",
    "meeting.delete_biometrics",
    "meeting.compare_claim",
]


def default_manager() -> MeetingSessionManager:
    path = os.path.expanduser(os.environ.get("MEETING_CORE_DB", ":memory:"))
    return MeetingSessionManager(storage=SqliteStorageAdapter(path))


class MeetingMCPFacade:
    def __init__(self, manager: MeetingSessionManager | None = None) -> None:
        self.manager = manager or default_manager()
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
            "research": [r.model_dump(mode="json") for r in session.state.research],
            "primitives": [p.model_dump(mode="json") for p in session.state.primitives],
            "export": session.export_package(),
            "pre_meeting": session.state.pre_meeting.model_dump(mode="json"),
        }
        if collection not in mapping:
            raise ValueError(f"Unknown collection: {collection}")
        return mapping[collection]

    async def call_tool_async(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        args = arguments or {}
        if name == "meeting.speak_private":
            session = self._require(args.get("session_id"))
            speech = await session.speak_private(
                args["text"],
                priority=int(args.get("priority", 80)),
                language=args.get("language", "en"),
                correlation_id=args.get("correlation_id"),
                interrupt=bool(args.get("interrupt", True)),
            )
            return speech.model_dump(mode="json")
        return self.call_tool(name, args)

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        args = arguments or {}
        if name == "meeting.start_session":
            session = self.manager.create(title=args.get("title"))
            if args.get("pre_meeting"):
                session.set_pre_meeting_context(args["pre_meeting"])
            if args.get("consent_recorded"):
                session.record_consent(recorded=True)
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
                auto_compare=bool(args.get("auto_compare", True)),
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
        if name == "meeting.compare_claim":
            session = self._require(args.get("session_id"))
            return session.apply_prior_comparison(args["claim_id"])
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
            raise RuntimeError("Use call_tool_async for meeting.speak_private")
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
            session.storage.save_session(session.state)
            return session.state.summary()
        if name == "meeting.set_pre_meeting_context":
            session = self._require(args.get("session_id"))
            ctx = session.set_pre_meeting_context(args.get("context") or args)
            return ctx.model_dump(mode="json")
        if name == "meeting.start_research":
            session = self._require(args.get("session_id"))
            job = session.start_research(
                args["query"],
                correlation_id=args.get("correlation_id"),
                trigger_event_type=args.get("trigger_event_type"),
            )
            return job.model_dump(mode="json")
        if name == "meeting.complete_research":
            session = self._require(args.get("session_id"))
            job = session.complete_research(
                args["research_id"],
                result_summary=args["result_summary"],
                evidence=args.get("evidence"),
                failed=bool(args.get("failed", False)),
                stale=bool(args.get("stale", False)),
            )
            return job.model_dump(mode="json")
        if name == "meeting.export_package":
            return self._require(args.get("session_id")).export_package()
        if name == "meeting.list_sessions":
            return self.manager.list_sessions()
        if name == "meeting.search_sessions":
            return self.manager.search_sessions(args["query"])
        if name == "meeting.delete_session":
            sid = args.get("session_id") or self._active_id
            if not sid:
                raise ValueError("session_id required")
            self.manager.delete_session(sid)
            if self._active_id == sid:
                self._active_id = None
            return {"deleted": sid}
        if name == "meeting.record_consent":
            session = self._require(args.get("session_id"))
            session.record_consent(recorded=bool(args.get("recorded", True)))
            return session.state.summary()
        if name == "meeting.delete_biometrics":
            session = self._require(args.get("session_id"))
            cleared = session.delete_biometrics()
            return {"cleared": cleared, "session_id": session.state.session_id}
        if name == "meeting.update_participant":
            session = self._require(args.get("session_id"))
            p = session.update_participant(
                args["participant_id"],
                display_name=args.get("display_name"),
                role=args.get("role"),
                company=args.get("company"),
                seat_position=args.get("seat_position"),
                biometric_consent=args.get("biometric_consent"),
            )
            return p.model_dump(mode="json")
        raise ValueError(f"Unknown tool: {name}")


def build_mcp_server(facade: MeetingMCPFacade | None = None):
    """Build an MCP SDK server exposing Meeting Core tools/resources over stdio."""
    from mcp.server.mcpserver import MCPServer

    facade = facade or MeetingMCPFacade()
    server = MCPServer(
        name="physical-meeting-copilot",
        version="0.1.0",
        instructions="Meeting Core MCP façade — inspect/control structured meeting state.",
    )

    def _json(data: Any) -> str:
        return json.dumps(data, ensure_ascii=False, default=str)

    @server.tool(name="meeting.start_session")
    async def start_session(
        title: str | None = None,
        consent_recorded: bool = False,
        pre_meeting: dict[str, Any] | None = None,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.start_session",
                {"title": title, "consent_recorded": consent_recorded, "pre_meeting": pre_meeting},
            )
        )

    @server.tool(name="meeting.stop_session")
    async def stop_session(session_id: str | None = None) -> str:
        return _json(await facade.call_tool_async("meeting.stop_session", {"session_id": session_id}))

    @server.tool(name="meeting.get_live_state")
    async def get_live_state(session_id: str | None = None) -> str:
        return _json(await facade.call_tool_async("meeting.get_live_state", {"session_id": session_id}))

    @server.tool(name="meeting.get_recent_context")
    async def get_recent_context(session_id: str | None = None, limit: int = 20) -> str:
        return _json(
            await facade.call_tool_async("meeting.get_recent_context", {"session_id": session_id, "limit": limit})
        )

    @server.tool(name="meeting.search_transcript")
    async def search_transcript(query: str, session_id: str | None = None) -> str:
        return _json(
            await facade.call_tool_async("meeting.search_transcript", {"session_id": session_id, "query": query})
        )

    @server.tool(name="meeting.list_speakers")
    async def list_speakers(session_id: str | None = None) -> str:
        return _json(await facade.call_tool_async("meeting.list_speakers", {"session_id": session_id}))

    @server.tool(name="meeting.assign_speaker")
    async def assign_speaker(
        speaker_id: str,
        display_name: str,
        session_id: str | None = None,
        role: str | None = None,
        company: str | None = None,
        seat_position: str | None = None,
        biometric_consent: bool = False,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.assign_speaker",
                {
                    "session_id": session_id,
                    "speaker_id": speaker_id,
                    "display_name": display_name,
                    "role": role,
                    "company": company,
                    "seat_position": seat_position,
                    "biometric_consent": biometric_consent,
                },
            )
        )

    @server.tool(name="meeting.create_claim")
    async def create_claim(
        statement: str,
        session_id: str | None = None,
        original_text: str | None = None,
        speaker_id: str | None = None,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.create_claim",
                {
                    "session_id": session_id,
                    "statement": statement,
                    "original_text": original_text,
                    "speaker_id": speaker_id,
                },
            )
        )

    @server.tool(name="meeting.update_claim")
    async def update_claim(
        claim_id: str,
        state: str,
        session_id: str | None = None,
        evidence: list[dict[str, Any]] | None = None,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.update_claim",
                {"session_id": session_id, "claim_id": claim_id, "state": state, "evidence": evidence},
            )
        )

    @server.tool(name="meeting.publish_finding")
    async def publish_finding(
        summary: str,
        session_id: str | None = None,
        detail: str | None = None,
        correlation_id: str | None = None,
        severity: str = "info",
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.publish_finding",
                {
                    "session_id": session_id,
                    "summary": summary,
                    "detail": detail,
                    "correlation_id": correlation_id,
                    "severity": severity,
                },
            )
        )

    @server.tool(name="meeting.push_private_alert")
    async def push_private_alert(
        text: str,
        session_id: str | None = None,
        priority: int = 50,
        correlation_id: str | None = None,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.push_private_alert",
                {
                    "session_id": session_id,
                    "text": text,
                    "priority": priority,
                    "correlation_id": correlation_id,
                },
            )
        )

    @server.tool(name="meeting.speak_private")
    async def speak_private(
        text: str,
        session_id: str | None = None,
        priority: int = 80,
        language: str = "en",
        correlation_id: str | None = None,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.speak_private",
                {
                    "session_id": session_id,
                    "text": text,
                    "priority": priority,
                    "language": language,
                    "correlation_id": correlation_id,
                },
            )
        )

    @server.tool(name="meeting.set_mode")
    async def set_mode(mode: str, session_id: str | None = None) -> str:
        return _json(await facade.call_tool_async("meeting.set_mode", {"session_id": session_id, "mode": mode}))

    @server.tool(name="meeting.set_language")
    async def set_language(
        session_id: str | None = None,
        target_language: str | None = None,
        source_languages: list[str] | None = None,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.set_language",
                {
                    "session_id": session_id,
                    "target_language": target_language,
                    "source_languages": source_languages,
                },
            )
        )

    @server.tool(name="meeting.set_alert_threshold")
    async def set_alert_threshold(threshold: int, session_id: str | None = None) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.set_alert_threshold", {"session_id": session_id, "threshold": threshold}
            )
        )

    @server.tool(name="meeting.record_commitment")
    async def record_commitment(
        text: str,
        session_id: str | None = None,
        speaker_id: str | None = None,
        due_date: str | None = None,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.record_commitment",
                {"session_id": session_id, "text": text, "speaker_id": speaker_id, "due_date": due_date},
            )
        )

    @server.tool(name="meeting.record_decision")
    async def record_decision(text: str, session_id: str | None = None, speaker_id: str | None = None) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.record_decision", {"session_id": session_id, "text": text, "speaker_id": speaker_id}
            )
        )

    @server.tool(name="meeting.record_question")
    async def record_question(
        text: str,
        session_id: str | None = None,
        suggested: bool = False,
        speaker_id: str | None = None,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.record_question",
                {"session_id": session_id, "text": text, "suggested": suggested, "speaker_id": speaker_id},
            )
        )

    @server.tool(name="meeting.update_participant")
    async def update_participant(
        participant_id: str,
        session_id: str | None = None,
        display_name: str | None = None,
        role: str | None = None,
        company: str | None = None,
        seat_position: str | None = None,
        biometric_consent: bool | None = None,
    ) -> str:
        payload: dict[str, Any] = {"session_id": session_id, "participant_id": participant_id}
        for key, val in {
            "display_name": display_name,
            "role": role,
            "company": company,
            "seat_position": seat_position,
            "biometric_consent": biometric_consent,
        }.items():
            if val is not None:
                payload[key] = val
        return _json(await facade.call_tool_async("meeting.update_participant", payload))

    @server.tool(name="meeting.set_pre_meeting_context")
    async def set_pre_meeting_context(context: dict[str, Any], session_id: str | None = None) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.set_pre_meeting_context", {"session_id": session_id, "context": context}
            )
        )

    @server.tool(name="meeting.start_research")
    async def start_research(
        query: str,
        session_id: str | None = None,
        correlation_id: str | None = None,
        trigger_event_type: str | None = None,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.start_research",
                {
                    "session_id": session_id,
                    "query": query,
                    "correlation_id": correlation_id,
                    "trigger_event_type": trigger_event_type,
                },
            )
        )

    @server.tool(name="meeting.complete_research")
    async def complete_research(
        research_id: str,
        result_summary: str,
        session_id: str | None = None,
        evidence: list[dict[str, Any]] | None = None,
        failed: bool = False,
        stale: bool = False,
    ) -> str:
        return _json(
            await facade.call_tool_async(
                "meeting.complete_research",
                {
                    "session_id": session_id,
                    "research_id": research_id,
                    "result_summary": result_summary,
                    "evidence": evidence,
                    "failed": failed,
                    "stale": stale,
                },
            )
        )

    @server.tool(name="meeting.export_package")
    async def export_package(session_id: str | None = None) -> str:
        return _json(await facade.call_tool_async("meeting.export_package", {"session_id": session_id}))

    @server.tool(name="meeting.list_sessions")
    async def list_sessions() -> str:
        return _json(await facade.call_tool_async("meeting.list_sessions", {}))

    @server.tool(name="meeting.search_sessions")
    async def search_sessions(query: str) -> str:
        return _json(await facade.call_tool_async("meeting.search_sessions", {"query": query}))

    @server.tool(name="meeting.delete_session")
    async def delete_session(session_id: str) -> str:
        return _json(await facade.call_tool_async("meeting.delete_session", {"session_id": session_id}))

    @server.tool(name="meeting.record_consent")
    async def record_consent(session_id: str | None = None, recorded: bool = True) -> str:
        return _json(
            await facade.call_tool_async("meeting.record_consent", {"session_id": session_id, "recorded": recorded})
        )

    @server.tool(name="meeting.delete_biometrics")
    async def delete_biometrics(session_id: str | None = None) -> str:
        return _json(await facade.call_tool_async("meeting.delete_biometrics", {"session_id": session_id}))

    @server.tool(name="meeting.compare_claim")
    async def compare_claim(claim_id: str, session_id: str | None = None) -> str:
        return _json(
            await facade.call_tool_async("meeting.compare_claim", {"session_id": session_id, "claim_id": claim_id})
        )

    @server.resource("meeting://sessions/{session_id}/state")
    async def res_state(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/state"))

    @server.resource("meeting://sessions/{session_id}/transcript")
    async def res_transcript(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/transcript"))

    @server.resource("meeting://sessions/{session_id}/participants")
    async def res_participants(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/participants"))

    @server.resource("meeting://sessions/{session_id}/claims")
    async def res_claims(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/claims"))

    @server.resource("meeting://sessions/{session_id}/commitments")
    async def res_commitments(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/commitments"))

    @server.resource("meeting://sessions/{session_id}/decisions")
    async def res_decisions(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/decisions"))

    @server.resource("meeting://sessions/{session_id}/questions")
    async def res_questions(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/questions"))

    @server.resource("meeting://sessions/{session_id}/findings")
    async def res_findings(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/findings"))

    @server.resource("meeting://sessions/{session_id}/alerts")
    async def res_alerts(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/alerts"))

    @server.resource("meeting://sessions/{session_id}/research")
    async def res_research(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/research"))

    @server.resource("meeting://sessions/{session_id}/primitives")
    async def res_primitives(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/primitives"))

    @server.resource("meeting://sessions/{session_id}/export")
    async def res_export(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/export"))

    @server.resource("meeting://sessions/{session_id}/pre_meeting")
    async def res_pre_meeting(session_id: str) -> str:
        return _json(facade.read_resource(f"meeting://sessions/{session_id}/pre_meeting"))

    return server
