"""Phase 1 acceptance tests."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from meeting_core.demo.simulate_meeting import run_simulation
from meeting_core.domain.models import PROTOCOL_VERSION, ClaimState, MeetingMode
from meeting_core.session import MeetingSession
from meeting_core.storage.sqlite import SqliteStorageAdapter

ROOT = Path(__file__).resolve().parents[3]
ENVELOPE_SCHEMA = json.loads(
    (ROOT / "packages" / "protocol" / "schemas" / "event-envelope.schema.json").read_text(encoding="utf-8")
)


def test_simulated_multi_speaker_meeting_maintains_state() -> None:
    result = run_simulation()
    summary = result["summary"]
    assert summary["status"] == "ENDED"
    assert summary["speaker_count"] == 4
    assert summary["transcript_segments"] == 5
    assert summary["translation_segments"] == 3
    assert summary["claims"] == 1
    assert summary["commitments"] == 1
    assert summary["findings"] == 1
    assert summary["alerts"] == 1
    assert summary["open_questions"] == 1
    assert "Li Wei" in result["speakers"].values()


def test_events_match_protocol_envelope() -> None:
    storage = SqliteStorageAdapter(":memory:")
    session = MeetingSession(storage=storage)
    session.start()
    session.add_transcript("你好", speaker_id="spk_1", language="zh-CN")
    session.stop()
    for event in session.bus.history:
        payload = json.loads(event.model_dump_json())
        jsonschema.validate(instance=payload, schema=ENVELOPE_SCHEMA)
        assert payload["protocol_version"] == PROTOCOL_VERSION


def test_claim_state_evolution_preserves_statement() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    session.start()
    claim = session.create_claim("Price is 100", original_text="价格是一百")
    original = claim.statement
    session.update_claim(claim.claim_id, state=ClaimState.INSUFFICIENT_INFORMATION, evidence=[{"note": "no doc"}])
    assert claim.statement == original
    assert claim.state == ClaimState.INSUFFICIENT_INFORMATION
    assert len(claim.evidence) == 1


def test_biometric_consent_defaults_false() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    session.start()
    p = session.assign_speaker("spk_9", display_name="Anon")
    assert p.biometric_consent is False


def test_default_mode_is_copilot() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    assert session.state.config.mode == MeetingMode.COPILOT


def test_search_transcript() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    session.start()
    session.add_transcript("Warranty is 24 months", speaker_id="spk_1", language="en")
    session.add_transcript("交付日期九月", speaker_id="spk_2", language="zh-CN")
    hits = session.search_transcript("warranty")
    assert len(hits) == 1


def test_crash_safe_reload_from_sqlite(tmp_path: Path) -> None:
    db = tmp_path / "meetings.db"
    storage = SqliteStorageAdapter(db)
    session = MeetingSession(storage=storage, title="persist")
    session.start()
    session.add_transcript("hello", speaker_id="spk_1", language="en")
    sid = session.state.session_id

    storage2 = SqliteStorageAdapter(db)
    loaded = storage2.load_session(sid)
    assert loaded is not None
    assert loaded.title == "persist"
    assert len(loaded.transcript) == 1
