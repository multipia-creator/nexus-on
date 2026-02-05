import unittest
from shared.api_management import TokenBucket, budget_check_and_reserve

class TestAPIManagement(unittest.TestCase):
    def test_token_bucket_allows(self):
        b = TokenBucket(60)
        self.assertTrue(b.allow())

    def test_budget_reserve(self):
        ok, _ = budget_check_and_reserve(0.0)
        self.assertTrue(ok)
