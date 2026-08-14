#!/usr/bin/env python3
"""Print the short re-anchor: goal, current unit, last progress lines."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glrp_lib import GLRP_DIR, assert_safe, resolve_root  # noqa: E402


def tail_lines(text: str, n: int = 20) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-n:])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cwd", default=".", type=Path)
    args = p.parse_args()
    root, how = resolve_root(args.cwd)
    assert_safe(root, how, allow_non_git=how != "git")
    d = root / GLRP_DIR
    if not d.is_dir():
        print("ERROR: no .glrp/ — run activate.py first.", file=sys.stderr)
        raise SystemExit(2)
    goal = (d / "GOAL.md").read_text(encoding="utf-8") if (d / "GOAL.md").exists() else ""
    unit = (d / "UNIT.md").read_text(encoding="utf-8") if (d / "UNIT.md").exists() else ""
    progress = (d / "progress.txt").read_text(encoding="utf-8") if (d / "progress.txt").exists() else ""
    print("=== GOAL ===")
    print(goal.rstrip())
    print()
    print("=== CURRENT UNIT ===")
    print(unit.rstrip())
    print()
    print("=== PROGRESS (tail) ===")
    print(tail_lines(progress) or "(empty)")


if __name__ == "__main__":
    main()
