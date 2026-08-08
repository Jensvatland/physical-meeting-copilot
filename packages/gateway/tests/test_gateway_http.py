import meeting_gateway.app as gateway_app
from meeting_gateway.app import GatewayState, _db_path
from starlette.testclient import TestClient


def test_health_and_session_start() -> None:
    gateway_app.STATE = GatewayState()
    client = TestClient(gateway_app.app)
    assert client.get("/health").json()["ok"] is True
    res = client.post("/api/sessions", json={"title": "t"})
    assert res.status_code == 200
    sid = res.json()["session_id"]
    state = client.get(f"/api/sessions/{sid}")
    assert state.json()["status"] == "ACTIVE"


def test_default_db_path_is_local_file(monkeypatch) -> None:
    monkeypatch.delenv("MEETING_CORE_DB", raising=False)
    path = _db_path()
    assert path.endswith("meetings.db")
    assert ":memory:" not in path
