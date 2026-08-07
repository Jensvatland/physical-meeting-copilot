"""In-memory StorageAdapter — useful for tests and ephemeral profiles."""

from __future__ import annotations

from typing import Any

from meeting_core.adapters.base import AdapterCapabilities, HealthStatus, StorageAdapter
from meeting_core.domain.models import SessionState


class MemoryStorageAdapter(StorageAdapter):
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            name="memory",
            languages=[],
            streaming=False,
            batch=True,
            online_required=False,
            notes="Ephemeral process-local storage",
        )

    def health(self) -> HealthStatus:
        return HealthStatus(healthy=True, detail="ok")

    def save_session(self, state: SessionState) -> None:
        self._sessions[state.session_id] = state.model_copy(deep=True)

    def load_session(self, session_id: str) -> SessionState | None:
        state = self._sessions.get(session_id)
        return state.model_copy(deep=True) if state else None

    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def list_session_ids(self) -> list[str]:
        return list(self._sessions.keys())

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        hits: list[dict[str, Any]] = []
        for state in self._sessions.values():
            title = (state.title or "").lower()
            blob = " ".join(s.text for s in state.transcript).lower()
            if q in title or q in blob:
                hits.append(state.summary())
        return hits
