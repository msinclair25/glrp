#!/usr/bin/env python3
"""Shared paths and git-root resolution for GLRP scripts."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_NUM_LINE = re.compile(r"^(\d+)\.\s+\S")

GLRP_DIR = ".glrp"
FILES = ("GOAL.md", "UNIT.md", "progress.txt", "config.toml", "completed.json")

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

    glrp_dir(root)
    if how != "git" and not allow_non_git:
        print(
            f"ERROR: {root} is not a git repository.\n"
            "  cd into a project repo, or pass --allow-non-git.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def numbered_product_lines(goal: str) -> list[str]:
    return [line.strip() for line in goal.splitlines() if _NUM_LINE.match(line.strip())]


def completed_units(root: Path) -> set[str]:
    path = glrp_dir(root) / "completed.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
            raise ValueError("expected a list of completed goal lines")
        return set(data)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"ERROR: cannot read {path}: {exc}") from exc


def record_completed(root: Path, units: list[str]) -> None:
    directory = glrp_dir(root)
    completed = sorted(completed_units(root).union(units))
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, delete=False) as fh:
        temporary = Path(fh.name)
        try:
            json.dump(completed, fh)
            fh.write("\n")
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(directory / "completed.json")
    finally:
        temporary.unlink(missing_ok=True)


def remaining_product_lines(root: Path) -> list[str]:
    d = glrp_dir(root)
    goal = (d / "GOAL.md").read_text(encoding="utf-8") if (d / "GOAL.md").exists() else ""
    done = completed_units(root)
    return [line for line in numbered_product_lines(goal) if line not in done]


def glrp_dir(root: Path) -> Path:
    directory = root / GLRP_DIR
    for path in (directory, *(directory / name for name in FILES)):
        expected_type = path.is_dir if path == directory else path.is_file
        if path.is_symlink() or (path.exists() and not expected_type()):
            raise SystemExit(f"ERROR: invalid state path {path}; use regular files in a local .glrp directory, without symlinks")
    return directory


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
