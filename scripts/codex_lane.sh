#!/bin/sh
# Launch one Codex lane in ITS OWN fresh clone at a named base SHA, from a written brief, backgrounded with stdin
# closed. Never two lanes on one worktree. Verify a lane by the model line in lane.log and by the artefact the brief
# names -- never by the wrapper's exit code (a codex exec left reading stdin exits 0 having done nothing).
#
# DISK (2026-09-15): a full clone is ~1.2 GB (.git 323 MB + 954 MB tree, 414 MB of it the run-r2 snapshots); seven of
# them filled C: and killed every lane at once. A lane clone now SHARES the integrator's object store (git clone -s,
# no object copy; lanes never commit) and sparse-checks-out the tree WITHOUT cache/*/snapshots/ (~213 MB), plus the
# extra paths the brief needs (4th arg, space-separated, e.g. "cache/<slug>/snapshots/2026-09-15r2-search_v2").
# The launcher refuses to start a lane with less than 3 GB free.
#   sh scripts/codex_lane.sh <LANE> <base_sha> <brief.md> ["<extra sparse path> ..."]
set -eu
LANE="$1"; BASE="$2"; BRIEF="$3"; EXTRA="${4:-}"
CLONE="/c/mh-r-$LANE"
[ -d "$CLONE" ] && { echo "REFUSED: $CLONE exists (never point two lanes at one worktree)"; exit 2; }
FREE_KB=$(df -k /c | awk 'NR==2{print $4}')
[ "$FREE_KB" -ge 3145728 ] || { echo "REFUSED: C: has $((FREE_KB/1024)) MB free (< 3 GB); not launching $LANE"; exit 3; }
git clone -q -s --no-checkout "C:/meta-harness" "$CLONE"
git -C "$CLONE" remote set-url origin https://github.com/mahmood726-cyber/meta-harness.git
git -C "$CLONE" sparse-checkout init --no-cone >/dev/null
{ echo "/*"; echo "!/cache/*/snapshots/"; for p in $EXTRA; do echo "/$p/"; done; } > "$CLONE/.git/info/sparse-checkout"
git -C "$CLONE" checkout -q --detach "$BASE"
cp "$BRIEF" "$CLONE/LANE_PROMPT.md"
mkdir -p "$CLONE/.tmp"
cd "$CLONE"
TMP="$CLONE/.tmp" TEMP="$CLONE/.tmp" TMPDIR="$CLONE/.tmp" \
  nohup codex exec -s workspace-write --skip-git-repo-check \
  "Read LANE_PROMPT.md in the current directory and do exactly what it says. Your finish condition and the artefact you must write are stated in it. Do not commit." \
  < /dev/null > lane.log 2>&1 &
echo "$!" > lane.pid          # MSYS pid of the shell job (NOT a Windows PID; tasklist cannot see it)
# The Windows PID of the codex process is what liveness is judged on: the youngest codex.exe whose command line is
# this launcher's prompt. Recorded after 8 s; the queue also judges by log growth.
sleep 8
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq 'codex.exe' -and \$_.CommandLine -match 'Read LANE_PROMPT' } | Sort-Object CreationDate -Descending | Select-Object -First 1 -ExpandProperty ProcessId" > lane.winpid 2>/dev/null || true
echo "LANE $LANE launched: clone=$CLONE base=$(git rev-parse --short HEAD) size=$(du -sm "$CLONE" | cut -f1)MB winpid=$(tr -d '[:space:]' < lane.winpid) log=$CLONE/lane.log"
