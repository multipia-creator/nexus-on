import unittest
import os

class TestV610(unittest.TestCase):
    def test_rehearsal_tools_exist(self):
        self.assertTrue(os.path.exists("tools/rehearsal_harness.py"))
        self.assertTrue(os.path.exists("tools/rehearsal_load_test.py"))
        self.assertTrue(os.path.exists("templates/REHEARSAL_SCORECARD.md"))
