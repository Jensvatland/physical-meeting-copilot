"""Domain models for Meeting Core — provider-independent."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

PROTOCOL_VERSION = "0.1.0"


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid4())


class MeetingMode(StrEnum):
    INTERPRETER = "INTERPRETER"
    COPILOT = "COPILOT"
    SILENT = "SILENT"


class SessionStatus(StrEnum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


class ClaimState(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    SUPPORTED_PROJECT_SOURCE = "SUPPORTED_PROJECT_SOURCE"
    SUPPORTED_EXTERNAL_SOURCE = "SUPPORTED_EXTERNAL_SOURCE"
    CONTRADICTED_PROJECT_SOURCE = "CONTRADICTED_PROJECT_SOURCE"
    CONTRADICTED_EXTERNAL_SOURCE = "CONTRADICTED_EXTERNAL_SOURCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"


class Provenance(BaseModel):
    adapter: str | None = None
    model: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class MeetingEvent(BaseModel):
    event_id: str = Field(default_factory=new_id)
    protocol_version: str = PROTOCOL_VERSION
    session_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    type: str
    source: str
    confidence: float | None = None
    speaker_id: str | None = None
    participant_id: str | None = None
    language: str | None = None
    text: str | None = None
    provenance: Provenance | dict[str, Any] | None = None
    correlation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class Participant(BaseModel):
    participant_id: str = Field(default_factory=new_id)
    speaker_id: str | None = None
    display_name: str | None = None
    role: str | None = None
    company: str | None = None
    seat_position: str | None = None
    language_primary: str | None = None
    biometric_consent: bool = False


class TranscriptSegment(BaseModel):
    segment_id: str = Field(default_factory=new_id)
    speaker_id: str | None = None
    participant_id: str | None = None
    language: str | None = None
    text: str
    is_final: bool = True
    start_ms: int | None = None
    end_ms: int | None = None
    confidence: float | None = None
    provenance: Provenance | dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class TranslationSegment(BaseModel):
    translation_id: str = Field(default_factory=new_id)
    source_segment_id: str
    speaker_id: str | None = None
    source_language: str | None = None
    target_language: str
    original_text: str
    translated_text: str
    is_final: bool = True
    provenance: Provenance | dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class Claim(BaseModel):
    claim_id: str = Field(default_factory=new_id)
    session_id: str
    statement: str
    original_text: str | None = None
    state: ClaimState = ClaimState.UNVERIFIED
    speaker_id: str | None = None
    participant_id: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    provenance: Provenance | dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Commitment(BaseModel):
    commitment_id: str = Field(default_factory=new_id)
    session_id: str
    text: str
    owner_participant_id: str | None = None
    speaker_id: str | None = None
    due_date: str | None = None
    provenance: Provenance | dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class Decision(BaseModel):
    decision_id: str = Field(default_factory=new_id)
    session_id: str
    text: str
    speaker_id: str | None = None
    provenance: Provenance | dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class Question(BaseModel):
    question_id: str = Field(default_factory=new_id)
    session_id: str
    text: str
    answered: bool = False
    speaker_id: str | None = None
    suggested: bool = False
    provenance: Provenance | dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class Finding(BaseModel):
    finding_id: str = Field(default_factory=new_id)
    session_id: str
    summary: str
    detail: str | None = None
    correlation_id: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    severity: str = "info"
    provenance: Provenance | dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class Alert(BaseModel):
    alert_id: str = Field(default_factory=new_id)
    session_id: str
    text: str
    priority: int = 50
    spoken: bool = False
    correlation_id: str | None = None
    mode_required: MeetingMode | None = None
    created_at: datetime = Field(default_factory=utc_now)


class SessionConfig(BaseModel):
    mode: MeetingMode = MeetingMode.COPILOT
    source_languages: list[str] = Field(default_factory=lambda: ["zh-CN", "en"])
    target_language: str = "en"
    alert_threshold: int = 40
    biometrics_enabled: bool = False


class SessionState(BaseModel):
    session_id: str = Field(default_factory=new_id)
    status: SessionStatus = SessionStatus.CREATED
    config: SessionConfig = Field(default_factory=SessionConfig)
    title: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    participants: list[Participant] = Field(default_factory=list)
    speakers: dict[str, str] = Field(default_factory=dict)  # speaker_id -> label
    transcript: list[TranscriptSegment] = Field(default_factory=list)
    translations: list[TranslationSegment] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    commitments: list[Commitment] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    questions: list[Question] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    alerts: list[Alert] = Field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "mode": self.config.mode.value,
            "title": self.title,
            "participant_count": len(self.participants),
            "speaker_count": len(self.speakers),
            "transcript_segments": len(self.transcript),
            "translation_segments": len(self.translations),
            "claims": len(self.claims),
            "commitments": len(self.commitments),
            "decisions": len(self.decisions),
            "questions": len(self.questions),
            "open_questions": sum(1 for q in self.questions if not q.answered),
            "findings": len(self.findings),
            "alerts": len(self.alerts),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }
