"""Lightweight evaluation harness for multi-speaker / Mandarin scenarios."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from meeting_core.domain.models import ClaimState
from meeting_core.session import MeetingSession
from meeting_core.storage.sqlite import SqliteStorageAdapter


@dataclass
class ScenarioTurn:
    speaker_id: str
    language: str
    text: str
    translation: str | None = None


@dataclass
class Scenario:
    name: str
    turns: list[ScenarioTurn]
    expect_min_speakers: int = 1
    expect_mandarin: bool = False
    noise_tag: str | None = None


@dataclass
class EvalReport:
    scenarios: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        passed = sum(1 for s in self.scenarios if s["passed"])
        return {
            "passed": passed,
            "total": len(self.scenarios),
            "scenarios": self.scenarios,
        }


DEFAULT_SCENARIOS = [
    Scenario(
        name="two_speaker_mandarin_english",
        expect_min_speakers=2,
        expect_mandarin=True,
        turns=[
            ScenarioTurn("spk_1", "zh-CN", "价格是一百万元", "The price is one million yuan"),
            ScenarioTurn("spk_2", "en", "Does that include VAT?", None),
        ],
    ),
    Scenario(
        name="four_speaker_overlap_sim",
        expect_min_speakers=4,
        expect_mandarin=True,
        noise_tag="restaurant",
        turns=[
            ScenarioTurn(
                "spk_1",
                "zh-CN",
                "我们这台设备的额定容量是五千吨。",
                "Our equipment's rated capacity is five thousand tons.",
            ),
            ScenarioTurn("spk_2", "en", "Is that nominal or usable at end of life?", None),
            ScenarioTurn("spk_3", "zh-CN", "质保是二十四个月。", "The warranty is twenty-four months."),
            ScenarioTurn("spk_4", "en", "That conflicts with the previous specification.", None),
        ],
    ),
    Scenario(
        name="code_switching_numbers_dates",
        expect_min_speakers=2,
        expect_mandarin=True,
        turns=[
            ScenarioTurn(
                "spk_1",
                "zh-CN",
                "交付日期可以改到九月十五日。",
                "The delivery date can be moved to September 15.",
            ),
            ScenarioTurn("spk_2", "en", "Confirm 2026-09-15 delivery.", None),
        ],
    ),
]


def run_scenario(scenario: Scenario) -> dict[str, Any]:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"), title=scenario.name)
    session.set_pre_meeting_context(
        {
            "prior_facts": [{"topic": "capacity", "value": 4200, "unit": "tons", "note": "usable EOL"}],
            "watch_items": ["price", "capacity", "warranty"],
            "goals": ["Validate supplier claims"],
        }
    )
    session.start()
    for turn in scenario.turns:
        seg = session.add_transcript(turn.text, speaker_id=turn.speaker_id, language=turn.language)
        if turn.translation:
            session.add_translation(
                source_segment_id=seg.segment_id,
                original_text=turn.text,
                translated_text=turn.translation,
                source_language=turn.language,
                target_language="en",
                speaker_id=turn.speaker_id,
            )
    if any("五千吨" in t.text or "5000" in t.text for t in scenario.turns):
        claim = session.create_claim("Rated capacity is 5000 tons", speaker_id="spk_1")
        assert claim.state in {
            ClaimState.CONTRADICTED_PROJECT_SOURCE,
            ClaimState.UNVERIFIED,
            ClaimState.INSUFFICIENT_INFORMATION,
        }
    session.stop()
    package = session.export_package()
    mandarin_ok = (not scenario.expect_mandarin) or any(
        (s.language or "").startswith("zh") for s in session.state.transcript
    )
    speakers_ok = len(session.state.speakers) >= scenario.expect_min_speakers
    passed = mandarin_ok and speakers_ok and package["session"]["transcript_segments"] == len(scenario.turns)
    return {
        "name": scenario.name,
        "passed": passed,
        "noise_tag": scenario.noise_tag,
        "speaker_count": len(session.state.speakers),
        "transcript_segments": len(session.state.transcript),
        "primitives": len(session.state.primitives),
        "claims": len(session.state.claims),
        "mandarin_ok": mandarin_ok,
        "speakers_ok": speakers_ok,
    }


def run_eval(scenarios: list[Scenario] | None = None) -> EvalReport:
    report = EvalReport()
    for scenario in scenarios or DEFAULT_SCENARIOS:
        report.scenarios.append(run_scenario(scenario))
    return report


def main() -> None:
    report = run_eval()
    data = report.as_dict()
    print(f"Eval {data['passed']}/{data['total']} passed")
    for row in data["scenarios"]:
        mark = "OK" if row["passed"] else "FAIL"
        print(f"  [{mark}] {row['name']} speakers={row['speaker_count']} primitives={row['primitives']}")


if __name__ == "__main__":
    main()
