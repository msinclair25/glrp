#!/usr/bin/env python3
"""Tests for GLRP skill scripts. No live Grok."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "scripts"


def run_script(name: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
    )


def git_init(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True, capture_output=True)


class TestActivate(unittest.TestCase):
    def test_refuses_home_directory(self) -> None:
        proc = run_script("activate.py", "--cwd", str(Path.home()))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("refusing", proc.stderr.lower())

    def test_refuses_non_git_without_flag(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            proc = run_script("activate.py", "--cwd", raw)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("not a git", proc.stderr.lower())

    def test_creates_missing_state_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            git_init(root)
            proc = run_script("activate.py", "--cwd", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            for name in ("GOAL.md", "UNIT.md", "progress.txt"):
                self.assertTrue((root / ".glrp" / name).is_file(), name)
            self.assertTrue((root / ".glrp" / "config.toml").is_file())

    def test_does_not_overwrite_existing_goal(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            git_init(root)
            dest = root / ".glrp"
            dest.mkdir()
            (dest / "GOAL.md").write_text("KEEPME\n", encoding="utf-8")
            proc = run_script("activate.py", "--cwd", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual((dest / "GOAL.md").read_text(encoding="utf-8"), "KEEPME\n")


class TestNext(unittest.TestCase):
    def test_prints_goal_unit_and_progress_tail(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            git_init(root)
            self.assertEqual(run_script("activate.py", "--cwd", str(root)).returncode, 0)
            (root / ".glrp" / "GOAL.md").write_text("# Goal\nShip the CLI.\n", encoding="utf-8")
            (root / ".glrp" / "UNIT.md").write_text("# Current unit\nAdd --tag.\n", encoding="utf-8")
            (root / ".glrp" / "progress.txt").write_text("old\nlatest fail\n", encoding="utf-8")
            proc = run_script("next.py", "--cwd", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = proc.stdout
            self.assertIn("Ship the CLI", out)
            self.assertIn("Add --tag", out)
            self.assertIn("latest fail", out)


class TestCheck(unittest.TestCase):
    def test_nonzero_verify_exits_10_and_appends_progress(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            git_init(root)
            self.assertEqual(run_script("activate.py", "--cwd", str(root)).returncode, 0)
            (root / ".glrp" / "config.toml").write_text('verify = "false"\n', encoding="utf-8")
            proc = run_script("check.py", "--cwd", str(root))
            self.assertEqual(proc.returncode, 10)
            progress = (root / ".glrp" / "progress.txt").read_text(encoding="utf-8")
            self.assertIn("verify failed", progress.lower())

    def test_ok_verify_exits_0(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            git_init(root)
            self.assertEqual(run_script("activate.py", "--cwd", str(root)).returncode, 0)
            (root / ".glrp" / "config.toml").write_text('verify = "true"\n', encoding="utf-8")
            proc = run_script("check.py", "--cwd", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)


class TestCloseUnit(unittest.TestCase):
    def test_refuses_when_check_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            git_init(root)
            self.assertEqual(run_script("activate.py", "--cwd", str(root)).returncode, 0)
            (root / ".glrp" / "config.toml").write_text('verify = "false"\n', encoding="utf-8")
            proc = run_script("close_unit.py", "--cwd", str(root))
            self.assertEqual(proc.returncode, 10)

    def test_records_close_when_check_passes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            git_init(root)
            self.assertEqual(run_script("activate.py", "--cwd", str(root)).returncode, 0)
            (root / ".glrp" / "config.toml").write_text('verify = "true"\n', encoding="utf-8")
            (root / ".glrp" / "UNIT.md").write_text("# Current unit\nAdd --tag.\n", encoding="utf-8")
            proc = run_script("close_unit.py", "--cwd", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            progress = (root / ".glrp" / "progress.txt").read_text(encoding="utf-8")
            self.assertIn("closed", progress.lower())
            self.assertIn("--tag", progress)

    def test_records_each_numbered_line(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            git_init(root)
            self.assertEqual(run_script("activate.py", "--cwd", str(root)).returncode, 0)
            (root / ".glrp" / "config.toml").write_text('verify = "true"\n', encoding="utf-8")
            (root / ".glrp" / "UNIT.md").write_text(
                "# Current unit\n1. person\n2. charge\n3. list\n",
                encoding="utf-8",
            )
            proc = run_script("close_unit.py", "--cwd", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            progress = (root / ".glrp" / "progress.txt").read_text(encoding="utf-8")
            self.assertIn("1. person", progress)
            self.assertIn("2. charge", progress)
            self.assertIn("3. list", progress)

    def test_tells_keep_going_when_goal_has_more(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            git_init(root)
            self.assertEqual(run_script("activate.py", "--cwd", str(root)).returncode, 0)
            (root / ".glrp" / "config.toml").write_text('verify = "true"\n', encoding="utf-8")
            (root / ".glrp" / "GOAL.md").write_text(
                "# Goal\n1. person\n2. charge\n3. list\n",
                encoding="utf-8",
            )
            (root / ".glrp" / "UNIT.md").write_text("# Current unit\n1. person\n", encoding="utf-8")
            proc = run_script("close_unit.py", "--cwd", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("KEEP GOING", proc.stdout)
            self.assertIn("2. charge", proc.stdout)
            self.assertIn("2 product steps left", proc.stdout)


if __name__ == "__main__":
    unittest.main()
