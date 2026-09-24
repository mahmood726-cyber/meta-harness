#!/usr/bin/env bash
# The lane's ONE codex slot: take jobs from evidence/codex_queue.txt one at a time, forever, until STOP exists.
# A job line: <kind> <key> <brief> <dest> [--with-adjudication]
# Finished lines move to evidence/codex_queue.done (with OK/FAILED); an empty queue waits 60 s and re-reads.
cd "$(dirname "$0")/../.." || exit 2
Q=evidence/codex_queue.txt; DONE=evidence/codex_queue.done
touch "$Q" "$DONE"
while [ ! -e evidence/codex_queue.STOP ]; do
  line=$(head -n 1 "$Q")
  if [ -z "$line" ]; then sleep 60; continue; fi
  tail -n +2 "$Q" > "$Q.tmp" && mv "$Q.tmp" "$Q"
  set -- $line
  kind=$1; key=$2; brief=$3; dest=$4; extra=$5
  if [ -s "$dest" ]; then echo "SKIP(exists) $line" >> "$DONE"; continue; fi
  if PYTHONIOENCODING=utf-8 timeout 1200 python evidence/scripts/codex_job.py --kind "$kind" --key "$key" --brief "$brief" --dest "$dest" $extra; then
    echo "OK $(date -u +%FT%TZ) $line" >> "$DONE"
  else
    echo "FAILED $(date -u +%FT%TZ) $line" >> "$DONE"
  fi
done
