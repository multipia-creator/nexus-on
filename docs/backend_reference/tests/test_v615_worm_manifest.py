import json
import tempfile
import os
import subprocess
import sys

def test_manifest_tool_runs():
    with tempfile.TemporaryDirectory() as d:
        f1 = os.path.join(d, "a.jsonl")
        open(f1,"w",encoding="utf-8").write('{"x":1}\n')
        archive = os.path.join(d, "worm")
        os.makedirs(archive, exist_ok=True)
        env = os.environ.copy()
        env["WORM_ARCHIVE_DIR"] = archive
        env["WORM_MANIFEST_HMAC_KEY"] = "k"
        r = subprocess.run([sys.executable, "tools/worm_snapshot.py", f1], cwd=os.path.dirname(__file__) + "/..", env=env, capture_output=True, text=True)
        assert r.returncode == 0
