"""Simulated TTS — returns a tiny WAV silence buffer and metadata."""

from __future__ import annotations

import struct
import wave
from io import BytesIO

from meeting_core.adapters.base import AdapterCapabilities, HealthStatus, TextToSpeechAdapter


class SimulatedTextToSpeechAdapter(TextToSpeechAdapter):
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            name="tts:sim",
            languages=["en", "zh-CN"],
            streaming=False,
            batch=True,
            online_required=False,
            notes="Silent WAV fixture for private-speech lifecycle tests",
        )

    def health(self) -> HealthStatus:
        return HealthStatus(healthy=True, latency_ms=12.0, detail="sim")

    async def synthesize(self, text: str, *, language: str = "en") -> bytes:
        # Short silence @ 16kHz mono PCM16 in WAV container; duration scales with text.
        sample_rate = 16000
        duration_ms = min(800, 80 + len(text) * 4)
        n_samples = int(sample_rate * duration_ms / 1000)
        buf = BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(struct.pack("<" + "h" * n_samples, *([0] * n_samples)))
        return buf.getvalue()
