"""Starlette gateway: browser mic PCM → Meeting Core via WebSocket.

LiveKit remains the preferred production transport (see LiveKitTransportAdapter).
This WebSocket path is the Phase 2 vertical slice that works without cloud creds.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

from meeting_core.realtime.pipeline import RealtimeIngestPipeline
from meeting_core.session import MeetingSessionManager
from meeting_core.storage.sqlite import SqliteStorageAdapter
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

WEB_DIR = Path(__file__).resolve().parents[4] / "clients" / "web" / "public"


def _db_path() -> str:
    return os.path.expanduser(os.environ.get("MEETING_CORE_DB", ":memory:"))


class GatewayState:
    def __init__(self) -> None:
        self.manager = MeetingSessionManager(storage=SqliteStorageAdapter(_db_path()))
        self.pipelines: dict[str, RealtimeIngestPipeline] = {}

    def ensure_session(self, title: str | None = None) -> tuple[str, RealtimeIngestPipeline]:
        session = self.manager.create(title=title or "Live meeting")
        session.start()
        pipeline = RealtimeIngestPipeline(session=session)
        self.pipelines[session.state.session_id] = pipeline
        return session.state.session_id, pipeline


STATE = GatewayState()


async def health(_: Request) -> JSONResponse:
    return JSONResponse({"ok": True, "service": "meeting-gateway"})


async def start_session(request: Request) -> JSONResponse:
    body = {}
    if request.headers.get("content-type", "").startswith("application/json"):
        body = await request.json()
    sid, _ = STATE.ensure_session(title=body.get("title"))
    return JSONResponse({"session_id": sid, "ws_url": f"/ws/audio/{sid}"})


async def session_state(request: Request) -> JSONResponse:
    sid = request.path_params["session_id"]
    session = STATE.manager.get(sid)
    if not session:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse(session.state.summary())


async def audio_ws(websocket: WebSocket) -> None:
    sid = websocket.path_params["session_id"]
    pipeline = STATE.pipelines.get(sid)
    if not pipeline:
        session = STATE.manager.get(sid)
        if not session:
            await websocket.close(code=4404)
            return
        pipeline = RealtimeIngestPipeline(session=session)
        STATE.pipelines[sid] = pipeline
    await websocket.accept()
    await websocket.send_json({"type": "ready", "session_id": sid})
    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
            if "text" in message and message["text"] is not None:
                data = json.loads(message["text"])
                await _handle_json_audio(pipeline, websocket, data)
            elif "bytes" in message and message["bytes"] is not None:
                result = await pipeline.on_audio(message["bytes"], timestamp_ms=0)
                await websocket.send_json(_public_result(result))
    finally:
        # Keep session alive for MCP inspection; client may call stop later.
        pass


async def _handle_json_audio(pipeline: RealtimeIngestPipeline, websocket: WebSocket, data: dict[str, Any]) -> None:
    if data.get("type") == "audio":
        pcm = base64.b64decode(data["pcm_b64"])
        ts = int(data.get("timestamp_ms", 0))
        if data.get("speaker_id"):
            pipeline.speaker_id = str(data["speaker_id"])
        if data.get("language_hint"):
            pipeline.language_hint = str(data["language_hint"])
        result = await pipeline.on_audio(pcm, timestamp_ms=ts)
        await websocket.send_json(_public_result(result))
    elif data.get("type") == "stop":
        pipeline.session.stop()
        await websocket.send_json({"type": "stopped", "summary": pipeline.session.state.summary()})


def _public_result(result: dict[str, Any]) -> dict[str, Any]:
    vad = result["vad"]
    return {
        "type": "ingest",
        "active": vad.active,
        "rms": vad.rms,
        "timestamp_ms": vad.timestamp_ms,
        "transcript": result.get("transcript"),
        "translation": result.get("translation"),
    }


async def index(_: Request) -> FileResponse:
    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        return JSONResponse(
            {"error": "web client missing", "hint": "clients/web/public/index.html"},
            status_code=404,
        )
    return FileResponse(index_path)


routes = [
    Route("/", index),
    Route("/health", health),
    Route("/api/sessions", start_session, methods=["POST"]),
    Route("/api/sessions/{session_id}", session_state),
    WebSocketRoute("/ws/audio/{session_id}", audio_ws),
]

if WEB_DIR.exists():
    routes.append(Mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static"))

app = Starlette(debug=True, routes=routes)


def main() -> None:
    import uvicorn

    host = os.environ.get("MEETING_GATEWAY_HOST", "127.0.0.1")
    port = int(os.environ.get("MEETING_GATEWAY_PORT", "8787"))
    uvicorn.run("meeting_gateway.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
