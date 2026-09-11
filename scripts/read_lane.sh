#!/bin/sh
# Read a Codex lane artefact TOPIC-SCOPED and VERIFIED-BY-NAME, so a stale file from a prior lane
# use (untracked files survive `git reset --hard`) can NEVER be mistaken for this lane's fresh
# output. This is the fix for the donor-evidence shape: two recall lanes once read another topic's
# stale RECALL-*.md and reported it as their own.
#   sh scripts/read_lane.sh <clone_dir> <kind> <slug>
# Prints the artefact ONLY if <clone>/<KIND>-<slug>.md exists AND its content references <slug>.
set -eu
CLONE="$1"; KIND="$2"; SLUG="$3"
F="$CLONE/${KIND}-${SLUG}.md"
if [ ! -f "$F" ]; then
  echo "READ-LANE: no artefact $F (lane did not produce ${KIND}-${SLUG}.md) — treat as a FAILED lane"; exit 3
fi
if ! grep -q "$SLUG" "$F"; then
  echo "READ-LANE: REFUSE — $F does not reference '$SLUG' in its content (stale/wrong-topic file); not reading"; exit 4
fi
echo "READ-LANE OK: $F (verified references $SLUG)"
cat "$F"
