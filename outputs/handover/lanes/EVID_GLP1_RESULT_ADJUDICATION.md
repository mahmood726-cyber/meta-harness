# For the release captain: GLP-1 MACE result-level adjudication of FLOW, ELIXA and FREEDOM-CVO (evidence lane, 2026-09-25)

**Read:** `evidence/glp1_adjudication/HANDOFF_RELEASE_CAPTAIN.md`. Everything below is on main; nothing under docs/ changed.

| trial | decision (protocol b10c53d3) | bound 3-point MACE | effect on the served pool |
|---|---|---|---|
| FLOW | eligible, CONVENTIONAL_GLP1RA (primary) | HR 0.82 (0.68–0.98), 212 vs 254, all randomised (not the kidney composite 0.76) | joins the primary pool **after Mahmood signs** |
| ELIXA | eligible, CONVENTIONAL_GLP1RA (primary) | HR 1.02 (0.887–1.172), 400 vs 392, ITT on-study (identified by definition + counts, not by the 4-point MACE+'s equal rounded HR) | joins the primary pool **after Mahmood signs** |
| FREEDOM-CVO | eligible on GLP1RA_ANY_DELIVERY only (protocol agent list) | HR 1.24 (0.90–1.70), 85 vs 69, ITT end of study | primary unaffected; caveat: the strand pair is still "proposed" in DECISION_CLASS_BOUNDARY_STRANDS.md |

- **Served-number change (NOT landed):** primary k=8, 0.856 (0.8086–0.9061) → k=10, 0.861 (0.807–0.919), PI 0.753–0.985. Conclusion unchanged. Computed through `harness.known_missing` → `harness.synth.pool`, with the recomputed BEFORE reproducing the served result.
- **Signature request:** `evidence/glp1_adjudication/SIGNATURE_REQUEST.md`, bundle sha256 `4bf8ec337f8b368ed171ef7e848a9ef44211c6586158a2421eb67a8644f36c0e`. Please do not land it unsigned.
- **Decision files:** `evidence/glp1_adjudication/{FLOW,ELIXA,FREEDOM-CVO}.json`. Each field has a sha256-pinned witness span.
- **Also for you (harness/, not fixed by this lane):** `<[^>]+>` tag stripping deletes text after a literal '<' ('P<0.001'). It truncated 65 of 359 of this lane's source renders. The call sites and a one-line reproduction are in the handoff, §2.
