"""Adapter contracts — Meeting Core stays provider-independent."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AdapterCapabilities:
    name: str
    languages: list[str] = field(default_factory=list)
    streaming: bool = False
    batch: bool = True
    online_required: bool = False
    notes: str = ""


@dataclass
class HealthStatus:
    healthy: bool
    latency_ms: float | None = None
    detail: str = ""
    degraded: bool = False


class Adapter(ABC):
    @abstractmethod
    def capabilities(self) -> AdapterCapabilities: ...

    @abstractmethod
    def health(self) -> HealthStatus: ...


class CaptureAdapter(Adapter):
    """Microphone / table mic / wearable capture."""

    @abstractmethod
    async def start(self, session_id: str) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...


class RealtimeTransportAdapter(Adapter):
    """WebRTC/WebSocket transport (e.g. LiveKit). Not MCP."""

    @abstractmethod
    async def connect(self, session_id: str, token: str | None = None) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...


class SpeechRecognitionAdapter(Adapter):
    @abstractmethod
    async def transcribe_stream(self, audio_chunk: bytes, *, language_hint: str | None = None) -> dict[str, Any]:
        """Return partial/final transcript dict; never blocks Meeting Core event loop excessively."""
        ...


class DiarizationAdapter(Adapter):
    @abstractmethod
    async def label(self, audio_chunk: bytes) -> dict[str, Any]:
        """Return speaker_id and optional overlap metadata."""
        ...


class SpeakerIdentityAdapter(Adapter):
    """Optional, consent-gated voice biometrics — separable from core diarization."""

    @abstractmethod
    async def identify(self, speaker_id: str, embedding: bytes) -> dict[str, Any] | None: ...

    @abstractmethod
    async def enroll(self, participant_id: str, samples: list[bytes], *, consent: bool) -> None: ...

    @abstractmethod
    async def delete_voiceprint(self, participant_id: str) -> None: ...


class TranslationAdapter(Adapter):
    @abstractmethod
    async def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
    ) -> dict[str, Any]: ...


class TextToSpeechAdapter(Adapter):
    @abstractmethod
    async def synthesize(self, text: str, *, language: str = "en") -> bytes: ...


class StorageAdapter(Adapter):
    @abstractmethod
    def save_session(self, state: Any) -> None: ...

    @abstractmethod
    def load_session(self, session_id: str) -> Any | None: ...

    @abstractmethod
    def delete_session(self, session_id: str) -> None: ...

    @abstractmethod
    def list_session_ids(self) -> list[str]: ...


class AgentBridgeAdapter(Adapter):
    """Push structured events toward an external host without embedding host logic."""

    @abstractmethod
    async def emit(self, event: dict[str, Any]) -> None: ...
