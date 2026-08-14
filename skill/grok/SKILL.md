---
name: glrp
description: >-
  Activate GLRP for agentic coding: re-anchor to goal and one unit,
  run the project check, write progress. Use when the user says
  "activate glrp", "activate long running", "long running project",
  or /glrp. Do not use for one-off questions.
user-invocable: true
argument-hint: "[optional unit]"
metadata:
  short-description: "Accurate, on-task Grok coding (goal + unit + check)"
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
   `python3 scripts/activate.py --cwd "$(git rev-parse --show-toplevel)"`  
   Creates `.glrp/` if missing. Does not overwrite filled files.  
   If the user dumped a long brief, write **all later work** into `.glrp/GOAL.md` once (including do-not-build).  
   Set `verify` in `.glrp/config.toml` to a command that can fail **for this unit**. Default `true` is a no-op.
3. **Re-anchor (every session, first).**  
   `python3 scripts/next.py --cwd "$(git rev-parse --show-toplevel)"`  
   Read that output before any other project file.
4. **One unit.** `.glrp/UNIT.md` is work to do **now**. Never write “do not implement yet” (that sabotages the next session). Touch only what this unit needs.
5. **Check.** After edits:  
   `python3 scripts/check.py --cwd "$(git rev-parse --show-toplevel)"`  
   If `verify` still points at a **previous** slice, change it so this unit can fail. Exit `10` → stay on this unit.
6. **Close.** Only when check is `0`:  
   `python3 scripts/close_unit.py --cwd "$(git rev-parse --show-toplevel)"`  
   Immediately replace `UNIT.md` with the **next** sitting from GOAL (or “all units closed”). Then stop or start that unit — do not implement the whole GOAL.
7. **Before compact / new / end.** Progress must be appended. Next session starts at step 3.

## Pitfalls

- Never put “do not implement yet” in `UNIT.md`. The next session will obey it and stall.
- `verify = "true"` never fails — accuracy will not improve until the check can fail for **this** unit.
- Do not rewrite `.glrp/GOAL.md` to match what you built.
- Stacking this with the old GLRP-Skill playbook dumps too much context.

## Verification

- `.glrp/GOAL.md`, `UNIT.md`, `progress.txt` exist.
- After a failed check, progress has a `verify failed` block.
- A new session that runs `next.py` reprints the same unit.
