import yaml
from pathlib import Path

def test_openapi_has_core_endpoints():
    p = Path("openapi.yaml")
    assert p.exists(), "openapi.yaml missing"
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    paths = doc.get("paths", {})
    for ep in ("/health", "/excel-kakao", "/tasks/{task_id}", "/agent/callback", "/llm/generate", "/metrics", "/dlq/peek", "/dlq/requeue", "/dlq/purge"):
        assert ep in paths, f"missing endpoint: {ep}"

def test_openapi_version():
    doc = yaml.safe_load(Path("openapi.yaml").read_text(encoding="utf-8"))
    ver = doc.get("info", {}).get("version")
    assert ver in ("1.9.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0", "2.5.0", "2.6.0", "2.7.0", "2.8.0", "2.9.0", "3.0.0", "3.1.0", "3.2.0", "3.3.0", "3.4.0", "3.5.0", "3.6.0", "3.7.0", "3.8.0", "3.9.0", "4.0.0", "4.1.0", "4.2.0", "4.3.0", "4.4.0", "4.5.0", "4.6.0", "4.7.0", "4.8.0", "4.9.0", "5.0.0", "5.1.0", "5.2.0", "5.3.0", "5.4.0", "5.5.0", "5.6.0", "5.7.0", "5.8.0", "5.9.0", "6.0.0", "6.1.0", "6.2.0", "6.3.0", "6.5.0", "6.6.0", "6.7.0", "6.8.0", "6.9.0", "6.10.0", "6.11.0"), f"unexpected version: {ver}"
