import unittest
from shared.errors import classify_http_status, ErrorCode

class TestRetryAfter(unittest.TestCase):
    def test_retry_after_passthrough(self):
        e = classify_http_status(429, "rate limited", retry_after_s=12.0)
        self.assertEqual(e.code, ErrorCode.PROVIDER_RATE_LIMIT)
        self.assertEqual(e.retry_after_s, 12.0)
