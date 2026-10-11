import unittest
from cognitive_bridge.laya_model_client import LayaModelClient
from cognitive_bridge.jev_rule_engine import JevRuleEngine
from cognitive_bridge.clef_security_filter import ClefSecurityFilter
from cognitive_bridge.reflex_router import ReflexRouter
from core.types import VoiceIntent


class TestCognitiveBridge(unittest.TestCase):
    def test_jev_rule_engine_hit(self):
        jev = JevRuleEngine()
        match = jev.match_rule("open terminal right now")
        self.assertIsNotNone(match)
        action, lat_us = match
        self.assertEqual(action.target, "com.apple.Terminal")
        self.assertLess(lat_us, 50.0)

    def test_clef_security_blocking(self):
        clef = ClefSecurityFilter()
        ok, msg, lat_us = clef.evaluate("rm -rf /")
        self.assertFalse(ok)
        self.assertIn("DESTRUCTIVE", msg)

    def test_reflex_router_flow(self):
        router = ReflexRouter()
        intent = VoiceIntent("vi_01", "revert commit", "revert commit", 0.99)
        ok, contract, meta = router.route_voice_intent(intent)
        self.assertTrue(ok)
        self.assertEqual(meta["tier"], "tier_0_jev_deterministic")
        self.assertEqual(contract.target_action.parameters["cmd"], "git reset --hard HEAD~1")


if __name__ == "__main__":
    unittest.main()
