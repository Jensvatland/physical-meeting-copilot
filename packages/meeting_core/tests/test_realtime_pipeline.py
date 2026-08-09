"""Phase 2 acceptance helpers: speech energy enters core as live events."""

from __future__ import annotations

import pytest
from meeting_core.realtime.pipeline import RealtimeIngestPipeline
from meeting_core.realtime.vad import synthesize_pcm_tone
from meeting_core.session import MeetingSession
from meeting_core.storage.sqlite import SqliteStorageAdapter


@pytest.mark.asyncio
async def test_physical_speech_enters_core_live() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"), title="live")
    session.record_consent(recorded=True)
    session.start()
    pipeline = RealtimeIngestPipeline(session=session, language_hint="zh-CN")
    pcm = synthesize_pcm_tone(duration_ms=120, amplitude=8000)
    result = await pipeline.on_audio(pcm, timestamp_ms=42)
    assert result["vad"].active is True
    assert result["transcript"] is not None
    assert session.state.transcript
    types = [e.type for e in session.bus.history]
    assert "audio.activity" in types
    assert "transcript.final" in types


@pytest.mark.asyncio
async def test_silence_does_not_force_transcript() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    session.record_consent(recorded=True)
    session.start()
    pipeline = RealtimeIngestPipeline(session=session)
    silent = b"\x00\x00" * 1600
    result = await pipeline.on_audio(silent, timestamp_ms=0)
    assert result["vad"].active is False
    assert result["transcript"] is None
