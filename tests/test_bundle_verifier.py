"""The independent verifier (scripts/verify_bundle.py, standard library only) agrees with the bundle, reproduces the
pool without importing the harness, and -- the property that separates a gate from a badge -- a single controlled
corruption of any mandatory per-row limb makes EXACTLY that row inadmissible.

Run as a subprocess so the verifier's independence from the harness is a fact of the test, not a convention."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "glp1-ra-mace-t2d"
VERIFIER = os.path.join(ROOT, "scripts", "verify_bundle.py")
PER_ROW_LIMBS = ("span", "effect", "components", "eligibility", "conflict")


def _run(*extra):
    p = subprocess.run([sys.executable, VERIFIER, "--root", "docs", "--slug", SLUG, "--json", *extra],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    assert p.returncode in (0, 1), p.stderr
    return json.loads(p.stdout)


def test_verifier_imports_nothing_from_the_repository():
    src = open(VERIFIER, encoding="utf-8").read()
    assert "from harness" not in src and "import harness" not in src and "sys.path.insert" not in src


@pytest.fixture(scope="module")
def baseline():
    return _run()


def test_baseline_passes_and_agrees_with_bundle(baseline):
    assert baseline["verdict"] == "PASS", baseline["failures"]
    assert all(a.get("bytes_ok") and a.get("declared_digest_ok") for a in baseline["artefacts"] if "bytes_ok" in a)
    assert all(s["ok"] for s in baseline["supporting"])
    assert baseline["certificate"]["release_sha256_recomputed"] and baseline["certificate"]["review_sha256_recomputed"]
    assert all(r["agrees_with_bundle"] and r["predicates_agree_with_bundle"] for r in baseline["rows"])
    assert all(r["offsets_reproduce_span"] for r in baseline["rows"])


def test_pool_reproduced_without_the_harness(baseline):
    p = baseline["pool"]
    assert p["reproduced_to_1e-9"], p["abs_deltas"]
    assert abs(p["recomputed"]["estimate"] - 0.8559934175938467) < 1e-9
    assert abs(p["recomputed"]["tau2"] - 0.00004447972517261924) < 1e-9
    assert abs(p["t_crit_recomputed"] - 2.3646242515927853) < 1e-9   # t_{0.975, 7}
    assert p["k_declared"] == 8 and p["admissible_rows"] == 7


def test_absence_claims_judged_from_recomputed_preservation(baseline):
    neg = [c for c in baseline["absence_claims"] if c["claim_kind"] == "NEGATIVE"]
    assert neg
    soul = [c for c in neg if c["pmid"] == "40162642"]
    assert soul and all(c["coverage_recomputed"] == "EXCERPT_ONLY" and c["negative_claim_admissible"] is False for c in soul)
    assert all(c["preservation"]["missing"] == c["preservation"]["units"] for c in soul)
    assert all(c["agrees"] for c in neg if "agrees" in c)


@pytest.mark.parametrize("pmid", ["40162642", "27295427"])
@pytest.mark.parametrize("limb", PER_ROW_LIMBS)
def test_one_corrupted_limb_makes_exactly_that_row_inadmissible(baseline, pmid, limb):
    base_bad = {r["pmid"] for r in baseline["rows"] if r["final"] == "INADMISSIBLE"}
    rep = _run("--corrupt", pmid, limb)
    now_bad = {r["pmid"] for r in rep["rows"] if r["final"] == "INADMISSIBLE"}
    assert now_bad == base_bad | {pmid}, (limb, sorted(now_bad))


def test_corrupting_the_shared_container_fails_every_row_that_depends_on_it(baseline):
    """records.json is one container for all abstracts; damaging it must not be silent for any row."""
    rep = _run("--corrupt", "40162642", "container")
    assert all(r["final"] == "INADMISSIBLE" for r in rep["rows"])
