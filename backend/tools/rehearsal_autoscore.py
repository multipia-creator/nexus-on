"""Auto-score ops rehearsal and emit a filled scorecard with evidence (v6.22 / PR-08).

Inputs
- logs/llm_audit.jsonl
- logs/llm_cost_ledger.jsonl
- optional: Prometheus textfile export (not required)
- optional: load test output json (if provided)

Outputs
- templates/REHEARSAL_SCORECARD_FILLED.md (default) with PASS/FAIL suggestion

This tool is intentionally conservative: if evidence is missing, marks NG.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

def _read_last_jsonl(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        if not lines:
            return {}
        return json.loads(lines[-1])
    except Exception:
        return {}


def _baseline_governance_status() -> list[str]:
    lines: list[str] = []
    gov_path = "tools/baseline_governance.json"
    base_path = "tools/character_rehearsal_baseline.json"
    cand_path = "logs/character_rehearsal_baseline_candidate.json"
    audit_path = "logs/baseline_audit.jsonl"

    gov = {}
    try:
        if os.path.exists(gov_path):
            gov = json.load(open(gov_path, "r", encoding="utf-8"))
    except Exception:
        gov = {}

    lines.append("#### Baseline Governance Status")
    lines.append(f"- 2인 승인(require_two_person): {bool(gov.get('require_two_person'))}")
    lines.append(f"- 승인 baseline 존재: {os.path.exists(base_path)}")
    lines.append(f"- candidate 존재: {os.path.exists(cand_path)}")

    last = _read_last_jsonl(audit_path) if os.path.exists(audit_path) else {}
    if last.get("event") == "baseline_promote":
        lines.append(f"- 마지막 승인(UTC): {last.get('ts_utc')}")
        a1 = last.get("approver")
        a2 = last.get("approver2")
        if a1 or a2:
            lines.append(f"- 승인자: {a1}{(' / ' + a2) if a2 else ''}")
        sha = last.get("new_baseline_sha256") or ""
        if sha:
            lines.append(f"- baseline sha256: {sha[:12]}…")
    else:
        lines.append("- 마지막 승인 이벤트: 없음")
    return lines

# Ensure repository root is importable when executed as a script
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from shared.settings import settings


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    out: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out

def load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def summarize_character_from_evidence(evidence_path: str) -> Dict[str, Any]:
    if not os.path.exists(evidence_path):
        return {"cases": 0, "avg_score": 0.0, "min_score": 0, "details": "missing evidence"}
    scores = []
    with open(evidence_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                scores.append(int(row.get("score") or 0))
            except Exception:
                continue
    if not scores:
        return {"cases": 0, "avg_score": 0.0, "min_score": 0, "details": "empty evidence"}
    return {"cases": len(scores), "avg_score": sum(scores)/len(scores), "min_score": min(scores)}




def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(ts: str) -> Optional[datetime]:
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def within(rows: List[Dict[str, Any]], minutes: int) -> List[Dict[str, Any]]:
    since = now_utc() - timedelta(minutes=minutes)
    out = []
    for r in rows:
        t = parse_ts(str(r.get("ts_utc") or ""))
        if t and t >= since:
            out.append(r)
    return out


def summarize_smoke(audit_rows: List[Dict[str, Any]], ledger_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    a = within(audit_rows, 120)
    l = within(ledger_rows, 120)
    ok_call = any(r.get("type") == "llm_success" for r in a)
    ok_ledger = any((r.get("actual_cost_usd") or 0) or r.get("approx_tokens") for r in l)
    sample_a = next((r for r in reversed(a) if r.get("type") == "llm_success"), None)
    sample_l = next((r for r in reversed(l) if (r.get("actual_cost_usd") or 0) or r.get("approx_tokens") is not None), None)
    return {
        "llm_call": ok_call,
        "ledger": ok_ledger,
        "audit_sample": sample_a,
        "ledger_sample": sample_l,
    }


def dedupe_hit_present(audit_rows: List[Dict[str, Any]]) -> bool:
    a = within(audit_rows, 240)
    return any(r.get("type") == "llm_dedupe_hit" for r in a)


def tagging_present(ledger_rows: List[Dict[str, Any]]) -> bool:
    l = within(ledger_rows, 240)
    for r in l:
        if r.get("team") and r.get("project") and (r.get("team") != "default" or r.get("project") != "nexus"):
            return True
    return False


def load_test_summary(path: str) -> Optional[Dict[str, Any]]:
    if not path:
        return None
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None



def run_character_rehearsal(golden_path: str, out_path: str, summary_path: str, baseline_path: str, min_score: int) -> Dict[str, Any]:
    """Run character rehearsal autoscore and return summary.

    This is a hard gate for production readiness of the character layer.
    If the tool fails or evidence is missing, returns NG.
    """
    try:
        import sys
        cmd = [sys.executable, "tools/character_rehearsal_autoscore.py", "--golden", golden_path, "--out", out_path, "--summary", summary_path, "--baseline", baseline_path, "--min_score", str(min_score)]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        ok_run = (p.returncode == 0)
        rich = load_json(summary_path)
        summary = dict(rich) if rich else summarize_character_from_evidence(out_path)
        summary["character_rehearsal"] = bool(summary.get("hard_gate_ok", summary.get("min_score", 0) >= min_score))
        summary["tool_rc"] = p.returncode
        summary["tool_stdout_tail"] = (p.stdout or "")[-400:]
        summary["tool_stderr_tail"] = (p.stderr or "")[-400:]
        # If tool run failed, force NG even if stale evidence exists
        if not ok_run:
            summary["character_rehearsal"] = False
            summary["details"] = "tool failed"
        return summary
    except Exception as e:
        return {"character_rehearsal": False, "details": f"exception: {e}"}


def render_scorecard(env: Dict[str, Any], results: Dict[str, Any]) -> str:
    dt = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append("# NEXUS 운영 리허설 스코어카드 (v6.22 / PR-08 자동 생성)")
    lines.append("")
    lines.append("환경")
    lines.append(f"- 날짜/시간(UTC): {now_utc().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 배포 버전: 6.22.0")
    lines.append(f"- 실행 환경(단일/멀티 노드, Redis 유무): {env.get('topology','unknown')}")
    lines.append(f"- 사용 Provider(우선/옵션): {env.get('providers','unknown')}")
    lines.append("")
    lines.append("0. Baseline Governance")
    for ln in _baseline_governance_status():
        lines.append(ln)
    lines.append("")
    # A
    sm = results["smoke"]
    lines.append("A. 30분 스모크")
    lines.append(f"1) LLM 호출/응답: {'OK' if sm['llm_call'] else 'NG'}")
    if sm["audit_sample"]:
        lines.append(f"- 증적(audit sample): {json.dumps(sm['audit_sample'], ensure_ascii=False)[:300]}")
    lines.append(f"2) cost ledger 기록: {'OK' if sm['ledger'] else 'NG'}")
    if sm["ledger_sample"]:
        lines.append(f"- 증적(ledger sample): {json.dumps(sm['ledger_sample'], ensure_ascii=False)[:300]}")
    lines.append("3) finops_report 생성: MANUAL")
    lines.append("- 증적: logs/finops_rehearsal.md 존재 여부를 확인")
    lines.append("4) 알림 배선: MANUAL")
    lines.append("- 증적: Slack/Teams 수신 확인(웹훅은 외부 시스템)")
    lines.append("")
    # B
    lines.append("B. 2시간 리허설")
    lines.append(f"5) Dedupe hit 확인: {'OK' if results['dedupe_hit'] else 'NG'}")
    lines.append(f"6) 태깅(team/project) 분리: {'OK' if results['tagging'] else 'NG'}")
    lt = results.get("load_test")
    if lt:
        ok = (lt.get("fail", 1) == 0)
        lines.append(f"7) 저강도 부하(p50/p95, fail율): {'OK' if ok else 'NG'}")
        lines.append(f"- 결과: {json.dumps(lt, ensure_ascii=False)}")
    else:
        lines.append("7) 저강도 부하(p50/p95, fail율): MANUAL")
        lines.append("- 증적: tools/rehearsal_load_test.py 출력 기록")
    lines.append("")
    # D
    ch = results.get("character", {})
    lines.append("D. 캐릭터 리허설 (하드 게이트)")
    lines.append(f"10) GoldenSet 자동채점: {'OK' if ch.get('character_rehearsal') else 'NG'}")
    if ch:
        lines.append(f"- 평균 점수/케이스: {ch.get('avg_score','?')}/{ch.get('cases','?')}")
        cov = (ch.get("coverage") or {})
        if cov:
            missing = (cov.get("required_prefix_missing") or [])
            lines.append(f"- 커버리지(필수 prefix): {'OK' if not missing else 'NG'} (missing={missing})")
            cats = cov.get("categories") or {}
            lines.append(f"- 카테고리 수: {len(cats)}")
        base = (ch.get("baseline") or {})
        if base.get("has_baseline"):
            # baseline metadata (if present)
            meta_ts = ch.get("approved_at_utc") or ch.get("generated_at_utc")
            if meta_ts:
                lines.append(f"- 베이스라인 시각(UTC): {meta_ts}")
            meta_by = ch.get("approved_by")
            if meta_by:
                lines.append(f"- 베이스라인 승인자: {meta_by}")
            meta_sha = ch.get("sha256")
            if meta_sha:
                lines.append(f"- 베이스라인 sha256: {meta_sha[:12]}…")

            reg = base.get("regressed")
            lines.append(f"- 베이스라인 비교: {'REGRESSION' if reg else 'OK'}")
        if ch.get("details"):
            lines.append(f"- 상세: {ch.get('details')}")
        if ch.get("tool_rc") is not None:
            lines.append(f"- 증적(out): logs/character_rehearsal_evidence.jsonl (rc={ch.get('tool_rc')})")
            lines.append(f"- 요약(summary): logs/character_rehearsal_summary.json")
    lines.append("")

    # C
    lines.append("C. 1일 리허설")
    lines.append("8) 크론 스케줄 동작: MANUAL")
    lines.append("9) 장애–복구 라운드트립: MANUAL")
    lines.append("")
    # Final
    must_ok = [sm["llm_call"], sm["ledger"], results["dedupe_hit"], results["tagging"], bool(results.get("character", {}).get("character_rehearsal"))]
    passed = all(must_ok)
    lines.append("최종 판정")
    lines.append(f"- {'PASS' if passed else 'FAIL'}")
    fixes = []
    if not sm["llm_call"]:
        fixes.append("Provider 키/네트워크/timeout 설정 점검 (LLM 호출 실패)")
    if not sm["ledger"]:
        fixes.append("LLM_COST_LEDGER_PATH 권한/경로 점검 (ledger 미기록)")
    if not results["dedupe_hit"]:
        fixes.append("LLM_DEDUPE_ENABLED/TTL/목적(purpose) 및 Redis 연결 점검 (dedupe 미작동)")
    if not results["tagging"]:
        fixes.append("LLM_DEFAULT_TEAM/PROJECT 또는 generate(context=...) 전달 점검 (태깅 미분리)")
    if not fixes:
        fixes = ["(없음) — 운영 핵심 신호가 정상입니다."]
    lines.append("- Top 3 Fixes:")
    for i, f in enumerate(fixes[:3], 1):
        lines.append(f"  {i}) {f}")
    lines.append("")
    lines.append("비고")
    lines.append("- MANUAL 항목은 외부 시스템/운영 환경 의존(웹훅 수신, 크론, 장애 유도 등)이라 자동화에서 제외했습니다.")
    return "\n".join(lines) + "\n"




def summarize_character_rehearsal() -> Dict[str, Any]:
    path = "logs/character_rehearsal_evidence.jsonl"
    if not os.path.exists(path):
        return {"character_rehearsal": False, "details": "missing evidence file"}
    rows = load_jsonl(path)
    if not rows:
        return {"character_rehearsal": False, "details": "empty evidence file"}
    # pass if all scores >= 90 (default expectation)
    ok = all((r.get("score") or 0) >= 90 for r in rows)
    avg = sum((r.get("score") or 0) for r in rows) / max(1, len(rows))
    return {"character_rehearsal": ok, "avg_score": avg, "cases": len(rows)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default=str(getattr(settings, "llm_audit_log_path", "logs/llm_audit.jsonl")))
    ap.add_argument("--ledger", default=str(getattr(settings, "llm_cost_ledger_path", "logs/llm_cost_ledger.jsonl")))
    ap.add_argument("--load-test-json", default="", help="Optional path to JSON summary from load test")
    ap.add_argument("--out", default="templates/REHEARSAL_SCORECARD_FILLED.md")
    ap.add_argument("--topology", default="unknown", help="single|multi + redis yes/no")
    ap.add_argument("--providers", default="unknown", help="e.g., gemini-first (openai/anthropic/glm optional)")
    ap.add_argument("--run-character", dest="run_character", action="store_true", help="Run character rehearsal autoscore (hard gate)")
    ap.add_argument("--no-run-character", dest="run_character", action="store_false", help="Skip character rehearsal (NOT recommended)")
    ap.set_defaults(run_character=True)
    ap.add_argument("--character-golden", default="tools/golden_conversation_set.jsonl")
    ap.add_argument("--character-out", default="logs/character_rehearsal_evidence.jsonl")
    ap.add_argument("--character-summary", default="logs/character_rehearsal_summary.json")
    ap.add_argument("--character-baseline", default="tools/character_rehearsal_baseline.json")
    ap.add_argument("--character-min-score", type=int, default=90)
    args = ap.parse_args()

    audit_rows = load_jsonl(args.audit)
    ledger_rows = load_jsonl(args.ledger)

    character_summary = None
    if args.run_character:
        character_summary = run_character_rehearsal(args.character_golden, args.character_out, args.character_summary, args.character_baseline, args.character_min_score)
    else:
        character_summary = {"character_rehearsal": False, "details": "skipped"}

    results = {
        "smoke": summarize_smoke(audit_rows, ledger_rows),
        "dedupe_hit": dedupe_hit_present(audit_rows),
        "tagging": tagging_present(ledger_rows),
        "load_test": load_test_summary(args.load_test_json),
        "character": character_summary,
    }
    env = {"topology": args.topology, "providers": args.providers}
    md = render_scorecard(env, results)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())