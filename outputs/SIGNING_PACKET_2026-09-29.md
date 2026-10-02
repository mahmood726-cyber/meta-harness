# Signing packet — 2026-09-29

One file, one decision per row. **Sign the SIGNABLE table.** The PENDING table is listed so the
picture is complete; those decisions are not signable today and are marked why.

A **CONCLUSION CHANGE** means the interval crosses the no-effect line, or a published result is
withdrawn. A value moving is routine; a claim becoming unsupported is not.

## A. SIGNABLE — derived on main `91f057a4`, which reproduces 32 of 32 (14 decisions)

| id | topic / outcome | old → new | conclusion change | notice sha256 |
|---|---|---|---|---|
| MAIN-01 | colchicine-postop-af — Treatment discontinuation | k=1 0.8765 (0.0558–13.7586) → withdrawn | **YES** | `06a78bed5253bf63…` |
| MAIN-02 | colchicine-recurrent-pericarditis — Adverse events (gastrointestinal) | k=1 1.0 (0.4112–2.4318) → withdrawn | **YES** | `71ffda763f8edce0…` |
| MAIN-03 | dpp4-mace-t2d — Hospitalization for heart failure | k=2 1.1296 → k=1 1.0 (0.83–1.2) | no | `16c375919adce14a…` |
| MAIN-04 | esketamine-trd-madrs — Observed-case Day-28 raw change-score MADRS MD | k=4 -3.3445 (-6.0701–-0.6189) → k=3 -3.1004 (-7.3323–1.1315) | **YES** | `8d10b28552da19db…` |
| MAIN-05 | noac-vs-warfarin-af-stroke — Major bleeding | k=4 0.8544 (0.6439–1.1336) → withdrawn | **YES** | `aa63ea44b96f8d6d…` |
| MAIN-06 | omega3-cardiovascular-events — Major vascular events / MACE | k=6 0.9505 (0.8207–1.1009) → k=5 0.937 (0.7726–1.1364) | no | `8a39cc3c4c8e3040…` |
| MAIN-07 | pcsk9-mace — Major adverse cardiovascular events | k=3 0.8106 (0.7032–0.9344) → k=2 0.8261 | no | `f5ce0892c46fbcb9…` |
| MAIN-08 | pcsk9-mace — Injection-site reactions | k=1 1.4019 (0.9502–2.0684) → withdrawn | **YES** | `d678cfa82d6b7a83…` |
| MAIN-09 | probiotics-aad-prevention — Antibiotic-associated diarrhoea | k=16 0.6907 (0.5193–0.9187) → k=11 0.6874 (0.4803–0.9839) | no | `374950cbe1421ad5…` |
| MAIN-10 | probiotics-aad-prevention — Any adverse events | k=3 1.0542 (0.5643–1.9694) → withdrawn | **YES** | `e34d75aecfa9fcfd…` |
| MAIN-11 | probiotics-aad-prevention — Serious adverse events | withdrawn → k=1 0.6556 (0.1882–2.284) | no | `83cfb48b90df6d2f…` |
| MAIN-12 | tocilizumab-covid19-mortality — Serious adverse events | k=3 0.8699 (0.4477–1.6902) → k=2 0.8109 | no | `c32993200619b66d…` |
| MAIN-13 | tranexamic-acid-pph — Thromboembolic events | k=1 0.8781 (0.5379–1.4336) → withdrawn | **YES** | `b3d1c2b0a7ec43be…` |
| MAIN-14 | spironolactone-hfref-mortality — All-cause mortality | k=3 0.7294 (0.5609–0.9486) → k=3 0.8759 (0.2918–2.629) | **YES** | `1a39b96c99f1435a…` |

**MAIN-01** — PMID 32720823 set aside (ENDPOINT_UNBOUND): tuple located in 3 spans of the held document; ambiguity abstains. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.

**MAIN-02** — PMID 24694983 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/colchicine-recurrent-pericarditis/records.json#PMID-24694983 (abstract): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.

**MAIN-03** — PMID 23992601 set aside (ENDPOINT_UNBOUND): span names neither components nor an endpoint. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.

**MAIN-04** — NCT02417064 (TRANSFORM-1) left the pool: its hand-transcribed combined-dose-arm values (mean, SD, n versus the shared placebo arm) are not located in the held record for the trial, so the binder set the row aside as KNOWN_REPORTED_NOT_YET_EXTRACTED (the trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong). The remaining three trials re-pool to a mean difference whose interval inclu

**MAIN-05** — PMID 19717844 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/noac-vs-warfarin-af-stroke/records.json#PMID-19717844 (abstract): no span carries it. PMID 21830957 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/noac-vs-warfarin-af-stroke/records.json#PMID-21830957 (abstract): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every

**MAIN-06** — PMID 22686415 set aside (ENDPOINT_UNBOUND): named endpoint has no definition span in the held text. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.

