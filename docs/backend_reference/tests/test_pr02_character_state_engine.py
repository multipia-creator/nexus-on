import json
from shared.character.state_engine import CharacterContext, decide_state, should_auto_trigger_sexy
from shared.character.presence import presence_to_live2d
from shared.json_guard import validate


def test_should_auto_trigger_sexy_threshold():
    ctx = CharacterContext(intimacy=51, jealousy_level=0)
    assert should_auto_trigger_sexy(ctx) is True
    ctx2 = CharacterContext(intimacy=50, jealousy_level=0)
    assert should_auto_trigger_sexy(ctx2) is False


def test_decide_state_priority_busy_jealous_sexy():
    ctx_busy = CharacterContext(intimacy=90, jealousy_level=3, task_busy=True)
    d = decide_state("안녕", ctx_busy)
    assert d.mode == "busy"

    ctx_jealous = CharacterContext(intimacy=90, jealousy_level=2, task_busy=False)
    d2 = decide_state("안녕", ctx_jealous)
    assert d2.mode == "jealous"

    ctx_sexy = CharacterContext(intimacy=80, jealousy_level=0)
    d3 = decide_state("안녕", ctx_sexy)
    assert d3.mode == "sexy"
    assert d3.sexy_level == 3


def test_presence_packet_silence_rule():
    ctx = CharacterContext(intimacy=70, jealousy_level=2)
    d = decide_state("안녕", ctx)
    p = presence_to_live2d("req-1", d, ctx)
    assert p["timing"]["silence_frame_ms"] == 500
    assert p["state"]["mode"] == "jealous"


def test_chat_response_schema_validation():
    ctx = CharacterContext(intimacy=60, jealousy_level=0)
    d = decide_state("안녕", ctx)
    presence = presence_to_live2d("req-2", d, ctx)
    payload = {
        "text": "테스트",
        "mode": d.mode,
        "presence_packet": presence
    }
    vr = validate(json.dumps(payload, ensure_ascii=False), "chat_response")
    assert vr.ok, vr.error
