import os
import time
import requests

import os
import pytest

E2E_ENABLED = os.getenv("NEXUS_E2E", "").strip() == "1"
if not E2E_ENABLED:
    pytest.skip("E2E tests disabled (set NEXUS_E2E=1 to run)", allow_module_level=True)


BASE = os.getenv("NEXUS_TEST_BASE", "http://localhost:8000")
API_KEY = os.getenv("NEXUS_API_KEY", "dev-key")

def _headers():
    return {"X-API-Key": API_KEY}

def test_health():
    r = requests.get(f"{BASE}/health", timeout=10)
    r.raise_for_status()
    j = r.json()
    assert j["status"] in ("ok", "degraded")

def test_metrics():
    r = requests.get(f"{BASE}/metrics", timeout=10)
    r.raise_for_status()
    assert "nexus_task_create_total" in r.text

def test_create_task_and_poll():
    payload = {
        "requested_by": "ci",
        "payload": {
            "sheet_id": "demo",
            "group_name": "CSD-공지",
            "members": [{"name": "홍길동", "phone": "+821012345678"}],
        },
    }
    r = requests.post(f"{BASE}/excel-kakao", json=payload, headers=_headers(), timeout=10)
    r.raise_for_status()
    task_id = r.json()["task_id"]
    assert task_id

    # poll
    for _ in range(40):
        s = requests.get(f"{BASE}/tasks/{task_id}", headers=_headers(), timeout=10)
        s.raise_for_status()
        j = s.json()
        if j["status"] in ("succeeded", "failed"):
            assert j["task_type"] == "excel_kakao"
            return
        time.sleep(1)
    raise AssertionError("task did not finish in time")


ADMIN_KEY = os.getenv("ADMIN_API_KEY", "admin-key")

def _admin_headers():
    return {"X-Admin-Key": ADMIN_KEY}

def test_dlq_peek_empty():
    r = requests.get(f"{BASE}/dlq/peek?limit=3", headers=_admin_headers(), timeout=10)
    r.raise_for_status()
    j = r.json()
    assert "count" in j
