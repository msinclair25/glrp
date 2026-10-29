<p align="center">
  <img src="docs/banner.png" alt="GLRP — Problem: long Grok coding sessions keep dying. Solution: a tiny skill that writes the plan, does one step, runs a real test, and leaves the next step for the next chat." width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-e8e4dc?labelColor=07080c" alt="MIT"></a>
  <a href="https://x.ai/build"><img src="https://img.shields.io/badge/Grok_Build-skill-f5c15c?labelColor=07080c" alt="Grok Build"></a>
  <a href="https://hermes-agent.nousresearch.com/"><img src="https://img.shields.io/badge/Hermes-skill-3ee0c5?labelColor=07080c" alt="Hermes"></a>
  <a href="#tests"><img src="https://img.shields.io/badge/tests-unittest-e8e4dc?labelColor=07080c" alt="tests"></a>
</p>

<p align="center">A skill for <a href="https://x.ai/build">Grok Build</a> and <a href="https://hermes-agent.nousresearch.com/">Hermes Agent</a>.</p>

---

## Problem

Long coding sessions with Grok keeps dying.

## Solution

A tiny skill. It writes the plan as a numbered list, does one step, runs a real test, writes down the next step. Next chat reads that file and keeps going.

## How

```mermaid
flowchart LR
  A[activate] --> B[numbered plan]
  B --> C[one step]
  C --> D[real test]
  D -->|not yet| C
  D -->|green| E[write the next step]
  E --> C
```

| File | Job |
|------|-----|
| `.glrp/GOAL.md` | The whole plan, numbered. |
| `.glrp/UNIT.md` | The one step happening now. |
| `.glrp/progress.txt` | Steps already done. |
| `.glrp/config.toml` | `verify` — your real test command. |

Scripts: `activate.py` · `next.py` · `check.py` · `close_unit.py`

## Grok 4.7 compatibility

Verified with **Grok Build CLI 1.0.41**, where `grok-4.7` is the default and
`grok-4.7-build-fast` is also available. GLRP is model-agnostic: it does not
hard-code a model or context limit, so both entries use the same skill and
workflow. Use `grok models` to check the live catalog. Requires Git and
Python 3.10+.

## Install

```bash
glrp_tmp="$(mktemp -d)" && (trap 'rm -rf "$glrp_tmp"' EXIT; git clone --depth 1 https://github.com/msinclair25/glrp.git "$glrp_tmp/glrp" && bash "$glrp_tmp/glrp/install.sh")
```

Puts the skill in `${GROK_HOME:-$HOME/.grok}/skills/glrp/` and, when a Hermes
home exists, `${HERMES_HOME:-$HOME/.hermes}/skills/glrp/`. On Grok Build it
also installs a Stop hook that kicks once if the model quits with steps left.
The temporary clone is removed automatically.

Start a **new session** so the skill and hook load. `grok inspect` should list
`glrp` under Skills and the installed Stop hook under Hooks.

## Use

In a git project:

1. Say `activate glrp` or `/glrp`.
2. Set `verify = "pytest -q"` (or whatever actually tests your project).
3. Paste the brief. It numbers the plan and starts step one.
4. It does that step, runs the test, writes the next step, and **keeps going** this sitting.
5. If you start a new chat, it reads the file and continues.

Use this current `glrp` edition by itself in a project. Do not activate the
deprecated `long-running-project` / `GLRP-Skill` playbook in the same project.

```
skill/scripts/   activate.py  next.py  check.py  close_unit.py
.glrp/           GOAL.md  UNIT.md  progress.txt  config.toml
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

[MIT](LICENSE) · Morgan Sinclair ([@msinclair25](https://github.com/msinclair25))
