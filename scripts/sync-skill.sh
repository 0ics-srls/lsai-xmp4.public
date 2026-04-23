#!/usr/bin/env bash
# sync-skill.sh — keep html/xmp4-skill.md (public URL source of truth)
# and skills/xmp4/SKILL.md (Open Plugins standard) identical.
#
# Usage:
#   scripts/sync-skill.sh          # copy html/ → skills/ (default)
#   scripts/sync-skill.sh check    # exit 1 if the two files differ
#   scripts/sync-skill.sh reverse  # copy skills/ → html/
#
# Run before committing any change to the skill so the two copies never
# drift. Install as a git pre-commit hook if you want it automatic.

set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
src="$repo_root/html/xmp4-skill.md"
dst="$repo_root/skills/xmp4/SKILL.md"

case "${1:-sync}" in
    sync)
        mkdir -p "$(dirname "$dst")"
        cp "$src" "$dst"
        echo "synced: html/xmp4-skill.md → skills/xmp4/SKILL.md"
        ;;
    reverse)
        cp "$dst" "$src"
        echo "synced: skills/xmp4/SKILL.md → html/xmp4-skill.md"
        ;;
    check)
        if ! diff -q "$src" "$dst" >/dev/null; then
            echo "DIFF: html/xmp4-skill.md and skills/xmp4/SKILL.md are out of sync" >&2
            diff "$src" "$dst" | head -20 >&2
            exit 1
        fi
        echo "in sync"
        ;;
    *)
        echo "usage: $0 [sync|reverse|check]" >&2
        exit 2
        ;;
esac
