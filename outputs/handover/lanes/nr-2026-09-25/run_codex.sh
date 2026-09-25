#!/bin/bash
# usage: run_codex.sh <job_dir> <call_id>   -- one slot; every call logged to CALL_LOG.jsonl; stdin </dev/null
set -u
J="$1"; ID="$2"; LOG=/c/mh-lanes/nr/codex/CALL_LOG.jsonl
[ -f "$J/LANE_CONTEXT.md" ] || { echo "no LANE_CONTEXT.md in $J" >&2; exit 2; }
if [ -e /c/mh-lanes/nr/codex/SLOT.lock ]; then echo "slot busy" >&2; exit 3; fi
echo "$ID $$" > /c/mh-lanes/nr/codex/SLOT.lock
PROMPT="Read LANE_CONTEXT.md, then BRIEF.md, in this directory, and do exactly what BRIEF.md says."
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
( cd "$J" && timeout 3000 codex exec --sandbox read-only --skip-git-repo-check -o "$J/last_message.txt" "$PROMPT" < /dev/null > "$J/stdout.txt" 2> "$J/stderr.txt" ); RC=$?
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
rm -f /c/mh-lanes/nr/codex/SLOT.lock
python /c/mh-lanes/nr/codex/log_call.py "$J" "$ID" "$START" "$END" "$RC" "$PROMPT" || { echo "LOG FAILED" >&2; exit 4; }
grep -q "\"call_id\": \"$ID\"" /c/mh-lanes/nr/codex/CALL_LOG.jsonl || { echo "LOG LINE ABSENT" >&2; exit 5; }
echo "rc=$RC"
