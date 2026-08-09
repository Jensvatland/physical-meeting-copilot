import pytest
from meeting_core.adapters.asr.sim import SimulatedSpeechRecognitionAdapter
from meeting_core.adapters.translation.sim import SimulatedTranslationAdapter
from meeting_core.realtime.pipeline import RealtimeIngestPipeline
from meeting_core.realtime.vad import synthesize_pcm_tone
from meeting_core.session import MeetingSession
from meeting_core.storage.sqlite import SqliteStorageAdapter


class FixedChineseASR(SimulatedSpeechRecognitionAdapter):
    async def transcribe_stream(self, audio_chunk: bytes, *, language_hint: str | None = None) -> dict:
        return {
            "text": "质保是二十四个月。",
            "is_final": True,
            "language": "zh-CN",
            "confidence": 0.91,
        }


@pytest.mark.asyncio
async def test_mandarin_preserved_with_english_translation() -> None:
    session = MeetingSession(storage=SqliteStorageAdapter(":memory:"))
    session.record_consent(recorded=True)
    session.start()
    pipeline = RealtimeIngestPipeline(
        session=session,
        asr=FixedChineseASR(),
        translator=SimulatedTranslationAdapter(),
        language_hint="zh-CN",
        target_language="en",
    )
    result = await pipeline.on_audio(synthesize_pcm_tone(amplitude=9000), timestamp_ms=10)
    assert result["transcript"]["text"] == "质保是二十四个月。"
    assert result["transcript"]["language"] == "zh-CN"
    assert result["translation"]["original_text"] == "质保是二十四个月。"
    assert "warranty" in result["translation"]["translated_text"].lower()
    assert session.state.transcript[0].text == "质保是二十四个月。"
