---
name: glrp
description: Keep a numbered coding plan moving through verified steps. Use for "activate glrp" or /glrp, not one-off questions.
user-invocable: true
argument-hint: "[optional goal]"
---

# GLRP

Use the current GLRP edition alone in a project; do not also activate the legacy long-running-project playbook.

## Workflow

Run commands from the user's project directory. Resolve its Git root first:
`git rev-parse --show-toplevel`. Stop if it fails; never activate the home directory.

1. Activate once:
   ```bash
   python3 "${GROK_HOME:-$HOME/.grok}/skills/glrp/scripts/activate.py" --cwd "$(git rev-parse --show-toplevel)"
   ```
   Fill `.glrp/GOAL.md` with unique numbered product steps (`1. …`, `2. …`).
   Keep exclusions unnumbered. Copy the exact current goal line into `.glrp/UNIT.md`.
   Set `verify` in `.glrp/config.toml` to a real test command for that step.
2. At each new session, read the handoff:
   ```bash
   python3 "${GROK_HOME:-$HOME/.grok}/skills/glrp/scripts/next.py" --cwd "$(git rev-parse --show-toplevel)"
   ```
3. Implement the current unit. Keep changes scoped to that step. Do not rewrite the goal to match incomplete work.
4. Verify and close in one command:
   ```bash
   python3 "${GROK_HOME:-$HOME/.grok}/skills/glrp/scripts/close_unit.py" --cwd "$(git rev-parse --show-toplevel)"
   ```
   This runs verification itself; no separate check is required. Failure never records completion.
   For diagnostics without closing, use `check.py` from the same installed scripts directory.
   If multiple steps were finished, put each exact goal line in UNIT before closing.
5. On `KEEP GOING`, copy the next unfinished goal line into UNIT and continue this sitting.
   Stop when every product step is verified, or when user input/authorization is needed.
   On a failed check, fix the current unit; do not advance it.
6. Before ending or compacting, leave UNIT describing the work to do next.
   `completed.json` is maintained by the close command; never edit it to bypass verification.
   `progress.txt` is a human-readable history, not completion authority.

The Grok Stop hook gives one continuation reminder when product steps remain.

## Upgrade note

Older text-log completions remain in progress.txt, but must be verified and closed once to populate completed.json. Review the existing work before re-closing; do not rebuild it merely because it lacks a new completion record.
