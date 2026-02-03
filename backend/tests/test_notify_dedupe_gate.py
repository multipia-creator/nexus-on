import unittest
from unittest.mock import patch

from shared.notify import route_payload


class FakeDedupe:
    class R:
        def __init__(self, allowed, ttl):
            self.allowed = allowed
            self.ttl_seconds = ttl

    def __init__(self):
        pass

    def allow(self, key):
        return self.R(False, 123)


class TestNotifyDedupeGate(unittest.TestCase):
    @patch("shared.notify._HAS_DEDUPE", True)
    @patch("shared.notify.AlertDedupe", FakeDedupe)
    def test_suppressed(self):
        payload = {"event": "alarm", "severity": "error", "title": "t", "message": "m", "dedupe_key": "x"}
        res = route_payload(payload, allow_alarm_queue=False, allow_github=False)
        self.assertTrue(res.get("overall_ok"))
        self.assertEqual(res["results"][0]["channel"], "dedupe_suppressed")
        self.assertEqual(res["results"][0]["ttl_seconds"], 123)
