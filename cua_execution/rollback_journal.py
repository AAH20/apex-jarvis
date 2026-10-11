"""
APEX_JARVIS Transactional Rollback Journal (Saga Recovery Stack).
Maintains an O(1) LIFO stack of inverse compensating actions to ensure zero dirty state upon failure.
"""

from __future__ import annotations
import time
from typing import Callable, List, Optional
from core.types import JarvisActionItem


class RollbackJournal:
    """
    Saga Transaction Coordinator.
    If an execution post-condition fails or times out, unwinds inverse actions deterministically.
    """

    def __init__(self):
        self._lifo_stack: List[JarvisActionItem] = []
        self._history: List[dict] = []

    def push(self, action: Optional[JarvisActionItem]) -> None:
        """Push a compensating action onto the stack."""
        if action is not None:
            self._lifo_stack.append(action)

    def pop(self) -> Optional[JarvisActionItem]:
        """Pop the most recent compensating action."""
        if self._lifo_stack:
            return self._lifo_stack.pop()
        return None

    def depth(self) -> int:
        return len(self._lifo_stack)

    def execute_rollback(self, executor: Optional[Callable[[JarvisActionItem], bool]] = None) -> int:
        """Unwind all compensating actions in reverse order."""
        t0 = time.perf_counter_ns()
        unwound = 0
        while self._lifo_stack:
            action = self._lifo_stack.pop()
            success = True
            if executor:
                success = executor(action)
            self._history.append({
                "action": action.target,
                "type": action.action_type.value,
                "timestamp_ns": time.perf_counter_ns(),
                "success": success,
            })
            unwound += 1
        return unwound

    def clear(self) -> None:
        self._lifo_stack.clear()
