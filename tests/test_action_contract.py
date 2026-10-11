import unittest
from core.types import ActionContract, JarvisActionItem, VoiceActionType
from cua_execution.action_contract_engine import ActionContractEngine
from cua_execution.rollback_journal import RollbackJournal


class TestActionContract(unittest.TestCase):
    def test_pre_condition_enforcement(self):
        journal = RollbackJournal()
        engine = ActionContractEngine(journal)

        contract = ActionContract(
            contract_id="c_test",
            directive="test",
            target_action=JarvisActionItem(VoiceActionType.APP_FOCUS, "Terminal"),
            pre_predicate=lambda s: s.get("power_on", False),  # False
            post_predicate=lambda s: True,
        )

        ok, code, state = engine.execute(contract, {"power_on": False}, lambda act: {})
        self.assertFalse(ok)
        self.assertIn("PRE_CONDITION_VIOLATION", code)

    def test_post_condition_failure_triggers_rollback(self):
        journal = RollbackJournal()
        engine = ActionContractEngine(journal)

        contract = ActionContract(
            contract_id="c_fail",
            directive="fail",
            target_action=JarvisActionItem(VoiceActionType.APP_FOCUS, "Terminal"),
            pre_predicate=lambda s: True,
            post_predicate=lambda s: False,  # Will fail
            compensating_action=JarvisActionItem(VoiceActionType.KEYSTROKE, "keyboard", {"keys": ["Escape"]}),
        )

        ok, code, state = engine.execute(contract, {"state": "clean"}, lambda act: {"state": "dirty"})
        self.assertFalse(ok)
        self.assertIn("ROLLED_BACK", code)
        self.assertEqual(journal.depth(), 0)  # Stack unwound


if __name__ == "__main__":
    unittest.main()
