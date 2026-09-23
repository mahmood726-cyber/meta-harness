#!/usr/bin/env bash
# Re-extract rows whose extraction FAILS verification, telling codex exactly which spans failed. ONE slot.
cd "$(dirname "$0")/../.." || exit 2
python evidence/scripts/verify_records.py > /dev/null
keys=$(python -c "import json;v=json.load(open('evidence/extractions/verification.json'));print(' '.join(k for k,x in v.items() if x['errors']))")
for k in $keys; do
  errs=$(python -c "import json,sys;print(' | '.join(json.load(open('evidence/extractions/verification.json'))[sys.argv[1]]['errors']))" "$k")
  mv "evidence/extractions/raw/$k.json" "evidence/extractions/raw/$k.attempt1.bak"
  codex exec --sandbox read-only --skip-git-repo-check --ephemeral -C "$PWD" -o "evidence/extractions/raw/$k.json.tmp" \
    "Read evidence/EXTRACTION_BRIEF.md and evidence/packets/$k.json. Your previous answer is evidence/extractions/raw/$k.attempt1.bak. A mechanical verifier REFUSED it: $errs. Every span must be an exact character-for-character substring of the named source's text (no joining, no ellipsis, no re-typed characters). Fix only what failed, keep everything else, and output only the corrected JSON object. Read no other files." \
    < /dev/null > "evidence/extractions/raw/$k.retry.log" 2>&1
  python - "evidence/extractions/raw/$k.json.tmp" "evidence/extractions/raw/$k.json" <<'PY'
import json,sys,re,os
t=open(sys.argv[1],encoding='utf-8').read().strip() if os.path.exists(sys.argv[1]) else ''
t=re.sub(r'^```(json)?|```$','',t.strip()).strip()
try: json.dump(json.loads(t),open(sys.argv[2],'w',encoding='utf-8'),indent=1,ensure_ascii=False); print('OK',sys.argv[2])
except Exception as e: open(sys.argv[2]+'.unparsed','w',encoding='utf-8').write(t); print('UNPARSED',sys.argv[2],e)
PY
done
python evidence/scripts/verify_records.py | tail -1
