#!/bin/sh
# Launch queued Codex lanes as RAM and disk allow, one at a time, without a Claude turn per launch.
# queue file lines: <LANE> <base_sha> <brief.md>   (a line starting with # or already-launched lanes are skipped)
# Floors: free RAM >= RAM_FLOOR_MB before a launch (measured, not assumed); the launcher itself refuses < 3 GB disk.
# Log: queue.log beside this script. Verify a launched lane by its lane.log tokens, never by this script's exit.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
QUEUE="$HERE/queue.txt"; LOG="$HERE/queue.log"
RAM_FLOOR_MB=${RAM_FLOOR_MB:-2000}
MAX_LANES=${MAX_LANES:-10}
INTERVAL=${INTERVAL:-240}
free_mb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1KB)" 2>/dev/null | tr -d '\r '; }
while :; do
  next=$(grep -v '^#' "$QUEUE" | while read -r lane base brief; do
    [ -n "${lane:-}" ] || continue
    [ -d "/c/mh-r-$lane" ] && continue
    echo "$lane $base $brief"; break
  done)
  [ -n "$next" ] || { echo "$(date +%T) queue empty; exiting" >> "$LOG"; exit 0; }
  set -- $next; lane=$1; base=$2; brief=$3
  ram=$(free_mb); [ -n "$ram" ] || ram=0
  nlanes=$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq 'codex.exe' -and \$_.CommandLine -match 'Read LANE_PROMPT' }).Count" 2>/dev/null | tr -d '
 '); [ -n "$nlanes" ] || nlanes=99
  if [ "$ram" -ge "$RAM_FLOOR_MB" ] && [ "$nlanes" -le "$MAX_LANES" ]; then
    echo "$(date +%T) launching $lane (free RAM ${ram} MB)" >> "$LOG"
    ( cd /c/meta-harness && sh scripts/codex_lane.sh "$lane" "$base" "$brief" ) >> "$LOG" 2>&1
    sleep 90   # let the clone + first model call settle before measuring RAM again
  else
    echo "$(date +%T) holding $lane: free RAM ${ram} MB (floor ${RAM_FLOOR_MB}); lane-root codex ${nlanes} (max ${MAX_LANES})" >> "$LOG"
    sleep "$INTERVAL"
  fi
done
