"""Simulated diarization — energy-gated round-robin speaker labels."""

from __future__ import annotations

import struct

from meeting_core.adapters.base import AdapterCapabilities, DiarizationAdapter, HealthStatus


class SimulatedDiarizationAdapter(DiarizationAdapter):
    def __init__(self, *, speaker_count: int = 4, rms_threshold: float = 400.0) -> None:
        self.speaker_count = max(1, speaker_count)
        self.rms_threshold = rms_threshold
        self._active_index = 0
        self._chunks_on_speaker = 0

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            name="diarization:sim",
            languages=[],
            streaming=True,
            batch=False,
            online_required=False,
            notes="Round-robin fixture for multi-speaker demos",
        )

    def health(self) -> HealthStatus:
        return HealthStatus(healthy=True, latency_ms=2.0, detail="sim")

    async def label(self, audio_chunk: bytes) -> dict:
        rms = self._rms(audio_chunk)
        active = rms >= self.rms_threshold
        if active:
            self._chunks_on_speaker += 1
            # Rotate every few active chunks to simulate turn-taking.
            if self._chunks_on_speaker >= 3:
                self._active_index = (self._active_index + 1) % self.speaker_count
                self._chunks_on_speaker = 0
        speaker_id = f"spk_{self._active_index + 1}"
        return {
            "speaker_id": speaker_id,
            "active": active,
            "rms": rms,
            "overlap": False,
            "confidence": 0.55 if active else 0.1,
        }

    @staticmethod
    def _rms(pcm: bytes) -> float:
        if len(pcm) < 2:
            return 0.0
        n = len(pcm) // 2
        samples = struct.unpack("<" + "h" * n, pcm[: n * 2])
        if not samples:
            return 0.0
        acc = sum(s * s for s in samples) / len(samples)
        return acc**0.5
