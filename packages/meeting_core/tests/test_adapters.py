import pytest
from meeting_core.adapters.asr.sim import SimulatedSpeechRecognitionAdapter
from meeting_core.adapters.realtime.livekit_stub import LiveKitTransportAdapter


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
