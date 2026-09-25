#!/usr/bin/env bash
# Land the lane branch on main: fast-forward ONLY, only after the `verify` check passed on the exact commit, only if
# the commit changes nothing under docs/ (served bytes). If main moves while CI runs, merge main, push, and retry --
# at most 5 attempts. Prints what it did; exit 0 only when main's remote ref equals the landed commit.
cd "$(dirname "$0")/../.." || exit 2
for attempt in 1 2 3 4 5; do
  git fetch -q origin
  if ! git merge-base --is-ancestor origin/main HEAD; then
    git merge -q --no-edit origin/main || { echo "MERGE_CONFLICT attempt $attempt"; exit 4; }
    git push -q origin HEAD:evid/evidence-records || exit 5
  fi
  S=$(git rev-parse HEAD)
  if [ "$(git diff --name-only origin/main "$S" -- docs | wc -l)" -ne 0 ]; then echo "REFUSED: $S changes docs/"; exit 6; fi
  until id=$(gh run list --commit "$S" --workflow verify --json databaseId -q '.[0].databaseId' 2>/dev/null) && [ -n "$id" ]; do sleep 30; done
  until s=$(gh run view "$id" --json status,conclusion -q '.status+" "+.conclusion') && [ "${s%% *}" = completed ]; do sleep 60; done
  echo "attempt $attempt: ci $s on ${S:0:8}"
  if [ "$s" != "completed success" ]; then gh run view "$id" --log-failed 2>/dev/null | grep -E "FAILED|REFUSED\]" | cut -c60-300 | head -8; exit 1; fi
  git fetch -q origin
  if git merge-base --is-ancestor origin/main "$S"; then
    git push origin "$S:refs/heads/main" 2>&1 | tail -1
    [ "$(git ls-remote origin refs/heads/main | cut -f1)" = "$S" ] && { echo "LANDED ${S:0:8}"; exit 0; }
  fi
  echo "main moved to $(git rev-parse --short origin/main); retrying"
done
echo "GAVE_UP after 5 attempts"; exit 3
