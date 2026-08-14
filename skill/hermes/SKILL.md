---
name: glrp
description: Keep Grok on one coding unit with a check.
version: 0.1.0
author: Morgan Sinclair (msinclair25), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Grok, Coding, Skills]
    related_skills: []
---

# GLRP

Keep Grok on one software unit: re-read the job, edit, run the check, write progress.

Do **not** load a playbook. Do **not** install the old `long-running-project` / GLRP-Skill activate in this repo at the same time.

## When to use

User is doing agentic coding (feature, bug, refactor) and wants less drift, less amnesia, more accuracy. Triggers: "activate glrp", "activate long running", `/glrp`.

Don't use for one-off questions.

## Procedure

Do these in order. Use the scripts next to this file (`scripts/`).

1. **Root.** `git rev-parse --show-toplevel`. If that fails, stop. Never activate `$HOME`.
2. **Activate (once).**  
   `terminal(command="python3 scripts/activate.py --cwd \"$(git rev-parse --show-toplevel)\"")`  
   Creates `.glrp/` if missing. Does not overwrite filled files.  
   Ask the user to set `verify` in `.glrp/config.toml` to a command that can fail (`pytest -q`, `npm test`, …). Default `true` is a no-op.
3. **Re-anchor (every session, first).**  
   `terminal(command="python3 scripts/next.py --cwd \"$(git rev-parse --show-toplevel)\"")`  
   Read that output before any other project file.
4. **One unit.** Fill `.glrp/UNIT.md` with one sitting of work. Touch only what that unit needs.
5. **Check.** After edits:  
   `terminal(command="python3 scripts/check.py --cwd \"$(git rev-parse --show-toplevel)\"")`  
   Exit `10` means stay on this unit. Read `.glrp/progress.txt` tail. Do not claim done.
6. **Close.** Only when check is `0`:  
   `terminal(command="python3 scripts/close_unit.py --cwd \"$(git rev-parse --show-toplevel)\"")`  
   Then write the next unit (or stop).
7. **Before compact / new / end.** Update `UNIT.md` and let check/close append progress. The next session starts at step 3.

Scripts live beside this file. If the skill was installed to `~/.hermes/skills/glrp/`, use that `scripts/` path.

## Pitfalls

- Stacking this with the old GLRP-Skill playbook dumps too much context (more drift).
- `verify = "true"` never fails — accuracy will not improve until the user sets a real check.
- Do not rewrite `.glrp/GOAL.md` to match what you built.

## Verification

- `.glrp/GOAL.md`, `UNIT.md`, `progress.txt` exist.
- After a failed check, progress has a `verify failed` block.
- A new session that runs `next.py` reprints the same unit.
