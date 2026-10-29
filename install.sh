#!/usr/bin/env bash
# Install GLRP skill into Grok Build and/or Hermes if those homes exist.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/skill"
for file in grok/SKILL.md hermes/SKILL.md grok/hooks/glrp-stop.json scripts/activate.py scripts/check.py scripts/close_unit.py scripts/glrp_lib.py scripts/next.py scripts/stop_gate.py; do
  if [[ ! -f "$SRC/$file" ]]; then
    echo "error: incomplete GLRP package; missing $SRC/$file" >&2
    exit 1
  fi
done
python3 -c 'import sys; assert sys.version_info >= (3, 10), "GLRP requires Python 3.10+"; import importlib; importlib.import_module("tomllib" if sys.version_info >= (3, 11) else "tomli")' || {
  echo "error: use Python 3.11+, or on Python 3.10 run: python3 -m pip install tomli" >&2
  exit 1
}

install_one() (
  local dest="$1"
  local wrapper="$2"
  if [[ -L "$dest" || ( -e "$dest" && ! -d "$dest" ) ]]; then
    echo "error: expected a regular skill directory at $dest" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$dest")"
  staging="$(mktemp -d "$(dirname "$dest")/.glrp-install.XXXXXX")"
  cleanup() {
    status=$?
    if [[ ! -e "$dest" && -d "$staging/previous" ]]; then
      mv "$staging/previous" "$dest" || {
        echo "error: previous installation retained at $staging/previous" >&2
        exit 1
      }
    fi
    rm -rf "$staging"
    exit "$status"
  }
  trap cleanup EXIT
  mkdir -p "$staging/new/scripts"
  cp "$SRC/scripts/"*.py "$staging/new/scripts/"
  chmod +x "$staging/new/scripts/"*.py
  cp "$wrapper" "$staging/new/SKILL.md"
  if [[ -d "$dest" ]]; then mv "$dest" "$staging/previous"; fi
  mv "$staging/new" "$dest"
  echo "Installed: $dest"
)

found=0
default_grok_home=""
default_hermes_home=""
if [[ -n "${HOME:-}" ]]; then
  default_grok_home="$HOME/.grok"
  default_hermes_home="$HOME/.hermes"
fi
grok_home="${GROK_HOME:-$default_grok_home}"
hermes_home="${HERMES_HOME:-$default_hermes_home}"

if [[ -n "$grok_home" && -d "$grok_home" ]]; then
  install_one "$grok_home/skills/glrp" "$SRC/grok/SKILL.md"
  mkdir -p "$grok_home/hooks"
  cp "$SRC/grok/hooks/glrp-stop.json" "$grok_home/hooks/glrp-stop.json"
  echo "Installed hook: $grok_home/hooks/glrp-stop.json"
  found=1
fi
if [[ -n "$hermes_home" && -d "$hermes_home" ]]; then
  install_one "$hermes_home/skills/glrp" "$SRC/hermes/SKILL.md"
  found=1
fi

if [[ "$found" -eq 0 ]]; then
  echo "error: neither a Grok home nor a Hermes home exists" >&2
  echo "set GROK_HOME or HERMES_HOME when using a non-default location" >&2
  exit 1
fi

echo
echo "Next: in a project, say  activate glrp"
echo "Then set verify in .glrp/config.toml to a command that can fail."
echo "Do not also activate the old long-running-project / GLRP-Skill playbook here."
