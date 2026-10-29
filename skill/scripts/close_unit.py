#!/usr/bin/env python3
"""Mark the current unit closed only if check.py succeeds."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import append_progress, run_check  # noqa: E402
from glrp_lib import (  # noqa: E402
    GLRP_DIR,
    assert_safe,
    numbered_product_lines,
    record_completed,
    remaining_product_lines,
    resolve_root,
)


def unit_summaries(root: Path) -> list[str]:
    """Require exact numbered goal lines; prose and decimal versions cannot close work."""
    try:
        goal = numbered_product_lines((root / GLRP_DIR / "GOAL.md").read_text(encoding="utf-8"))
        units = numbered_product_lines((root / GLRP_DIR / "UNIT.md").read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"ERROR: activate GLRP and fill GOAL.md and UNIT.md: {exc}") from exc
    numbers = [line.split(".", 1)[0] for line in goal]
    if not goal or len(numbers) != len(set(numbers)) or not units or any(unit not in goal for unit in units):
        raise SystemExit("ERROR: GOAL.md needs unique numbered steps; UNIT.md must copy the exact goal lines being closed")
    return units


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cwd", default=".", type=Path)
    args = p.parse_args()
    root, how = resolve_root(args.cwd)
    assert_safe(root, how, allow_non_git=how != "git")
    units = unit_summaries(root)
    code = run_check(root)
    if code != 0:
        print("check failed — unit not closed", file=sys.stderr)
        raise SystemExit(10)
    record_completed(root, units)
    for summary in units:
        append_progress(root, f"closed unit: {summary}")
    print("Unit closed.")
    leftover = remaining_product_lines(root)
    if leftover:
        print("KEEP GOING — do the next unit now:")
        print(leftover[0])
        print(f"({len(leftover)} product steps left)")
    else:
        print("All product steps closed.")


if __name__ == "__main__":
    main()
