"""Write SIGNATURE_REQUEST.md for V1.0.1: FLOW + ELIXA enter the GLP-1 MACE primary pool (a served-number change),
regenerated AGAINST THE V1.0 CANDIDATE TREE (runbook step 0b): the bound review.json is the one V1.0 serves, the
admission mechanism and its decisions are the ones on this branch, and the derived before -> after comes from
BEFORE_AFTER.json (compute_before_after.py; the primary scenario's rows come from the mechanism itself). The bundle
hash over the sha256 of every bound file is what Mahmood signs. Regenerate after any change to a bound file.
  python evidence/glp1_adjudication/make_signature_request.py"""
import datetime, hashlib, json, os, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = "evidence/glp1_adjudication"
CANDIDATE = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"      # origin/v1/candidate, the V1.0 cut
BOUND = [
    # the decisions and how they were made
    f"{D}/FLOW.json", f"{D}/ELIXA.json", f"{D}/FREEDOM-CVO.json", f"{D}/build_decisions.py",
    # the derived before -> after and how it was derived
    f"{D}/BEFORE_AFTER.json", f"{D}/compute_before_after.py",
    # the admission mechanism the build reads
    "topics/glp1-ra-mace-t2d.json", "harness/result_adjudication.py", "harness/pipeline.py", "harness/target_endpoint.py",
    "harness/known_missing.py", "harness/invalidation.py", "evidence/scripts/textrep.py",
    # its proof
    "tests/test_glp1_admission_identity.py", "tests/test_glp1_signed_admission.py",
    # what V1.0 serves today (runbook 0b: the bytes the signature is taken against) and the rules
    "docs/reviews/glp1-ra-mace-t2d/review.json", "protocols/glp1-ra-mace-t2d.md",
    "outputs/handover/lanes/DECISION_CLASS_BOUNDARY_STRANDS.md",
]


def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def fmt(r):
    return (f"k={r['k']}, HR {r['estimate']} (95% CI {r['ci_low']}–{r['ci_high']}), prediction interval "
            f"{r.get('pi_low')}–{r.get('pi_high')}, tau² {r['tau2']}")


