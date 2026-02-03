import unittest
from shared.github_comments import _update_body_with_history, NEXUS_HISTORY_START, NEXUS_HISTORY_END

class TestIssueHistoryBody(unittest.TestCase):
    def test_insert_markers_and_limit(self):
        base = "HEADER\n\n" + NEXUS_HISTORY_START + "\n" + NEXUS_HISTORY_END + "\n"
        body = _update_body_with_history(base, "E1", max_entries=2)
        body = _update_body_with_history(body, "E2", max_entries=2)
        body = _update_body_with_history(body, "E3", max_entries=2)
        self.assertIn(NEXUS_HISTORY_START, body)
        self.assertIn(NEXUS_HISTORY_END, body)
        self.assertIn("E3", body)
        self.assertIn("E2", body)
        self.assertNotIn("E1", body)
