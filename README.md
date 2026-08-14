# GLRP

A **skill** for [Grok Build](https://x.ai/build) and [Hermes Agent](https://hermes-agent.nousresearch.com/) (Grok as the model).

It is meant to make agentic coding **more accurate**, **less amnesiac**, and **less drifted** — not another playbook.

This is **not** [GLRP-Skill](https://github.com/msinclair25/GLRP-Skill) (file scaffold + long playbook). Do not install both on the same project until this skill has been measured.

## Status

New. Scripts and `SKILL.md` are not here yet. Planning lives in a local vault; this repo will hold only the skill package.

## Intended install (when shipped)

One command copies the skill into `~/.grok/skills/glrp/` and/or `~/.hermes/skills/glrp/` if those homes exist.

Then, in a project: activate the skill. It keeps three small files (goal, current unit, progress), re-reads them first each session, works one unit, and runs **your** test/smoke command before calling the unit done.

## License

MIT
