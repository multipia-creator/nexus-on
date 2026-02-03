from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import redis


_TOKEN_RE = re.compile(r"[A-Za-z0-9가-힣]{2,}")


def _utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _tokens(text: str) -> List[str]:
    if not text:
        return []
    t = text.lower()
    return _TOKEN_RE.findall(t)


@dataclass
class RagDoc:
    doc_id: str
    text: str
    meta: Dict[str, Any]


class NaiveRAG:
    """
    P0-grade RAG in Redis:
      - stores full text per doc_id
      - query uses token-overlap scoring (fast, deterministic, no embeddings)
    This is intentionally simple so it can be swapped with vector DB later.

    Keys (per tenant):
      - nexus:rag:{tenant}:docs  (hash) doc_id -> json({text, meta, ingested_at})
    """

    def __init__(self, redis_url: str):
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

    def _k(self, tenant: str) -> str:
        return f"nexus:rag:{tenant}:docs"

    def ingest(self, tenant: str, doc_id: str, text: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not doc_id:
            raise ValueError("doc_id required")
        if not text or not text.strip():
            raise ValueError("text required")

        payload = {
            "doc_id": doc_id,
            "text": text,
            "meta": meta or {},
            "ingested_at": _utc_iso(),
            "len": len(text),
        }
        self.r.hset(self._k(tenant), doc_id, json.dumps(payload, ensure_ascii=False))
        return {"ok": True, "doc_id": doc_id, "len": len(text)}

    def delete(self, tenant: str, doc_id: str) -> Dict[str, Any]:
        removed = self.r.hdel(self._k(tenant), doc_id)
        return {"ok": True, "doc_id": doc_id, "removed": int(removed)}

    def list_docs(self, tenant: str, limit: int = 50) -> List[Dict[str, Any]]:
        k = self._k(tenant)
        ids = self.r.hkeys(k)[: int(limit)]
        out = []
        for doc_id in ids:
            raw = self.r.hget(k, doc_id)
            if not raw:
                continue
            try:
                j = json.loads(raw)
            except Exception:
                continue
            out.append({"doc_id": j.get("doc_id", doc_id), "len": j.get("len", 0), "meta": j.get("meta", {}), "ingested_at": j.get("ingested_at", "")})
        return out

    def query(self, tenant: str, q: str, top_k: int = 5, max_docs_scan: int = 200) -> List[Dict[str, Any]]:
        q = (q or "").strip()
        if not q:
            raise ValueError("query required")
        qtok = set(_tokens(q))
        if not qtok:
            # fallback: short query -> treat as raw substring
            qtok = {q.lower()}

        k = self._k(tenant)
        doc_ids = self.r.hkeys(k)[: int(max_docs_scan)]
        scored = []
        for doc_id in doc_ids:
            raw = self.r.hget(k, doc_id)
            if not raw:
                continue
            try:
                j = json.loads(raw)
            except Exception:
                continue
            text = j.get("text", "") or ""
            tok = set(_tokens(text))
            overlap = len(qtok.intersection(tok))
            if overlap <= 0:
                # substring boost
                if q.lower() in text.lower():
                    overlap = 1
                else:
                    continue
            scored.append((overlap, j))

        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for score, j in scored[: int(top_k)]:
            text = j.get("text", "") or ""
            qlower = q.lower()
            idx = text.lower().find(qlower)
            if idx < 0:
                # best-effort snippet: first 240 chars
                snippet = text[:240]
            else:
                lo = max(0, idx - 80)
                hi = min(len(text), idx + 160)
                snippet = text[lo:hi]
            out.append({
                "doc_id": j.get("doc_id", ""),
                "score": int(score),
                "snippet": snippet.replace("\n", " ").strip(),
                "meta": j.get("meta", {}),
                "ingested_at": j.get("ingested_at", ""),
            })
        return out
