#!/usr/bin/env bash
# Refuses changes to Closed revisions and to existing evaluation files (CONTRIBUTING.md, section 10).
# Usage: bash .github/scripts/check-closed.sh <base-commit>
# Each Closed revision folder and each evaluation file of the base MUST exist in HEAD with the same Git object
# (the same content). Only the stage folder MAY change: <Stage>_WorkFlow/<Name>_WorkFlow/<Target>/...
set -euo pipefail

base="${1:?Usage: check-closed.sh <base-commit>}"
git cat-file -e "$base^{tree}" 2>/dev/null || { echo "ERROR: $base is not a commit or a tree."; exit 1; }
closed_re='^[A-Za-z]+_WorkFlow/[^/]+_WorkFlow/[^/]+/Revision_[0-9]{4}_Closed$'
eval_re='^[A-Za-z]+_WorkFlow/[^/]+_WorkFlow/[^/]+/Evaluations/[^/]+\.md$'

items() {   # the protected paths of one commit: Closed folders and evaluation files
  { git ls-tree -r -d --name-only "$1" | grep -E "$closed_re"; git ls-tree -r --name-only "$1" | grep -E "$eval_re"; } || true
}
without_stage() { printf '%s' "${1#*_WorkFlow/}"; }

mapfile -t now < <(items HEAD)
errors=0
while IFS= read -r old; do
  [[ -z "$old" ]] && continue
  object=$(git rev-parse "$base:$old")
  found=""
  for new in "${now[@]}"; do
    if [[ "$(without_stage "$new")" == "$(without_stage "$old")" && "$(git rev-parse "HEAD:$new")" == "$object" ]]; then
      found="$new"; break
    fi
  done
  if [[ -z "$found" ]]; then
    echo "REFUSED: $old changed, or was deleted. Closed revisions and evaluations do not change."
    errors=$((errors + 1))
  fi
done < <(items "$base")

if (( errors > 0 )); then
  echo "$errors protected path(s) changed. Put a correction in the Working revision, or in a new evaluation file."
  exit 1
fi
echo "OK: no Closed revision and no evaluation changed."
