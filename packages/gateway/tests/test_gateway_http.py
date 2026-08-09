from __future__ import annotations

import base64

from meeting_core.realtime.vad import synthesize_pcm_tone
from meeting_gateway.app import app
from starlette.testclient import TestClient


def test_health_and_session_start_requires_consent() -> None:
    client = TestClient(app)
    health = client.get("/health").json()
    assert health["ok"] is True
    assert health["consent_required"] is True
    assert "path" not in health["db"]
    denied = client.post("/api/sessions", json={"title": "t"})
    assert denied.status_code == 400
    assert denied.json()["code"] == "consent_required"
    res = client.post("/api/sessions", json={"title": "t", "consent_recorded": True})
    assert res.status_code == 200
    sid = res.json()["session_id"]
    state = client.get(f"/api/sessions/{sid}")
    assert state.json()["status"] == "ACTIVE"
    assert state.json()["consent_recorded"] is True


def test_websocket_pcm_ingest_with_consent() -> None:
    client = TestClient(app)
    res = client.post("/api/sessions", json={"title": "ws", "consent_recorded": True})
    sid = res.json()["session_id"]
    with client.websocket_connect(f"/ws/audio/{sid}") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "ready"
        assert ready.get("simulated_asr") is True
        pcm = synthesize_pcm_tone(duration_ms=120, amplitude=9000)
        ws.send_json(
            {
                "type": "audio",
                "pcm_b64": base64.b64encode(pcm).decode("ascii"),
                "timestamp_ms": 12,
                "language_hint": "zh-CN",
            }
        )
        msg = ws.receive_json()
        assert msg["type"] == "ingest"
        assert msg["active"] is True
        assert msg["transcript"] is not None
        ws.send_json({"type": "stop"})
        stopped = ws.receive_json()
        assert stopped["type"] == "stopped"
        assert "export" in stopped


def test_stop_and_export_http() -> None:
    client = TestClient(app)
    sid = client.post("/api/sessions", json={"title": "export", "consent_recorded": True}).json()["session_id"]
    stopped = client.post(f"/api/sessions/{sid}/stop")
    assert stopped.json()["status"] == "ENDED"
    exported = client.get(f"/api/sessions/{sid}/export")
    assert exported.status_code == 200
    assert "session" in exported.json()
