"""Heuristic intelligence primitives — lightweight, provider-independent."""

from __future__ import annotations

import re
from typing import Any

from meeting_core.domain.models import IntelligencePrimitive, PrimitiveKind

_CN_NUM = {
    "零": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
    "百": 100,
    "千": 1000,
    "万": 10000,
}

_PRICE_RE = re.compile(
    r"(?P<num>\d+(?:[.,]\d+)?)\s*(?P<unit>万元|万|元|RMB|USD|\$|tons?|吨|months?|个月)",
    re.IGNORECASE,
)
_CN_PRICE_RE = re.compile(r"(?P<body>[一二两三四五六七八九十百千万]+)\s*(?P<unit>万元|万|元|吨|个月)")
_DATE_RE = re.compile(
    r"(?P<d>\d{4}-\d{2}-\d{2})|"
    r"(?P<md>(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2})|"
    r"(?P<cn>(一月|二月|三月|四月|五月|六月|七月|八月|九月|十月|十一月|十二月)\s*\d{1,2}\s*日?)",
    re.IGNORECASE,
)
_RISK_NEEDLES = (
    "conflict",
    "conflicts",
    "risk",
    "delay",
    "cannot",
    "无法",
    "冲突",
    "风险",
    "延迟",
    "不足",
)


def _cn_to_int(text: str) -> float | None:
    if not text:
        return None
    total = 0
    current = 0
    for ch in text:
        if ch not in _CN_NUM:
            return None
        val = _CN_NUM[ch]
        if val >= 10:
            current = (current or 1) * val
            if val >= 10000:
                total += current
                current = 0
        else:
            current += val
    return float(total + current)


def extract_primitives(
    text: str,
    *,
    session_id: str,
    speaker_id: str | None = None,
    source_segment_id: str | None = None,
) -> list[IntelligencePrimitive]:
    found: list[IntelligencePrimitive] = []
    for m in _PRICE_RE.finditer(text):
        raw = m.group("num").replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            continue
        unit = m.group("unit")
        kind = PrimitiveKind.PRICE if unit.lower() in {"万元", "万", "元", "rmb", "usd", "$"} else PrimitiveKind.NUMBER
        if unit in {"months", "month", "个月"}:
            kind = PrimitiveKind.DEADLINE
        found.append(
            IntelligencePrimitive(
                session_id=session_id,
                kind=kind,
                text=m.group(0),
                normalized=f"{value} {unit}",
                value=value,
                unit=unit,
                speaker_id=speaker_id,
                source_segment_id=source_segment_id,
                confidence=0.7,
            )
        )
    for m in _CN_PRICE_RE.finditer(text):
        value = _cn_to_int(m.group("body"))
        if value is None:
            continue
        unit = m.group("unit")
        kind = PrimitiveKind.PRICE if "元" in unit or unit == "万" else PrimitiveKind.NUMBER
        found.append(
            IntelligencePrimitive(
                session_id=session_id,
                kind=kind,
                text=m.group(0),
                normalized=f"{value} {unit}",
                value=value,
                unit=unit,
                speaker_id=speaker_id,
                source_segment_id=source_segment_id,
                confidence=0.65,
            )
        )
    for m in _DATE_RE.finditer(text):
        found.append(
            IntelligencePrimitive(
                session_id=session_id,
                kind=PrimitiveKind.DEADLINE,
                text=m.group(0),
                normalized=m.group(0),
                speaker_id=speaker_id,
                source_segment_id=source_segment_id,
                confidence=0.6,
            )
        )
    lower = text.lower()
    if any(n in lower for n in _RISK_NEEDLES):
        found.append(
            IntelligencePrimitive(
                session_id=session_id,
                kind=PrimitiveKind.RISK,
                text=text[:160],
                normalized="risk_signal",
                speaker_id=speaker_id,
                source_segment_id=source_segment_id,
                confidence=0.55,
            )
        )
    return found


def primitives_as_dicts(items: list[IntelligencePrimitive]) -> list[dict[str, Any]]:
    return [p.model_dump(mode="json") for p in items]
