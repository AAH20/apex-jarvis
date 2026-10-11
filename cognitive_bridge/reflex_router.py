"""
APEX_JARVIS Multi-Tier Reflex Decision Router.
Arbitrates between deterministic Jev shortcuts, Clef security filters, and the host Laya model (:8765).
"""

from __future__ import annotations
import time
from typing import Any, Dict, Optional, Tuple
from core.types import ActionContract, JarvisActionItem, VoiceActionType, VoiceIntent
from cognitive_bridge.clef_security_filter import ClefSecurityFilter
from cognitive_bridge.jev_rule_engine import JevRuleEngine
from cognitive_bridge.laya_model_client import LayaModelClient


class ReflexRouter:
    """
    Sub-millisecond cognitive triage engine.
    """

    def __init__(self, laya_client: Optional[LayaModelClient] = None):
        self.jev = JevRuleEngine()
        self.clef = ClefSecurityFilter()
        self.laya = laya_client or LayaModelClient()

    def route_voice_intent(self, intent: VoiceIntent) -> Tuple[bool, ActionContract, Dict[str, Any]]:
        t0 = time.perf_counter_ns()
        directive = intent.normalized_directive

        # 1. Tier 1: Security Guardrail Check
        allowed, sec_msg, sec_lat_us = self.clef.evaluate(directive)
        if not allowed:
            elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
            abort_action = JarvisActionItem(
                action_type=VoiceActionType.VOICE_SPEAK,
                target="speaker",
                parameters={"warning": sec_msg},
            )
            contract = ActionContract(
                contract_id=f"contract_{intent.intent_id}_blocked",
                directive=directive,
                target_action=abort_action,
                pre_predicate=lambda s: False,  # Immediate abort
                post_predicate=lambda s: True,
            )
            return False, contract, {
                "tier": "tier_1_clef_blocked",
                "reason": sec_msg,
                "latency_ms": elapsed_ms,
            }

        # 2. Tier 0: Deterministic Jev Rule Solver (<0.002ms)
        jev_match = self.jev.match_rule(directive)
        if jev_match:
            action, jev_lat_us = jev_match
            elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
            contract = ActionContract(
                contract_id=f"contract_{intent.intent_id}_jev",
                directive=directive,
                target_action=action,
                pre_predicate=lambda s: s.get("ready", True),
                post_predicate=lambda s: s.get("committed", True),
                compensating_action=action.inverse_action,
            )
            return True, contract, {
                "tier": "tier_0_jev_deterministic",
                "rule_action": action.action_type.value,
                "latency_ms": elapsed_ms,
            }

        # 3. Tier 2: Host Laya Reflex Model (:8765)
        laya_res = self.laya.query_decision(directive)
        elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0

        decision_target = laya_res.get("target", "com.apple.Terminal")
        action = JarvisActionItem(
            action_type=VoiceActionType.APP_FOCUS,
            target=decision_target,
            parameters={"directive": directive, "confidence": laya_res.get("confidence", 0.95)},
            inverse_action=JarvisActionItem(VoiceActionType.KEYSTROKE, "keyboard", {"keys": ["Escape"]}),
        )
        contract = ActionContract(
            contract_id=f"contract_{intent.intent_id}_laya",
            directive=directive,
            target_action=action,
            pre_predicate=lambda s: True,
            post_predicate=lambda s: True,
            compensating_action=action.inverse_action,
        )
        return True, contract, {
            "tier": "tier_2_laya_model",
            "decision": laya_res.get("decision", "FOCUS"),
            "live_service": laya_res.get("live_service", False),
            "latency_ms": elapsed_ms,
        }
