from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

import redis

from shared.doc_extract import HwpConversionRequired, extract_chunks


def _utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()


@dataclass
class FolderIngestResult:
    ok: bool
    scanned: int
    candidates: int
    ingested_chunks: int
    skipped: int
    errors: List[Dict[str, Any]]
    pending_hwp: int
    started_at: str
    finished_at: str
    folder: str


class RagFolderIngestor:
    """Incremental folder ingest into NaiveRAG.

    - Tracks per-file mtime in Redis (tenant-scoped)
    - Extracts text from pdf/docx/pptx/xlsx/txt/md
    - HWP requires prior conversion (preferred: sibling .pdf/.txt with same basename)
    """

    def __init__(self, redis_url: str, rag_engine: Any):
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)
        self.rag = rag_engine

    def _k_index(self, tenant: str) -> str:
        return f"nexus:rag:{tenant}:file_index"

    def _k_last(self, tenant: str) -> str:
        return f"nexus:rag:{tenant}:last_ingest"

    @staticmethod
    def _find_hwp_fallback(path: str) -> str | None:
        base = os.path.splitext(path)[0]
        for ext in ("pdf", "txt", "md", "docx"):
            p = f"{base}.{ext}"
            if os.path.exists(p):
                return p
        return None

    def ingest_folder(
        self,
        *,
        tenant: str,
        folder: str,
        allowed_exts: Sequence[str],
        max_files: int = 5000,
        max_file_mb: int = 50,
        max_chars_per_chunk: int = 12000,
        xlsx_cell_limit: int = 20000,
    ) -> FolderIngestResult:
        started = _utc_iso()
        folder = os.path.abspath(folder)
        errors: List[Dict[str, Any]] = []

        if not os.path.isdir(folder):
            res = FolderIngestResult(
                ok=False,
                scanned=0,
                candidates=0,
                ingested_chunks=0,
                skipped=0,
                errors=[{"path": folder, "error": "FOLDER_NOT_FOUND"}],
                pending_hwp=0,
                started_at=started,
                finished_at=_utc_iso(),
                folder=folder,
            )
            self.r.set(self._k_last(tenant), str(res.__dict__))
            return res

        allow = {e.lower().lstrip(".") for e in allowed_exts}
        scanned = 0
        candidates = 0
        ingested = 0
        skipped = 0
        pending_hwp = 0

        idx_key = self._k_index(tenant)
        limit_bytes = max_file_mb * 1024 * 1024

        for root, _, files in os.walk(folder):
            for fn in files:
                scanned += 1
                if scanned > max_files:
                    break

                path = os.path.join(root, fn)
                ext = os.path.splitext(fn)[1].lower().lstrip(".")
                if ext not in allow:
                    continue
                candidates += 1

                try:
                    st = os.stat(path)
                except Exception as e:
                    skipped += 1
                    errors.append({"path": path, "error": "STAT_FAILED", "detail": str(e)})
                    continue

                if st.st_size <= 0 or st.st_size > limit_bytes:
                    skipped += 1
                    continue

                mtime = int(st.st_mtime)
                prev = self.r.hget(idx_key, path)
                if prev and int(prev) >= mtime:
                    skipped += 1
                    continue

                path_use = path
                if ext == "hwp":
                    fb = self._find_hwp_fallback(path)
                    if fb:
                        path_use = fb
                    else:
                        pending_hwp += 1
                        skipped += 1
                        self.r.hset(idx_key, path, str(mtime))
                        continue

                rel = os.path.relpath(path_use, folder).replace(os.sep, "/")
                base_doc_id = f"{rel}::{_sha1(path_use)}"

                try:
                    chunks = extract_chunks(path_use, max_chars=max_chars_per_chunk, xlsx_cell_limit=xlsx_cell_limit)
                except HwpConversionRequired as e:
                    pending_hwp += 1
                    skipped += 1
                    self.r.hset(idx_key, path, str(mtime))
                    errors.append({"path": path, "error": "HWP_CONVERSION_REQUIRED", "detail": str(e)})
                    continue
                except Exception as e:
                    skipped += 1
                    self.r.hset(idx_key, path, str(mtime))
                    errors.append({"path": path_use, "error": "EXTRACT_FAILED", "detail": str(e)})
                    continue

                if not chunks:
                    skipped += 1
                    self.r.hset(idx_key, path, str(mtime))
                    continue

                for ch in chunks:
                    doc_id = f"{base_doc_id}::{ch.chunk_id}"
                    meta = {
                        "source_path": path_use,
                        "source_rel": rel,
                        "source_ext": os.path.splitext(path_use)[1].lower().lstrip("."),
                        "source_mtime": mtime,
                        "source_size": int(st.st_size),
                        "chunk_id": ch.chunk_id,
                    }
                    meta.update(ch.meta or {})
                    self.rag.ingest(tenant_id=tenant, doc_id=doc_id, text=ch.text, meta=meta)
                    ingested += 1

                self.r.hset(idx_key, path, str(mtime))

        finished = _utc_iso()
        res = FolderIngestResult(
            ok=True,
            scanned=scanned,
            candidates=candidates,
            ingested_chunks=ingested,
            skipped=skipped,
            errors=errors[:20],
            pending_hwp=pending_hwp,
            started_at=started,
            finished_at=finished,
            folder=folder,
        )
        self.r.set(self._k_last(tenant), str(res.__dict__))
        return res

    def last_result_raw(self, tenant: str) -> str | None:
        return self.r.get(self._k_last(tenant))
