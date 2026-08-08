import meeting_gateway.app as gateway_app
from meeting_gateway.app import GatewayState, _db_path
from starlette.testclient import TestClient


def test_health_and_session_start() -> None:
    gateway_app.STATE = GatewayState()
    client = TestClient(gateway_app.app)
    health = client.get("/health").json()
    assert health["ok"] is True
    assert health["asr"] == "simulated"
    assert "zh-CN" in health["languages"]

    denied = client.post("/api/sessions", json={"title": "t"})
    assert denied.status_code == 400
    assert denied.json()["error"] == "consent_required"

    res = client.post("/api/sessions", json={"title": "t", "consent": True})
    assert res.status_code == 200
    body = res.json()
    sid = body["session_id"]
    assert body["asr"] == "simulated"
    state = client.get(f"/api/sessions/{sid}")
    assert state.json()["status"] == "ACTIVE"
    assert state.json()["consent_recorded"] is True


def test_default_db_path_is_local_file(monkeypatch) -> None:
    monkeypatch.delenv("MEETING_CORE_DB", raising=False)
    path = _db_path()
    assert path.endswith("meetings.db")
    assert ":memory:" not in path
