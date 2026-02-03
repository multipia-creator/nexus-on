\
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional, Tuple

import requests

def now_iso() -> str:
    # localtime ISO without milliseconds
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())

def load_config() -> Dict[str, Any]:
    cfg_path = os.environ.get("NEXUS_COMPANION_CONFIG", "config.json")
    if not os.path.exists(cfg_path):
        print(f"[!] Missing {cfg_path}. Copy config.example.json -> config.json and edit.")
        sys.exit(1)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)

def headers_tenant(cfg: Dict[str, Any]) -> Dict[str, str]:
    return {
        "x-org-id": cfg.get("org_id", "o"),
        "x-project-id": cfg.get("project_id", "p"),
    }

def post_json(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    if r.status_code >= 300:
        raise RuntimeError(f"POST {url} failed: {r.status_code} {r.text}")
    return r.json()

def get_json(url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code >= 300:
        raise RuntimeError(f"GET {url} failed: {r.status_code} {r.text}")
    return r.json()

def auth_headers(token: str) -> Dict[str, str]:
    return {"authorization": f"Bearer {token}"}

def start_pairing(cfg: Dict[str, Any]) -> Tuple[str, str, str]:
    base = cfg["backend_base_url"].rstrip("/")
    resp = post_json(
        f"{base}/devices/pairing/start",
        {
            "device_type": "windows_companion",
            "device_name": cfg.get("device_name", "HW-PC"),
            "capabilities": cfg.get("capabilities", []),
        },
        headers={"content-type": "application/json", **headers_tenant(cfg)},
    )
    return resp["pairing_id"], resp["pairing_code"], resp["device_nonce"]

def wait_and_complete(cfg: Dict[str, Any], pairing_id: str, device_nonce: str) -> Tuple[str, str]:
    base = cfg["backend_base_url"].rstrip("/")
    # Wait until web confirms the code; then claim device token via complete
    while True:
        try:
            resp = post_json(
                f"{base}/devices/pairing/complete",
                {"pairing_id": pairing_id, "device_nonce": device_nonce},
                headers={"content-type": "application/json"},
            )
            return resp["device_id"], resp["device_token"]
        except Exception as e:
            # Not confirmed yet; keep waiting
            time.sleep(1.5)

def send_heartbeat(cfg: Dict[str, Any], device_id: str, token: str) -> None:
    base = cfg["backend_base_url"].rstrip("/")
    payload = {"status": "online", "metrics": {}, "agent_version": "win-companion-poc-1.0"}
    r = requests.post(
        f"{base}/devices/{device_id}/heartbeat",
        json=payload,
        headers={"content-type": "application/json", **auth_headers(token)},
        timeout=10,
    )
    # ignore non-2xx for now; raise only if hard errors
    if r.status_code >= 300:
        raise RuntimeError(f"heartbeat failed: {r.status_code} {r.text}")

def pull_commands(cfg: Dict[str, Any], device_id: str, token: str, cursor: Optional[str]) -> Tuple[list, Optional[str]]:
    base = cfg["backend_base_url"].rstrip("/")
    url = f"{base}/devices/{device_id}/commands"
    if cursor:
        url += f"?cursor={cursor}"
    resp = get_json(url, headers=auth_headers(token))
    return resp.get("commands", []), resp.get("next_cursor")

def ack(cfg: Dict[str, Any], device_id: str, token: str, command_id: str) -> None:
    base = cfg["backend_base_url"].rstrip("/")
    post_json(
        f"{base}/devices/{device_id}/commands/{command_id}/ack",
        {"received_at": now_iso()},
        headers={"content-type": "application/json", **auth_headers(token)},
    )

def approval_level_from_risk(risk: str) -> str:
    r = (risk or "").upper()
    if r == "RED":
        return "red"
    if r == "YELLOW":
        return "yellow"
    return "green"

def push_report(cfg: Dict[str, Any], device_id: str, token: str, report: Dict[str, Any]) -> None:
    base = cfg["backend_base_url"].rstrip("/")
    post_json(
        f"{base}/devices/{device_id}/reports",
        {"reports": [report]},
        headers={"content-type": "application/json", **auth_headers(token)},
    )

def make_report(cfg: Dict[str, Any], approval_level: str, title: str, detail: str, correlation_id: str = "") -> Dict[str, Any]:
    tenant = f"{cfg.get('org_id','o')}:{cfg.get('project_id','p')}"
    session_id = cfg.get("session_id", "s1")
    return {
        "meta": {
            "mode": "focused",
            "approval_level": approval_level,
            "confidence": 0.85,
            "report_id": f"dev_{int(time.time()*1000)}",
            "created_at": now_iso(),
            "event_id": 0,
            "tenant": tenant,
            "session_id": session_id,
            "user_id": "u",
            "json_repaired": False,
            "causality": {"correlation_id": correlation_id, "command_id": None, "ask_id": None, "type": "device.exec"},
        },
        "done": [{"title": title, "detail": detail}],
        "next": [],
        "blocked": [],
        "ask": [],
        "risk": [],
        "rationale": "",
        "undo": [],
        "ui_hint": {"surface": "dashboard", "cards": [{"type":"note","title": title, "body": detail}], "actions": []},
        "persona_id": "seria.istj",
        "skin_id": "seria.default",
    }

def run_allowlisted_command(cmd_type: str, params: Dict[str, Any]) -> str:
    # Minimal allowlist for POC
    cmd_type = (cmd_type or "").lower()
    if cmd_type == "os.open_app":
        app_id = (params or {}).get("app_id", "notepad")
        mapping = {
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
        }
        exe = mapping.get(app_id, app_id)
        subprocess.Popen([exe], shell=False)
        return f"opened app: {exe}"
    if cmd_type == "os.open_url":
        url = (params or {}).get("url", "https://example.com")
        # Windows: use 'start' to open default browser
        subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)
        return f"opened url: {url}"
    if cmd_type == "system.say":
        text = (params or {}).get("text", "ok")
        # POC: no TTS; just log
        return f"say: {text}"
    raise RuntimeError(f"command not allowed: {cmd_type}")

def main():
    cfg = load_config()
    pairing_id, pairing_code, device_nonce = start_pairing(cfg)
    print("=== NEXUS Windows Companion (POC) ===")
    print(f"Pairing code: {pairing_code}")
    print("Enter this code in Web UI -> Devices -> Confirm")
    print("(Waiting for confirmation...)")

    device_id, token = wait_and_complete(cfg, pairing_id, device_nonce)
    print(f"[OK] Paired. device_id={device_id}")
    print("Running sync loop (Ctrl+C to stop).")

    cursor = None
    last_hb = 0.0
    hb_interval = float(cfg.get("heartbeat_interval_sec", 10.0))
    poll_interval = float(cfg.get("poll_interval_sec", 2.0))

    # initial report
    push_report(cfg, device_id, token, make_report(cfg, "green", "paired", f"device {device_id} is online"))

    while True:
        now = time.time()
        if now - last_hb > hb_interval:
            send_heartbeat(cfg, device_id, token)
            last_hb = now

        cmds, cursor = pull_commands(cfg, device_id, token, cursor)
        for c in cmds:
            command_id = c.get("command_id", "")
            cmd_type = c.get("type", "")
            params = c.get("params", {}) or {}
            cc = (c.get("client_context") or {})
            corr = cc.get("correlation_id") or ""
            policy = c.get("policy") or {}
            approval = approval_level_from_risk(policy.get("risk", "YELLOW"))

            try:
                result = run_allowlisted_command(cmd_type, params)
                push_report(cfg, device_id, token, make_report(cfg, approval, cmd_type, result, correlation_id=corr))
            except Exception as e:
                push_report(cfg, device_id, token, make_report(cfg, "yellow", "error", f"{cmd_type}: {e}", correlation_id=corr))
            finally:
                if command_id:
                    try:
                        ack(cfg, device_id, token, command_id)
                    except Exception:
                        pass

        time.sleep(poll_interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n[stop]")
