"""Meeting session lifecycle and state mutations."""

from __future__ import annotations

from typing import Any

from meeting_core.adapters.base import TextToSpeechAdapter
from meeting_core.adapters.tts.sim import SimulatedTextToSpeechAdapter
from meeting_core.bus.event_bus import EventBus
from meeting_core.domain.models import (
    PROTOCOL_VERSION,
    Alert,
    Claim,
    ClaimState,
    Commitment,
    Decision,
    Finding,
    IntelligencePrimitive,
    MeetingEvent,
    MeetingMode,
    Participant,
    PreMeetingContext,
    PrivateSpeechItem,
    Question,
    ResearchJob,
    ResearchStatus,
    SessionConfig,
    SessionState,
    SessionStatus,
    TranscriptSegment,
    TranslationSegment,
    new_id,
    utc_now,
)
from meeting_core.intelligence.contradiction import compare_claim_to_prior
from meeting_core.intelligence.export import build_post_meeting_package
from meeting_core.intelligence.extract import extract_primitives
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
        tts: TextToSpeechAdapter | None = None,
    ) -> None:
        self.bus = bus or EventBus()
        self.storage = storage or SqliteStorageAdapter()
        self.tts = tts or SimulatedTextToSpeechAdapter()
        self.state = SessionState(
            session_id=session_id or SessionState().session_id,
            config=config or SessionConfig(),
            title=title,
        )
        self.storage.save_session(self.state)

    def _emit(self, event_type: str, *, source: str = "core", **kwargs: Any) -> MeetingEvent:
        event = MeetingEvent(
            session_id=self.state.session_id,
            type=event_type,
            source=source,
            **kwargs,
        )
        self.bus.publish(event)
        self._audit(event_type, source=source, payload=kwargs.get("payload") or {})
        self.storage.save_session(self.state)
        return event

    def _audit(self, action: str, *, source: str, payload: dict[str, Any] | None = None) -> None:
        self.state.audit_log.append(
            {
                "at": utc_now().isoformat(),
                "action": action,
                "source": source,
                "payload": payload or {},
            }
        )
        # Cap audit log to keep SQLite payloads bounded.
        if len(self.state.audit_log) > 500:
            self.state.audit_log = self.state.audit_log[-500:]

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

    def set_pre_meeting_context(self, context: PreMeetingContext | dict[str, Any]) -> PreMeetingContext:
        if isinstance(context, dict):
            context = PreMeetingContext.model_validate(context)
        self.state.pre_meeting = context
        self._emit(
            "meeting.pre_context_set",
            payload={
                "agenda": context.agenda,
                "goals": context.goals,
                "watch_items": context.watch_items,
                "prior_facts": context.prior_facts,
                "expected_participants": context.expected_participants,
            },
        )
        return context

    def record_consent(self, *, recorded: bool = True) -> None:
        self.state.config.consent_recorded = recorded
        self._emit("meeting.consent_recorded", payload={"consent_recorded": recorded})

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
        extract: bool = True,
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
        if is_final and extract and text:
            self.ingest_primitives_from_text(
                text,
                speaker_id=speaker_id,
                source_segment_id=segment.segment_id,
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

    def ingest_primitives_from_text(
        self,
        text: str,
        *,
        speaker_id: str | None = None,
        source_segment_id: str | None = None,
    ) -> list[IntelligencePrimitive]:
        items = extract_primitives(
            text,
            session_id=self.state.session_id,
            speaker_id=speaker_id,
            source_segment_id=source_segment_id,
        )
        for item in items:
            self.state.primitives.append(item)
            self._emit(
                "primitive.detected",
                speaker_id=speaker_id,
                text=item.text,
                source="intelligence:heuristic",
                payload={
                    "primitive_id": item.primitive_id,
                    "kind": item.kind.value,
                    "normalized": item.normalized,
                    "value": item.value,
                    "unit": item.unit,
                },
            )
        return items

    def create_claim(
        self,
        statement: str,
        *,
        original_text: str | None = None,
        speaker_id: str | None = None,
        state: ClaimState = ClaimState.UNVERIFIED,
        provenance: dict[str, Any] | None = None,
        auto_compare: bool = True,
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
        if auto_compare and self.state.pre_meeting.prior_facts:
            self.apply_prior_comparison(claim.claim_id)
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

    def apply_prior_comparison(self, claim_id: str) -> dict[str, Any]:
        claim = next(c for c in self.state.claims if c.claim_id == claim_id)
        result = compare_claim_to_prior(claim, self.state.pre_meeting)
        suggested = ClaimState(result["suggested_state"])
        if suggested != claim.state:
            self.update_claim(claim_id, state=suggested, evidence=result.get("evidence"))
        return result

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

    def start_research(
        self,
        query: str,
        *,
        correlation_id: str | None = None,
        trigger_event_type: str | None = None,
    ) -> ResearchJob:
        job = ResearchJob(
            session_id=self.state.session_id,
            query=query,
            correlation_id=correlation_id or new_id(),
            trigger_event_type=trigger_event_type,
        )
        self.state.research.append(job)
        self._emit(
            "research.started",
            text=query,
            correlation_id=job.correlation_id,
            source="agent:bridge",
            payload={"research_id": job.research_id, "query": query, "trigger_event_type": trigger_event_type},
        )
        return job

    def complete_research(
        self,
        research_id: str,
        *,
        result_summary: str,
        evidence: list[dict[str, Any]] | None = None,
        failed: bool = False,
        stale: bool = False,
    ) -> ResearchJob:
        job = next(r for r in self.state.research if r.research_id == research_id)
        job.result_summary = result_summary
        job.evidence = evidence or []
        job.completed_at = utc_now()
        job.stale = stale
        if failed:
            job.status = ResearchStatus.FAILED
        elif stale:
            job.status = ResearchStatus.STALE
        else:
            job.status = ResearchStatus.COMPLETED
        self._emit(
            "research.completed",
            text=result_summary,
            correlation_id=job.correlation_id,
            source="agent:bridge",
            payload={
                "research_id": job.research_id,
                "status": job.status.value,
                "evidence": job.evidence,
                "stale": stale,
            },
        )
        return job

    async def speak_private(
        self,
        text: str,
        *,
        priority: int = 80,
        language: str = "en",
        correlation_id: str | None = None,
        interrupt: bool = True,
    ) -> PrivateSpeechItem:
        if interrupt:
            for item in self.state.private_speech:
                if not item.spoken:
                    item.interrupted = True
        audio = await self.tts.synthesize(text, language=language)
        speech = PrivateSpeechItem(
            session_id=self.state.session_id,
            text=text,
            priority=priority,
            language=language,
            correlation_id=correlation_id,
            audio_bytes_len=len(audio),
        )
        self.state.private_speech.append(speech)
        self._emit(
            "private_speech.queued",
            text=text,
            correlation_id=correlation_id,
            source=self.tts.capabilities().name,
            payload={
                "speech_id": speech.speech_id,
                "priority": priority,
                "audio_bytes_len": speech.audio_bytes_len,
                "interrupted_others": interrupt,
            },
        )
        # Sim path marks spoken immediately (local fixture TTS).
        speech.spoken = True
        speech.spoken_at = utc_now()
        alert = next((a for a in self.state.alerts if a.text == text and not a.spoken), None)
        if alert:
            alert.spoken = True
        else:
            alert = self.push_private_alert(text, priority=priority, correlation_id=correlation_id)
            alert.spoken = True
        self._emit(
            "private_speech.spoken",
            text=text,
            correlation_id=correlation_id,
            source=self.tts.capabilities().name,
            payload={"speech_id": speech.speech_id, "alert_id": alert.alert_id},
        )
        return speech

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
            "speakers": dict(self.state.speakers),
            "participants": [p.model_dump(mode="json") for p in self.state.participants],
            "pre_meeting": self.state.pre_meeting.model_dump(mode="json"),
            "recent_transcript": [s.model_dump(mode="json") for s in self.state.transcript[-limit:]],
            "recent_translations": [t.model_dump(mode="json") for t in self.state.translations[-limit:]],
            "open_questions": [q.model_dump(mode="json") for q in self.state.questions if not q.answered],
            "claims": [c.model_dump(mode="json") for c in self.state.claims],
            "findings": [f.model_dump(mode="json") for f in self.state.findings[-10:]],
            "alerts": [a.model_dump(mode="json") for a in self.state.alerts[-10:]],
            "research": [r.model_dump(mode="json") for r in self.state.research[-10:]],
            "primitives": [p.model_dump(mode="json") for p in self.state.primitives[-20:]],
        }

    def export_package(self) -> dict[str, Any]:
        package = build_post_meeting_package(self.state)
        self._emit("meeting.exported", payload={"keys": sorted(package.keys())})
        return package

    def delete_biometrics(self) -> int:
        """Clear consent-gated biometric flags (voiceprints live outside core)."""
        cleared = 0
        for p in self.state.participants:
            if p.biometric_consent:
                p.biometric_consent = False
                cleared += 1
        self.state.config.biometrics_enabled = False
        self._emit("privacy.biometrics_cleared", payload={"cleared": cleared})
        return cleared


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

    def list_sessions(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for sid in self.storage.list_session_ids():
            session = self.get(sid)
            if session:
                out.append(session.state.summary())
        return out

    def search_sessions(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        hits: list[dict[str, Any]] = []
        for sid in self.storage.list_session_ids():
            session = self.get(sid)
            if not session:
                continue
            title = (session.state.title or "").lower()
            blob = " ".join(s.text for s in session.state.transcript).lower()
            if q in title or q in blob:
                hits.append(session.state.summary())
        return hits

    def delete_session(self, session_id: str) -> None:
        self.storage.delete_session(session_id)
        self._sessions.pop(session_id, None)
