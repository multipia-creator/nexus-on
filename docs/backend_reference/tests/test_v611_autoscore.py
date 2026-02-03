import unittest
import os

class TestV611(unittest.TestCase):
    def test_autoscore_exists(self):
        self.assertTrue(os.path.exists("tools/rehearsal_autoscore.py"))
