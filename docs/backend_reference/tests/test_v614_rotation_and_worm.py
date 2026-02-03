import os
import json
import tempfile

from shared.worm_archive import archive_file
from shared.callback_rotation import load_callback_secrets, rotate_activate, dump_secrets_json

def test_worm_archive_file_copy():
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "a.jsonl")
        with open(src, "w", encoding="utf-8") as f:
            f.write('{"x":1}\n')
        ad = os.path.join(d, "worm")
        dst = archive_file(src, ad, chmod_readonly=False)
        assert dst is not None
        assert os.path.exists(dst)

def test_rotation_activate_and_dump():
    raw = json.dumps([
        {"id":"k1","secret":"s1","active":True},
        {"id":"k2","secret":"s2","active":False},
    ])
    secrets = load_callback_secrets("env", raw, "")
    updated, msg = rotate_activate(secrets, "k2")
    out = dump_secrets_json(updated)
    assert "k2" in out
