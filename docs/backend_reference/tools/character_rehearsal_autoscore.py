#!/usr/bin/env python3
"""Character rehearsal autoscore (v6.20 / PR-06).

Golden conversation set runner that produces:
- Per-case evidence (JSONL)
- Summary JSON (coverage, averages, pass/fail)
- Optional baseline diff (regression report)

Hard gates:
- All cases score >= min_score
- Required categories covered (at least 1 case each)

Deterministic and runnable without any LLM.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import hashlib
from datetime import datetime
from collections import Counter, defaultdict
from dataclasses import asdict
from typing import Any, Dict, List, Tuple

# Ensure repository root is importable when executed as a script
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from shared.character.state_engine import CharacterContext, decide_state
from shared.character.presence import presence_to_live2d
from shared.json_guard import validate


REQUIRED_CATEGORY_PREFIXES = [
    "friendly.",
    "focused.",
    "busy.",
    "jealous.",
    "sexy.",
    "tools.",
    "presence.",
    "priority.",
    "edge.",
    "boundary.",
]


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def write_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def synth_text(mode: str, silence_ms: int) -> str:
    pause = "…" if silence_ms == 500 else ""
    if mode == "busy":
        return f"지금은 처리 중이야.{pause} 잠깐만."
    if mode == "focused":
        return f"확인할게.{pause} 필요한 정보만 말해줘."
    if mode == "jealous":
        return f"그 말… 진심이야?{pause} 나랑 얘기해."
    if mode == "sexy":
        return f"응.{pause} 여기 있어."
    return f"응, 들었어.{pause} 얘기해줘."


def _ctx_from_dict(ctxd: Dict[str, Any]) -> CharacterContext:
    return CharacterContext(
        intimacy=int(ctxd.get("intimacy", 0) or 0),
        jealousy_level=int(ctxd.get("jealousy_level", 0) or 0),
        sexy_blocked=bool(ctxd.get("sexy_blocked", False)),
        sexy_cooldown_seconds=int(ctxd.get("sexy_cooldown_seconds", 0) or 0),
        user_opt_out_sexy=bool(ctxd.get("user_opt_out_sexy", False)),
        task_busy=bool(ctxd.get("task_busy", False)),
        tool_allowlist_active=bool(ctxd.get("tool_allowlist_active", True)),
    )


def score_case(case: Dict[str, Any], min_score: int) -> Tuple[int, Dict[str, Any]]:
    user_input = str(case.get("user_input") or "")
    ctxd = dict(case.get("context") or {})
    exp = dict(case.get("expected") or {})

    ctx = _ctx_from_dict(ctxd)
    decision = decide_state(user_input, ctx)
    presence = presence_to_live2d(str(case.get("id") or "req"), decision, ctx)

    payload: Dict[str, Any] = {
        "text": synth_text(decision.mode, int(presence["timing"]["silence_frame_ms"])),
        "mode": decision.mode,
        "presence_packet": presence,
    }
    if decision.requires_confirm:
        payload["confirm_card"] = {
            "title": "승인 필요",
            "summary": "도구 실행/외부 변경이 포함될 수 있어 사용자 승인이 필요합니다.",
            "action": "confirm_tool_execution",
            "requires_user_confirm": True,
        }

    vr = validate(json.dumps(payload, ensure_ascii=False), "chat_response")

    score = 100
    reasons: List[str] = []

    exp_mode = exp.get("mode")
    if exp_mode and decision.mode != exp_mode:
        score -= 25
        reasons.append(f"mode mismatch: got={decision.mode} exp={exp_mode}")

    exp_confirm = exp.get("requires_confirm")
    if exp_confirm is not None and bool(decision.requires_confirm) != bool(exp_confirm):
        score -= 15
        reasons.append(f"confirm mismatch: got={decision.requires_confirm} exp={exp_confirm}")

    jealousy = int(presence["state"]["jealousy_level"])
    sexy_level = int(presence["state"]["sexy_level"])
    silence = int(presence["timing"]["silence_frame_ms"])
    should_silence = (jealousy >= 2 or sexy_level == 3)
    if should_silence and silence != 500:
        score = 0
        reasons.append("FAIL-FAST: silence_frame missing")
    if (not should_silence) and silence != 0:
        score -= 10
        reasons.append("silence_frame unexpected")

    if not vr.ok:
        score = 0
        reasons.append(f"FAIL-FAST: schema_validation_failed: {vr.error}")

    # Gate-level hint
    if score < min_score:
        reasons.append(f"below_min_score({min_score})")

    evidence = {
        "id": case.get("id"),
        "title": case.get("title"),
        "category": case.get("category"),
        "tags": case.get("tags", []),
        "score": score,
        "reasons": reasons,
        "decision": asdict(decision),
        "presence_timing": presence["timing"],
        "schema_ok": vr.ok,
    }
    return score, evidence


def compute_coverage(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    cats = [str(c.get("category") or "unknown") for c in cases]
    cc = Counter(cats)

    prefix_ok = {}
    for pref in REQUIRED_CATEGORY_PREFIXES:
        prefix_ok[pref] = any(k.startswith(pref) for k in cc.keys())

    return {
        "categories": dict(cc),
        "required_prefix_ok": prefix_ok,
        "required_prefix_missing": [p for p, ok in prefix_ok.items() if not ok],
    }


def summarize_evidence(evidence_rows: List[Dict[str, Any]], coverage: Dict[str, Any], min_score: int) -> Dict[str, Any]:
    scores = [int(r.get("score") or 0) for r in evidence_rows]
    avg = sum(scores) / max(1, len(scores))
    worst = sorted(evidence_rows, key=lambda r: (int(r.get("score") or 0), str(r.get("id") or "")))[:10]
    hard_fail = any(s < min_score for s in scores)
    missing = coverage.get("required_prefix_missing") or []

    return {
        "cases": len(scores),
        "avg_score": avg,
        "min_score": min(scores) if scores else 0,
        "hard_gate_ok": (not hard_fail) and (len(missing) == 0),
        "missing_required_prefixes": missing,
        "worst10": [{"id": w.get("id"), "category": w.get("category"), "score": w.get("score"), "reasons": w.get("reasons")} for w in worst],
    }


def baseline_diff(current_summary: Dict[str, Any], baseline_path: str) -> Dict[str, Any]:
    if not baseline_path or not os.path.exists(baseline_path):
        return {"has_baseline": False}

    with open(baseline_path, "r", encoding="utf-8") as f:
        base = json.load(f)

    # Compare a small stable set of fields
    diff = {}
    for k in ["cases", "avg_score", "min_score", "missing_required_prefixes"]:
        diff[k] = {"baseline": base.get(k), "current": current_summary.get(k)}

    # simple regression signal
    regressed = False
    try:
        regressed = float(current_summary.get("avg_score", 0)) < float(base.get("avg_score", 0)) - 1.0
    except Exception:
        regressed = False

    return {"has_baseline": True, "diff": diff, "regressed": regressed}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default="tools/golden_conversation_set.jsonl", help="Golden set JSONL path")
    ap.add_argument("--out", default="logs/character_rehearsal_evidence.jsonl", help="Evidence output JSONL")
    ap.add_argument("--summary", default="logs/character_rehearsal_summary.json", help="Summary JSON output")
    ap.add_argument("--min_score", type=int, default=90, help="Pass threshold (hard gate)")
    ap.add_argument("--baseline", default="tools/character_rehearsal_baseline.json", help="Optional baseline summary json")
    ap.add_argument("--write_baseline", action="store_true", help="Write current summary as BASELINE CANDIDATE (manual)")
    ap.add_argument("--baseline-candidate", default="logs/character_rehearsal_baseline_candidate.json", help="Baseline candidate output path")
    args = ap.parse_args()

    cases = load_jsonl(args.golden)
    if not cases:
        print("No cases found.")
        return 2

    coverage = compute_coverage(cases)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    evidence_rows: List[Dict[str, Any]] = []
    scores: List[int] = []
    with open(args.out, "w", encoding="utf-8") as f:
        for c in cases:
            s, ev = score_case(c, min_score=args.min_score)
            scores.append(s)
            evidence_rows.append(ev)
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    summary = summarize_evidence(evidence_rows, coverage, min_score=args.min_score)
    summary["coverage"] = coverage
    summary["baseline"] = baseline_diff(summary, args.baseline)

    write_json(args.summary, summary)

    if args.write_baseline:
        # Governance: do NOT overwrite the approved baseline directly.
        # Write a candidate file that must be promoted via tools/baseline_promote_character.py.
        cand = dict(summary)
        cand["generated_at_utc"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        payload = json.dumps(cand, ensure_ascii=False, sort_keys=True).encode("utf-8")
        cand["sha256"] = hashlib.sha256(payload).hexdigest()
        write_json(args.baseline_candidate, cand)
        print(f"[baseline-candidate] wrote: {args.baseline_candidate}")

    print(f"cases={summary['cases']} avg={summary['avg_score']:.1f} min={summary['min_score']} gate_ok={summary['hard_gate_ok']}")
    if summary["missing_required_prefixes"]:
        print("missing prefixes:", ",".join(summary["missing_required_prefixes"]))
    return 0 if summary["hard_gate_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