def main():
    if git("diff", "--name-only", CANDIDATE, "--", "docs/reviews/glp1-ra-mace-t2d/review.json"):
        raise SystemExit("REFUSED: docs/reviews/glp1-ra-mace-t2d/review.json differs from the V1.0 candidate's; "
                         "runbook 0b binds the bytes V1.0 serves -- regenerate from a tree whose review.json is the candidate's")
    ba = json.load(open(os.path.join(ROOT, D, "BEFORE_AFTER.json"), encoding="utf-8"))
    b, A = ba["served_before"], ba["after"]
    prim = A["CONVENTIONAL_GLP1RA (primary strand): + FLOW + ELIXA"]
    anyd = A["GLP1RA_ANY_DELIVERY (alongside): + FLOW + ELIXA + FREEDOM-CVO"]
    alt = A["CONVENTIONAL_GLP1RA: + FLOW + ELIXA (ELIXA at its Table 8 rendering 0.89-1.18)"]
    rows = {r["label"]: r for r in ba.get("admitted_rows", [])}
    manifest = "\n".join(f"{sha(p)}  {p}" for p in BOUND)
    bundle = hashlib.sha256(manifest.encode()).hexdigest()
    head = git("rev-parse", "HEAD")
    txt = f"""# Signature request, V1.0.1: the GLP-1 MACE primary pool gains FLOW and ELIXA (a served-number change), NOT LANDED

**Status: QUEUED for Mahmood's signature. Nothing served has changed.** Regenerated {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%MZ')} by `make_signature_request.py` on branch `evid/v1.0.1-glp1-admission`, against the **V1.0 candidate** `{CANDIDATE[:12]}` (runbook step 0b): the bound `review.json` is byte-identical to the one V1.0 serves (checked; this script refuses otherwise). Tree at generation: `{head[:12]}` plus this request.

## What the signature admits
Under the protocol's B-prime rules (`protocols/glp1-ra-mace-t2d.md` at `b10c53d3`), through the admission mechanism the build reads (`topics/glp1-ra-mace-t2d.json` `adjudicated_results` -> `harness/result_adjudication.py`):
- **FLOW** (semaglutide, T2D + CKD): 3-point MACE HR 0.82 (0.68–0.98), 212 vs 254. **Identified by its source row**: FDA label Table 10, row "Composite of cardiovascular death, non-fatal myocardial infarction, non-fatal stroke (time to first occurrence)" -- the label itself enumerates the three components; the kidney composite 0.76 in the same table is a different row. Class EXACT_TARGET.
- **ELIXA** (lixisenatide, T2D after ACS): 3-point MACE HR 1.02 (0.887–1.172), 400 vs 392. **Identified by its source row, never by its numbers**: FDA statistical review Table 8 "Analysis of the MACE Endpoint", row "MACE endpoint (on-study)", the definition of that label ("secondary MACE event (defined as CV death, non-fatal MI and non-fatal stroke)") and the event counts 400/392, which must also appear in the sentence carrying the tuple. Class EXACT_TARGET. The 4-point MACE+ primary is printed with the SAME numbers, HR 1.02 (0.89, 1.17), in the same review (Table 1, 406 vs 399); that row is **refused as DIFFERENT_OUTCOME** by the mechanism (its label MACE+ is defined with hospitalization for unstable angina), with a test.
- **FREEDOM-CVO** (ITCA 650): eligible only on `GLP1RA_ANY_DELIVERY`; **not** in the primary pool, not declared to the mechanism (a declaration naming the primary strand is refused, with a test).

**ELIXA prespecification dispute (disclosed on the page, in the result-change notice):** the FDA statistical review calls the 3-point MACE a secondary endpoint analysed by a pre-specified Cox model; the FDA summary review calls it a sensitivity analysis; the registry lists the 4-point primary and 5-/6-point secondaries but no 3-point MACE. The same statistical review renders the on-study interval three ways: (0.887, 1.172) in the section 3.3.4.3 text (bound), (0.89, 1.18) in Table 8, (0.89, 1.17) in the executive summary.

Every field carries a witness span re-verified against sha256-pinned held bytes at build time ({rows.get('FLOW', {}).get('decision_sha256', '')[:12]} FLOW, {rows.get('ELIXA', {}).get('decision_sha256', '')[:12]} ELIXA decision sha256 prefixes).

## Derived before -> after (production path; the recomputed BEFORE reproduces the V1.0 served result exactly; the primary AFTER's rows come from the admission mechanism)
| | pool |
|---|---|
| **before (V1.0 served)** | {fmt(b)} |
| **after: primary, + FLOW + ELIXA** | {fmt(prim)} |
| after, ELIXA at its Table 8 rendering (0.89–1.18) | {fmt(alt)} |
| alongside: ANY_DELIVERY, + FLOW + ELIXA + FREEDOM-CVO | {fmt(anyd)} |

**Derived notice for the served page:** the pooled HR moves {b['estimate']} -> {prim['estimate']}; direction and significance UNCHANGED. Heterogeneity is no longer ~0: tau² {b['tau2']} -> {prim['tau2']}; the prediction interval widens from {b['pi_low']}–{b['pi_high']} to {prim['pi_low']}–{prim['pi_high']}. The k=8 result stays on the page as the previous result.

## Open before V1.0.1 can land (none of these changes a number in this request)
- **Build on the candidate tree** (held for disk; the captain's go): `build_topic.py glp1-ra-mace-t2d`, bundle, site-wide certificate refresh (harness code moved), the runbook's Step 3-6 checks and `verify_all.py`. The admission suite `tests/test_glp1_signed_admission.py` needs cache/ and has not been run on this tree; `tests/test_glp1_admission_identity.py` (cache-free) passes.
- **Bundle verifier limit L14** (PubMed records only) refuses the two FDA-text rows; lifting it is the captain's decision.
- **ELIXA rendering**: bound = the unrounded text interval; the Table 8 rendering gives the same result to 3 dp (row above). Changing it changes a bound file and this bundle.

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
