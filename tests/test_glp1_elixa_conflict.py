"""GLP-1 MACE k=10 admission (signature item). Written BEFORE the fix.
(1) ELIXA 3-point MACE (on-study, 400/3,034 vs 392/3,034): the SAME FDA statistical review page gives HR 1.02 (0.887,
    1.172) in the section 3.3.4.3 narrative and 1.02 (0.89, 1.18) in Table 8; 1.172 does not round to 1.18. Both
    locations are recorded, SOURCE_EFFECT_CONFLICT is raised, and a governing version is DECIDED with its reason before
    the signature request (and its derived notice) can be generated; the notice discloses it.
(3) FREEDOM-CVO: the individual-trial Table 19 row, never the adjacent Table 18 pooled 3-study row (1.13), whose
    ITCA 650 arm has the SAME numerator (85/2649 vs FREEDOM's 85/2075)."""
import hashlib
import importlib.util
import json
import os
import shutil
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "evidence", "glp1_adjudication")
sys.path.insert(0, os.path.join(ROOT, "evidence", "scripts"))
import textrep  # noqa: E402

STATR = "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf"


def _load(name):
    return json.load(open(os.path.join(D, name), encoding="utf-8"))


def _witness_ok(w):
    assert hashlib.sha256(open(os.path.join(ROOT, w["ref"]), "rb").read()).hexdigest() == w["sha256"]
    assert w["span"] in textrep.render(w["ref"])


def test_elixa_records_both_locations_as_a_source_effect_conflict():
    c = _load("ELIXA.json")["bound_result"]["source_effect_conflict"]
    assert c["kind"] == "SOURCE_EFFECT_CONFLICT"
    locs = {l["where"]: l for l in c["locations"]}
    assert len(locs) == 2
    narr = next(l for l in c["locations"] if l["ci"] == [0.887, 1.172])
    tab8 = next(l for l in c["locations"] if l["ci"] == [0.89, 1.18])
    for l in (narr, tab8):
        assert l["witness"]["ref"] == STATR
        _witness_ok(l["witness"])
    assert "(0.887, 1.172)" in narr["witness"]["span"] and "(0.89, 1.18)" in tab8["witness"]["span"]
    assert "400" in tab8["witness"]["span"] and "392" in tab8["witness"]["span"]


def test_the_governing_version_is_decided_with_a_computed_reason():
    c = _load("ELIXA.json")["bound_result"]["source_effect_conflict"]
    g = c["governing"]
    assert g["state"] == "DECIDED" and g["ci"] == [0.887, 1.172] and len(g["reason"]) > 80
    ev = g["evidence"]
    assert abs(ev["narrative"]["log_midpoint_hr"] - 1.0196) < 5e-4 and abs(ev["table8"]["log_midpoint_hr"] - 1.0248) < 5e-4
    assert abs(ev["narrative"]["se_ratio_to_event_count_se"] - 1.0) < 1e-3
    assert ev["narrative_upper_rounded_2dp"] == 1.17
    assert _load("ELIXA.json")["bound_result"]["ci"]["value"] == g["ci"]


def test_the_signature_request_refuses_an_undecided_conflict(tmp_path):
    # PLANT: the same decision with its governing decision removed -> no bundle is generated
    d = tmp_path / "evidence" / "glp1_adjudication"
    d.mkdir(parents=True)
    for f in os.listdir(D):
        if f.endswith((".json", ".py")):
            shutil.copyfile(os.path.join(D, f), d / f)
    e = json.load(open(d / "ELIXA.json", encoding="utf-8"))
    e["bound_result"]["source_effect_conflict"].pop("governing")
    (d / "ELIXA.json").write_text(json.dumps(e), encoding="utf-8")
    spec = importlib.util.spec_from_file_location("msr", os.path.join(D, "make_signature_request.py"))
    msr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(msr)
    with pytest.raises(SystemExit, match="SOURCE_EFFECT_CONFLICT"):
        msr.check_conflicts(str(tmp_path))


def test_the_notice_discloses_the_conflict_and_both_diagnostic_pools():
    t = open(os.path.join(D, "SIGNATURE_REQUEST.md"), encoding="utf-8").read()
    assert "SOURCE_EFFECT_CONFLICT" in t and "(0.887, 1.172)" in t and "(0.89, 1.18)" in t
    ba = _load("BEFORE_AFTER.json")["after"]
    n = ba["CONVENTIONAL_GLP1RA: + ELIXA only"]["estimate"]
    t8 = ba["CONVENTIONAL_GLP1RA: + ELIXA only (ELIXA at its Table 8 rendering 0.89-1.18)"]["estimate"]
    assert (round(n, 4), round(t8, 4)) == (0.863, 0.8629)
    assert f"{n:.4f}" in t and f"{t8:.4f}" in t


def test_the_signature_request_binds_the_current_bytes():
    """A stale bundle signs bytes that no longer exist: every manifest hash must be the file's current hash."""
    t = open(os.path.join(D, "SIGNATURE_REQUEST.md"), encoding="utf-8").read()
    block = t.split("```")[1].strip().splitlines()
    assert block
    for line in block:
        h, p = line.split("  ", 1)
        assert hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() == h, p


def test_freedom_cvo_names_the_adjacent_pooled_row_it_is_not():
    f = _load("FREEDOM-CVO.json")["bound_result"]
    assert "85/2075" in f["endpoint"]["span"] and "1.24 (0.90, 1.70)" in f["endpoint"]["span"]
    w = f["not_these_rows"]["Table 18 pooled CLP-103/105/107 3-point row (1.13; same ITCA numerator 85, denominator 2649)"]
    _witness_ok(w)
    assert "85/2649" in w["span"] and "1.13 (0.82, 1.54)" in w["span"]
    assert "Pooled Analysis of CLP-103, CLP- 105, and CLP-107" in f["not_these_rows"]["Table 18 title"]["span"]
