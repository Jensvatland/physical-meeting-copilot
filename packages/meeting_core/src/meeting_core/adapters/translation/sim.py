"""Simulated translation adapter — preserves originals in Meeting Core."""

from __future__ import annotations

from meeting_core.adapters.base import AdapterCapabilities, HealthStatus, TranslationAdapter

# Tiny glossary for demos / tests (not a real MT system).
_GLOSSARY = {
    "我们这台设备的额定容量是五千吨。": "Our equipment's rated capacity is five thousand tons.",
    "交付日期可以改到九月十五日。": "The delivery date can be moved to September 15.",
    "质保是二十四个月。": "The warranty is twenty-four months.",
    "你好": "Hello",
    "价格是一百万元": "The price is one million yuan",
}


class SimulatedTranslationAdapter(TranslationAdapter):
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            name="translation:sim",
            languages=["zh-CN", "en"],
            streaming=True,
            batch=True,
            online_required=False,
            notes="Fixture MT for demos; production uses Qwen/other adapters",
        )

    def health(self) -> HealthStatus:
        return HealthStatus(healthy=True, latency_ms=8.0, detail="sim")

    async def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
    ) -> dict:
        if source_language.startswith("en") and target_language.startswith("en"):
            translated = text
        else:
            translated = _GLOSSARY.get(text.strip(), f"[{target_language}] {text}")
        return {
            "translated_text": translated,
            "source_language": source_language,
            "target_language": target_language,
            "original_text": text,
            "is_final": True,
        }
