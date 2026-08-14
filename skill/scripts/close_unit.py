#!/usr/bin/env python3
"""Mark the current unit closed only if check.py succeeds."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import append_progress, run_check  # noqa: E402
from glrp_lib import GLRP_DIR, assert_safe, resolve_root  # noqa: E402


def unit_summaries(root: Path) -> list[str]:
    """Every numbered GOAL line in UNIT.md, else the first body line.

    A sitting that shipped 1–3 must list those numbers so progress records
    all of them. Recording only the first line made the next session rewind.
    """
    text = (root / GLRP_DIR / "UNIT.md").read_text(encoding="utf-8")
    numbered: list[str] = []
    fallback = ""
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line[:1].isdigit() and "." in line[:4]:
            numbered.append(line)
        elif not fallback:
            fallback = line
    if numbered:
        return numbered
    return [fallback or "(empty UNIT.md)"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cwd", default=".", type=Path)
    args = p.parse_args()
    root, how = resolve_root(args.cwd)
    assert_safe(root, how, allow_non_git=how != "git")
    code = run_check(root)
    if code != 0:
        print("check failed — unit not closed", file=sys.stderr)
        raise SystemExit(10)
    for summary in unit_summaries(root):
        append_progress(root, f"closed unit: {summary}")
    print("Unit closed.")


if __name__ == "__main__":
    main()
