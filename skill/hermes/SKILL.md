---
name: glrp
description: Keep Grok on one coding unit with a check.
version: 0.1.1
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

Do these in order. Scripts live beside this file (`scripts/`). If installed to `~/.hermes/skills/glrp/`, use that path.

1. **Root.** `git rev-parse --show-toplevel`. If that fails, stop. Never activate `$HOME`.
2. **Activate (once).**  
   `terminal(command="python3 scripts/activate.py --cwd \"$(git rev-parse --show-toplevel)\"")`  
   If the user dumped a long brief, write **all later work** into `.glrp/GOAL.md` once (including do-not-build).  
   Set `verify` to a command that can fail **for this unit**.
3. **Re-anchor (every session, first).**  
   `terminal(command="python3 scripts/next.py --cwd \"$(git rev-parse --show-toplevel)\"")`
4. **One unit.** `UNIT.md` is work to do **now**. Never write “do not implement yet.”
5. **Check.**  
   `terminal(command="python3 scripts/check.py --cwd \"$(git rev-parse --show-toplevel)\"")`  
   If `verify` still points at a previous slice, change it. Exit `10` → stay on this unit.
6. **Close.** Only when check is `0`:  
   `terminal(command="python3 scripts/close_unit.py --cwd \"$(git rev-parse --show-toplevel)\"")`  
   Immediately replace `UNIT.md` with the next sitting from GOAL. Do not implement the whole GOAL.
7. **Before compact / new / end.** Progress must be appended. Next session starts at step 3.

## Pitfalls

- Never put “do not implement yet” in `UNIT.md`.
- `verify = "true"` never fails for this unit.
- Do not rewrite `GOAL.md` to match what you built.
- Do not stack the old GLRP-Skill playbook.

## Verification

- `.glrp/` files exist. Failed check appends `verify failed`. `next.py` reprints the current unit.
