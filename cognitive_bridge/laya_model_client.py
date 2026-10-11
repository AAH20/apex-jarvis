"""
APEX_JARVIS Laya Model Client.
Direct, proxy-free HTTP interface to the live Hermes Reflex Laya service on port 8765.
Model: convaiinnovations/laya-typed-decisions
"""

from __future__ import annotations
import json
import time
import urllib.request
from typing import Any, Dict, Optional


class LayaModelClient:
    """
    Client for the host Laya System-1 reflex service.
    Bypasses environmental HTTP proxies via an empty ProxyHandler.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8765",
        model_name: str = "convaiinnovations/laya-typed-decisions",
        timeout_seconds: float = 1.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout_seconds
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def check_health(self) -> Dict[str, Any]:
        """Queries /healthz on the active Laya service."""
        url = f"{self.base_url}/healthz"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            return {"ok": False, "error": str(exc), "provider": "Laya (Offline/Unreachable)"}

    def query_decision(self, directive: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Dispatches spoken directive to Laya System-1 reflex.
        Returns typed choice decision in sub-10ms.
        """
        t0 = time.perf_counter_ns()
        url = f"{self.base_url}/v1/systemone"
        payload = {
            "state": context or {"active_app": "com.apple.Terminal", "focused": True},
            "questions": {
                "directive": directive,
                "options": ["EXECUTE_TERMINAL", "FOCUS_IDE", "REVERT_GIT", "SAFE_DISMISS"],
                "criteria": ["safety", "latency", "reversibility"],
            },
            "model": self.model_name,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )

        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
                result["latency_ms"] = round(elapsed_ms, 3)
                result["live_service"] = True
                return result
        except Exception as exc:
            # Fallback to local heuristic if host socket is sandboxed
            elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
            return {
                "decision": "EXECUTE_LOCAL_FALLBACK",
                "target": "com.apple.Terminal",
                "confidence": 0.92,
                "latency_ms": round(elapsed_ms, 3),
                "live_service": False,
                "fallback_reason": str(exc),
            }
