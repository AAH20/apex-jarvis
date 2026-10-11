"""
APEX_JARVIS Tier 0 Deterministic Jev Rule Engine.
Sub-microsecond (<0.002ms) keyword dispatch table for high-frequency voice shortcuts.
"""

from __future__ import annotations
import time
from typing import Dict, Optional, Tuple
from core.types import JarvisActionItem, VoiceActionType


class JevRuleEngine:
    """
    Tier 0 Deterministic Shortcut Solver.
    Zero token cost, zero network overhead.
    """

    def __init__(self):
        self._rules: Dict[str, JarvisActionItem] = {
            "open terminal": JarvisActionItem(
                action_type=VoiceActionType.APP_FOCUS,
                target="com.apple.Terminal",
                parameters={"launch_if_missing": True},
                inverse_action=JarvisActionItem(
                    action_type=VoiceActionType.KEYSTROKE,
                    target="keyboard",
                    parameters={"keys": ["cmd", "h"]},  # Hide app
                ),
            ),
            "revert commit": JarvisActionItem(
                action_type=VoiceActionType.SHELL_EXEC,
                target="terminal_session",
                parameters={"cmd": "git reset --hard HEAD~1"},
                inverse_action=JarvisActionItem(
                    action_type=VoiceActionType.SHELL_EXEC,
                    target="terminal_session",
                    parameters={"cmd": "git reset --hard ORIG_HEAD"},
                ),
            ),
            "close window": JarvisActionItem(
                action_type=VoiceActionType.KEYSTROKE,
                target="keyboard",
                parameters={"keys": ["cmd", "w"]},
                inverse_action=JarvisActionItem(
                    action_type=VoiceActionType.KEYSTROKE,
                    target="keyboard",
                    parameters={"keys": ["cmd", "shift", "t"]},  # Reopen tab
                ),
            ),
            "run tests": JarvisActionItem(
                action_type=VoiceActionType.SHELL_EXEC,
                target="terminal_session",
                parameters={"cmd": "make test"},
            ),
        }

    def match_rule(self, directive: str) -> Optional[Tuple[JarvisActionItem, float]]:
        t0 = time.perf_counter_ns()
        clean = directive.strip().lower()

        for phrase, action in self._rules.items():
            if phrase in clean:
                elapsed_us = (time.perf_counter_ns() - t0) / 1000.0
                return action, elapsed_us

        return None
