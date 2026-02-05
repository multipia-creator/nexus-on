"""Run DLQ apply as a cron job (recommended: dry-run first).

Usage:
  python ops/run_dlq_apply.py --base-url http://localhost:8000 --admin-key xxx --sample 500 --dry-run true
"""

from __future__ import annotations

import argparse
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", required=True)
    p.add_argument("--admin-key", required=True)
    p.add_argument("--sample", type=int, default=500)
    p.add_argument("--dry-run", default="true")
    p.add_argument("--send-alert", default="true")
    p.add_argument("--max-requeue", type=int, default=200)
    p.add_argument("--max-hold", type=int, default=200)
    p.add_argument("--max-alarm", type=int, default=50)
    args = p.parse_args()

    url = args.base_url.rstrip("/") + "/dlq/apply"
    params = {
        "sample": args.sample,
        "dry_run": args.dry_run.lower() == "true",
        "send_alert": args.send_alert.lower() == "true",
        "max_requeue": args.max_requeue,
        "max_hold": args.max_hold,
        "max_alarm": args.max_alarm,
    }
    headers = {"x-admin-key": args.admin_key}
    r = requests.post(url, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    print(r.json())


if __name__ == "__main__":
    main()
