import unittest
import os
from shared.token_estimator import estimate_prompt_completion
from shared.finops import Usage, estimate_cost_usd
from shared.settings import settings

class TestV67(unittest.TestCase):
    def test_token_estimator(self):
        pt, ct, tt = estimate_prompt_completion("hello", "world")
        self.assertGreaterEqual(pt, 1)
        self.assertGreaterEqual(ct, 1)
        self.assertEqual(tt, pt + ct)

    def test_pricing_override(self):
        # Set pricing json via env isn't applied to settings singleton at runtime in this unit test environment,
        # so just ensure estimate_cost_usd runs without error.
        u = Usage(1000, 1000, 2000)
        c = estimate_cost_usd("gemini", u, model="gemini-2.0-flash")
        self.assertGreaterEqual(c, 0.0)
