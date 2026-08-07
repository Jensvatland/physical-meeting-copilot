from meeting_gateway.app import app
from starlette.testclient import TestClient


def test_health_and_session_start() -> None:
    client = TestClient(app)
    assert client.get("/health").json()["ok"] is True
    res = client.post("/api/sessions", json={"title": "t"})
    assert res.status_code == 200
    sid = res.json()["session_id"]
    state = client.get(f"/api/sessions/{sid}")
    assert state.json()["status"] == "ACTIVE"
