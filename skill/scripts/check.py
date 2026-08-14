#!/usr/bin/env python3
"""Run the project's verify command. Exit 0 ok, 10 failed (appends progress)."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glrp_lib import (  # noqa: E402
    GLRP_DIR,
    assert_safe,
    numbered_product_lines,
    resolve_root,
)

_NOOP = {"true", "/bin/true", "/usr/bin/true"}


def read_verify(config: Path) -> str:
    text = config.read_text(encoding="utf-8") if config.exists() else ""
    m = re.search(r'(?m)^\s*verify\s*=\s*["\'](.+)["\']\s*$', text)
    if not m:
        print("ERROR: no verify = \"...\" in .glrp/config.toml", file=sys.stderr)
        raise SystemExit(2)
    return m.group(1)


def append_progress(root: Path, body: str) -> None:
    path = root / GLRP_DIR / "progress.txt"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n--- {stamp} ---\n{body.rstrip()}\n")


def run_check(root: Path) -> int:
    cmd = read_verify(root / GLRP_DIR / "config.toml")
    goal_path = root / GLRP_DIR / "GOAL.md"
    goal = goal_path.read_text(encoding="utf-8") if goal_path.exists() else ""
    if cmd.strip() in _NOOP and numbered_product_lines(goal):
        msg = (
            "verify is a no-op (true). Set .glrp/config.toml to a command "
            "that can fail for this unit — a story does not count."
        )
        print(msg, file=sys.stderr)
        append_progress(root, "verify failed: no-op true with a numbered GOAL")
        return 10
    proc = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True)
    if proc.returncode == 0:
        return 0
    tail = (proc.stdout + proc.stderr)[-2000:]
    append_progress(root, f"verify failed ({proc.returncode}): {cmd}\n{tail}")
    return 10


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cwd", default=".", type=Path)
    args = p.parse_args()
    root, how = resolve_root(args.cwd)
    assert_safe(root, how, allow_non_git=how != "git")
    code = run_check(root)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
