#!/usr/bin/env python3
"""Grok Build Stop gate: one kick if the agent quits with product steps left.

Allow the stop when there is no .glrp/, nothing left, this is not end_turn,
or we already kicked this turn (stopHookActive). Never loops to 8.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glrp_lib import remaining_product_lines, resolve_root  # noqa: E402


def _payload() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _root(data: dict) -> Path | None:
    env = os.environ.get("GROK_WORKSPACE_ROOT")
    if env:
        return Path(env)
    cwd = data.get("cwd") or data.get("workspaceRoot")
    if cwd:
        return Path(str(cwd))
    return Path.cwd()


def main() -> None:
    data = _payload()
    if data.get("reason") not in (None, "end_turn"):
        return
    if data.get("stopHookActive") is True:
        return
    root_path = _root(data)
    if root_path is None:
        return
    try:
        root, how = resolve_root(root_path)
    except Exception:
        return
    if not (root / ".glrp").is_dir():
        return
    leftover = remaining_product_lines(root)
    if not leftover:
        return
    reason = (
        f"You stopped with {len(leftover)} product step(s) left. "
        f"Do this UNIT now (do not explain): {leftover[0]} "
        "Then run check.py and close_unit.py. KEEP GOING."
    )
    print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    main()
