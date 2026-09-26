"""ELIXA endpoint identity for the V1.0.1 signed admission: bound to the 3-POINT row of the FDA statistical review by
its table header, row label, the definition of that label, and the event counts -- NEVER by the numbers.

Why numbers cannot identify it: in the same FDA review the 3-point secondary MACE is reported as HR 1.02 (0.89, 1.17)
(executive summary; 400 vs 392 events) and the 4-point primary MACE+ ALSO as 1.02 (0.89, 1.17) (Table 1; 406 vs 399).
The auditor uses the 4-point row as an attack fixture: a row carrying those identical numbers must be refused as
DIFFERENT_OUTCOME, never admitted because its numbers match.

Written BEFORE the identity binding existed (see evidence/glp1_adjudication/ADMISSION_TESTS_PREFIX.txt). Needs no
cache/: result_adjudication.verify reads only the decision, the held documents and the committed text extractions.
"""
import copy
import hashlib
import json
import os
import re

import pytest

from harness import result_adjudication as RA, target_endpoint

ROOT = RA.ROOT
SLUG = "glp1-ra-mace-t2d"
STATR = "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf"
STATR_TXT = "outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt"
ELIXA = "PMID 26630143"


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec():
    config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    return dict(config["primary_outcome"], primary=True)


def _entry(spec):
    return next(e for e in spec["adjudicated_results"] if e["id"] == ELIXA)


def _statr_text():
    return RA._norm(open(os.path.join(ROOT, STATR_TXT), encoding="utf-8").read())


def _cut(start, end):
    """A span of the committed text extraction (normalised), from `start` through the first `end` after it."""
    t = _statr_text()
    i = t.index(start)
    return t[i:t.index(end, i) + len(end)]


def _w(span):
    return {"ref": STATR, "sha256": _sha(os.path.join(ROOT, STATR)), "span": span}


def _decision():
    return json.load(open(os.path.join(ROOT, _entry(_spec())["decision"]), encoding="utf-8"))


def _repinned(tmp_path, d):
    spec = copy.deepcopy(_spec())
    p = tmp_path / "ELIXA.json"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    _entry(spec).update(decision=str(p), decision_sha256=_sha(p))
    return spec


# the 4-point MACE+ row and its definition, exactly as the FDA review prints them
FOUR_POINT_ROW = ("Table 1: Pre-specified Analysis of Primary MACE+ Endpoint", "406 (13.4%)")
FOUR_POINT_DEF = ("(MACE+), defined as any of the following adjudicated events:", "hospitalization for unstable angina.")
FOUR_POINT_RESULT = ("In the 6068 randomized subjects, a total of 805 primary MACE+ events", "confidence interval of (0.89, 1.17).")
THREE_POINT_SUMMARY = ("There were 792 secondary MACE events observed in the study", "confidence interval of (0.89, 1.17).")


def test_the_hazard_is_real_three_and_four_point_print_the_same_numbers():
    three, four = _cut(*THREE_POINT_SUMMARY), _cut(*FOUR_POINT_RESULT)
    assert "1.02" in three and "(0.89, 1.17)" in three
    assert "1.02" in four and "(0.89, 1.17)" in four


def test_admitted_elixa_is_identified_by_the_three_point_row_header_label_definition_and_counts():
    row = RA.verify(_spec(), _entry(_spec()))
    ident = row["endpoint_identity"]
    assert row["target_endpoint_class"] == "EXACT_TARGET"
    assert row["endpoint_binding"] == RA.BINDING and row["endpoint_binding"] != "unbound_legacy"
    assert ident["table_header"] == "Table 8: Analysis of the MACE Endpoint"
    assert ident["row_label"] == "MACE endpoint (on-study)"
    assert ident["label_term"] == "MACE"
    assert ident["events"] == {"lixisenatide": 400, "placebo": 392}
    assert ident["class"] == "EXACT_TARGET" and ident["components"] == ["cardiovascular death", "myocardial infarction", "stroke"]
    assert ident["identified_by"] == ["table_header", "row_label", "label_definition", "event_counts"]
    kept, refused = target_endpoint.admit_rows(_spec(), [row])
    assert refused == [] and kept[0]["endpoint_admissibility"] == "EXACT_TARGET"


def test_PLANT_four_point_row_with_identical_numbers_is_refused_as_DIFFERENT_OUTCOME(tmp_path):
    """The auditor's fixture: ELIXA's 4-point MACE+ row, HR 1.02 (0.89, 1.17), claimed as the 3-point result."""
    d = _decision()
    b = d["bound_result"]
    b["endpoint"] = _w(_cut(*FOUR_POINT_RESULT))
    b["estimate"]["value"], b["ci"]["value"] = 1.02, [0.89, 1.17]
    b["events"] = {"lixisenatide": 406, "placebo": 399}
    b["endpoint_identity"] = {"row": _w(_cut(*FOUR_POINT_ROW)),
                              "table_header": "Table 1: Pre-specified Analysis of Primary MACE+ Endpoint",
                              "row_label": "Primary CV endpoint", "label_term": "MACE+",
                              "definition": _w(_cut(*FOUR_POINT_DEF)),
                              "events": {"lixisenatide": 406, "placebo": 399}}
    with pytest.raises(RA.AdjudicationRefused) as exc:
        RA.verify(_repinned(tmp_path, d), _entry(_repinned(tmp_path, d)))
    assert exc.value.endpoint_class == "DIFFERENT_OUTCOME", str(exc.value)
    assert "unstable angina" in str(exc.value)


