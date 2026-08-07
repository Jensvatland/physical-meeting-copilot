"""LiveKit RealtimeTransportAdapter stub (Phase 2).

LiveKit is the preferred realtime plane. This stub declares capabilities and
health without requiring the LiveKit SDK at install time. Wire the real SDK
behind this adapter when LIVEKIT_* env vars are present.
"""

from __future__ import annotations

import os

from meeting_core.adapters.base import (
    AdapterCapabilities,
    HealthStatus,
    RealtimeTransportAdapter,
)


class LiveKitTransportAdapter(RealtimeTransportAdapter):
    def __init__(self, url: str | None = None) -> None:
        self.url = url or os.environ.get("LIVEKIT_URL")
        self._connected = False
        self._session_id: str | None = None

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            name="livekit",
            languages=[],
            streaming=True,
            batch=False,
            online_required=True,
            notes="Preferred WebRTC transport; raw audio never via MCP",
        )

    def health(self) -> HealthStatus:
        if not self.url:
            return HealthStatus(healthy=False, degraded=True, detail="LIVEKIT_URL not configured")
        return HealthStatus(healthy=True, detail="configured", degraded=not self._connected)

    async def connect(self, session_id: str, token: str | None = None) -> None:
        if not self.url:
            raise RuntimeError("LIVEKIT_URL required for live transport")
        # Real SDK connect lands in Phase 2 implementation slice.
        self._session_id = session_id
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False
        self._session_id = None
