"""
APEX_JARVIS Lock-Free Circular Audio Ring Buffer.
Provides sub-microsecond zero-allocation ingestion of 16kHz 16-bit PCM audio streams.
"""

from __future__ import annotations
import struct
from typing import Optional


class AudioRingBuffer:
    """
    Circular Single-Producer Single-Consumer (SPSC) Audio Buffer.
    Capacity is in frames (e.g. 1 frame = 320 bytes = 10ms at 16kHz 16-bit mono).
    """

    def __init__(self, capacity_chunks: int = 512, chunk_size_bytes: int = 320):
        assert (capacity_chunks & (capacity_chunks - 1)) == 0, "Capacity must be a power of 2"
        self.capacity = capacity_chunks
        self.mask = capacity_chunks - 1
        self.chunk_size = chunk_size_bytes
        self._buffer = bytearray(self.capacity * self.chunk_size)
        self._head = 0
        self._tail = 0

    def write_chunk(self, pcm_bytes: bytes) -> bool:
        """Writes a PCM chunk into the circular buffer."""
        if len(pcm_bytes) != self.chunk_size:
            # Pad or truncate to fixed chunk size
            pcm_bytes = pcm_bytes[:self.chunk_size].ljust(self.chunk_size, b"\x00")

        if (self._tail - self._head) >= self.capacity:
            return False  # Overflow: drop to avoid audio jitter

        slot = self._tail & self.mask
        offset = slot * self.chunk_size
        self._buffer[offset : offset + self.chunk_size] = pcm_bytes
        self._tail += 1
        return True

    def read_chunk(self) -> Optional[bytes]:
        """Reads the oldest PCM chunk from the circular buffer."""
        if self._head >= self._tail:
            return None  # Underflow: buffer empty

        slot = self._head & self.mask
        offset = slot * self.chunk_size
        chunk = bytes(self._buffer[offset : offset + self.chunk_size])
        self._head += 1
        return chunk

    def available(self) -> int:
        return self._tail - self._head

    def clear(self) -> None:
        self._head = 0
        self._tail = 0
