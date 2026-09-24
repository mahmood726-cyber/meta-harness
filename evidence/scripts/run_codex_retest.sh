#!/usr/bin/env bash
# ONE codex slot, sequential. Skips rows whose output already parses. Usage: run_codex.sh KEY [KEY...]
cd "$(dirname "$0")/../.." || exit 2
mkdir -p evidence/extractions/retest
for k in "$@"; do
  out="evidence/extractions/retest/$k.json"
  if [ -s "$out" ] && python -c "import json,sys;json.load(open(sys.argv[1],encoding='utf-8'))" "$out" 2>/dev/null; then continue; fi
  codex exec --sandbox read-only --skip-git-repo-check --ephemeral -C "$PWD" -o "$out.tmp" \
    "Read evidence/EXTRACTION_BRIEF.md, then read evidence/packets/$k.json, and follow the brief for that packet. Output only the JSON object." \
    < /dev/null > "evidence/extractions/retest/$k.log" 2>&1
  python - "$out.tmp" "$out" <<'PY'
import json,sys,re
t=open(sys.argv[1],encoding='utf-8').read().strip() if __import__('os').path.exists(sys.argv[1]) else ''
t=re.sub(r'^```(json)?|```$','',t.strip()).strip()
try:
    d=json.loads(t); json.dump(d,open(sys.argv[2],'w',encoding='utf-8'),indent=1,ensure_ascii=False); print('OK',sys.argv[2])
except Exception as e:
    open(sys.argv[2]+'.unparsed','w',encoding='utf-8').write(t); print('UNPARSED',sys.argv[2],e)
PY
done
