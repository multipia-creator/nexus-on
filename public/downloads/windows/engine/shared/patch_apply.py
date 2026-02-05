from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


class PatchApplyError(Exception):
    pass


@dataclass
class FilePatch:
    path: str
    hunks: List[Tuple[int, int, int, int, List[str]]]  # (a_start,a_len,b_start,b_len,lines)


def _parse_hunk_header(line: str) -> Tuple[int, int, int, int]:
    # @@ -a_start,a_len +b_start,b_len @@
    m = re.match(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@", line.strip())
    if not m:
        raise PatchApplyError(f"invalid hunk header: {line}")
    a_start = int(m.group(1))
    a_len = int(m.group(2) or "1")
    b_start = int(m.group(3))
    b_len = int(m.group(4) or "1")
    return a_start, a_len, b_start, b_len


def split_unified_diff(diff_text: str) -> List[FilePatch]:
    """Split a unified diff into per-file patches.
    Supports either 'diff --git' blocks or a single-file diff with ---/+++ headers.
    """
    diff_text = diff_text.replace("\r\n", "\n")
    lines = diff_text.splitlines(True)

    patches: List[FilePatch] = []
    i = 0

    def parse_one(start: int) -> Tuple[FilePatch, int]:
        path = None
        hunks = []
        j = start

        # Skip leading lines until ---/+++
        while j < len(lines) and not lines[j].startswith("--- "):
            j += 1
        if j >= len(lines):
            raise PatchApplyError("missing --- header")
        # --- a/path
        j += 1
        if j >= len(lines) or not lines[j].startswith("+++ "):
            raise PatchApplyError("missing +++ header")
        # +++ b/path
        plus = lines[j].strip()
        m = re.match(r"^\+\+\+\s+b/(.+)$", plus)
        if not m:
            # allow +++ path without b/
            m2 = re.match(r"^\+\+\+\s+(.+)$", plus)
            if not m2:
                raise PatchApplyError("invalid +++ header")
            path = m2.group(1)
        else:
            path = m.group(1)
        j += 1

        # hunks
        while j < len(lines):
            if lines[j].startswith("diff --git "):
                break
            if lines[j].startswith("--- "):
                break
            if lines[j].startswith("@@ "):
                a_start, a_len, b_start, b_len = _parse_hunk_header(lines[j])
                j += 1
                hunk_lines = []
                while j < len(lines) and not lines[j].startswith("@@ ") and not lines[j].startswith("diff --git ") and not lines[j].startswith("--- "):
                    hunk_lines.append(lines[j])
                    j += 1
                hunks.append((a_start, a_len, b_start, b_len, hunk_lines))
                continue
            # metadata lines (index, new file mode, etc.)
            j += 1

        if not path:
            raise PatchApplyError("could not determine path")
        return FilePatch(path=path, hunks=hunks), j

    # If diff --git exists, walk blocks
    while i < len(lines):
        if lines[i].startswith("diff --git "):
            # move to next header
            i += 1
            fp, i = parse_one(i)
            patches.append(fp)
            continue
        # If we see --- then treat as single-file diff
        if lines[i].startswith("--- "):
            fp, i = parse_one(i)
            patches.append(fp)
            continue
        i += 1

    if not patches and diff_text.strip():
        raise PatchApplyError("no patches found")
    return patches


def apply_file_patch(original_text: str, patch: FilePatch) -> str:
    """Apply hunks to the original text. Strict: context must match."""
    orig_lines = original_text.replace("\r\n", "\n").splitlines(True)
    out = orig_lines[:]

    # We apply hunks in order; need to keep offset adjustments.
    delta = 0
    for (a_start, a_len, b_start, b_len, hunk_lines) in patch.hunks:
        # a_start is 1-based
        idx = (a_start - 1) + delta
        # Build expected segment and new segment
        expected = []
        newseg = []
        cur = idx

        for hl in hunk_lines:
            if not hl:
                continue
            tag = hl[0]
            content = hl[1:]
            if tag == " ":
                expected.append(content)
                newseg.append(content)
                cur += 1
            elif tag == "-":
                expected.append(content)
                cur += 1
            elif tag == "+":
                newseg.append(content)
            elif tag == "\\":
                # "\ No newline at end of file" - ignore
                continue
            else:
                raise PatchApplyError(f"invalid hunk line tag: {tag}")

        # Verify expected matches current slice
        slice_ = out[idx: idx + len(expected)]
        if [l for l in slice_] != expected:
            raise PatchApplyError("context mismatch while applying patch")

        # Replace
        out[idx: idx + len(expected)] = newseg

        # Update delta
        delta += len(newseg) - len(expected)

    return "".join(out)


def apply_unified_diff(original_by_path: Dict[str, str], diff_text: str) -> Dict[str, str]:
    """Apply a unified diff to a dict of file contents; returns updated dict."""
    patches = split_unified_diff(diff_text)
    updated = dict(original_by_path)
    for fp in patches:
        if fp.path not in updated:
            raise PatchApplyError(f"file not provided: {fp.path}")
        updated[fp.path] = apply_file_patch(updated[fp.path], fp)
    return updated
