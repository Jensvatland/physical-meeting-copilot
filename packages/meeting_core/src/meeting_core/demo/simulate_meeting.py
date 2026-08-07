"""Phase 1 acceptance: simulated multi-speaker Mandarin/English meeting."""

from __future__ import annotations

from meeting_core.domain.models import ClaimState
from meeting_core.session import MeetingSession
from meeting_core.storage.sqlite import SqliteStorageAdapter


def run_simulation() -> dict:
    storage = SqliteStorageAdapter(":memory:")
    session = MeetingSession(storage=storage, title="Shipyard capacity negotiation")
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
    session.update_claim(
        claim.claim_id,
        state=ClaimState.CONTRADICTED_PROJECT_SOURCE,
        evidence=[{"source": "prior_spec", "note": "Previous usable EOL capacity was 4200 tons"}],
    )
    session.record_commitment("Delivery by 2026-09-15", speaker_id="spk_1", due_date="2026-09-15")
    session.record_question("Is the quoted capacity nominal or usable at end of life?", suggested=True)
    finding = session.publish_finding(
        "Capacity claim conflicts with previous specification",
        detail="Ask whether 5000t is nominal or usable at EOL.",
        correlation_id=claim.claim_id,
        severity="high",
        evidence=[{"claim_id": claim.claim_id}],
    )
    session.push_private_alert(
        "That conflicts with the previous specification. "
        "Ask whether the quoted capacity is nominal or usable at end of life.",
        priority=90,
        correlation_id=finding.finding_id,
    )
    session.stop()

    reloaded = storage.load_session(session.state.session_id)
    assert reloaded is not None
    summary = reloaded.summary()
    return {
        "session_id": session.state.session_id,
        "summary": summary,
        "speakers": reloaded.speakers,
        "events": len(session.bus.history),
    }


def main() -> None:
    result = run_simulation()
    print("Simulation OK")
    print(f"  session_id: {result['session_id']}")
    print(f"  speakers: {result['speakers']}")
    print(f"  summary: {result['summary']}")
    print(f"  events: {result['events']}")


if __name__ == "__main__":
    main()
