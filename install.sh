#!/usr/bin/env bash
# Install GLRP skill into Grok Build and/or Hermes if those homes exist.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/skill"
if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "error: missing $SRC/SKILL.md" >&2
  exit 1
fi

install_one() {
  local dest="$1"
  local wrapper="$2"
  mkdir -p "$dest/scripts"
  rm -f "$dest/scripts/"*.py
  cp "$SRC/scripts/"*.py "$dest/scripts/"
  chmod +x "$dest/scripts/"*.py
  cp "$wrapper" "$dest/SKILL.md"
  echo "Installed: $dest"
}

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
