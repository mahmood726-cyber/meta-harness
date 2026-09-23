#!/usr/bin/env bash
# ONE codex slot, sequential; second adjudication of named rulings. Output verified by artefact (quotes checked
# against the same bytes by second_check.py), never by exit code.
cd "$(dirname "$0")/../.." || exit 2
for k in "$@"; do
  out="evidence/second_adjudication/$k.json"
  [ -s "$out" ] && continue
  codex exec --sandbox read-only --skip-git-repo-check --ephemeral -C "$PWD" -o "$out.tmp" \
    "Read evidence/SECOND_ADJUDICATION_BRIEF.md, then evidence/adjudication/$k.json and evidence/packets/$k.json. Follow the brief for KEY=$k. Read no other files. Output only the JSON object." \
    < /dev/null > "evidence/second_adjudication/$k.log" 2>&1
  python - "$out.tmp" "$out" <<'PY'
import json,sys,re,os
t=open(sys.argv[1],encoding='utf-8').read().strip() if os.path.exists(sys.argv[1]) else ''
t=re.sub(r'^```(json)?|```$','',t.strip()).strip()
try: json.dump(json.loads(t),open(sys.argv[2],'w',encoding='utf-8'),indent=1,ensure_ascii=False); print('OK',sys.argv[2])
except Exception as e: open(sys.argv[2]+'.unparsed','w',encoding='utf-8').write(t); print('UNPARSED',sys.argv[2],e)
PY
done
