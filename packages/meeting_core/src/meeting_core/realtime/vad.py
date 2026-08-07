"""Lightweight energy VAD for Phase 2 sync/timestamps.

Not a neural VAD model — a practical adapter-friendly helper until Silero/LiveKit
VAD is wired. Keeps Meeting Core free of heavy ML deps.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass


@dataclass
class VadResult:
    active: bool
    rms: float
    timestamp_ms: int


def pcm16_rms(pcm: bytes) -> float:
    if not pcm:
        return 0.0
    # Ensure even length for int16 samples
    n = len(pcm) // 2
    if n == 0:
        return 0.0
    samples = struct.unpack("<" + "h" * n, pcm[: n * 2])
    acc = sum(s * s for s in samples)
    return math.sqrt(acc / n)


class EnergyVad:
    def __init__(self, *, threshold: float = 500.0, sample_width: int = 2) -> None:
        self.threshold = threshold
        self.sample_width = sample_width

    def process(self, pcm: bytes, *, timestamp_ms: int) -> VadResult:
        if self.sample_width != 2:
            raise ValueError("Only PCM16 little-endian is supported in Phase 2 VAD")
        rms = pcm16_rms(pcm)
        return VadResult(active=rms >= self.threshold, rms=rms, timestamp_ms=timestamp_ms)


def synthesize_pcm_tone(duration_ms: int = 100, sample_rate: int = 16000, amplitude: int = 3000) -> bytes:
    """Test helper: generate a short PCM16 mono tone."""
    n = int(sample_rate * duration_ms / 1000)
    frames = [int(amplitude * math.sin(2 * math.pi * 440 * i / sample_rate)) for i in range(n)]
    return struct.pack("<" + "h" * n, *frames)