def test_PLANT_four_point_row_relabelled_with_the_three_point_definition_is_refused(tmp_path):
    """The 4-point row cannot borrow the 3-point definition: its header names MACE+, not MACE."""
    d = _decision()
    b = d["bound_result"]
    b["endpoint"] = _w(_cut(*FOUR_POINT_RESULT))
    b["estimate"]["value"], b["ci"]["value"] = 1.02, [0.89, 1.17]
    b["events"] = {"lixisenatide": 406, "placebo": 399}
    b["endpoint_identity"] = dict(b["endpoint_identity"], row=_w(_cut(*FOUR_POINT_ROW)),
                                  table_header="Table 1: Pre-specified Analysis of Primary MACE+ Endpoint",
                                  row_label="Primary CV endpoint", events={"lixisenatide": 406, "placebo": 399})
    with pytest.raises(RA.AdjudicationRefused) as exc:
        RA.verify(_repinned(tmp_path, d), _entry(_repinned(tmp_path, d)))
    assert exc.value.endpoint_class == "DIFFERENT_OUTCOME", str(exc.value)


def test_PLANT_three_point_row_with_the_four_point_counts_is_refused(tmp_path):
    d = _decision()
    d["bound_result"]["endpoint_identity"]["events"] = {"lixisenatide": 406, "placebo": 399}
    d["bound_result"]["events"] = {"lixisenatide": 406, "placebo": 399}
    with pytest.raises(RA.AdjudicationRefused, match="event count"):
        RA.verify(_repinned(tmp_path, d), _entry(_repinned(tmp_path, d)))


def test_PLANT_decision_without_an_endpoint_identity_is_refused(tmp_path):
    """No identity block means no admission: a row is never admitted on numbers plus a free-floating definition."""
    d = _decision()
    d["bound_result"].pop("endpoint_identity")
    with pytest.raises(RA.AdjudicationRefused, match="endpoint_identity"):
        RA.verify(_repinned(tmp_path, d), _entry(_repinned(tmp_path, d)))


def test_PLANT_admissibility_refuses_a_row_whose_identity_class_is_not_exact():
    row = RA.verify(_spec(), _entry(_spec()))
    forged = dict(row, target_endpoint_class="NEAR_MATCH")
    kept, refused = target_endpoint.admit_rows(_spec(), [forged])
    assert kept == [] and refused


def test_PLANT_flow_identity_pointed_at_its_kidney_composite_row_is_refused(tmp_path):
    """FLOW's Table 10 carries the kidney composite (HR 0.76) in the same table; naming that row label as the
    identity is refused as DIFFERENT_OUTCOME (moved here from the admission suite when identity replaced the bare
    definition witness)."""
    spec = copy.deepcopy(_spec())
    e = next(x for x in spec["adjudicated_results"] if x["trial"] == "FLOW")
    d = json.load(open(os.path.join(ROOT, e["decision"]), encoding="utf-8"))
    ident = d["bound_result"]["endpoint_identity"]
    row = RA._norm(ident["row"]["span"])
    i = row.index("Composite Endpoint (")
    ident["row_label"] = row[i:row.index("(time to first occurrence)", i) + len("(time to first occurrence)")]
    p = tmp_path / "FLOW.json"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    e.update(decision=str(p), decision_sha256=_sha(p))
    with pytest.raises(RA.AdjudicationRefused) as exc:
        RA.verify(spec, e)
    assert exc.value.endpoint_class == "DIFFERENT_OUTCOME", str(exc.value)


def test_flow_is_identified_by_its_own_row_label():
    spec = _spec()
    e = next(x for x in spec["adjudicated_results"] if x["trial"] == "FLOW")
    row = RA.verify(spec, e)
    assert row["target_endpoint_class"] == "EXACT_TARGET"
    assert row["endpoint_identity"]["identified_by"] == ["table_header", "row_label", "row_label_enumerates_components", "event_counts"]
    assert row["endpoint_identity"]["events"] == {"semaglutide": 212, "placebo": 254}
    assert (row["effect"], row["ci_low"], row["ci_high"]) == (0.82, 0.68, 0.98)


def test_hand_route_never_pools_the_elixa_tuple_whichever_row_it_cites():
    """The other route an attacker would use: a hand-extracted row HR 1.02 (0.89, 1.17) against the FDA review.
    The hand binder cannot tell the 3-point from the 4-point by numbers, so it sets the tuple aside (ENDPOINT_UNBOUND,
    abstain) -- never pooled -- whether it cites nothing, the 4-point Table 1 row, or either summary sentence. ELIXA
    therefore enters ONLY through the identity-bound adjudication above."""
    ref = STATR_TXT
    base = {"label": "ELIXA", "id": ELIXA, "effect": 1.02, "ci_low": 0.89, "ci_high": 1.17, "scale": "HR",
            "provenance": "fulltext_verified", "document_ref": ref, "document_sha256": _sha(os.path.join(ROOT, ref)),
            "source_level": 2, "kind": "extracted_effect", "source": "attack fixture"}
    for cited in (None, _cut(*FOUR_POINT_ROW), _cut(*FOUR_POINT_RESULT), _cut(*THREE_POINT_SUMMARY)):
        row = dict(base, **({"source_span": cited} if cited else {}))
        kept, refused = target_endpoint.admit_rows(_spec(), [row])
        assert kept == [], f"the ELIXA tuple was POOLED through the hand route citing {str(cited)[:60]!r}"
        assert refused and refused[0]["reason_code"] in ("ENDPOINT_UNBOUND", "RESULT_INCOMPATIBLE"), refused
