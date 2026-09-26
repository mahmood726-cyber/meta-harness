#!/bin/sh
# Wait for main to move off the frozen 6260e70c (only the release captain lands, so the new main IS V1), then run the whole
# post-deploy phase on it. v1_final's first step waits for the production record + the CDN max-age before anything served.
# The work directory goes on whichever of C:/F: has more free space AT TRIGGER TIME (both drives swing by GBs as lanes run).
FROZEN=6260e70cc998
for i in $(seq 1 480); do             # up to 16 h, polling every 2 min
  new=$(timeout 60 git -C C:/mh-lanes/pva ls-remote origin refs/heads/main 2>/dev/null | cut -c1-40)
  if [ -n "$new" ] && [ "${new#$FROZEN}" = "$new" ]; then
    c=$(df -m /c | awk 'NR==2{print $4}'); f=$(df -m /f | awk 'NR==2{print $4}')
    if [ "$c" -ge "$f" ]; then WORK=C:/mh-pva-v1final; WT=C:/mh-pva-wt; else WORK=F:/mh-pva-v1final; WT=F:/mh-pva-wt; fi
    echo "$(date +%H:%M:%S) main moved: $new -- starting v1_final in $WORK (C ${c} MB, F ${f} MB free)"
    timeout 120 git -C C:/mh-lanes/pva fetch -q origin main production-records
    python C:/mh-lanes/pva/v1/v1_final.py --v1 "$new" --work "$WORK" --wt-root "$WT" < /dev/null
    echo "$(date +%H:%M:%S) v1_final exited rc=$?"
    exit 0
  fi
  sleep 120
done
echo "$(date +%H:%M:%S) main did not move in 16 h"
