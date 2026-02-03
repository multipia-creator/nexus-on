"""NEXUS v6.0 smoke test (dry-run)

Usage:
  python scripts/smoke_test.py --repo org/repo --pr 123

This script does NOT modify GitHub by default. It validates configuration and renders example payloads.
If you set NEXUS_SMOKE_LIVE=true it will attempt a GET of PR + check-runs to validate token access.
"""

import os, argparse, requests
from shared.settings import settings
from shared.github_comments import _get_top_failing_check, _send_webhook_alert

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    args = ap.parse_args()

    print("== env check ==")
    print("AUTOFIX_ALERT_WEBHOOK_ENABLED:", settings.autofix_alert_webhook_enabled)
    print("AUTOFIX_ALERT_WEBHOOK_FORMAT:", settings.autofix_alert_webhook_format)
    print("AUTOFIX_COMMENT_ISSUE_FALLBACK:", settings.autofix_comment_issue_fallback)

    # Override repo function via env for dry-run context
    os.environ["GITHUB_REPOSITORY"] = args.repo

    name, url = _get_top_failing_check(args.pr)
    print("Top failing check:", name, url)

    server = (os.getenv("GITHUB_SERVER_URL") or "https://github.com").rstrip("/")
    pr_url = f"{server}/{args.repo}/pull/{args.pr}"
    checks_url = f"{server}/{args.repo}/pull/{args.pr}/checks"
    run_url = (f"{server}/{args.repo}/actions/runs/{os.getenv('GITHUB_RUN_ID')}" if os.getenv("GITHUB_RUN_ID") else "")

    ok = _send_webhook_alert("[NEXUS smoke] payload rendering OK", pr_url=pr_url, checks_url=checks_url, run_url=run_url, top_check_name=name, top_check_url=url)
    print("Webhook send attempted:", ok)

    if os.getenv("NEXUS_SMOKE_LIVE","").lower() == "true":
        tok = os.getenv("GITHUB_TOKEN","")
        if not tok:
            raise SystemExit("NEXUS_SMOKE_LIVE=true requires GITHUB_TOKEN")
        base = os.getenv("GITHUB_API_URL") or "https://api.github.com"
        r = requests.get(f"{base}/repos/{args.repo}/pulls/{args.pr}", headers={"Authorization": f"Bearer {tok}", "Accept":"application/vnd.github+json"}, timeout=20)
        print("Live PR GET:", r.status_code)
        if r.status_code >= 300:
            print(r.text[:300])
        else:
            sha = ((r.json() or {}).get("head") or {}).get("sha")
            rr = requests.get(f"{base}/repos/{args.repo}/commits/{sha}/check-runs", headers={"Authorization": f"Bearer {tok}", "Accept":"application/vnd.github+json"}, timeout=20)
            print("Live check-runs GET:", rr.status_code)

if __name__ == "__main__":
    main()
