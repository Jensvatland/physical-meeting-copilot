"""Meeting session lifecycle and state mutations."""

from __future__ import annotations

from typing import Any

from meeting_core.bus.event_bus import EventBus
from meeting_core.domain.models import (
    PROTOCOL_VERSION,
    Alert,
    Claim,
    ClaimState,
    Commitment,
    Decision,
    Finding,
    MeetingEvent,
    MeetingMode,
    Participant,
    Question,
    SessionConfig,
    SessionState,
    SessionStatus,
    TranscriptSegment,
    TranslationSegment,
    utc_now,
)
from meeting_core.storage.sqlite import SqliteStorageAdapter


class MeetingSession:
    def __init__(
        self,
        *,
        bus: EventBus | None = None,
        storage: SqliteStorageAdapter | None = None,
        config: SessionConfig | None = None,
        title: str | None = None,
        session_id: str | None = None,
    ) -> None:
        self.bus = bus or EventBus()
        self.storage = storage or SqliteStorageAdapter()
        self.state = SessionState(
            session_id=session_id or SessionState().session_id,
            config=config or SessionConfig(),
            title=title,
        )
        if session_id is None:
            # regenerate cleanly if we used a throwaway
            pass
        self.storage.save_session(self.state)

    def _emit(self, event_type: str, *, source: str = "core", **kwargs: Any) -> MeetingEvent:
        event = MeetingEvent(
            session_id=self.state.session_id,
            type=event_type,
            source=source,
            **kwargs,
        )
        self.bus.publish(event)
        self.storage.save_session(self.state)
        return event

    def start(self) -> MeetingEvent:
        if self.state.status == SessionStatus.ENDED:
            raise RuntimeError("Cannot restart an ended session; create a new one")
        self.state.status = SessionStatus.ACTIVE
        self.state.started_at = utc_now()
        return self._emit(
            "meeting.started",
            payload={"mode": self.state.config.mode.value, "protocol_version": PROTOCOL_VERSION},
        )

    def stop(self) -> MeetingEvent:
        self.state.status = SessionStatus.ENDED
        self.state.ended_at = utc_now()
        return self._emit("meeting.ended")

    def ensure_speaker(self, speaker_id: str) -> str:
        if speaker_id not in self.state.speakers:
            label = f"Speaker {len(self.state.speakers) + 1}"
            self.state.speakers[speaker_id] = label
            self._emit(
                "speaker.detected",
                speaker_id=speaker_id,
                payload={"label": label},
                source="diarization:sim",
            )
        return self.state.speakers[speaker_id]

    def assign_speaker(
        self,
        speaker_id: str,
        *,
        display_name: str,
        role: str | None = None,
        company: str | None = None,
        seat_position: str | None = None,
        biometric_consent: bool = False,
    ) -> Participant:
        self.ensure_speaker(speaker_id)
        existing = next((p for p in self.state.participants if p.speaker_id == speaker_id), None)
        if existing:
            existing.display_name = display_name
            existing.role = role
            existing.company = company
            existing.seat_position = seat_position
            if biometric_consent:
                existing.biometric_consent = True
            participant = existing
        else:
            participant = Participant(
                speaker_id=speaker_id,
                display_name=display_name,
                role=role,
                company=company,
                seat_position=seat_position,
                biometric_consent=biometric_consent,
            )
            self.state.participants.append(participant)
        self.state.speakers[speaker_id] = display_name
        self._emit(
            "speaker.identity",
            speaker_id=speaker_id,
            participant_id=participant.participant_id,
            payload={
                "display_name": display_name,
                "role": role,
                "company": company,
                "biometric_consent": participant.biometric_consent,
            },
        )
        return participant

    def add_transcript(
        self,
        text: str,
        *,
        speaker_id: str | None = None,
        language: str | None = None,
        is_final: bool = True,
        confidence: float | None = None,
        start_ms: int | None = None,
        end_ms: int | None = None,
        source: str = "asr:sim",
        provenance: dict[str, Any] | None = None,
    ) -> TranscriptSegment:
        if speaker_id:
            self.ensure_speaker(speaker_id)
            participant = next((p for p in self.state.participants if p.speaker_id == speaker_id), None)
            participant_id = participant.participant_id if participant else None
        else:
            participant_id = None

        segment = TranscriptSegment(
            speaker_id=speaker_id,
            participant_id=participant_id,
            language=language,
            text=text,
            is_final=is_final,
            confidence=confidence,
            start_ms=start_ms,
            end_ms=end_ms,
            provenance=provenance,
        )
        if is_final or not self.state.transcript:
            self.state.transcript.append(segment)
        else:
            # replace last partial for same speaker if present
            last = self.state.transcript[-1]
            if not last.is_final and last.speaker_id == speaker_id:
                self.state.transcript[-1] = segment
            else:
                self.state.transcript.append(segment)

        event_type = "transcript.final" if is_final else "transcript.partial"
        self._emit(
            event_type,
            speaker_id=speaker_id,
            participant_id=participant_id,
            language=language,
            text=text,
            confidence=confidence,
            source=source,
            provenance=provenance,
            payload={"segment_id": segment.segment_id, "start_ms": start_ms, "end_ms": end_ms},
        )
        return segment

    def add_translation(
        self,
        *,
        source_segment_id: str,
        original_text: str,
        translated_text: str,
        target_language: str,
        source_language: str | None = None,
        speaker_id: str | None = None,
        is_final: bool = True,
        source: str = "translation:sim",
        provenance: dict[str, Any] | None = None,
    ) -> TranslationSegment:
        tr = TranslationSegment(
            source_segment_id=source_segment_id,
            speaker_id=speaker_id,
            source_language=source_language,
            target_language=target_language,
            original_text=original_text,
            translated_text=translated_text,
            is_final=is_final,
            provenance=provenance,
        )
        self.state.translations.append(tr)
        event_type = "translation.final" if is_final else "translation.partial"
        self._emit(
            event_type,
            speaker_id=speaker_id,
            language=target_language,
            text=translated_text,
            source=source,
            provenance=provenance,
            payload={
                "translation_id": tr.translation_id,
                "source_segment_id": source_segment_id,
                "original_text": original_text,
                "source_language": source_language,
            },
        )
        return tr

    def create_claim(
        self,
        statement: str,
        *,
        original_text: str | None = None,
        speaker_id: str | None = None,
        state: ClaimState = ClaimState.UNVERIFIED,
        provenance: dict[str, Any] | None = None,
    ) -> Claim:
        participant = next((p for p in self.state.participants if p.speaker_id == speaker_id), None)
        claim = Claim(
            session_id=self.state.session_id,
            statement=statement,
            original_text=original_text,
            state=state,
            speaker_id=speaker_id,
            participant_id=participant.participant_id if participant else None,
            provenance=provenance,
        )
        self.state.claims.append(claim)
        self._emit(
            "claim.created",
            speaker_id=speaker_id,
            participant_id=claim.participant_id,
            text=statement,
            payload={"claim_id": claim.claim_id, "state": claim.state.value, "original_text": original_text},
        )
        return claim

    def update_claim(self, claim_id: str, *, state: ClaimState, evidence: list[dict[str, Any]] | None = None) -> Claim:
        claim = next(c for c in self.state.claims if c.claim_id == claim_id)
        # Never overwrite original statement; only state/evidence evolve.
        claim.state = state
        claim.updated_at = utc_now()
        if evidence:
            claim.evidence.extend(evidence)
        self._emit(
            "claim.updated",
            text=claim.statement,
            payload={"claim_id": claim.claim_id, "state": claim.state.value, "evidence": claim.evidence},
        )
        return claim

    def record_commitment(self, text: str, *, speaker_id: str | None = None, due_date: str | None = None) -> Commitment:
        participant = next((p for p in self.state.participants if p.speaker_id == speaker_id), None)
        item = Commitment(
            session_id=self.state.session_id,
            text=text,
            speaker_id=speaker_id,
            owner_participant_id=participant.participant_id if participant else None,
            due_date=due_date,
        )
        self.state.commitments.append(item)
        self._emit(
            "commitment.recorded", speaker_id=speaker_id, text=text, payload={"commitment_id": item.commitment_id}
        )
        return item

    def record_decision(self, text: str, *, speaker_id: str | None = None) -> Decision:
        item = Decision(session_id=self.state.session_id, text=text, speaker_id=speaker_id)
        self.state.decisions.append(item)
        self._emit("decision.recorded", speaker_id=speaker_id, text=text, payload={"decision_id": item.decision_id})
        return item

    def record_question(self, text: str, *, suggested: bool = False, speaker_id: str | None = None) -> Question:
        item = Question(session_id=self.state.session_id, text=text, suggested=suggested, speaker_id=speaker_id)
        self.state.questions.append(item)
        self._emit(
            "question.recorded",
            speaker_id=speaker_id,
            text=text,
            payload={"question_id": item.question_id, "suggested": suggested},
        )
        return item

    def publish_finding(
        self,
        summary: str,
        *,
        detail: str | None = None,
        correlation_id: str | None = None,
        evidence: list[dict[str, Any]] | None = None,
        severity: str = "info",
    ) -> Finding:
        finding = Finding(
            session_id=self.state.session_id,
            summary=summary,
            detail=detail,
            correlation_id=correlation_id,
            evidence=evidence or [],
            severity=severity,
        )
        self.state.findings.append(finding)
        self._emit(
            "finding.published",
            text=summary,
            correlation_id=correlation_id,
            payload={"finding_id": finding.finding_id, "detail": detail, "evidence": finding.evidence},
        )
        return finding

    def push_private_alert(self, text: str, *, priority: int = 50, correlation_id: str | None = None) -> Alert:
        alert = Alert(
            session_id=self.state.session_id,
            text=text,
            priority=priority,
            correlation_id=correlation_id,
        )
        self.state.alerts.append(alert)
        self._emit(
            "alert.pushed",
            text=text,
            correlation_id=correlation_id,
            payload={"alert_id": alert.alert_id, "priority": priority},
        )
        return alert

    def set_mode(self, mode: MeetingMode) -> None:
        self.state.config.mode = mode
        self._emit("meeting.mode_changed", payload={"mode": mode.value})

    def set_language(self, *, target_language: str | None = None, source_languages: list[str] | None = None) -> None:
        if target_language:
            self.state.config.target_language = target_language
        if source_languages is not None:
            self.state.config.source_languages = source_languages
        self._emit(
            "meeting.language_changed",
            payload={
                "target_language": self.state.config.target_language,
                "source_languages": self.state.config.source_languages,
            },
        )

    def search_transcript(self, query: str) -> list[TranscriptSegment]:
        q = query.lower()
        return [s for s in self.state.transcript if q in s.text.lower()]

    def get_recent_context(self, *, limit: int = 20) -> dict[str, Any]:
        return {
            "session": self.state.summary(),
            "recent_transcript": [s.model_dump(mode="json") for s in self.state.transcript[-limit:]],
            "recent_translations": [t.model_dump(mode="json") for t in self.state.translations[-limit:]],
            "open_questions": [q.model_dump(mode="json") for q in self.state.questions if not q.answered],
            "claims": [c.model_dump(mode="json") for c in self.state.claims],
            "findings": [f.model_dump(mode="json") for f in self.state.findings[-10:]],
            "alerts": [a.model_dump(mode="json") for a in self.state.alerts[-10:]],
        }


class MeetingSessionManager:
    def __init__(self, storage: SqliteStorageAdapter | None = None) -> None:
        self.storage = storage or SqliteStorageAdapter()
        self._sessions: dict[str, MeetingSession] = {}

    def create(self, **kwargs: Any) -> MeetingSession:
        session = MeetingSession(storage=self.storage, **kwargs)
        self._sessions[session.state.session_id] = session
        return session

    def get(self, session_id: str) -> MeetingSession | None:
        if session_id in self._sessions:
            return self._sessions[session_id]
        loaded = self.storage.load_session(session_id)
        if not loaded:
            return None
        session = MeetingSession(storage=self.storage, session_id=session_id)
        session.state = loaded
        self._sessions[session_id] = session
        return session
