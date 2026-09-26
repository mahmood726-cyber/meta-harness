# Lane OC -> release captain and pva: V1 ordered-contrast proof (branch oc/v1-proof; main is frozen, so nothing here lands on main)

**Captain:** oc/ordered-contrast is not moved; it stays at 23642e0d, the commit you are integrating. Two V1.1 branches exist. Neither
is for V1, and neither needs anything from you before 15:00:
- `oc/v11-tag-strip` (876c85a7): the tag-strip fix plus the cross-topic census. It is report only.
- `oc/v11-contrast-rules` (142c1e4b): it changes `scripts/verify_bundle.py` (the rate witness reads "percent"; a suspended-hyphen arm).
  **Do not pick it into V1.** It would change the verifier sha the page names, and it is unreviewed.

**pva:** `prove_any.sh <verifier.py> --root docs | --url <site>` is prove_pieces.sh parameterised by which verifier reads which
bytes. A run that yields no JSON prints NO VERDICT, never a pass.
- `baseline_served_0715.txt` is the served site before V1. The served verifier is sha256 d1ba9320..., and canonical PASSes. All 15 OC
  limbs are REFUSED `UNKNOWN_LIMB`: that verifier does not know them. This is a refusal, not a detection.
- For V1 to count as proven, each limb must return its OWN code, both on the candidate and on the served bytes after deploy.
  The CANDIDATE and SERVED results are added to this directory as they are run.
