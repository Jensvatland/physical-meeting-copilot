"""Contradiction / change detection against prior meeting facts."""

from __future__ import annotations

import re
from typing import Any

from meeting_core.domain.models import Claim, ClaimState, PreMeetingContext

_NUM_RE = re.compile(r"(\d+(?:[.,]\d+)?)")


def _numbers(text: str) -> list[float]:
    out: list[float] = []
    for m in _NUM_RE.finditer(text):
        try:
            out.append(float(m.group(1).replace(",", "")))
        except ValueError:
            continue
    return out


def compare_claim_to_prior(claim: Claim, pre_meeting: PreMeetingContext) -> dict[str, Any]:
    """Compare a claim statement to prior_facts watch items.

    Returns a recommendation payload; Meeting Core does not auto-overwrite claim state
    unless the caller applies the suggested state.
    """
    statement = claim.statement.lower()
    claim_nums = _numbers(claim.statement)
    matches: list[dict[str, Any]] = []
    for fact in pre_meeting.prior_facts:
        topic = str(fact.get("topic", "")).lower()
        value = fact.get("value")
        note = str(fact.get("note", ""))
        topic_hit = bool(topic) and topic in statement
        if not topic_hit and topic:
            # loose keyword overlap
            tokens = [t for t in re.split(r"\W+", topic) if len(t) > 2]
            topic_hit = any(t in statement for t in tokens)
        if not topic_hit:
            continue
        prior_nums = _numbers(str(value)) if value is not None else _numbers(note)
        contradicted = False
        if claim_nums and prior_nums and claim_nums[0] != prior_nums[0]:
            contradicted = True
        elif value is not None and str(value).lower() not in statement and claim_nums and prior_nums:
            contradicted = claim_nums[0] != prior_nums[0]
        matches.append(
            {
                "fact": fact,
                "contradicted": contradicted,
                "claim_numbers": claim_nums,
                "prior_numbers": prior_nums,
            }
        )

    if not matches:
        return {
            "suggested_state": ClaimState.INSUFFICIENT_INFORMATION.value,
            "evidence": [{"source": "prior_facts", "note": "No matching prior fact"}],
            "matches": [],
        }

    if any(m["contradicted"] for m in matches):
        return {
            "suggested_state": ClaimState.CONTRADICTED_PROJECT_SOURCE.value,
            "evidence": [
                {
                    "source": "prior_facts",
                    "note": f"Conflicts with prior {m['fact'].get('topic')}: {m['fact'].get('value')}",
                    "fact": m["fact"],
                }
                for m in matches
                if m["contradicted"]
            ],
            "matches": matches,
        }

    return {
        "suggested_state": ClaimState.SUPPORTED_PROJECT_SOURCE.value,
        "evidence": [
            {"source": "prior_facts", "note": "Consistent with prior project fact", "fact": m["fact"]}
            for m in matches
        ],
        "matches": matches,
    }
