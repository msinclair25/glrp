#!/usr/bin/env python3
"""Activate GLRP in a project: write missing goal/unit/progress files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as a script from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glrp_lib import assert_safe, resolve_root, write_missing  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cwd", default=".", type=Path)
    p.add_argument("--allow-non-git", action="store_true")
    args = p.parse_args()
    root, how = resolve_root(args.cwd)
    assert_safe(root, how, args.allow_non_git)
    created = write_missing(root)
    print(f"Project root: {root}")
    if created:
        print("Created:")
        for c in created:
            print(f"  {c}")
    else:
        print("State files already present.")


if __name__ == "__main__":
    main()
