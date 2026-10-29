"""Behavioral regressions from the completion, safety and installation review."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill/scripts"


class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "project"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.assertEqual(self.run_script("activate.py").returncode, 0)
        self.state = self.root / ".glrp"

    def run_script(self, name):
        return subprocess.run([sys.executable, str(SCRIPTS / name), "--cwd", str(self.root)],
                              capture_output=True, text=True)

    def plan(self, unit="1. Build widget", goal="1. Build widget\n2. Ship widget"):
        (self.state / "GOAL.md").write_text(goal)
        (self.state / "UNIT.md").write_text(unit)
        (self.state / "config.toml").write_text('verify = "echo checked"\n')

    def test_output_and_old_logs_cannot_close_work(self):
        self.plan()
        (self.state / "config.toml").write_text('verify = "echo closed unit: 1. Build widget; exit 1"\n')
        self.assertEqual(self.run_script("check.py").returncode, 10)
        next_step = self.run_script("next.py").stdout.split("=== UNFINISHED GOAL STEPS ===")[1]
        self.assertIn("1. Build widget", next_step)
        self.assertFalse((self.state / "completed.json").exists())

    def test_template_and_invalid_units_cannot_close(self):
        self.assertNotEqual(self.run_script("close_unit.py").returncode, 0)
        for unit in ("1.2 a version", "", "1. Wrong work", "9. Missing goal"):
            with self.subTest(unit=unit):
                self.plan(unit=unit)
                self.assertNotEqual(self.run_script("close_unit.py").returncode, 0)
                self.assertFalse((self.state / "completed.json").exists())

    def test_close_verifies_once_and_tracks_exact_goal(self):
        self.plan()
        (self.state / "config.toml").write_text('verify = "echo run >> count.txt"\n')
        closed = self.run_script("close_unit.py")
        self.assertEqual(closed.returncode, 0, closed.stderr)
        self.assertEqual((self.root / "count.txt").read_text().splitlines(), ["run"])
        self.assertEqual(json.loads((self.state / "completed.json").read_text()), ["1. Build widget"])
        self.assertIn("2. Ship widget", closed.stdout)
        self.plan(goal="1. Different work\n2. Ship widget")
        unfinished = self.run_script("next.py").stdout.split("=== UNFINISHED GOAL STEPS ===")[1]
        self.assertIn("1. Different work", unfinished)

    def test_real_toml_comments_quotes_and_invalid_values(self):
        self.plan()
        command = f'{sys.executable} -c "assert 1 + 1 == 2"'
        (self.state / "config.toml").write_text("verify = " + json.dumps(command) + " # comment\n")
        result = self.run_script("check.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        for value in ('verify = 3', 'verify = ""', 'verify = "unterminated'):
            (self.state / "config.toml").write_text(value)
            self.assertNotEqual(self.run_script("check.py").returncode, 0)

    def test_symlinked_state_directory_and_files_are_refused(self):
        self.plan()
        outside = self.base / "outside"
        self.state.rename(outside)
        self.state.symlink_to(outside, target_is_directory=True)
        before = {p.name: p.read_bytes() for p in outside.iterdir()}
        for name in ("activate.py", "check.py", "close_unit.py", "next.py"):
            self.assertNotEqual(self.run_script(name).returncode, 0)
        self.assertEqual(before, {p.name: p.read_bytes() for p in outside.iterdir()})
        self.state.unlink()
        outside.rename(self.state)
        for filename in ("GOAL.md", "progress.txt", "config.toml", "completed.json"):
            path = self.state / filename
            old = path.read_bytes() if path.exists() else None
            path.unlink(missing_ok=True)
            path.symlink_to(self.base / "missing-target")
            self.assertNotEqual(self.run_script("activate.py").returncode, 0)
            self.assertFalse((self.base / "missing-target").exists())
            path.unlink()
            if old is not None:
                path.write_bytes(old)

    def test_failed_install_preserves_working_package(self):
        package = self.base / "package"
        shutil.copytree(ROOT / "skill", package / "skill")
        shutil.copyfile(ROOT / "install.sh", package / "install.sh")
        home = self.base / "grok"
        home.mkdir()
        env = dict(os.environ, GROK_HOME=str(home), HERMES_HOME=str(self.base / "absent"))
        command = ["bash", str(package / "install.sh")]
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = home / "skills/glrp/scripts/activate.py"
        before = installed.read_bytes()
        (package / "skill/scripts/activate.py").unlink()
        self.assertNotEqual(subprocess.run(command, env=env, capture_output=True).returncode, 0)
        self.assertEqual(installed.read_bytes(), before)
        shutil.copyfile(SCRIPTS / "activate.py", package / "skill/scripts/activate.py")
        # Fail the copy after validation to exercise staging, not just preflight.
        bin_dir = self.base / "bin"
        bin_dir.mkdir()
        cp = bin_dir / "cp"
        cp.write_text("#!/bin/sh\nexit 1\n")
        cp.chmod(0o755)
        env["PATH"] = str(bin_dir) + os.pathsep + env["PATH"]
        self.assertNotEqual(subprocess.run(command, env=env, capture_output=True).returncode, 0)
        self.assertEqual(installed.read_bytes(), before)

    def test_installed_documented_commands_and_stop_hook(self):
        grok_home, hermes_home = self.base / "grok", self.base / "hermes"
        grok_home.mkdir()
        hermes_home.mkdir()
        env = dict(os.environ, GROK_HOME=str(grok_home), HERMES_HOME=str(hermes_home),
                   GROK_WORKSPACE_ROOT=str(self.root))
        installed = subprocess.run(["bash", str(ROOT / "install.sh")], env=env,
                                   capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        for home in (grok_home, hermes_home):
            wrapper = (home / "skills/glrp/SKILL.md").read_text()
            commands = re.findall(r"```bash\n(.*?)\n\s*```", wrapper, re.DOTALL)
            self.assertEqual(len(commands), 3)
            self.plan(goal="1. Build widget")
            for command in commands:
                proc = subprocess.run(["bash", "-c", command], env=env, cwd=self.root,
                                      capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("All product steps closed.", proc.stdout)
        hook = subprocess.run([sys.executable, str(grok_home / "skills/glrp/scripts/stop_gate.py")],
                              env=env, input='{"reason":"end_turn"}', capture_output=True, text=True)
        self.assertEqual(hook.returncode, 0, hook.stderr)
        self.assertEqual(hook.stdout.strip(), "")
