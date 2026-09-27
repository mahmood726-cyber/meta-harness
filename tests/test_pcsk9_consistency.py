"""PCSK9 review (2026-09-27; retrospective, Dispatch under Mahmood's delegation).

(1) ONE RESULT OBJECT ACROSS ANALYSES: VESALIUS-CV's 3-point MACE HR 0.75 (0.65-0.86) is REFUSED by the served main pool and
    ADMITTED by the supplemental strict 3-point strand (FOURIER + VESALIUS -> 0.784243, 0.473854-1.297945). Same source-bound
    result, contradictory decisions, no declared reason -> the consistency check fails.
(3) SPARSE DATA: a zero cell needs an explicitly declared method; there is no silent continuity correction. Served at the pinned
    candidate: RECOVERY serious adverse events 1/16 vs 0/14 pooled as RR 2.8065 through an automatic 0.5 correction.
Held bytes at 3876a62d (a missing commit fails, never skips)."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import result_objects as ro, synth   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"


def _review(slug):
    p = subprocess.run(["git", "show", f"{PINNED}:docs/reviews/{slug}/review.json"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]} review {slug} not in history (never a skip)", pytrace=False)
    return json.loads(p.stdout)


# ------------------------------------------------------------------ (1) one result object
def test_plant_the_served_page_admits_and_refuses_the_same_vesalius_result():
    r = _review("pcsk9-mace")
    c = ro.consistency(ro.ledger(r))
    assert c["state"] == "CONTRADICTORY_ADMISSION"
    (x,) = c["contradictions"]
    assert x["result_id"] == "41211925|HR|0.75|0.65|0.86"
    assert (x["admitted_in"], x["refused_in"], x["refusal_code"]) == ("strand:strict_3p_mace", "outcome:Major adverse cardiovascular events",
                                                                      "RESULT_INCOMPATIBLE")
    strand = r["strands"]["strands"][0]
    assert round(strand["pool"]["estimate"], 6) == 0.784243                  # the supplemental analysis that admitted it


def test_a_declared_waiver_explains_a_difference_and_consistent_sharing_passes():
    r = _review("pcsk9-mace")
    r["strands"]["strands"][0]["requirements"] = {"waives": ["RESULT_INCOMPATIBLE"],
                                                  "because": "the strand's declared component set accepts CHD death for CV death"}
    c = ro.consistency(ro.ledger(r))
    assert c["state"] == "CONSISTENT" and len(c["explained_differences"]) == 1
    fourier = [e for e in ro.ledger(_review("pcsk9-mace")) if e["result_id"].startswith("28304224|")]
    assert {e["decision"] for e in fourier} == {"ADMITTED"} and len({e["analysis"] for e in fourier}) == 2


def test_the_corpus_has_exactly_one_contradiction():
    names = [n.split("/")[2] for n in subprocess.run(["git", "ls-tree", "-r", "--name-only", PINNED, "docs/reviews"], cwd=ROOT,
                                                       capture_output=True, text=True).stdout.split()
             if n.count("/") == 3 and n.endswith("review.json")]
    bad = [(s, x["result_id"]) for s in names for x in ro.consistency(ro.ledger(_review(s)))["contradictions"]]
    assert len(names) == 32 and bad == [("pcsk9-mace", "41211925|HR|0.75|0.65|0.86")]


def test_the_gate_refuses_a_contradictory_page(tmp_path):
    from harness import gate
    d = tmp_path / "docs" / "reviews" / "pcsk9-mace"
    d.mkdir(parents=True)
    (d / "review.json").write_text(json.dumps(_review("pcsk9-mace")), encoding="utf-8")
    out = gate.check_result_object_consistency(str(d))
    assert out and "41211925|HR|0.75|0.65|0.86" in out[0] and "no declared waiver" in out[0]
    (d / "review.json").write_text(json.dumps(_review("esketamine-trd-madrs")), encoding="utf-8")
    assert gate.check_result_object_consistency(str(d)) == []


# ------------------------------------------------------------------ (3) sparse data
def test_plant_the_served_zero_cell_row_was_corrected_silently():
    o = next(x for x in _review("corticosteroids-covid19-mortality")["outcomes"] if x["name"] == "Serious adverse events")
    t = next(x for x in o["trials"] if x["id"] == "PMID 34138478")
    assert (t["ai"], t["n1i"], t["ci"], t["n2i"]) == (1, 16, 0, 14) and o["result"]["estimate"] == 2.8065


def test_a_zero_cell_needs_a_declared_method():
    with pytest.raises(synth.SparseDataMethodNotDeclared):
        synth.Study("RECOVERY", 1, 16, 0, 14).yi_vi()
    y, v = synth.Study("RECOVERY", 1, 16, 0, 14, zero_event_method="CC_0.5").yi_vi()
    assert y > 0 and v > 0                                                  # declared: corrected, and recorded as declared
    y2, _ = synth.Study("no zero", 5, 16, 3, 14).yi_vi()                    # no zero cell: untouched, no method needed
    assert abs(y2 - __import__("math").log((5 / 16) / (3 / 14))) < 1e-12
