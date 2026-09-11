#!/bin/sh
# Harvest a Codex lane's UNCOMMITTED artefacts to durable scratch BEFORE the clone is ever
# reset or reused. Codex cannot commit (sandbox blocks .git), so a lane's output lives only as
# untracked files in its clone -- and a `git reset --hard`/`clean`/reuse destroys it (this cost
# us empagliflozin once and the gated statins page once). Run this the moment a lane completes.
#   sh scripts/harvest_lane.sh <clone_dir> <harvest_dir>
set -eu
CLONE="$1"; DEST="$2"
mkdir -p "$DEST"
# copy exactly the artefact kinds a lane produces; -a preserves, || true so a missing kind is fine
for p in VERIFY-*.md RECALL-*.md CLASSIFY-*.md REATTEMPT-*.md CMPK-*.md; do
  cp -a "$CLONE"/$p "$DEST"/ 2>/dev/null || true
done
for d in topics protocols cache; do
  [ -d "$CLONE/$d" ] && cp -a "$CLONE/$d" "$DEST"/ 2>/dev/null || true
done
echo "harvested $CLONE -> $DEST ($(ls "$DEST" | wc -l) entries)"
