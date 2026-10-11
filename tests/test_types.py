import unittest
import time
from core.types import (
    AudioChunk,
    VoiceIntent,
    VoiceActionType,
    JarvisActionItem,
    ActionContract,
    VisemeID,
    VisemeFrame,
)


class TestJarvisTypes(unittest.TestCase):
    def test_voice_intent_schema(self):
        intent = VoiceIntent(
            intent_id="vi_001",
            raw_transcript="Open terminal and run tests",
            normalized_directive="open terminal and run tests",
            confidence=0.98,
        )
        self.assertEqual(intent.intent_id, "vi_001")
        self.assertTrue(intent.confidence > 0.9)

    def test_action_contract_evaluation(self):
        contract = ActionContract(
            contract_id="c_001",
            directive="focus terminal",
            target_action=JarvisActionItem(VoiceActionType.APP_FOCUS, "com.apple.Terminal"),
            pre_predicate=lambda s: s.get("ready", True),
            post_predicate=lambda s: s.get("focused", True),
        )
        self.assertTrue(contract.verify_pre({"ready": True}))
        self.assertFalse(contract.verify_pre({"ready": False}))
        self.assertTrue(contract.verify_post({"focused": True}))


if __name__ == "__main__":
    unittest.main()
