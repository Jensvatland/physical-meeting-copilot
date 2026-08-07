"""Simulated ASR adapter for tests and offline demos (not a production model)."""

from __future__ import annotations

from meeting_core.adapters.base import AdapterCapabilities, HealthStatus, SpeechRecognitionAdapter


class SimulatedSpeechRecognitionAdapter(SpeechRecognitionAdapter):
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            name="asr:sim",
            languages=["zh-CN", "en"],
            streaming=True,
            batch=True,
            online_required=False,
            notes="Fixture adapter for Phase 1–2 tests",
        )

    def health(self) -> HealthStatus:
        return HealthStatus(healthy=True, latency_ms=5.0, detail="sim")

    async def transcribe_stream(self, audio_chunk: bytes, *, language_hint: str | None = None) -> dict:
        # Deterministic stub: length-based fake partial.
        text = f"[sim:{language_hint or 'auto'}:{len(audio_chunk)}B]"
        return {
            "text": text,
            "is_final": len(audio_chunk) > 0,
            "language": language_hint or "zh-CN",
            "confidence": 0.5,
        }
