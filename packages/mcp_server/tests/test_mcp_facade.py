"""Phase 7-oriented MCP façade tests (mock agent)."""

from __future__ import annotations

from meeting_mcp.server import RESOURCE_TEMPLATES, TOOL_NAMES, MeetingMCPFacade


def test_tool_surface_matches_protocol() -> None:
    assert "meeting.start_session" in TOOL_NAMES
    assert "meeting.push_private_alert" in TOOL_NAMES
    assert "meeting.delete_biometrics" in TOOL_NAMES
    assert any(t.endswith("/transcript") for t in RESOURCE_TEMPLATES)


def test_mock_agent_can_inspect_and_control_state() -> None:
    mcp = MeetingMCPFacade()
    started = mcp.call_tool("meeting.start_session", {"title": "Dinner", "consent_recorded": True})
    sid = started["session_id"]

    # Simulate ASR via core through a side channel: inject via manager session.
    session = mcp.manager.get(sid)
    assert session is not None
    session.add_transcript("价格是一百万元", speaker_id="spk_1", language="zh-CN")
    mcp.call_tool(
        "meeting.assign_speaker",
        {"session_id": sid, "speaker_id": "spk_1", "display_name": "Wang", "company": "SteelCo"},
    )
    claim = mcp.call_tool(
        "meeting.create_claim",
        {"session_id": sid, "statement": "Price is 1,000,000 RMB", "speaker_id": "spk_1"},
    )
    mcp.call_tool(
        "meeting.publish_finding",
        {"session_id": sid, "summary": "Verify quoted price", "correlation_id": claim["claim_id"]},
    )
    alert = mcp.call_tool(
        "meeting.push_private_alert",
        {"session_id": sid, "text": "Confirm whether price includes VAT.", "priority": 70},
    )

    state = mcp.read_resource(f"meeting://sessions/{sid}/state")
    transcript = mcp.read_resource(f"meeting://sessions/{sid}/transcript")
    claims = mcp.read_resource(f"meeting://sessions/{sid}/claims")
    alerts = mcp.read_resource(f"meeting://sessions/{sid}/alerts")

    assert state["transcript_segments"] == 1
    assert transcript[0]["text"] == "价格是一百万元"
    assert claims[0]["statement"] == "Price is 1,000,000 RMB"
    assert alerts[0]["alert_id"] == alert["alert_id"]

    cleared = mcp.call_tool("meeting.delete_biometrics", {"session_id": sid})
    assert cleared["cleared"] == 0
    try:
        mcp.call_tool("meeting.update_participant", {"session_id": sid, "participant_id": "missing"})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "Unknown participant_id" in str(exc)

    stopped = mcp.call_tool("meeting.stop_session", {"session_id": sid})
    assert stopped["status"] == "ENDED"
