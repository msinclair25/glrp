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
   If the user dumped a long brief, write **product** work into `.glrp/GOAL.md` as a numbered list (1., 2., 3. …). If the brief contradicts itself, keep the **later** correction. Put do-not-build in a short unnumbered list at the bottom — those are not units.  
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
   Immediately set `UNIT.md` to the lowest **product** GOAL number not yet in `progress.txt` (cite the number). If this sitting finished several numbers, list all of them in `UNIT.md` before close. If UNIT is already implemented, close it and advance. Never make a do-not-build line the current unit. “all units closed” only when every **product** number is in `progress.txt`.
7. **Before compact / new / end.** Progress must be appended. Next session starts at step 3.

## Pitfalls

- Never put “do not implement yet” in `UNIT.md`. The next session will obey it and stall.
- A sitting that ships 1–3 must close 1, 2, and 3. Closing only “1” makes the next session rewind.
- Do-not-build is not a unit. Don’t sit on “don’t build Venmo.”
- `verify = "true"` never fails — accuracy will not improve until the check can fail for **this** unit.
- Do not rewrite `.glrp/GOAL.md` to match what you built.
- Stacking this with the old GLRP-Skill playbook dumps too much context.

## Verification

- `.glrp/GOAL.md`, `UNIT.md`, `progress.txt` exist.
- After a failed check, progress has a `verify failed` block.
- A new session that runs `next.py` reprints the same unit.
