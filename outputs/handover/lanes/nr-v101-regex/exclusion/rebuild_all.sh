#!/bin/bash
# usage: rebuild_all.sh OUTDIR   -- rebuild every served topic in F:/mh-nr101 with its CURRENT harness; save review.json;
# restore docs/ and registry/ after each build so each topic is built from the committed tree
cd F:/mh-nr101 || exit 1
out=$1; mkdir -p "$out"
for d in docs/reviews/*/; do
  slug=$(basename "$d")
  [ -f "topics/$slug.json" ] || continue
  git cat-file -e "HEAD:docs/reviews/$slug/review.json" 2>/dev/null || continue
  if PYTHONUTF8=1 python scripts/build_topic_recorded.py "$slug" --now 2026-09-11 > "$out/$slug.log" 2>&1; then
    cp "docs/reviews/$slug/review.json" "$out/$slug.review.json"; echo "OK $slug"
  else
    echo "FAIL $slug rc=$? $(tail -1 "$out/$slug.log")"
  fi
  git checkout -q -- docs registry 2>/dev/null
  git clean -qfd docs 2>/dev/null
done
echo DONE
