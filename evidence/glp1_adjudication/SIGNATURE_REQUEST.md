# Signature request: GLP-1 MACE primary pool gains FLOW and ELIXA (served-number change), NOT LANDED

**Status: QUEUED for Mahmood's signature. Nothing served has changed.** Prepared 2026-09-25 14:11Z by the evidence lane (evid/evidence-records) on a senior external review's assignment, which Mahmood forwarded.

## What the signature admits
Under the protocol's explicit B-prime rules (`protocols/glp1-ra-mace-t2d.md` at `b10c53d3`), the lane decided:
- **FLOW** (semaglutide, T2D + CKD): eligible; 3-point MACE HR 0.82 (0.68–0.98), 212 vs 254, all randomised, end of randomised follow-up. Kept distinct from the kidney composite 0.76 (0.66–0.88) **by table row**. → primary pool.
- **ELIXA** (lixisenatide, T2D after ACS): eligible; prespecified secondary 3-point MACE HR 1.02 (0.887–1.172), 400 vs 392, ITT on-study. Identified **by its definition sentence and event counts**, never by its number: the 4-point MACE+ primary rounds to the same 1.02 (0.89–1.17) but is 406 vs 399. → primary pool.
- **FREEDOM-CVO** (ITCA 650 osmotic-pump exenatide): eligible **only on the `GLP1RA_ANY_DELIVERY` strand**. The protocol's own agent list places ITCA 650 there and names `CONVENTIONAL_GLP1RA` as the primary strand, so the protocol settles it (not UNRESOLVED). 3-point MACE end-of-study ITT HR 1.24 (0.90–1.70), 85 vs 69. → **not** in the primary pool.

Every field of every decision carries its own witness span (sha256-pinned; checked by gate condition 6).

## Derived before → after (computed through the production path, not by hand)
`harness.known_missing._study_from_trial` + `_pool_result` (`harness.synth.pool`: PM τ², HKSJ on t_(k−1) with the max(1, Q/(k−1)) floor). The recomputed BEFORE reproduces the served primary result exactly; the script refuses to write otherwise.

| | pool |
|---|---|
| **before (served)** | k=8, HR 0.856 (95% CI 0.8086–0.9061), prediction interval 0.8069–0.9081, tau² 4e-05 |
| **after: primary, + FLOW + ELIXA** | k=10, HR 0.8613 (95% CI 0.8069–0.9194), prediction interval 0.7531–0.9852, tau² 0.0027 |
| after, ELIXA at its Table 8 rendering (0.89–1.18) | k=10, HR 0.8612 (95% CI 0.807–0.919), prediction interval 0.7539–0.9838, tau² 0.00263 |
| alongside: ANY_DELIVERY, + FLOW + ELIXA + FREEDOM-CVO | k=11, HR 0.8673 (95% CI 0.7999–0.9404), prediction interval 0.7046–1.0675, tau² 0.00737 |

**Derived notice for the served page:** the pooled HR moves 0.856 → 0.861 and stays significant with the same direction (conclusion UNCHANGED). Heterogeneity is no longer ~0: τ² rises to 0.0027, and the prediction interval widens from 0.8069–0.9081 to 0.7531–0.9852. With FREEDOM-CVO on the any-delivery strand, the prediction interval crosses 1 (0.7046–1.0675).

## Bytes this signature binds (sha256)
```
f53c1fd410d59c22d0646354c1436355343d1fdb3c372957a51a13577311ff69  evidence/glp1_adjudication/FLOW.json
1f76381c6e8bf56818f5e00723472b3f174aa773e247e975cf26ebc167c077ab  evidence/glp1_adjudication/ELIXA.json
c17a3c61264edcfa6c47e324b6d0ed05f316844e86c7acf30e0b0b069256afb7  evidence/glp1_adjudication/FREEDOM-CVO.json
f853bd30711833ebcd88c7d3ab6e58b5934f8b45c9e67d1ed303e9b369022570  evidence/glp1_adjudication/BEFORE_AFTER.json
22010a487dfffea2075b67296389e479a3de8264d7ebcddfb03c8e0c810b2070  evidence/glp1_adjudication/compute_before_after.py
97504d147699a18eedf365296b239043cf5ffda2366d92b1015686b27caba5db  evidence/glp1_adjudication/build_decisions.py
79c3d0092330a239833789ace48f8aef5f88de6598c8b4604ae378393a1bea7d  docs/reviews/glp1-ra-mace-t2d/review.json
d7208503c823d1b4f10fb8e356b69d30b3f25874420a8b678d25319811a7ae4c  protocols/glp1-ra-mace-t2d.md
```
**Bundle sha256 (sign this): `9b86df7ab18f3af2249cd1759287b680a5ed24ac02e912c974f2bf8cc37bd943`**

Signature: `SIGNED-BY: ______  BUNDLE: 9b86df7ab18f3af2249cd1759287b680a5ed24ac02e912c974f2bf8cc37bd943  DATE: ______` (not signed: this request lands nothing)
