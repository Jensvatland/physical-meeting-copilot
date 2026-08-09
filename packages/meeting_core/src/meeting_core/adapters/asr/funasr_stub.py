"""FunASR/SenseVoice adapter stub (China profile — Phase 3/11).

Does not vendor FunASR. Declares capabilities and fails gracefully until the
optional runtime extra is installed and configured.
"""

from __future__ import annotations

import os

from meeting_core.adapters.base import (
    AdapterCapabilities,
    HealthStatus,
    SpeechRecognitionAdapter,
)


class FunASRSpeechRecognitionAdapter(SpeechRecognitionAdapter):
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.environ.get("FUNASR_MODEL", "SenseVoiceSmall")
        self._ready = os.environ.get("FUNASR_ENABLED", "").lower() in {"1", "true", "yes"}

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            name="asr:funasr",
            languages=["zh-CN", "en"],
            streaming=True,
            batch=True,
            online_required=False,
            notes="China-first ASR candidate; optional dependency",
        )

    def health(self) -> HealthStatus:
        if not self._ready:
            return HealthStatus(
                healthy=False,
                degraded=True,
                detail="FUNASR_ENABLED not set; use SimulatedSpeechRecognitionAdapter",
            )
        # Enabled but not wired: advertise degraded so operators do not trust a green health check.
        return HealthStatus(
            healthy=False,
            degraded=True,
            detail=f"model={self.model}; runtime not wired (transcribe_stream raises NotImplementedError)",
        )

    async def transcribe_stream(self, audio_chunk: bytes, *, language_hint: str | None = None) -> dict:
        if not self._ready:
            raise RuntimeError("FunASR adapter not enabled")
        raise NotImplementedError("Wire FunASR/SenseVoice runtime in Phase 3/11")
