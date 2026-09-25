#!/usr/bin/env bash
# One codex slot, sequential over the job ids given. Verified by ARTEFACT (check_typed_arms.py), never by exit code.
# Every call is logged: the exact prompt, the model, the raw --json event stream (off-repo, C:/mh-lanes/evid2-logs),
# and a summary line (files read, commands run, tokens) appended to CALL_LOG.jsonl in the lane logs dir.
JOBS="${JOBS:-C:/mh-lanes/evid2-codex/typed_arms}"; LOGS="${LOGS:-C:/mh-lanes/evid2-logs}"; MODEL="${MODEL:-gpt-6-astra}"
PROMPT="${PROMPT:-Read LANE_CONTEXT.md and BRIEF.md in the current directory and follow BRIEF.md exactly for the row in row.json. Read only files in the current directory. Write only out.json in the current directory.}"
for k in "$@"; do
  d="$JOBS/$k"; [ -s "$d/out.json" ] && continue
  ts=$(date -u +%Y%m%dT%H%M%SZ)
  codex exec --json --sandbox workspace-write --skip-git-repo-check --ephemeral -m "$MODEL" \
     -c model_reasoning_effort=medium -c project_doc_max_bytes=0 -C "$d" "$PROMPT" \
     < /dev/null > "$LOGS/$k.$ts.jsonl" 2> "$LOGS/$k.$ts.stderr"
  # one summary file per call, then CALL_LOG.jsonl rebuilt by concatenation: two slots appending to one file on
  # Windows lost one line and interleaved another (2026-09-25); a rebuild from complete per-call files cannot.
  python "$(dirname "$0")/log_call.py" "$k" "$d" "$LOGS/$k.$ts.jsonl" "$MODEL" "$PROMPT" > "$LOGS/$k.$ts.call.json"
  cat "$LOGS"/*.call.json > "$LOGS/CALL_LOG.jsonl.$$.tmp" && mv -f "$LOGS/CALL_LOG.jsonl.$$.tmp" "$LOGS/CALL_LOG.jsonl"
done
