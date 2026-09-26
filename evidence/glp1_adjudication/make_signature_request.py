"""Write SIGNATURE_REQUEST.md: the served-number change (FLOW + ELIXA into the primary GLP-1 MACE pool) with the derived
before -> after from BEFORE_AFTER.json and the sha256 of every byte the signature binds; the bundle hash is what Mahmood
signs. Regenerate after any change to a bound file (a stale bundle hash would sign bytes that no longer exist).
  python evidence/glp1_adjudication/make_signature_request.py"""
import datetime, hashlib, json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = "evidence/glp1_adjudication"
BOUND = [f"{D}/FLOW.json", f"{D}/ELIXA.json", f"{D}/FREEDOM-CVO.json", f"{D}/BEFORE_AFTER.json", f"{D}/compute_before_after.py",
         f"{D}/build_decisions.py", "docs/reviews/glp1-ra-mace-t2d/review.json", "protocols/glp1-ra-mace-t2d.md",
         "outputs/handover/lanes/DECISION_CLASS_BOUNDARY_STRANDS.md"]


def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()


def fmt(r):
    return (f"k={r['k']}, HR {r['estimate']} (95% CI {r['ci_low']}–{r['ci_high']}), prediction interval "
            f"{r.get('pi_low')}–{r.get('pi_high')}, tau² {r['tau2']}")


def main():
    ba = json.load(open(os.path.join(ROOT, D, "BEFORE_AFTER.json"), encoding="utf-8"))
    b, A = ba["served_before"], ba["after"]
    prim = A["CONVENTIONAL_GLP1RA (primary strand): + FLOW + ELIXA"]
    anyd = A["GLP1RA_ANY_DELIVERY (alongside): + FLOW + ELIXA + FREEDOM-CVO"]
    alt = A["CONVENTIONAL_GLP1RA: + FLOW + ELIXA (ELIXA at its Table 8 rendering 0.89-1.18)"]
    manifest = "\n".join(f"{sha(p)}  {p}" for p in BOUND)
    bundle = hashlib.sha256(manifest.encode()).hexdigest()
    txt = f"""# Signature request: the GLP-1 MACE primary pool gains FLOW and ELIXA (a served-number change), NOT LANDED

**Status: QUEUED for Mahmood's signature. Nothing served has changed.** Prepared by the evidence lane (evid/evidence-records) on a senior external review's assignment, which Mahmood forwarded. Regenerated {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%MZ')} by `make_signature_request.py`.

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
| **before (served)** | {fmt(b)} |
| **after: primary, + FLOW + ELIXA** | {fmt(prim)} |
| after, ELIXA at its Table 8 rendering (0.89–1.18) | {fmt(alt)} |
| alongside: ANY_DELIVERY, + FLOW + ELIXA + FREEDOM-CVO | {fmt(anyd)} |

**Derived notice for the served page:** the pooled HR moves {b['estimate']} → {prim['estimate']} and stays significant with the same direction (conclusion UNCHANGED). Heterogeneity is no longer ~0: τ² rises to {prim['tau2']}, and the prediction interval widens from {b['pi_low']}–{b['pi_high']} to {prim['pi_low']}–{prim['pi_high']}. On the any-delivery strand the prediction interval crosses 1 ({anyd['pi_low']}–{anyd['pi_high']}).

## Bytes this signature binds (sha256)
```
{manifest}
```
**Bundle sha256 (sign this): `{bundle}`**

Signature: `SIGNED-BY: ______  BUNDLE: {bundle}  DATE: ______` (unsigned: this request lands nothing)
"""
    open(os.path.join(ROOT, D, "SIGNATURE_REQUEST.md"), "w", encoding="utf-8", newline="\n").write(txt)
    print("bundle", bundle)


if __name__ == "__main__":
    main()
