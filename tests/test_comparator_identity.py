"""V1.0.1 comparator identity (harness/comparator_identity.py). Fixture from the CAP-corticosteroids review: the
protocol names "Wu et al." but PMID 38128217 / DOI 10.1016/j.jcrc.2023.154507 resolve to Cheema HA et al. 2024."""
import json
import os

import pytest

from harness import comparator_identity as ci, comparator_models as cm, gate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAP = "corticosteroids-cap-mortality"


def _check(slug):
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    return ci.check(ROOT, slug, cfg["comparator_pmid"])


def test_PLANT_CAP_named_Wu_resolves_to_Cheema():
    r = _check(CAP)
    assert r["state"] == "COMPARATOR_IDENTITY_MISMATCH"
    assert r["protocol"]["named_author"] == "Wu" and r["resolved"]["first_author"] == "Cheema HA"
    assert r["checks"]["pmid"] == "MATCH" and r["checks"]["doi"] == "MATCH" and r["checks"]["title"] == "MATCH"
    assert r["checks"]["author"].startswith("NOT_AMONG_RESOLVED") and "13 authors" in r["checks"]["author"]


@pytest.mark.parametrize("slug,state", [
    ("glp1-ra-mace-t2d", "MATCH"),                       # Giugliano et al. -> Giugliano D
    ("doac-vte-recurrence", "MATCH"),                    # 'van Es et al.' -> 'van Es N' (particle surname)
    ("colchicine-recurrent-pericarditis", "MATCH"),      # the protocol quotes the title without its subtitle
    ("tranexamic-acid-pph", "MATCH"),                    # a DOI with parentheses: 10.1016/S0140-6736(24)02102-0
    ("esketamine-trd-madrs", "PROTOCOL_DOES_NOT_NAME"),  # nothing named: nothing to check, not a pass
])
def test_controls_that_must_not_flag(slug, state):
    assert _check(slug)["state"] == state


def test_PLANT_a_named_author_listed_but_not_first_is_a_citation_defect_not_a_mismatch():
    r = _check("dapagliflozin-hfpef-hosp")
    assert r["state"] == "MATCH" and r["citation_defects"] and "author 2 of 4" in r["citation_defects"][0]


def test_PLANT_protocol_and_config_naming_different_papers():
    r = _check("empagliflozin-hfpef-hosp")
    assert r["state"] == "COMPARATOR_IDENTITY_MISMATCH"
    assert r["checks"]["pmid"].startswith("PROTOCOL ['36914068']") and "37773799" in r["checks"]["pmid"]


def test_gate_refuses_an_unrendered_mismatch(tmp_path):
    ident = _check(CAP)
    # a served review always carries its comparator PMID; the gate also checks it against the governing record
    (tmp_path / "review.json").write_text(json.dumps({"comparator": {"pmid": (ident.get("governing") or {}).get("served_pmid"),
                                                                     "identity": ident}}), encoding="utf-8")
    assert gate.check_comparator_identity_disclosed(str(tmp_path), "<html></html>")
    html = ci.render_block(_check(CAP))
    assert gate.check_comparator_identity_disclosed(str(tmp_path), html) == []


def test_CAP_participant_count_mismatch_is_kept_with_each_sides_evidence_state():
    doc = cm.load_reported(ROOT, CAP)
    m = doc["mismatches"][0]
    assert m["code"] == "COMPARATOR_INTERNAL_MISMATCH" and m["kind"] == "PARTICIPANT_COUNT_ABSTRACT_VS_FIGURE_TOTALS"
    held, reported = m["sides"]
    assert held["state"] == "HELD" and held["value"] == 3252
    assert reported["state"] == "REPORTED_NOT_HELD" and reported["value"] == 3622 and reported["reported_by"]
    assert doc["reported_trial_membership"]["used_for_overlap"] is False


def test_PLANT_a_HELD_side_that_is_not_in_the_held_bytes_is_refused(tmp_path):
    import shutil
    d = tmp_path / "cache" / CAP
    d.mkdir(parents=True)
    shutil.copy(os.path.join(ROOT, "cache", CAP, "records.json"), d / "records.json")
    doc = json.load(open(os.path.join(ROOT, "cache", CAP, "comparator_reported_mismatches.json"), encoding="utf-8"))
    doc["mismatches"][0]["sides"][0]["quote"] = "Fifteen RCTs (n = 3622 patients) were included in this review."
    doc["mismatches"][0]["sides"][0]["document_ref"] = f"cache/{CAP}/records.json"
    (d / "comparator_reported_mismatches.json").write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(cm.FigureRefused, match="not located"):
        cm.load_reported(str(tmp_path), CAP)


def test_served_CAP_page_shows_both_and_keeps_the_overlap_uncomputed():
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", CAP, "review.json"), encoding="utf-8"))
    comp = rev["comparator"]
    assert comp["identity"]["state"] == "COMPARATOR_IDENTITY_MISMATCH"
    assert any(m.get("evidence_state") == "ONE_SIDE_HELD" for m in comp["internal_mismatches"])
    assert comp["overlap_relation"]["relation"] == "NOT_ENUMERABLE"
    html = open(os.path.join(ROOT, "docs", "reviews", CAP, "index.html"), encoding="utf-8").read()
    assert "Cheema HA" in html and "COMPARATOR_IDENTITY_MISMATCH" in html and "3252" in html and "REPORTED_NOT_HELD" in html
