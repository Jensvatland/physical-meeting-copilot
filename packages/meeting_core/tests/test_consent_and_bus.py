"""Consent gate + EventBus isolation."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from meeting_core.bus.event_bus import EventBus
from meeting_core.domain.models import MeetingEvent
from meeting_core.realtime.pipeline import RealtimeIngestPipeline
from meeting_core.realtime.vad import synthesize_pcm_tone
from meeting_core.session import ConsentRequiredError, MeetingSession
from meeting_core.storage.sqlite import SqliteStorageAdapter

ROOT = Path(__file__).resolve().parents[3]
CLAIM_SCHEMA = json.loads(
    (ROOT / "packages" / "protocol" / "schemas" / "claim.schema.json").read_text(encoding="utf-8")
)


def test_transcript_requires_recording_consent() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    session.start()
    with pytest.raises(ConsentRequiredError):
        session.add_transcript("hello", speaker_id="spk_1", language="en")


@pytest.mark.asyncio
async def test_pipeline_requires_recording_consent() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    session.start()
    pipeline = RealtimeIngestPipeline(session=session)
    with pytest.raises(ConsentRequiredError):
        await pipeline.on_audio(synthesize_pcm_tone(amplitude=8000), timestamp_ms=1)


def test_event_bus_isolates_handler_failures() -> None:
    bus = EventBus()

    def boom(_: MeetingEvent) -> None:
        raise RuntimeError("subscriber failed")

    seen: list[str] = []

    def ok(event: MeetingEvent) -> None:
        seen.append(event.type)

    bus.subscribe(boom)
    bus.subscribe(ok)
    event = MeetingEvent(
        session_id="00000000-0000-0000-0000-000000000001",
        type="meeting.started",
        source="test",
    )
    bus.publish(event)
    assert seen == ["meeting.started"]
    assert bus.handler_errors


def test_claims_match_protocol_schema() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    session.record_consent(recorded=True)
    session.start()
    claim = session.create_claim("Price is 100", original_text="价格是一百", speaker_id="spk_1")
    payload = json.loads(claim.model_dump_json(exclude_none=True))
    jsonschema.validate(instance=payload, schema=CLAIM_SCHEMA)


def test_delete_biometrics_clears_flags() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    session.start()
    p = session.assign_speaker("spk_1", display_name="A", biometric_consent=True)
    assert p.biometric_consent is True
    cleared = session.delete_biometrics()
    assert cleared == 1
    assert p.biometric_consent is False
