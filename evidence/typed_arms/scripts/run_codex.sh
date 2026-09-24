#!/usr/bin/env bash
# One codex slot, sequential over the job ids given. Verified by ARTEFACT (check_typed_arms.py), never by exit code.
# Every call is logged: the exact prompt, the model, the raw --json event stream (off-repo, C:/mh-lanes/evid2-logs),
# and a summary line (files read, commands run, tokens) appended to CALL_LOG.jsonl in the lane logs dir.
JOBS="${JOBS:-C:/mh-lanes/evid2-codex/typed_arms}"; LOGS="${LOGS:-C:/mh-lanes/evid2-logs}"; MODEL="${MODEL:-gpt-6-astra}"
PROMPT='Read LANE_CONTEXT.md and BRIEF.md in the current directory and follow BRIEF.md exactly for the row in row.json. Read only files in the current directory. Write only out.json in the current directory.'
for k in "$@"; do
  d="$JOBS/$k"; [ -s "$d/out.json" ] && continue
  ts=$(date -u +%Y%m%dT%H%M%SZ)
  codex exec --json --sandbox workspace-write --skip-git-repo-check --ephemeral -m "$MODEL" \
     -c model_reasoning_effort=medium -c project_doc_max_bytes=0 -C "$d" "$PROMPT" \
     < /dev/null > "$LOGS/$k.$ts.jsonl" 2> "$LOGS/$k.$ts.stderr"
  python "$(dirname "$0")/log_call.py" "$k" "$d" "$LOGS/$k.$ts.jsonl" "$MODEL" "$PROMPT" >> "$LOGS/CALL_LOG.jsonl"
done
