import subprocess
import sys


def test_character_rehearsal_autoscore_runs():
    # Ensure tool runs and returns 0/1 deterministically; for unit test keep min_score low
    proc = subprocess.run(
        [sys.executable, "tools/character_rehearsal_autoscore.py", "--golden", "tools/golden_conversation_set.jsonl", "--min_score", "0"],
        capture_output=True,
        text=True,
        cwd=".",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
