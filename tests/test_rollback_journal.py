import unittest
from core.types import JarvisActionItem, VoiceActionType
from cua_execution.rollback_journal import RollbackJournal


class TestRollbackJournal(unittest.TestCase):
    def test_lifo_compensation_order(self):
        journal = RollbackJournal()
        a1 = JarvisActionItem(VoiceActionType.KEYSTROKE, "k1")
        a2 = JarvisActionItem(VoiceActionType.KEYSTROKE, "k2")

        journal.push(a1)
        journal.push(a2)
        self.assertEqual(journal.depth(), 2)

        executed_order = []
        journal.execute_rollback(lambda a: executed_order.append(a.target) or True)

        self.assertEqual(executed_order, ["k2", "k1"])  # LIFO order
        self.assertEqual(journal.depth(), 0)


if __name__ == "__main__":
    unittest.main()