**MAIN-07** — PMID 41211925 set aside (ENDPOINT_UNBOUND): result sentence names an endpoint but the held text holds 2 different definitions of it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.

**MAIN-08** — PMID 25773378 set aside (ENDPOINT_UNBOUND) -- a STALE APPROVAL caught by digest, not a number that could not be found: the entry's approval was recorded against the held registry document cache/pcsk9-mace/harms_aact_held.json at sha256 108efeb5ed7e…, and that document now has sha256 142c68c1dd5a…; whatever was approved was approved against bytes that have since changed, so the approval no longer certifies this number

**MAIN-09** — PMID 24456384 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/probiotics-aad-prevention/records.json#PMID-24456384 (abstract): no span carries it. PMID 26973849 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/probiotics-aad-prevention/ft_26973849.txt (xml): no span carries it. PMID 34541475 set aside (ENDPOINT_UNBOUND): table label 'AAD – Abx+30d (n, %)' names an 

**MAIN-10** — PMID 26973849 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/probiotics-aad-prevention/ft_26973849.txt (xml): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.

**MAIN-11** — PMID 39529939 set aside (ENDPOINT_UNBOUND): tuple located in 9 spans of the held document; ambiguity abstains. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.

**MAIN-12** — PMID 33085857 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/tocilizumab-covid19-mortality/ft_33085857.txt (xml): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.

**MAIN-13** — PMID 28456509 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/tranexamic-acid-pph/records.json#PMID-28456509 (abstract): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.

**MAIN-14** — J-EMPHASIS (PMID 28824029) contributed its CV-death/HHF COMPOSITE HR 0.85 (0.53-1.36) to an ALL-CAUSE MORTALITY pool. Bound instead to the trial's own ITT all-cause mortality HR 1.77 (0.81-3.87), 17/111 vs 10/110 (Table 3; Table 4's on-treatment 1.36 is not the one). k unchanged at 3. Derived through harness.synth.pool under the declared estimator.

## B. PENDING RE-DERIVATION — oc's 31-move stack (8 shown of 21 pooled deltas)

**Not signable.** The oc stack (`v1.0.1/oc-stack` @ `9a2deb45`) reproduces **2 of 32** topics and
its gate refused 7 of 11 limbs. Signing a number derived on a branch that does not reproduce would
bind a signature to bytes nobody can regenerate. These re-enter section A once oc reproduces 32/32.

| topic / outcome | old → new | conclusion change |
|---|---|---|
| balanced-crystalloids-vs-saline-mortality — Mortality | k=2 HR 0.9774 → WITHDRAWN (no pooled result) | **YES** |
| noac-vs-warfarin-af-stroke — Stroke or systemic embolism | HR 0.8069 (0.6611-0.985) → REFUSED: mixed ratio types, no declared policy | **YES** |
| probiotics-aad-prevention — Antibiotic-associated diarrhoea | RR 0.6874 → WITHDRAWN (an adjusted RR pooled with unadjusted ones) | **YES** |
| corticosteroids-covid19-mortality — 28-day all-cause mortality | RR 0.83 (0.75-0.93) → OR 0.8596 (0.7606-0.9716) -- RECOVERY reports a RATE ratio | no |
| colchicine-recurrent-pericarditis — Recurrent pericarditis | k=2 RR 0.4643 → k=1 RR 0.44 (0.27-0.73) | no |
| esketamine-trd-madrs — Observed-case Day-28 MADRS | k=3 MD -3.10 (-7.33, 1.13) → k=4 MD -3.34 (-6.07, -0.62) | **YES** |
| corticosteroids-cap-mortality — Hyperglycaemia | scale INCOMPATIBLE (OR+RR) → scale RR | no |
| doac-vte-recurrence — Symptomatic recurrent VTE | scale HR → scale mixed ratio (HR+RR, DECLARED) | no |

## C. Also outstanding, not yet derived as notices

- **corticosteroids-cap-mortality, All-cause mortality**: PMID 25688779 contributes a *composite
  treatment-failure* endpoint to an all-cause-mortality pool — the same defect as J-EMPHASIS, found
  by the composite sweep (5 of 123 pooled rows flagged; 1 new, 1 confirmed, 1 metadata-only,
  1 regex false positive, 1 already adjudicated). Needs binding before a notice can be derived.
- **Q1 EMPA-KIDNEY DKA**, **Q3 COVID STEROID SAE-pool removal**, **2× evid harms-incomplete**,
  **FLOW/ELIXA k=10** (bundle `4bf8ec33`, signature-gated).

---

**Integrity.** This file cannot state its own sha256 (hashing it would change it). The digest
is in the sidecar `SIGNING_PACKET_2026-09-29.md.sha256`. Verify with:

    sha256sum -c outputs/SIGNING_PACKET_2026-09-29.md.sha256
