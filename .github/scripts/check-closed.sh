#!/usr/bin/env bash
# Refuses changes inside Closed revisions (CONTRIBUTING.md, section 9).
# Usage: bash .github/scripts/check-closed.sh <base-commit>
# Each Closed revision of the base MUST exist in HEAD with an identical Git tree (the same content, file by file).
# The stage folder MAY change: <Stage>_WorkFlow/<Name>_WorkFlow/<Target>/Revision_NNNN_Closed.
set -euo pipefail

base="${1:?Usage: check-closed.sh <base-commit>}"
closed_re='Revision_[0-9]{4}_Closed$'

closed_folders() {
  git ls-tree -r -d --name-only "$1" | grep -E "(^|/)${closed_re}" || true
}

# The path without the stage folder: <Name>_WorkFlow/<Target>/Revision_NNNN_Closed.
without_stage() {
  printf '%s' "${1#*_WorkFlow/}"
}

mapfile -t now < <(closed_folders HEAD)
errors=0
while IFS= read -r old; do
  [[ -z "$old" ]] && continue
  old_tree=$(git rev-parse "$base:$old")
  found=""
  for new in "${now[@]}"; do
    if [[ "$(without_stage "$new")" == "$(without_stage "$old")" && "$(git rev-parse "HEAD:$new")" == "$old_tree" ]]; then
      found="$new"
      break
    fi
  done
  if [[ -z "$found" ]]; then
    echo "REFUSED: $old changed, or was deleted. Closed revisions do not change."
    git diff --stat "$base" HEAD -- "$old" | sed 's/^/  /'
    errors=$((errors + 1))
  fi
done < <(closed_folders "$base")

if (( errors > 0 )); then
  echo "$errors Closed revision(s) changed. Put the change in the Working revision. See CONTRIBUTING.md, section 6."
  exit 1
fi
echo "OK: no change inside Closed revisions."
