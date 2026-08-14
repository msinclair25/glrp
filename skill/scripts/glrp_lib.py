#!/usr/bin/env python3
"""Shared paths and git-root resolution for GLRP scripts."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

_NUM_LINE = re.compile(r"^(\d+)\.\s+\S")

GLRP_DIR = ".glrp"
FILES = ("GOAL.md", "UNIT.md", "progress.txt", "config.toml")

GOAL_TMPL = """# Goal

One page. What this project must be when done. Do not grow this into a playbook.

"""

UNIT_TMPL = """# Current unit

One sitting of work. What files. How we will know it is done (a command).

"""

PROGRESS_TMPL = ""

CONFIG_TMPL = """# Command that can fail. Change this to your project check.
verify = "true"
"""


def resolve_root(cwd: Path) -> tuple[Path, str]:
    cwd = cwd.resolve()
    try:
        out = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        return Path(out.stdout.strip()).resolve(), "git"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return cwd, "cwd"


def assert_safe(root: Path, how: str, allow_non_git: bool) -> None:
    home = Path.home().resolve()
    tmp = Path(os.environ.get("TMPDIR", "/tmp")).resolve()
    if root in {home, Path("/").resolve(), tmp} or root == home:
        print(
            f"ERROR: refusing to activate in {root}\n"
            "  That looks like home, temp, or filesystem root — not a project.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    if how != "git" and not allow_non_git:
        print(
            f"ERROR: {root} is not a git repository.\n"
            "  cd into a project repo, or pass --allow-non-git.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def numbered_product_lines(goal: str) -> list[str]:
    return [line.strip() for line in goal.splitlines() if _NUM_LINE.match(line.strip())]


def closed_numbers(progress: str) -> set[str]:
    found: set[str] = set()
    for line in progress.splitlines():
        if "closed unit:" not in line.lower():
            continue
        match = re.search(r"(\d+)\.", line)
        if match:
            found.add(match.group(1))
    return found


def remaining_product_lines(root: Path) -> list[str]:
    d = root / GLRP_DIR
    goal = (d / "GOAL.md").read_text(encoding="utf-8") if (d / "GOAL.md").exists() else ""
    progress = (
        (d / "progress.txt").read_text(encoding="utf-8") if (d / "progress.txt").exists() else ""
    )
    done = closed_numbers(progress)
    remaining: list[str] = []
    for line in numbered_product_lines(goal):
        number = line.split(".", 1)[0]
        if number not in done:
            remaining.append(line)
    return remaining


def glrp_dir(root: Path) -> Path:
    return root / GLRP_DIR


def write_missing(root: Path) -> list[str]:
    d = glrp_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    templates = {
        "GOAL.md": GOAL_TMPL,
        "UNIT.md": UNIT_TMPL,
        "progress.txt": PROGRESS_TMPL,
        "config.toml": CONFIG_TMPL,
    }
    created: list[str] = []
    for name, body in templates.items():
        path = d / name
        if path.exists():
            continue
        path.write_text(body, encoding="utf-8")
        created.append(str(path))
    return created
