from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ChangeSummary:
    apply_patches: bool
    changed_files: int
    changed_lines: int


def summarize_fix_pr_artifacts(pr_res: Any) -> ChangeSummary:
    # pr_res is FixPRResult. We don't rely on exact shape; best-effort.
    apply_patches = bool(getattr(pr_res, "applied_patches", False))
    changed_files = int(getattr(pr_res, "changed_files", 0) or 0)
    changed_lines = int(getattr(pr_res, "changed_lines", 0) or 0)
    return ChangeSummary(apply_patches, changed_files, changed_lines)
