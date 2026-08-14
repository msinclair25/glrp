# GLRP

A **skill** for [Grok Build](https://x.ai/build) and [Hermes Agent](https://hermes-agent.nousresearch.com/) (Grok as the model).

More **accurate**, less **amnesiac**, less **drifted** agentic coding. Not a playbook.

Not [GLRP-Skill](https://github.com/msinclair25/GLRP-Skill). Do not run both on the same project.

## Install

```bash
git clone https://github.com/msinclair25/glrp.git
bash glrp/install.sh
```

Copies into `~/.grok/skills/glrp/` and/or `~/.hermes/skills/glrp/` if those homes exist. New session so skills reload.

## Use

In a **git project**:

1. Say `activate glrp` or `/glrp`.
2. Set `.glrp/config.toml` → `verify = "pytest -q"` (or your real check). `true` never fails.
3. Fill `.glrp/GOAL.md` (one page) and `.glrp/UNIT.md` (one sitting).
4. After edits the agent must run `check.py`. Red → stay on the unit.
5. New session: run `next.py` first.

## Layout

```
skill/scripts/   activate.py  next.py  check.py  close_unit.py
.glrp/           GOAL.md  UNIT.md  progress.txt  config.toml
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT
