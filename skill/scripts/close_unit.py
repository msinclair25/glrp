#!/usr/bin/env python3
"""Mark the current unit closed only if check.py succeeds."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import append_progress, run_check  # noqa: E402
from glrp_lib import GLRP_DIR, assert_safe, resolve_root  # noqa: E402


def unit_summary(root: Path) -> str:
    text = (root / GLRP_DIR / "UNIT.md").read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return "(empty UNIT.md)"


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
    append_progress(root, f"closed unit: {unit_summary(root)}")
    print("Unit closed.")


if __name__ == "__main__":
    main()
