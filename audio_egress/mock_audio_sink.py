"""
APEX_JARVIS Mock Audio & Viseme Egress Sink.
Collects emitted audio buffers and avatar visemes for latency verification.
"""

from typing import List
from core.types import JarvisVoiceResponse


class MockAudioSink:
    def __init__(self):
        self.received_responses: List[JarvisVoiceResponse] = []

    def consume(self, response: JarvisVoiceResponse) -> int:
        self.received_responses.append(response)
        return len(response.audio_pcm)
