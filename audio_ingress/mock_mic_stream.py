"""
APEX_JARVIS Synthetic Microphone Stream Generator.
Generates realistic 16kHz 16-bit PCM waveforms with speech and background noise for automated benchmarks.
"""

from __future__ import annotations
import math
import struct
from typing import Iterator


class MockMicStream:
    """
    Produces deterministic 16kHz audio chunks.
    Chunk size: 320 bytes (160 samples = 10ms frame).
    """

    def __init__(self, sample_rate_hz: int = 16000, chunk_duration_ms: int = 10):
        self.sample_rate = sample_rate_hz
        self.samples_per_chunk = (sample_rate_hz * chunk_duration_ms) // 1000
        self.chunk_size_bytes = self.samples_per_chunk * 2

    def generate_silence_chunk(self) -> bytes:
        """Low-amplitude white noise simulating ambient room silence."""
        samples = [int(15 * math.sin(i * 0.1)) for i in range(self.samples_per_chunk)]
        return struct.pack(f"={self.samples_per_chunk}h", *samples)

    def generate_speech_chunk(self, freq_hz: float = 440.0) -> bytes:
        """Synthesized voiced speech tone (RMS > 2000)."""
        samples = [
            int(3000 * math.sin(2 * math.pi * freq_hz * (i / self.sample_rate)))
            for i in range(self.samples_per_chunk)
        ]
        return struct.pack(f"={self.samples_per_chunk}h", *samples)

    def stream_speech_burst(self, num_speech_chunks: int = 20) -> Iterator[bytes]:
        """Streams 5 silence frames, N speech frames, and 5 silence frames."""
        for _ in range(5):
            yield self.generate_silence_chunk()
        for _ in range(num_speech_chunks):
            yield self.generate_speech_chunk()
        for _ in range(5):
            yield self.generate_silence_chunk()
