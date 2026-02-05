import json
import time

from shared.callback_rotation import parse_rotatable_secrets, reconcile_expired, rotate_activate_rotatable, dump_rotatable_secrets_json

def test_expiry_reconcile():
    raw = json.dumps([
        {"id":"k1","secret":"s1","active":True, "deactivate_at": int(time.time())-1},
        {"id":"k2","secret":"s2","active":True},
    ])
    secrets = parse_rotatable_secrets(raw)
    secrets, changed = reconcile_expired(secrets, now=int(time.time()))
    assert changed is True
    assert any((s.id=="k1" and s.active is False) for s in secrets)

def test_rotate_sets_deactivate_at():
    raw = json.dumps([
        {"id":"k1","secret":"s1","active":True},
        {"id":"k2","secret":"s2","active":False},
    ])
    secrets = parse_rotatable_secrets(raw)
    secrets, msg = rotate_activate_rotatable(secrets, "k2", grace_seconds=10, now=1000)
    # old active scheduled
    k1 = [s for s in secrets if s.id=="k1"][0]
    assert k1.deactivate_at == 1010
    out = dump_rotatable_secrets_json(secrets)
    assert "deactivate_at" in out
