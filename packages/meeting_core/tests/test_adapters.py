import pytest
from meeting_core.adapters.asr.funasr_stub import FunASRSpeechRecognitionAdapter
from meeting_core.adapters.asr.sim import SimulatedSpeechRecognitionAdapter
from meeting_core.adapters.realtime.livekit_stub import LiveKitTransportAdapter
from meeting_core.adapters.select import select_asr


def test_livekit_stub_degraded_without_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LIVEKIT_URL", raising=False)
    adapter = LiveKitTransportAdapter()
    health = adapter.health()
    assert health.healthy is False
    assert health.degraded is True
    caps = adapter.capabilities()
    assert caps.streaming is True
    assert caps.name == "livekit"


@pytest.mark.asyncio
async def test_sim_asr_returns_partial_structure() -> None:
    asr = SimulatedSpeechRecognitionAdapter()
    result = await asr.transcribe_stream(b"\x00\x01", language_hint="zh-CN")
    assert result["language"] == "zh-CN"
    assert result["is_final"] is True
    assert "text" in result


def test_funasr_disabled_is_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FUNASR_ENABLED", raising=False)
    adapter = FunASRSpeechRecognitionAdapter()
    health = adapter.health()
    assert health.healthy is False
    assert health.degraded is True


def test_funasr_enabled_without_runtime_is_not_healthy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FUNASR_ENABLED", "1")
    adapter = FunASRSpeechRecognitionAdapter()
    health = adapter.health()
    assert health.healthy is False
    assert health.degraded is True
    assert "not wired" in health.detail


@pytest.mark.asyncio
async def test_funasr_enabled_raises_not_implemented(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FUNASR_ENABLED", "1")
    adapter = FunASRSpeechRecognitionAdapter()
    with pytest.raises(NotImplementedError):
        await adapter.transcribe_stream(b"\x00\x01", language_hint="zh-CN")


def test_select_asr_respects_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FUNASR_ENABLED", raising=False)
    monkeypatch.setenv("MEETING_ASR", "sim")
    assert select_asr().capabilities().name.startswith("asr:sim")
    monkeypatch.setenv("MEETING_ASR", "funasr")
    monkeypatch.setenv("FUNASR_ENABLED", "1")
    assert select_asr().capabilities().name == "asr:funasr"
