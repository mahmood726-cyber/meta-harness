#!/usr/bin/env bash
# Keeps the lane's one codex slot busy with USEFUL work when the queue is empty: enqueue ONE blind recorded
# re-extraction of a random U23/S16 row (seeded by the UTC hour, recorded in the dest path). evidence/scripts/
# canary_score.py compares each result with the adjudicated served number: a drift measure over time, and any
# divergence names a row to re-open. Stops when evidence/codex_queue.STOP exists.
cd "$(dirname "$0")/../.." || exit 2
while [ ! -e evidence/codex_queue.STOP ]; do
  if [ ! -s evidence/codex_queue.txt ]; then
    stamp=$(date -u +%Y%m%dT%H%M)
    key=$(python -c "
import json,random,sys
ks=sorted(w['key'] for w in json.load(open('evidence/worklist.json'))['rows'] if w['kind'] in ('U23','S16'))
print(random.Random(sys.argv[1]).choice(ks))" "$stamp")
    echo "retest $key evidence/EXTRACTION_BRIEF.md evidence/extractions/canary/$stamp-$key.json" >> evidence/codex_queue.txt
  fi
  sleep 45
done
