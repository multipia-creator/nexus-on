import unittest
import os

class TestV68(unittest.TestCase):
    def test_report_tool_exists(self):
        self.assertTrue(os.path.exists("tools/finops_report.py"))
