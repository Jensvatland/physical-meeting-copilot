"""MCP façade expansion + stdio server construction."""

from __future__ import annotations

import asyncio

from meeting_mcp.server import TOOL_NAMES, MeetingMCPFacade, build_mcp_server


def test_new_tools_present() -> None:
    for name in (
        "meeting.export_package",
        "meeting.start_research",
        "meeting.set_pre_meeting_context",
        "meeting.list_sessions",
        "meeting.speak_private",
    ):
        assert name in TOOL_NAMES


def test_export_and_research_tools() -> None:
    async def _run() -> None:
        mcp = MeetingMCPFacade()
        started = mcp.call_tool(
            "meeting.start_session",
            {
                "title": "MCP dinner",
                "consent_recorded": True,
                "pre_meeting": {"prior_facts": [{"topic": "price", "value": 800000}]},
            },
        )
        sid = started["session_id"]
        session = mcp.manager.get(sid)
        assert session is not None
        session.add_transcript("价格是一百万元", speaker_id="spk_1", language="zh-CN")
        claim = mcp.call_tool(
            "meeting.create_claim",
            {"session_id": sid, "statement": "Price is 1000000 RMB", "speaker_id": "spk_1"},
        )
        job = mcp.call_tool(
            "meeting.start_research",
            {"session_id": sid, "query": "verify price", "correlation_id": claim["claim_id"]},
        )
        mcp.call_tool(
            "meeting.complete_research",
            {
                "session_id": sid,
                "research_id": job["research_id"],
                "result_summary": "Price above prior budget",
                "evidence": [{"source": "prior_facts"}],
            },
        )
        speech = await mcp.call_tool_async(
            "meeting.speak_private",
            {"session_id": sid, "text": "Confirm VAT inclusion", "priority": 85},
        )
        package = mcp.call_tool("meeting.export_package", {"session_id": sid})
        assert package["session"]["research_jobs"] == 1
        assert speech["spoken"] is True
        research = mcp.read_resource(f"meeting://sessions/{sid}/research")
        assert research[0]["status"] == "COMPLETED"

    asyncio.run(_run())


def test_build_stdio_server() -> None:
    server = build_mcp_server(MeetingMCPFacade())
    assert server.name == "physical-meeting-copilot"
