"""Env-driven adapter selection — keeps vendor choice out of session core."""

from __future__ import annotations

import os

from meeting_core.adapters.asr.funasr_stub import FunASRSpeechRecognitionAdapter
from meeting_core.adapters.asr.sim import SimulatedSpeechRecognitionAdapter
from meeting_core.adapters.base import (
    DiarizationAdapter,
    SpeechRecognitionAdapter,
    TextToSpeechAdapter,
    TranslationAdapter,
)
from meeting_core.adapters.diarization.sim import SimulatedDiarizationAdapter
from meeting_core.adapters.translation.sim import SimulatedTranslationAdapter
from meeting_core.adapters.tts.sim import SimulatedTextToSpeechAdapter


def meeting_profile() -> str:
    return os.environ.get("MEETING_PROFILE", "global").strip().lower() or "global"


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def select_asr() -> SpeechRecognitionAdapter:
    """Choose ASR adapter.

    Defaults to simulated ASR. Set ``MEETING_ASR=funasr`` or ``FUNASR_ENABLED=1`` to
    select the FunASR stub (capabilities/health only until the runtime is wired).
    """
    choice = os.environ.get("MEETING_ASR", "auto").strip().lower() or "auto"
    if choice == "sim":
        return SimulatedSpeechRecognitionAdapter()
    if choice == "funasr" or (choice == "auto" and _truthy("FUNASR_ENABLED")):
        return FunASRSpeechRecognitionAdapter()
    return SimulatedSpeechRecognitionAdapter()


def select_translation() -> TranslationAdapter:
    return SimulatedTranslationAdapter()


def select_diarization() -> DiarizationAdapter:
    return SimulatedDiarizationAdapter()


def select_tts() -> TextToSpeechAdapter:
    return SimulatedTextToSpeechAdapter()


def adapter_selection_info() -> dict[str, str]:
    asr = select_asr()
    return {
        "profile": meeting_profile(),
        "asr": asr.capabilities().name,
        "translation": select_translation().capabilities().name,
        "diarization": select_diarization().capabilities().name,
        "tts": select_tts().capabilities().name,
        "funasr_enabled": "1" if _truthy("FUNASR_ENABLED") else "0",
    }
