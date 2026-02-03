import unittest
from unittest.mock import patch

from shared.github_client import upsert_alert_issue


class TestGitHubAlertUpsert(unittest.TestCase):
    @patch("shared.github_client._update_issue_body")
    @patch("shared.github_client._get_issue_body")
    @patch("shared.github_client._search_open_issue_by_dedupe")
    @patch("shared.github_client._repo")
    @patch("shared.github_client.settings")
    def test_upsert_updates_existing(self, st, _repo, search, get_body, upd):
        st.github_token = "tok"
        st.github_repo = "org/repo"
        st.github_api_base = "https://api.github.com"

        _repo.return_value = "org/repo"
        search.return_value = (12, "https://github.com/org/repo/issues/12")
        get_body.return_value = "HEADER\n\n<!-- NEXUS_HISTORY_START -->\n<!-- NEXUS_HISTORY_END -->\n"

        upd.return_value.ok = True
        upd.return_value.status_code = 200
        upd.return_value.url = None
        upd.return_value.error = None

        r = upsert_alert_issue(
            title="[alarm] T",
            header="H",
            entry="E",
            dedupe_key="k1",
            labels=["ops"],
            max_history=3,
        )
        self.assertTrue(r.ok)
        upd.assert_called()
        args, _ = upd.call_args
        self.assertEqual(args[0], 12)
        body2 = args[1]
        self.assertIn("NEXUS_DEDUPE:k1", body2)
        self.assertIn("NEXUS_HISTORY_START", body2)

    @patch("shared.github_client.create_issue")
    @patch("shared.github_client._search_open_issue_by_dedupe")
    @patch("shared.github_client._repo")
    @patch("shared.github_client.settings")
    def test_upsert_creates_new(self, st, _repo, search, create):
        st.github_token = "tok"
        st.github_repo = "org/repo"
        st.github_api_base = "https://api.github.com"

        _repo.return_value = "org/repo"
        search.return_value = (0, "")

        create.return_value.ok = True
        create.return_value.status_code = 201
        create.return_value.url = "https://github.com/org/repo/issues/99"

        r = upsert_alert_issue(
            title="[alarm] T",
            header="H",
            entry="E",
            dedupe_key="k2",
            labels=["ops"],
            max_history=3,
        )
        self.assertTrue(r.ok)
        create.assert_called()
        args, kwargs = create.call_args
        # Body should include dedupe marker somewhere
        body = args[1] if len(args) > 1 else kwargs.get("body", "")
        self.assertIn("NEXUS_DEDUPE:k2", body)
