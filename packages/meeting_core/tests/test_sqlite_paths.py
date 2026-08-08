"""SQLite path convenience for first-run Mac installs."""

from __future__ import annotations

from pathlib import Path

from meeting_core.session import MeetingSession
from meeting_core.storage.sqlite import SqliteStorageAdapter


def test_file_db_creates_parent_directories(tmp_path: Path) -> None:
    db = tmp_path / "nested" / "data" / "meetings.db"
    assert not db.parent.exists()
    storage = SqliteStorageAdapter(db)
    session = MeetingSession(storage=storage, title="path-test")
    session.start()
    session.stop()
    assert db.exists()
    reloaded = SqliteStorageAdapter(db).load_session(session.state.session_id)
    assert reloaded is not None
    assert reloaded.title == "path-test"
