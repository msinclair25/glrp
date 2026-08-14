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
if [[ -d "${GROK_HOME:-$HOME/.grok}" ]]; then
  install_one "${GROK_HOME:-$HOME/.grok}/skills/glrp" "$SRC/grok/SKILL.md"
  found=1
fi
if [[ -d "${HERMES_HOME:-$HOME/.hermes}" ]]; then
  install_one "${HERMES_HOME:-$HOME/.hermes}/skills/glrp" "$SRC/hermes/SKILL.md"
  found=1
fi

if [[ "$found" -eq 0 ]]; then
  echo "error: neither ~/.grok nor ~/.hermes exists" >&2
  exit 1
fi

echo
echo "Next: in a project, say  activate glrp"
echo "Then set verify in .glrp/config.toml to a command that can fail."
echo "Do not also activate the old long-running-project / GLRP-Skill playbook here."
