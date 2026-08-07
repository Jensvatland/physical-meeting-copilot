"""Realtime ingest pipeline: audio → VAD → diarization → ASR → Meeting Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from meeting_core.adapters.asr.sim import SimulatedSpeechRecognitionAdapter
from meeting_core.adapters.base import DiarizationAdapter, SpeechRecognitionAdapter, TranslationAdapter
from meeting_core.adapters.diarization.sim import SimulatedDiarizationAdapter
from meeting_core.adapters.translation.sim import SimulatedTranslationAdapter
from meeting_core.domain.models import MeetingEvent
from meeting_core.realtime.vad import EnergyVad, VadResult
from meeting_core.session import MeetingSession


@dataclass
class PipelineMetrics:
    chunks: int = 0
    active_chunks: int = 0
    transcripts: int = 0
    last_latency_ms: float | None = None
    last_speaker_id: str | None = None


@dataclass
class RealtimeIngestPipeline:
    session: MeetingSession
    asr: SpeechRecognitionAdapter = field(default_factory=SimulatedSpeechRecognitionAdapter)
    translator: TranslationAdapter = field(default_factory=SimulatedTranslationAdapter)
    diarizer: DiarizationAdapter = field(default_factory=SimulatedDiarizationAdapter)
    vad: EnergyVad = field(default_factory=EnergyVad)
    speaker_id: str | None = None
    language_hint: str | None = "zh-CN"
    target_language: str = "en"
    metrics: PipelineMetrics = field(default_factory=PipelineMetrics)

    async def on_audio(self, pcm: bytes, *, timestamp_ms: int) -> dict[str, Any]:
        self.metrics.chunks += 1
        vad = self.vad.process(pcm, timestamp_ms=timestamp_ms)
        event = self._emit_activity(vad)
        diar = await self.diarizer.label(pcm)
        speaker_id = self.speaker_id or str(diar.get("speaker_id") or "spk_1")
        if diar.get("active"):
            self.session.ensure_speaker(speaker_id)
            if self.metrics.last_speaker_id and self.metrics.last_speaker_id != speaker_id:
                self.session._emit(  # noqa: SLF001
                    "speaker.turn",
                    speaker_id=speaker_id,
                    source=self.diarizer.capabilities().name,
                    payload={"from": self.metrics.last_speaker_id, "to": speaker_id},
                )
            self.metrics.last_speaker_id = speaker_id

        result: dict[str, Any] = {
            "vad": vad,
            "activity_event_id": event.event_id,
            "diarization": diar,
            "speaker_id": speaker_id,
            "transcript": None,
        }
        if not vad.active:
            return result
        self.metrics.active_chunks += 1
        asr_out = await self.asr.transcribe_stream(pcm, language_hint=self.language_hint)
        segment = self.session.add_transcript(
            asr_out.get("text", ""),
            speaker_id=speaker_id,
            language=asr_out.get("language") or self.language_hint,
            is_final=bool(asr_out.get("is_final", True)),
            confidence=asr_out.get("confidence"),
            start_ms=timestamp_ms,
            end_ms=timestamp_ms + max(1, len(pcm) // 32),
            source=self.asr.capabilities().name,
            provenance={"adapter": self.asr.capabilities().name},
        )
        self.metrics.transcripts += 1
        self.metrics.last_latency_ms = 0.0
        result["transcript"] = segment.model_dump(mode="json")
        lang = segment.language or self.language_hint or ""
        if lang.startswith("zh") and self.target_language.startswith("en") and segment.text:
            mt = await self.translator.translate(
                segment.text,
                source_language=lang,
                target_language=self.target_language,
            )
            tr = self.session.add_translation(
                source_segment_id=segment.segment_id,
                original_text=segment.text,
                translated_text=mt["translated_text"],
                source_language=lang,
                target_language=self.target_language,
                speaker_id=speaker_id,
                source=self.translator.capabilities().name,
                provenance={"adapter": self.translator.capabilities().name},
            )
            result["translation"] = tr.model_dump(mode="json")
        return result

    def _emit_activity(self, vad: VadResult) -> MeetingEvent:
        return self.session._emit(  # noqa: SLF001 — pipeline is a core collaborator
            "audio.activity",
            source="vad:energy",
            confidence=min(1.0, vad.rms / (self.vad.threshold * 4) if self.vad.threshold else 0.0),
            payload={
                "active": vad.active,
                "rms": vad.rms,
                "timestamp_ms": vad.timestamp_ms,
            },
        )
