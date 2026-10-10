#!/usr/bin/env bash
# Refuses changes inside Closed revisions (CONTRIBUTING.md, section 9).
# Usage: bash .github/scripts/check-closed.sh <base-commit>
# Accepts: files in a new Revision_NNNN_Closed folder; the move of a Closed revision with no change of content.
set -euo pipefail

base="${1:?Usage: check-closed.sh <base-commit>}"
closed_re='Revision_[0-9]{4}_Closed'

# The Closed revision folders that exist on the base.
mapfile -t existing < <(git ls-tree -r -d --name-only "$base" | grep -E "(^|/)${closed_re}\$" || true)

inside_existing() {
  local path="$1" dir
  for dir in "${existing[@]}"; do
    [[ "$path" == "$dir/"* ]] && return 0
  done
  return 1
}

# The part of a path from the revision folder down, for example Revision_0001_Closed/kit/AGENTS.md.
revision_part() {
  [[ "$1" =~ (${closed_re}/.*)$ ]] && printf '%s' "${BASH_REMATCH[1]}"
}

errors=0
while IFS=$'\t' read -r status old new; do
  if [[ "$status" == R100 ]]; then
    # A move with no change of content: accepted only if the file keeps its place in the same Closed revision.
    if inside_existing "$old"; then
      if [[ -z "$(revision_part "$new")" || "$(revision_part "$old")" != "$(revision_part "$new")" ]]; then
        echo "REFUSED: $old moved to $new (a file of a Closed revision must keep its place in the revision)"
        errors=$((errors + 1))
      fi
    fi
    continue
  fi
  for path in "$old" ${new:+"$new"}; do
    if inside_existing "$path"; then
      echo "REFUSED: $status $path (Closed revisions do not change)"
      errors=$((errors + 1))
    fi
  done
done < <(git diff --name-status -M100% "$base" HEAD)

if (( errors > 0 )); then
  echo "$errors change(s) inside Closed revisions. Put the change in the Working revision. See CONTRIBUTING.md, section 6."
  exit 1
fi
echo "OK: no change inside Closed revisions."
