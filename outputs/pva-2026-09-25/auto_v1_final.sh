#!/bin/sh
# Wait for main to move off the frozen 6260e70c (only the release captain lands, so the new main IS V1), then run the whole
# post-deploy phase on it. v1_final's first step waits for the production record + the CDN max-age before anything served.
FROZEN=6260e70cc998
WORK=F:/mh-pva-v1final
for i in $(seq 1 240); do             # up to 8 h, polling every 2 min
  new=$(timeout 60 git -C C:/mh-lanes/pva ls-remote origin refs/heads/main 2>/dev/null | cut -c1-40)
  if [ -n "$new" ] && [ "${new#$FROZEN}" = "$new" ]; then
    echo "$(date +%H:%M:%S) main moved: $new -- starting v1_final"
    timeout 120 git -C C:/mh-lanes/pva fetch -q origin main production-records
    python C:/mh-lanes/pva/v1/v1_final.py --v1 "$new" --work "$WORK" --wt-root F:/mh-pva-wt < /dev/null
    echo "$(date +%H:%M:%S) v1_final exited rc=$?"
    exit 0
  fi
  sleep 120
done
echo "$(date +%H:%M:%S) main did not move in 8 h"
