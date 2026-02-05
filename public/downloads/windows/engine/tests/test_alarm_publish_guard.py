import unittest

from shared.notify import _alarm_publish_allowed


class TestAlarmPublishGuard(unittest.TestCase):
    def test_blocks_alarm_worker_origin(self):
        self.assertFalse(_alarm_publish_allowed({"origin": "alarm_worker"}))

    def test_blocks_routed_via_alarm_queue(self):
        self.assertFalse(_alarm_publish_allowed({"origin": "notify", "routed_via": ["alarm_queue"]}))

    def test_allows_default(self):
        self.assertTrue(_alarm_publish_allowed({"origin": "notify"}))

    def test_opt_out_flag(self):
        self.assertFalse(_alarm_publish_allowed({"origin": "notify", "suppress_alarm_queue": True}))
