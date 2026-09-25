# Handoff to the release captain (main lane): GLP-1 MACE result-level adjudication, plus a renderer defect in harness/

From: the evidence lane (evid/evidence-records), 2026-09-25, ahead of the Sat 09:00 V1 freeze. Assignment: a senior external review, forwarded by Mahmood.

## 1. Decisions (evidence/glp1_adjudication/): nothing served changed
| trial | eligibility (protocol b10c53d3) | bound 3-point MACE result | consequence |
|---|---|---|---|
| FLOW | ELIGIBLE, CONVENTIONAL_GLP1RA (primary) | HR 0.82 (0.68–0.98), 212/1767 vs 254/1766, all randomised, in-trial, Cox stratified by SGLT2i (FDA label Table 10; NEJM abstract agrees) | primary pool (signature) |
| ELIXA | ELIGIBLE, CONVENTIONAL_GLP1RA (primary) | HR 1.02 (0.887–1.172), 400 vs 392 of 3,034 per arm, ITT on-study (FDA StatR s3.3.4.3); **not** the 4-point MACE+ 1.017 (0.886–1.168), 406 vs 399 | primary pool (signature) |
| FREEDOM-CVO | ELIGIBLE on GLP1RA_ANY_DELIVERY **only** (the protocol's agent list places ITCA 650 there) | HR 1.24 (0.90–1.70), 85/2075 vs 69/2081, ITT end-of-study (FDA briefing Table 19); **not** the on-treatment 1.36 or the 4-point 1.21 | any-delivery strand only; primary unaffected |

- Before → after: `BEFORE_AFTER.json`, from your production path (`harness.known_missing` → `harness.synth.pool`). The recomputed BEFORE reproduces the served k=8 0.856 (0.8086–0.9061) exactly. The primary strand after + FLOW + ELIXA is k=10, 0.861 (0.807–0.919), PI 0.753–0.985. Conclusion unchanged; heterogeneity no longer ~0.
- **Queued for Mahmood:** `SIGNATURE_REQUEST.md` (bundle sha256 inside). Please do not land the admission unsigned.
- Relation to the integrator's proposals in `outputs/handover/glp1_regulatory/ADJUDICATIONS.json`: these decisions **agree** with ADJ-GLP1-001 (FREEDOM end-of-study row), ADJ-GLP1-003 (FLOW label row, in-trial) and ADJ-GLP1-005 (ELIXA unrounded text, identity by definition plus counts). They **add** per-field witnesses (population, analysis, contrast, timepoint) that the served `held_regulatory_facts` currently leave null, and the strand decision for FREEDOM-CVO from the protocol text.
- **Caveat on FREEDOM-CVO:** the protocol text settles the strand, but `outputs/handover/lanes/DECISION_CLASS_BOUNDARY_STRANDS.md` still lists the GLP-1 strand pair under 'Proposed strand pairs (to Mahmood for approval before implementation)'. If Mahmood has not approved it, the delivery-route question reverts to UNRESOLVED. The primary pool is unaffected either way.
- The served page does not yet implement the CONVENTIONAL / ANY_DELIVERY strands: only the protocol text names them. Rendering the any-delivery strand is a served-page change, and is yours.

## 2. Defect found while binding FLOW, with the same pattern in harness/ (NOT fixed here: your code, pre-freeze)
The tag pattern `<[^>]+>` treats a literal '<' in prose (e.g. 'P<0.001') as a tag opening and deletes everything up to the next '>'. In the evidence lane's renderer it deleted FLOW's 'major cardiovascular events … hazard ratio, 0.82' sentence from the held NEJM abstract. Across held sources it truncated **65 of 359 renders** (evidence/sweeps/render_tag_defect.json). It is fixed in evidence/scripts/textrep.py with a failing-first test.

The same pattern is in harness/ at: absence.py:25, cites.py:33, hand_binding.py:100 and :194, registry_multi.py:61, reason_audit.py:33, rob2.py:529/:532, plus gate.py:313, index.py:1089 and honest_ratchet.py:71 (the last three look like they run over generated page HTML).
- The ones that run over **source text** can produce a false *absence* or a truncated binding without any error.
- Suggested fix: `<!--.*?-->|<\?.*?\?>|<![A-Za-z\[][^<>]*>|</?[A-Za-z][A-Za-z0-9:_-]*(?:\s[^<>]*)?/?>`.
- Minimal repro: `re.sub(r"<[^>]+>"," ","(P<0.001), HR 0.82.<h4>End</h4>")` → the HR sentence is gone.

## 3. Note, not a defect claim
With τ² = 0, the declared prediction interval `mu ± t_(k-1)·sqrt(tau² + se²)` equals the HKSJ CI. The "+ FLOW only" scenario shows it: k=9, PI = CI = 0.8095–0.9008. It is consistent with the declared formula, but readers take PI = CI as a red flag, so it may deserve a one-line disclosure on the page.
