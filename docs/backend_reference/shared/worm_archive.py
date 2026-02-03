from __future__ import annotations

import os
import shutil
from datetime import datetime
from typing import Optional

def _ts() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def archive_file(src_path: str, archive_dir: str, chmod_readonly: bool = True) -> Optional[str]:
    """Copy file to archive_dir with timestamp suffix; optionally chmod read-only.

    This is a file-based approximation of WORM. For real WORM, mount a WORM volume or
    use S3 Object Lock and sync externally. This function is intentionally dependency-free.
    """
    if not src_path or not archive_dir:
        return None
    if not os.path.exists(src_path):
        return None
    os.makedirs(archive_dir, exist_ok=True)
    base = os.path.basename(src_path)
    dst = os.path.join(archive_dir, f"{base}.{_ts()}.worm")
    shutil.copy2(src_path, dst)
    if chmod_readonly:
        try:
            os.chmod(dst, 0o444)
        except Exception:
            pass
    return dst
