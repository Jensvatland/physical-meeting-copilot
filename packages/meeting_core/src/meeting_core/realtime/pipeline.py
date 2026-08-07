"""Realtime ingest pipeline: audio → VAD → ASR adapter → Meeting Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from meeting_core.adapters.asr.sim import SimulatedSpeechRecognitionAdapter
from meeting_core.adapters.base import SpeechRecognitionAdapter
from meeting_core.domain.models import MeetingEvent
from meeting_core.realtime.vad import EnergyVad, VadResult
from meeting_core.session import MeetingSession


@dataclass
class PipelineMetrics:
    chunks: int = 0
    active_chunks: int = 0
    transcripts: int = 0
    last_latency_ms: float | None = None


@dataclass
class RealtimeIngestPipeline:
    session: MeetingSession
    asr: SpeechRecognitionAdapter = field(default_factory=SimulatedSpeechRecognitionAdapter)
    vad: EnergyVad = field(default_factory=EnergyVad)
    speaker_id: str = "spk_room"
    language_hint: str | None = "zh-CN"
    metrics: PipelineMetrics = field(default_factory=PipelineMetrics)

    async def on_audio(self, pcm: bytes, *, timestamp_ms: int) -> dict[str, Any]:
        self.metrics.chunks += 1
        vad = self.vad.process(pcm, timestamp_ms=timestamp_ms)
        event = self._emit_activity(vad)
        result: dict[str, Any] = {"vad": vad, "activity_event_id": event.event_id, "transcript": None}
        if not vad.active:
            return result
        self.metrics.active_chunks += 1
        asr_out = await self.asr.transcribe_stream(pcm, language_hint=self.language_hint)
        segment = self.session.add_transcript(
            asr_out.get("text", ""),
            speaker_id=self.speaker_id,
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
