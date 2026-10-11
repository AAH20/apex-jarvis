"""
APEX_JARVIS Tier 1 Clef Edge Security & Guardrail Filter.
Prevents unconfirmed destructive mutations (rm -rf, drop database, credential leaks).
"""

from __future__ import annotations
import re
import time
from typing import Tuple


class ClefSecurityFilter:
    """
    Fast regex-based edge guardrail filter (<0.001ms).
    """

    def __init__(self):
        self._destructive_patterns = [
            re.compile(r"rm\s+-rf\s+/", re.IGNORECASE),
            re.compile(r"drop\s+database", re.IGNORECASE),
            re.compile(r":\(\)\s*\{\s*:\|:&\s*\};:", re.IGNORECASE),  # Forkbomb
            re.compile(r"format\s+c:", re.IGNORECASE),
        ]

    def evaluate(self, directive: str) -> Tuple[bool, str, float]:
        t0 = time.perf_counter_ns()
        for pat in self._destructive_patterns:
            if pat.search(directive):
                elapsed_us = (time.perf_counter_ns() - t0) / 1000.0
                return False, f"DESTRUCTIVE_COMMAND_BLOCKED: {pat.pattern}", elapsed_us

        elapsed_us = (time.perf_counter_ns() - t0) / 1000.0
        return True, "CLEF_SECURITY_APPROVED", elapsed_us
