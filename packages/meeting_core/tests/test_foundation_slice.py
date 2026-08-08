"""Vertical-slice tests for phases 4–19 foundation."""

from __future__ import annotations

import asyncio

from meeting_core.adapters.diarization.sim import SimulatedDiarizationAdapter
from meeting_core.adapters.tts.sim import SimulatedTextToSpeechAdapter
from meeting_core.domain.models import ClaimState
from meeting_core.eval.harness import run_eval
from meeting_core.intelligence.export import build_post_meeting_package
from meeting_core.reliability.health import aggregate_health
from meeting_core.session import MeetingSession, MeetingSessionManager
from meeting_core.storage.sqlite import SqliteStorageAdapter


def test_pre_meeting_contradiction_and_export() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"), title="Factory visit")
    session.set_pre_meeting_context(
        {
            "prior_facts": [{"topic": "capacity", "value": 4200, "unit": "tons"}],
            "watch_items": ["capacity"],
            "goals": ["Validate capacity"],
        }
    )
    session.start()
    session.add_transcript("额定容量是五千吨", speaker_id="spk_1", language="zh-CN")
    claim = session.create_claim("Rated capacity is 5000 tons", speaker_id="spk_1")
    assert claim.state == ClaimState.CONTRADICTED_PROJECT_SOURCE
    assert session.state.primitives
    package = session.export_package()
    assert package["session"]["claims"] == 1
    assert "actions" in package
    assert build_post_meeting_package(session.state)["protocol_version"]


def test_research_and_private_speech_lifecycle() -> None:
    async def _run() -> None:
        session = MeetingSession(storage=SqliteStorageAdapter(":memory:"), tts=SimulatedTextToSpeechAdapter())
        session.start()
        job = session.start_research("check warranty", correlation_id="c1", trigger_event_type="claim.created")
        session.complete_research(job.research_id, result_summary="ok", evidence=[{"source": "sim"}])
        speech = await session.speak_private("Ask about warranty terms", priority=90, correlation_id=job.correlation_id)
        assert speech.spoken is True
        assert any(e.type == "private_speech.spoken" for e in session.bus.history)
        assert any(e.type == "research.completed" for e in session.bus.history)

    asyncio.run(_run())


def test_session_history_search_and_delete() -> None:
    mgr = MeetingSessionManager(storage=SqliteStorageAdapter(":memory:"))
    a = mgr.create(title="Dinner Beijing")
    a.start()
    a.add_transcript("价格是一百万元", speaker_id="spk_1", language="zh-CN")
    a.stop()
    b = mgr.create(title="Other")
    b.start()
    b.add_transcript("hello", speaker_id="spk_1", language="en")
    hits = mgr.search_sessions("一百万元")
    assert any(h["session_id"] == a.state.session_id for h in hits)
    mgr.delete_session(a.state.session_id)
    assert mgr.get(a.state.session_id) is None


def test_diarization_and_health() -> None:
    async def _run() -> None:
        d = SimulatedDiarizationAdapter(speaker_count=4)
        # loud-ish PCM16 silence-ish but non-zero
        pcm = b"\x00\x10" * 800
        label = await d.label(pcm)
        assert label["speaker_id"].startswith("spk_")
        health = aggregate_health({"diarization": d, "tts": SimulatedTextToSpeechAdapter()})
        assert health["overall"] == "ok"

    asyncio.run(_run())


def test_eval_harness_passes() -> None:
    report = run_eval().as_dict()
    assert report["passed"] == report["total"]
    assert report["total"] >= 3
