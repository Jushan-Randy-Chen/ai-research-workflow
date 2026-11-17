#!/usr/bin/env bash
# Overleaf <-> paper/ via plain git (Overleaf "Git integration", premium feature; or GitHub sync).
#
#   scripts/overleaf.sh clone <overleaf-project-id>   # one-time: clones into paper/ (its own git repo, ignored here)
#   scripts/overleaf.sh pull                          # always safe; run before editing
#   scripts/overleaf.sh push "message"                # refused while research-loop gate 4 is closed and the
#                                                     # staged change touches figures/ or tables/ (results)
#
# Authentication: Overleaf git tokens go in a git credential store OUTSIDE the repo, never in a URL:
#   git config --global credential.https://git.overleaf.com.helper "store --file=$HOME/.config/overleaf/credentials"
#   (username "git", password = the token from Overleaf > Account settings > Git integration)
set -euo pipefail
cd "$(dirname "$0")/.."
PAPER=paper

case "${1:-}" in
  clone)
    [ -n "${2:-}" ] || { echo "usage: $0 clone <overleaf-project-id>"; exit 2; }
    [ -d "$PAPER/.git" ] && { echo "$PAPER/ is already a git checkout"; exit 1; }
    tmp=$(mktemp -d)
    git clone "https://git.overleaf.com/$2" "$tmp/paper"
    cp -rn "$tmp/paper/." "$PAPER/" && rm -rf "$tmp"
    echo "cloned into $PAPER/ (remote: $(git -C "$PAPER" remote get-url origin))"
    ;;
  pull)
    git -C "$PAPER" pull --ff-only
    ;;
  push)
    msg="${2:-Update from research repo}"
    git -C "$PAPER" add -A
    if git -C "$PAPER" diff --cached --name-only | grep -Eq '^(figures|tables)/'; then
      if ! uv run research-loop gate 4 --skip-results; then
        echo "Refusing: results in figures/ or tables/ changed while gate 4 is CLOSED (see: uv run research-loop status)."
        git -C "$PAPER" reset -q
        exit 1
      fi
    fi
    git -C "$PAPER" commit -m "$msg" && git -C "$PAPER" push
    ;;
  *)
    sed -n '2,12p' "$0"; exit 2 ;;
esac
