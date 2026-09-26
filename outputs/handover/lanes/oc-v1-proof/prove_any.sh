#!/bin/sh
# prove_pieces.sh, parameterised by WHICH verifier and WHICH bytes it reads.
# usage: sh prove_any.sh <verifier.py> <source args: "--root docs" | "--url https://.../meta-harness/">
V="$1"; shift; SRC="$*"
echo "verifier $V sha256 $(sha256sum "$V" | cut -c1-64)"
echo "source   $SRC"
run() {
  python "$V" $SRC --slug glp1-ra-mace-t2d --json $2 > .oc_proof.json 2>/dev/null
  python - "$1" <<'EOF'
import json, sys
try:
    r = json.load(open(".oc_proof.json", encoding="utf-8"))
except Exception as e:
    print(f"{sys.argv[1]:<44} NO VERDICT ({type(e).__name__}) -- the check did not execute; not a pass"); sys.exit(0)
row = next((x for x in r.get("rows", []) if x["pmid"] == "27295427"), {})
codes = sorted({f.split(" ")[0] for f in r.get("failures", [])})
print(f"{sys.argv[1]:<44} verdict {r['verdict']:<4} LEADER {row.get('final')!s:<12} codes {codes}")
EOF
}
echo "(1) effect-scoped estimator witness + P10 value + ESTIMATOR_VALUE_MISMATCH incl. HR->RR"
run "canonical (witness = LEADER's result clause)" ""
run "estimator_owner_methods" "--corrupt 27295427 estimator_owner_methods"
run "estimator_claim_or" "--corrupt 27295427 estimator_claim_or"
run "estimator_label_rr (HR->RR, class matches)" "--corrupt 27295427 estimator_label_rr"
run "estimator_hr_abbrev (control)" "--corrupt 27295427 estimator_hr_abbrev"
run "estimator_linked_method (control)" "--corrupt 27295427 estimator_linked_method"
echo "(2) P11 registered contrast/estimator + COMPARATOR_DIRECTION_MISMATCH + declared reciprocal (PERMITTED)"
run "contrast_reverse (no reciprocal)" "--corrupt 27295427 contrast_reverse"
run "contrast_reverse_served" "--corrupt 27295427 contrast_reverse_served"
run "contrast_reverse_declared (served policy)" "--corrupt 27295427 contrast_reverse_declared"
run "contrast_reverse_declared_forbidden" "--corrupt 27295427 contrast_reverse_declared_forbidden"
run "contrast_reverse_declared_away (0.87->1.149)" "--corrupt 27295427 contrast_reverse_declared_away"
run "estimator_genuine_rr (RR not registered)" "--corrupt 27295427 estimator_genuine_rr"
echo "(3) measure-agnostic pooling refused before any log"
run "measure_unidentified" "--corrupt 27295427 measure_unidentified"
run "pool_input_reciprocal" "--corrupt 27295427 pool_input_reciprocal"
run "estimator_genuine_rr_permitted (row ok, pool mixed)" "--corrupt 27295427 estimator_genuine_rr_permitted"
echo "restore"
run "canonical again" ""
rm -f .oc_proof.json
