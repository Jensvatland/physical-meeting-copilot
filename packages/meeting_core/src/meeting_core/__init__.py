"""Physical Meeting Copilot — Meeting Core."""

from meeting_core.domain.models import (
    PROTOCOL_VERSION,
    ClaimState,
    MeetingMode,
    SessionStatus,
)
from meeting_core.session import MeetingSession, MeetingSessionManager

__all__ = [
    "PROTOCOL_VERSION",
    "ClaimState",
    "MeetingMode",
    "MeetingSession",
    "MeetingSessionManager",
    "SessionStatus",
]

__version__ = "0.1.0"
