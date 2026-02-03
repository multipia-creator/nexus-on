import json
import subprocess
import sys
import os


def test_character_rehearsal_produces_summary_and_coverage(tmp_path):
    out = tmp_path / "evidence.jsonl"
    summary = tmp_path / "summary.json"
    proc = subprocess.run(
        [sys.executable, "tools/character_rehearsal_autoscore.py", "--golden", "tools/golden_conversation_set.jsonl", "--out", str(out), "--summary", str(summary), "--min_score", "0"],
        capture_output=True,
        text=True,
        cwd=".",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert summary.exists()
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert "coverage" in data
    cov = data["coverage"]
    assert "required_prefix_ok" in cov
    # at least one required prefix is True
    assert any(cov["required_prefix_ok"].values())
