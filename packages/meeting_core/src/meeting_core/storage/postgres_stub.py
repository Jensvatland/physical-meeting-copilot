"""PostgreSQL StorageAdapter stub — Phase 21 optional backend.

Meeting Core talks only to StorageAdapter; swapping SQLite → Postgres must not
change domain logic. This stub documents the contract until a driver is wired.
"""

from __future__ import annotations

import os

from meeting_core.adapters.base import AdapterCapabilities, HealthStatus, StorageAdapter
from meeting_core.domain.models import SessionState


class PostgresStorageAdapter(StorageAdapter):
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or os.environ.get("MEETING_CORE_POSTGRES_DSN", "")
        self._ready = False

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            name="postgres",
            languages=[],
            streaming=False,
            batch=True,
            online_required=True,
            notes="Optional; enable with MEETING_CORE_POSTGRES_DSN",
        )

    def health(self) -> HealthStatus:
        if not self.dsn:
            return HealthStatus(healthy=False, degraded=True, detail="MEETING_CORE_POSTGRES_DSN unset")
        return HealthStatus(healthy=False, degraded=True, detail="driver not installed; use SqliteStorageAdapter")

    def save_session(self, state: SessionState) -> None:
        raise NotImplementedError("Postgres adapter pending driver install; use SqliteStorageAdapter")

    def load_session(self, session_id: str) -> SessionState | None:
        raise NotImplementedError("Postgres adapter pending driver install; use SqliteStorageAdapter")

    def delete_session(self, session_id: str) -> None:
        raise NotImplementedError("Postgres adapter pending driver install; use SqliteStorageAdapter")
