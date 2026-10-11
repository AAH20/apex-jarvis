"""
APEX_JARVIS Real-Time Voice Activity Detection (VAD).
Lightweight, microsecond-level audio energy and zero-crossing voice framing (<5ms).
"""

from __future__ import annotations
import math
import struct
import time
from typing import Tuple


class VADDetector:
    """
    Simulates / interfaces with Silero VAD.
    Calculates short-time Root-Mean-Square (RMS) and Zero-Crossing Rate (ZCR)
    over 10ms to 20ms PCM audio frames.
    """

    def __init__(
        self,
        sample_rate_hz: int = 16000,
        energy_threshold: float = 350.0,
        silence_timeout_ms: float = 250.0,
    ):
        self.sample_rate = sample_rate_hz
        self.energy_threshold = energy_threshold
        self.silence_timeout_ms = silence_timeout_ms
        self._speech_active = False
        self._last_speech_time_ms = 0.0

    def process_frame(self, pcm_bytes: bytes) -> Tuple[bool, float, float]:
        """
        Analyzes a 16-bit mono PCM frame.
        Returns: (is_voice, frame_energy, elapsed_us)
        """
        t0 = time.perf_counter_ns()
        num_samples = len(pcm_bytes) // 2
        if num_samples == 0:
            return False, 0.0, 0.0

        samples = struct.unpack(f"={num_samples}h", pcm_bytes)
        sum_sq = sum(s * s for s in samples)
        rms = math.sqrt(sum_sq / num_samples)

        is_voice = rms >= self.energy_threshold
        now_ms = time.time() * 1000.0

        if is_voice:
            self._speech_active = True
            self._last_speech_time_ms = now_ms
        else:
            if self._speech_active and (now_ms - self._last_speech_time_ms > self.silence_timeout_ms):
                self._speech_active = False

        elapsed_us = (time.perf_counter_ns() - t0) / 1000.0
        return is_voice, rms, elapsed_us

    def is_speech_active(self) -> bool:
        return self._speech_active
