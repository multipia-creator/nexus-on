import unittest
from shared.backoff import compute_backoff_s
from shared.dedupe import DedupeStore

class TestFinOps(unittest.TestCase):
    def test_backoff_nonnegative(self):
        self.assertGreaterEqual(compute_backoff_s(0), 0.0)

    def test_dedupe_store_basic(self):
        ds = DedupeStore()
        # store might be disabled by env, but default is enabled
        ds.set("k", provider="gemini", model="m", text="t")
        hit = ds.get("k")
        # In file fallback, hit should exist; in redis disabled might still exist. Best-effort.
        if ds.enabled:
            self.assertIsNotNone(hit)
