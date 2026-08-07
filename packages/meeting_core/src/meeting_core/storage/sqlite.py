"""SQLite StorageAdapter — default local-first persistence."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from meeting_core.adapters.base import AdapterCapabilities, HealthStatus, StorageAdapter
from meeting_core.domain.models import SessionState


class SqliteStorageAdapter(StorageAdapter):
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            name="sqlite",
            languages=[],
            streaming=False,
            batch=True,
            online_required=False,
            notes="Default local-first storage",
        )

    def health(self) -> HealthStatus:
        try:
            self._conn.execute("SELECT 1")
            return HealthStatus(healthy=True, detail="ok")
        except sqlite3.Error as exc:
            return HealthStatus(healthy=False, detail=str(exc))

    def save_session(self, state: SessionState) -> None:
        payload = state.model_dump_json()
        self._conn.execute(
            """
            INSERT INTO sessions(session_id, state_json, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(session_id) DO UPDATE SET
              state_json=excluded.state_json,
              updated_at=excluded.updated_at
            """,
            (state.session_id, payload),
        )
        self._conn.commit()

    def load_session(self, session_id: str) -> SessionState | None:
        row = self._conn.execute(
            "SELECT state_json FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if not row:
            return None
        return SessionState.model_validate(json.loads(row[0]))

    def delete_session(self, session_id: str) -> None:
        self._conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        self._conn.commit()

    def list_session_ids(self) -> list[str]:
        rows = self._conn.execute("SELECT session_id FROM sessions ORDER BY updated_at DESC").fetchall()
        return [r[0] for r in rows]

    def close(self) -> None:
        self._conn.close()
