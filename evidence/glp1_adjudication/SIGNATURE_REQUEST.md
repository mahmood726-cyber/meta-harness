# Signature request: the GLP-1 MACE primary pool gains FLOW and ELIXA (a served-number change), NOT LANDED

**Status: QUEUED for Mahmood's signature. Nothing served has changed.** Prepared by the evidence lane (evid/evidence-records) on a senior external review's assignment, which Mahmood forwarded. Regenerated 2026-09-25 16:25Z by `make_signature_request.py`.

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

**Derived notice for the served page:** the pooled HR moves 0.856 → 0.8613 and stays significant with the same direction (conclusion UNCHANGED). Heterogeneity is no longer ~0: τ² rises to 0.0027, and the prediction interval widens from 0.8069–0.9081 to 0.7531–0.9852. On the any-delivery strand the prediction interval crosses 1 (0.7046–1.0675).

## Bytes this signature binds (sha256)
```
33670e6a13021c10c97a8a741b0d9e3e2e97a6ae738d905999ff800456f68f8f  evidence/glp1_adjudication/FLOW.json
6127eb2815269ee8bc7c6258ff7d9d9555d67df2024447636c15e5ce9ee0255c  evidence/glp1_adjudication/ELIXA.json
f593aa1ee0b5d9ae823778c40444c699633860aa676c7cc735eefe371f5589ef  evidence/glp1_adjudication/FREEDOM-CVO.json
f853bd30711833ebcd88c7d3ab6e58b5934f8b45c9e67d1ed303e9b369022570  evidence/glp1_adjudication/BEFORE_AFTER.json
22010a487dfffea2075b67296389e479a3de8264d7ebcddfb03c8e0c810b2070  evidence/glp1_adjudication/compute_before_after.py
3856cbab58d53e60ca5f947b27679dbdfb4bef8782bb2937f126211d3bf22b63  evidence/glp1_adjudication/build_decisions.py
3e374d6d9a56451d1e612ab8b9c9c3c3b6a177ad6aeeb5fe4236be0dbd84b1bf  docs/reviews/glp1-ra-mace-t2d/review.json
d7208503c823d1b4f10fb8e356b69d30b3f25874420a8b678d25319811a7ae4c  protocols/glp1-ra-mace-t2d.md
7d9922c55c43a8732c8c2e666478b2ae507ad9f904434c45c6213109f99714bc  outputs/handover/lanes/DECISION_CLASS_BOUNDARY_STRANDS.md
```
**Bundle sha256 (sign this): `170c692283a451d9f031ae39924aba23000116c59a867914ca96f076e0efce1e`**

Signature: `SIGNED-BY: ______  BUNDLE: 170c692283a451d9f031ae39924aba23000116c59a867914ca96f076e0efce1e  DATE: ______` (unsigned: this request lands nothing)
