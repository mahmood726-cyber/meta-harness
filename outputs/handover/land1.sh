#!/bin/sh
# Landing 1 chain, detached: wait for the hook commit (by HEAD moving, never rc) -> push branch -> wait for CI on that
# SHA -> on green push SHA:main -> prove by ls-remote -> poll the served manifest until commit_sha matches.
# Log: land1.log beside this script. Every step writes the artefact it proves, never an exit code alone.
set -u
HERE=$(cd "$(dirname "$0")" && pwd); LOG="$HERE/land1.log"; INT=/c/mh-int; PREV=768c98fb539969c99716a5974e118d134ad6cf62
log() { echo "$(date +%T) $*" >> "$LOG"; }
log "waiting for the hook commit (commit2.log COMMIT_RC)"
until grep -q COMMIT_RC "$HERE/commit2.log" 2>/dev/null; do sleep 20; done
SHA=$(git -C $INT rev-parse HEAD)
if [ "$SHA" = "$PREV" ]; then log "HOOK REFUSED: HEAD still $PREV"; tail -40 "$HERE/commit2.log" >> "$LOG"; exit 1; fi
log "commit exists: $SHA ($(git -C $INT show --stat --format= HEAD | tail -1))"
git -C $INT push -q origin fix/phase1-integration >> "$LOG" 2>&1
log "branch ls-remote: $(git -C $INT ls-remote origin refs/heads/fix/phase1-integration)"
RUN=""; n=0
while [ -z "$RUN" ] && [ $n -lt 30 ]; do sleep 20; n=$((n+1))
  RUN=$(cd $INT && gh run list --branch fix/phase1-integration --limit 5 --json databaseId,headSha --jq ".[] | select(.headSha==\"$SHA\") | .databaseId" | head -1); done
[ -n "$RUN" ] || { log "no CI run found for $SHA after 10 min"; exit 1; }
log "CI run $RUN on $SHA"
STATUS=""; n=0
while [ "$STATUS" != "completed" ] && [ $n -lt 180 ]; do sleep 30; n=$((n+1))
  STATUS=$(cd $INT && gh run view "$RUN" --json status --jq .status); done
CONC=$(cd $INT && gh run view "$RUN" --json conclusion --jq .conclusion)
log "CI $RUN: status=$STATUS conclusion=$CONC"
if [ "$CONC" != "success" ]; then (cd $INT && gh run view "$RUN" --log-failed 2>/dev/null | grep -E "REFUSED|FAIL |Error" | sed 's/^[^\t]*\t[^\t]*\t//' | head -20) >> "$LOG"; log "NOT pushing to main"; exit 1; fi
git -C $INT push origin "$SHA:main" >> "$LOG" 2>&1
log "main ls-remote: $(git -C $INT ls-remote origin refs/heads/main)"
n=0; SERVED=""
while [ "$SERVED" != "$SHA" ] && [ $n -lt 60 ]; do sleep 60; n=$((n+1))
  SERVED=$(curl -s -m 20 https://mahmood726-cyber.github.io/meta-harness/_production/manifest.json | python -c "import sys,json; print(json.load(sys.stdin).get('commit_sha',''))" 2>/dev/null); done
log "served manifest commit_sha: $SERVED (pushed $SHA) after $n min"
(cd $INT && gh run list --branch main --limit 3 --json databaseId,status,conclusion,workflowName,headSha --jq '.[] | "\(.workflowName) \(.headSha[0:8]) \(.status) \(.conclusion)"') >> "$LOG" 2>&1
log "done"
