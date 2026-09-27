# Signature request: the GLP-1 MACE primary pool gains FLOW and ELIXA (a served-number change), NOT LANDED

**Status: QUEUED for Mahmood's signature. Nothing served has changed.** Prepared by the evidence lane (evid/evidence-records) on a senior external review's assignment, which Mahmood forwarded. Regenerated 2026-09-27 17:53Z by `make_signature_request.py`.

## What the signature admits
Under the protocol's explicit B-prime rules (`protocols/glp1-ra-mace-t2d.md` at `b10c53d3`):
- **FLOW** (semaglutide, T2D + CKD): eligible. 3-point MACE HR 0.82 (0.68–0.98), 212 vs 254, all randomised, end of randomised follow-up. Kept distinct from the kidney composite 0.76 (0.66–0.88) **by table row**. → primary pool.
- **ELIXA** (lixisenatide, T2D after ACS): eligible. Prespecified secondary 3-point MACE HR 1.02 (0.887–1.172), 400 vs 392, ITT on-study. Identified **by its definition sentence and event counts**, never by its number: the 4-point MACE+ primary rounds to the same 1.02 (0.89–1.17) but is 406 vs 399. → primary pool.
- **FREEDOM-CVO** (ITCA 650 osmotic-pump exenatide): eligible **only on the `GLP1RA_ANY_DELIVERY` strand**. The protocol's agent list places ITCA 650 there and names `CONVENTIONAL_GLP1RA` primary. 3-point MACE end-of-study ITT HR 1.24 (0.90–1.70), 85 vs 69. → **not** in the primary pool.
  - **Caveat for you to confirm:** the class-boundary decision document still lists the GLP-1 strand pair as *proposed for your approval* (the SGLT2 pair is marked decided). If you have not approved it, FREEDOM-CVO's delivery-route question reverts to UNRESOLVED. That changes nothing in the primary pool below.

Every field of every decision carries its own witness span (sha256-pinned; re-verified by the lane gate, condition 6).

## Derived before → after (production path: `harness.known_missing` → `harness.synth.pool`; the recomputed BEFORE reproduces the served result exactly)
| | pool |
|---|---|
| **before (served)** | k=8, HR 0.856 (95% CI 0.8086–0.9061), prediction interval 0.8069–0.9081, tau² 4e-05 |
| **after: primary, + FLOW + ELIXA** | k=10, HR 0.8613 (95% CI 0.8069–0.9194), prediction interval 0.7531–0.9852, tau² 0.0027 |
| after, ELIXA at its Table 8 rendering (0.89–1.18) | k=10, HR 0.8612 (95% CI 0.807–0.919), prediction interval 0.7539–0.9838, tau² 0.00263 |
| alongside: ANY_DELIVERY, + FLOW + ELIXA + FREEDOM-CVO | k=11, HR 0.8673 (95% CI 0.7999–0.9404), prediction interval 0.7046–1.0675, tau² 0.00737 |

**SOURCE_EFFECT_CONFLICT (ELIXA):** the regulator's document states the same result two ways -- section 3.3.4.3 narrative, FDA statistical review 208471Orig1s000StatR, printed page 23 (PDF page 24): (0.887, 1.172); Table 8 'Analysis of the MACE Endpoint', MACE endpoint (on-study) row, same page: (0.89, 1.18). Governing version: **section 3.3.4.3 narrative (0.887, 1.172)**, DECIDED because the narrative interval (0.887, 1.172) is centred on the stated point estimate 1.02 on the log scale and its implied standard error equals the one the 400 vs 392 events imply; Table 8's (0.89, 1.18) is centred on 1.025 and 1.2% too wide, and its upper bound is not the 2-decimal rounding of the narrative's 1.172 (which is 1.17) while its lower bound is (0.887 -> 0.89): Table 8's 1.18 is the rendering error. Both renderings are pooled for disclosure; the conclusion is identical. Diagnostic (the conflicting trial added alone, k=9): HR 0.8630 on the governing version vs 0.8629 on the other.

**Derived notice for the served page:** the pooled HR moves 0.856 → 0.8613 and stays significant with the same direction (conclusion UNCHANGED). Heterogeneity is no longer ~0: τ² rises to 0.0027, and the prediction interval widens from 0.8069–0.9081 to 0.7531–0.9852. On the any-delivery strand the prediction interval crosses 1 (0.7046–1.0675). The FDA statistical review states ELIXA's 3-point MACE interval two ways on one page, (0.887, 1.172) in its text and (0.89, 1.18) in Table 8; the text version is used (it is centred on the point estimate and matches the event counts), and the pooled result under the Table 8 version is 0.8612 (0.807–0.919), the same conclusion.

## Bytes this signature binds (sha256)
```
61919e4fd5ec66e5074df9f4f694aef296ed38300ba0725e817db984c5c34428  evidence/glp1_adjudication/FLOW.json
e41d05f34a1e2743431322da5328c6db7e8ffae28dce285b7e401de557ec2abe  evidence/glp1_adjudication/ELIXA.json
68e8d3990b7e99e22cdde3b06cb2a03f87382743179ee13d79bac201e5786fc7  evidence/glp1_adjudication/FREEDOM-CVO.json
e880b8f755673f6a6058e3a6ac464e77d121aa8c7b686e68fb31b5cd84435b56  evidence/glp1_adjudication/BEFORE_AFTER.json
3c82a1dea34436c37b3f746258ed8eca0af3731d6a1394dac8e20efd5aec54c4  evidence/glp1_adjudication/compute_before_after.py
f4b3b1b7b06758d5ac2dfa697a602d60aa860eff3559ec026e2a2c794706761b  evidence/glp1_adjudication/build_decisions.py
30de05b2e3c5fd43d328750fe1f26422328f266769805986385e4b6a2fee28e7  docs/reviews/glp1-ra-mace-t2d/review.json
d7208503c823d1b4f10fb8e356b69d30b3f25874420a8b678d25319811a7ae4c  protocols/glp1-ra-mace-t2d.md
7d9922c55c43a8732c8c2e666478b2ae507ad9f904434c45c6213109f99714bc  outputs/handover/lanes/DECISION_CLASS_BOUNDARY_STRANDS.md
```
**Bundle sha256 (sign this): `3dd61b27e55ec2207896a6cf0a4d60abaf2aa6692056801682013d75ac150ac8`**

Signature: `SIGNED-BY: ______  BUNDLE: 3dd61b27e55ec2207896a6cf0a4d60abaf2aa6692056801682013d75ac150ac8  DATE: ______` (unsigned: this request lands nothing)
