#!/bin/sh
# Install the llmref Claude skill into a directory Claude Code discovers.
#
#   curl -fsSL https://raw.githubusercontent.com/reclear-io/llmref-skill/main/install.sh | sh
#
# Override the target with LLMREF_SKILL_DIR (default: ~/.claude/skills/llmref):
#
#   LLMREF_SKILL_DIR=.claude/skills/llmref sh -c "$(curl -fsSL .../install.sh)"

set -eu

REPO="https://github.com/reclear-io/llmref-skill"
TARBALL="https://codeload.github.com/reclear-io/llmref-skill/tar.gz/refs/heads/main"
DEST="${LLMREF_SKILL_DIR:-$HOME/.claude/skills/llmref}"

if [ -e "$DEST" ]; then
  printf 'llmref-skill: target already exists: %s\n' "$DEST" >&2
  printf 'Remove it or set LLMREF_SKILL_DIR to a different path, then re-run.\n' >&2
  exit 1
fi

mkdir -p "$DEST"

if command -v git >/dev/null 2>&1; then
  # Clone in place so `git pull` can update later.
  rmdir "$DEST" 2>/dev/null || true
  git clone --depth 1 "$REPO" "$DEST"
else
  # No git — fall back to fetching and extracting the tarball.
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$TARBALL" | tar -xz -C "$DEST" --strip-components=1
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- "$TARBALL" | tar -xz -C "$DEST" --strip-components=1
  else
    printf 'llmref-skill: need git, curl, or wget to install.\n' >&2
    exit 1
  fi
fi

printf '\nllmref skill installed to %s\n' "$DEST"
printf 'Reload Claude Code (or run `claude skills`) to pick it up.\n'
