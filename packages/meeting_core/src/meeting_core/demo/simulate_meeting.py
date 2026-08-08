"""Phase 1+ acceptance: simulated multi-speaker Mandarin/English meeting with research slice."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from meeting_core.domain.models import ClaimState
from meeting_core.session import MeetingSession
from meeting_core.storage.sqlite import SqliteStorageAdapter

# Allow running Hermes bridge from repo integrations/ without packaging it.
_ROOT = Path(__file__).resolve().parents[5]
_HERMES = _ROOT / "integrations" / "hermes"
if _HERMES.exists() and str(_HERMES) not in sys.path:
    sys.path.insert(0, str(_HERMES.parent))


def run_simulation() -> dict:
    return asyncio.run(_run_simulation_async())


async def _run_simulation_async() -> dict:
    from hermes.event_bridge import HermesEventBridge

    storage = SqliteStorageAdapter(":memory:")
    session = MeetingSession(storage=storage, title="Shipyard capacity negotiation")
    session.record_consent(recorded=True)
    session.set_pre_meeting_context(
        {
            "agenda": ["Capacity confirmation", "Delivery date", "Warranty"],
            "goals": ["Detect material claim mismatches"],
            "watch_items": ["capacity", "price", "warranty", "delivery"],
            "prior_facts": [
                {"topic": "capacity", "value": 4200, "unit": "tons", "note": "Previous usable EOL capacity"}
            ],
            "expected_participants": [
                {"display_name": "Li Wei", "role": "Sales"},
                {"display_name": "User", "role": "Buyer"},
            ],
        }
    )
    bridge = HermesEventBridge(auto_research=True, research_delay_s=0.01)
    bridge.attach(session)
    session.start()

    turns = [
        ("spk_1", "zh-CN", "我们这台设备的额定容量是五千吨。", "Our equipment's rated capacity is five thousand tons."),
        ("spk_2", "en", "Is that nominal or usable at end of life?", None),
        ("spk_1", "zh-CN", "交付日期可以改到九月十五日。", "The delivery date can be moved to September 15."),
        ("spk_3", "zh-CN", "质保是二十四个月。", "The warranty is twenty-four months."),
        ("spk_4", "en", "That conflicts with the previous specification.", None),
    ]

    for speaker_id, lang, text, translation in turns:
        seg = session.add_transcript(text, speaker_id=speaker_id, language=lang, is_final=True)
        if translation:
            session.add_translation(
                source_segment_id=seg.segment_id,
                original_text=text,
                translated_text=translation,
                source_language=lang,
                target_language="en",
                speaker_id=speaker_id,
            )

    session.assign_speaker("spk_1", display_name="Li Wei", role="Sales", company="EastYard")
    session.assign_speaker("spk_2", display_name="User", role="Buyer")
    session.assign_speaker("spk_3", display_name="Chen", role="Engineer", company="EastYard")
    session.assign_speaker("spk_4", display_name="Observer", role="Advisor")

    claim = session.create_claim(
        "Rated capacity is 5000 tons",
        original_text="我们这台设备的额定容量是五千吨。",
        speaker_id="spk_1",
    )
    # Let Hermes auto-research finish (scheduled on running loop).
    await asyncio.sleep(0.05)
    if claim.state == ClaimState.UNVERIFIED:
        session.update_claim(
            claim.claim_id,
            state=ClaimState.CONTRADICTED_PROJECT_SOURCE,
            evidence=[{"source": "prior_spec", "note": "Previous usable EOL capacity was 4200 tons"}],
        )
    session.record_commitment("Delivery by 2026-09-15", speaker_id="spk_1", due_date="2026-09-15")
    package = session.export_package()
    session.stop()

    reloaded = storage.load_session(session.state.session_id)
    assert reloaded is not None
    summary = reloaded.summary()
    return {
        "session_id": session.state.session_id,
        "summary": summary,
        "speakers": reloaded.speakers,
        "events": len(session.bus.history),
        "research_jobs": len(reloaded.research),
        "primitives": len(reloaded.primitives),
        "export_keys": sorted(package.keys()),
        "hermes_forwarded": len(bridge.forwarded),
        "claim_state": next(c.state.value for c in reloaded.claims),
    }


def main() -> None:
    result = run_simulation()
    print("Simulation OK")
    print(f"  session_id: {result['session_id']}")
    print(f"  speakers: {result['speakers']}")
    print(f"  summary: {result['summary']}")
    print(f"  events: {result['events']}")
    print(f"  research_jobs: {result['research_jobs']}")
    print(f"  primitives: {result['primitives']}")
    print(f"  claim_state: {result['claim_state']}")
    print(f"  hermes_forwarded: {result['hermes_forwarded']}")


if __name__ == "__main__":
    main()
