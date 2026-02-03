import unittest
from unittest.mock import patch, MagicMock
from shared.github_api import request_json, GitHubAPIError

class TestGitHubAPIWrapper(unittest.TestCase):
    @patch("shared.github_api.requests.request")
    def test_retries_on_5xx(self, req):
        r1 = MagicMock(status_code=502, headers={}, json=lambda: {"message":"bad"}, text="bad")
        r2 = MagicMock(status_code=200, headers={}, json=lambda: {"ok": True}, text="ok")
        req.side_effect = [r1, r2]
        code, js, _ = request_json("GET", "https://api.github.com/x", retries=2, base_ms=1, respect_retry_after=False)
        self.assertEqual(code, 200)
        self.assertTrue(js.get("ok"))

    @patch("shared.github_api.requests.request")
    def test_no_retry_on_403(self, req):
        r1 = MagicMock(status_code=403, headers={}, json=lambda: {"message":"forbidden"}, text="forbidden")
        req.return_value = r1
        with self.assertRaises(GitHubAPIError):
            request_json("GET", "https://api.github.com/x", retries=3, base_ms=1)
        self.assertEqual(req.call_count, 1)
