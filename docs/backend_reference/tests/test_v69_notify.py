import unittest
import os

class TestV69(unittest.TestCase):
    def test_anomaly_tool_exists(self):
        self.assertTrue(os.path.exists("tools/anomaly_watch.py"))
