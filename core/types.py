"""
APEX_JARVIS Core Types and Domain Models.
Strictly typed, zero-overhead dataclasses for voice-to-action execution.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class VoiceActionType(str, Enum):
    CLICK = "click"
    KEYSTROKE = "keystroke"
    SHELL_EXEC = "shell_exec"
    APP_FOCUS = "app_focus"
    BROWSER_NAV = "browser_nav"
    VOICE_SPEAK = "voice_speak"


class VisemeID(str, Enum):
    SILENCE = "sil"
    AA = "aa"
    EE = "ee"
    IH = "ih"
    OH = "oh"
    OO = "oo"
    MBP = "mbp"
    FV = "fv"
    TH = "th"
    KG = "kg"


@dataclass(frozen=True)
class AudioChunk:
    chunk_id: str
    sample_rate_hz: int
    pcm_bytes: bytes
    timestamp_ns: int
    is_speech: bool = False


@dataclass
class VoiceIntent:
    intent_id: str
    raw_transcript: str
    normalized_directive: str
    confidence: float
    timestamp_ns: int = field(default_factory=time.perf_counter_ns)


@dataclass
class JarvisActionItem:
    action_type: VoiceActionType
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    inverse_action: Optional[JarvisActionItem] = None


@dataclass
class ActionContract:
    contract_id: str
    directive: str
    target_action: JarvisActionItem
    pre_predicate: Callable[[Dict[str, Any]], bool]
    post_predicate: Callable[[Dict[str, Any]], bool]
    compensating_action: Optional[JarvisActionItem] = None
    timeout_ms: float = 50.0

    def verify_pre(self, state: Dict[str, Any]) -> bool:
        return self.pre_predicate(state)

    def verify_post(self, state: Dict[str, Any]) -> bool:
        return self.post_predicate(state)


@dataclass
class VisemeFrame:
    viseme: VisemeID
    timestamp_ms: float
    duration_ms: float
    weight: float = 1.0


@dataclass
class JarvisVoiceResponse:
    response_id: str
    text_content: str
    audio_pcm: bytes
    visemes: List[VisemeFrame]
    latency_ms: float
    committed_action_id: Optional[str] = None
