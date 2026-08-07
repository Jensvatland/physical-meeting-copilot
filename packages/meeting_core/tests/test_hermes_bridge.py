"""Hermes bridge stays outside Meeting Core package imports of Hermes."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from meeting_core.session import MeetingSession
from meeting_core.storage.sqlite import SqliteStorageAdapter

ROOT = Path(__file__).resolve().parents[3]


def _load_bridge():
    path = ROOT / "integrations" / "hermes" / "event_bridge.py"
    spec = importlib.util.spec_from_file_location("hermes_event_bridge", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.HermesEventBridge


def test_hermes_bridge_forwards_material_events() -> None:
    HermesEventBridge = _load_bridge()
    seen: list[dict] = []
    bridge = HermesEventBridge(on_event=seen.append)
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    bridge.attach(session)
    session.start()
    session.add_transcript("质保二十四个月", speaker_id="spk_1", language="zh-CN")
    session.create_claim("Warranty is 24 months", speaker_id="spk_1")
    assert any(e["event"]["type"] == "claim.created" for e in seen)
    assert any(e["priority_hint"] == "warranty" for e in seen)
