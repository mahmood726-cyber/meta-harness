"""V1.0.1: THE comparator overlap relation is computed from the pooled trial-family sets (harness/overlap_relation.py)
and every surface reads that one object. Plants on synthetic reviews, the balanced-crystalloids plant from the
external review, and a sweep of every served page."""
import glob, json, os

import pytest

from harness import gate, overlap_relation as orel, parity_relation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YEARS = {"P1": 2021, "P2": 2022, "P3": 2010, "P4": 2012, "P5": 2016}


def _review(pooled, members=None, comp_year=2018, endpoints=None, overlap=None):
    fams = [{"family_id": f, "aliases": {"report_ids": [p], "registry_ids": [], "acronym": []}} for f, p in pooled]
    rev = {"comparator": {"pmid": "999", "year": str(comp_year), "overlap": overlap or {}},
           "outcomes": [{"name": "Mortality", "primary": True,
                         "trials": [{"family_id": f, "id": f"PMID {p}", "label": p} for f, p in pooled]}],
           "trial_families": fams, "comparator_panel": []}
    if members is not None:
        rev["comparator_panel"] = [{"id": "c", "citation": "Comparator PMID 999", "document_ref": "x",
                                    "outcome_endpoints": endpoints or {},
                                    "trial_set": [{"family_id": n, "endpoint": ep,
                                                   "aliases": ([{"id": a}] if a else [])} for n, a, ep in members]}]
    return rev


def _rel(rev):
    return orel.compute(rev, lambda rid: YEARS.get(str(rid)))


@pytest.mark.parametrize("pooled,members,want", [
    ([("F3", "P3"), ("F4", "P4")], [("T3", "P3", None), ("T4", "P4", None)], "IDENTICAL_SET"),
    ([("F3", "P3")], [("T3", "P3", None), ("T4", "P4", None)], "SUBSET"),
    ([("F3", "P3"), ("F4", "P4")], [("T3", "P3", None)], "SUPERSET"),
    ([("F3", "P3"), ("F4", "P4")], [("T3", "P3", None), ("T5", "P5", None)], "OVERLAPPING"),
    ([("F3", "P3")], [("T4", "P4", None), ("T5", "P5", None)], "DISJOINT"),
])
def test_relation_is_a_set_operation_on_bound_families(pooled, members, want):
    assert _rel(_review(pooled, members))["relation"] == want


def test_PLANT_the_count_only_defect_never_says_overlapping():
    # the served balanced-crystalloids object before V1.0.1: ours 2, theirs 6 by count, shared "not verifiable",
    # only_ours naming both pooled trials -- the count logic called it OVERLAPPING
    ov = {"ours_k": 2, "theirs_k": 6, "shared_k": "not exactly verifiable", "only_ours": ["P1", "P2"], "only_theirs": []}
    obj = _rel(_review([("F1", "P1"), ("F2", "P2")], overlap=ov))
    assert obj["relation"] == "DISJOINT" and obj["basis"].startswith("date proof") and obj["shared_k"] == 0


def test_no_enumeration_and_no_date_proof_is_not_enumerable_never_a_guess():
    obj = _rel(_review([("F3", "P3"), ("F1", "P1")]))
    assert obj["relation"] == "NOT_ENUMERABLE" and obj["shared_k"] is None
    assert any("not a subset" in c for c in obj["constraints"])       # what IS known is kept as a constraint


def test_unbound_comparator_trial_blocks_a_relation_unless_date_proof_covers_ours():
    # an unbound member could be F3 (2010, not excluded by date) -> undecidable
    assert _rel(_review([("F3", "P3")], [("Smith 2009", None, None)]))["relation"] == "NOT_ENUMERABLE"
    # the same unbound member cannot be F1 (2021 > 2018) -> decidable, DISJOINT
    obj = _rel(_review([("F1", "P1")], [("Smith 2009", None, None)]))
    assert obj["relation"] == "DISJOINT" and "date proof" in obj["basis"]


def test_other_endpoint_members_are_out_of_scope_not_theirs():
    rev = _review([("F3", "P3"), ("F4", "P4")], [("T3", "P3", "3-point"), ("T4", "P4", "3-point"), ("T5", "P5", "4-point")],
                  endpoints={"Mortality": "3-point"})
    obj = _rel(rev)
    assert obj["relation"] == "IDENTICAL_SET" and [m["name"] for m in obj["theirs"]["out_of_scope"]] == ["T5"]


def test_parity_row_reads_the_computed_object_but_validity_verdicts_keep_precedence():
    rev = _review([("F1", "P1"), ("F2", "P2")])
    rev["comparator"]["overlap_relation"] = _rel(rev)
    assert parity_relation.compute({"status": "OVERLAPPING", "our_k": 2}, rev)["relation"] == "DISJOINT"
    assert parity_relation.compute({"status": "COMPARATOR_INVALID", "our_k": 2}, rev)["relation"] == "COMPARATOR_INVALID"


BC = os.path.join(ROOT, "docs", "reviews", "balanced-crystalloids-vs-saline-mortality")


def test_PLANT_balanced_crystalloids_is_disjoint_on_every_surface():
    rev = json.load(open(os.path.join(BC, "review.json"), encoding="utf-8"))
    obj = rev["comparator"]["overlap_relation"]
    assert obj["relation"] == "DISJOINT" and obj["ours_k"] == 2 and obj["theirs_k"] == 5 and obj["shared_k"] == 0
    assert sorted(m["name"] for m in obj["theirs"]["members"]) == ["SALT", "SMART", "Verma 2016", "Young 2014", "Young 2015"]
    assert [m["name"] for m in obj["theirs"]["out_of_scope"]] == ["Ratanarat 2017"]
    assert obj["date_proof"]["holds_for_every_pooled_family"] is True
    assert rev["comparator"]["overlap"]["relation"] == "DISJOINT"
    assert rev["reproduction"]["parity"]["parity_relation"]["relation"] == "DISJOINT"
    man = json.load(open(os.path.join(BC, "manifest.json"), encoding="utf-8"))
    assert man["comparator"]["overlap"]["relation"] == "DISJOINT"
    page = open(os.path.join(BC, "index.html"), encoding="utf-8").read()
    assert "data-relation='DISJOINT'" in page and "computed trial-set relation is DISJOINT" in page
    idx = open(os.path.join(ROOT, "docs", "index.html"), encoding="utf-8").read()
    row = idx[idx.index("reviews/balanced-crystalloids-vs-saline-mortality/index.html"):]
    row = row[:row.index("</tr>")]
    assert "DISJOINT" in row and "OVERLAPPING" not in row


@pytest.mark.parametrize("review_dir", sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*"))),
                         ids=lambda p: os.path.basename(p))
def test_every_served_page_reads_the_one_object(review_dir):
    html = open(os.path.join(review_dir, "index.html"), encoding="utf-8").read()
    assert gate.check_overlap_relation_one_object(review_dir, html) == []


@pytest.mark.parametrize("breaks", ["overlap_word", "parity_word", "manifest_word", "no_block", "no_object"])
def test_PLANT_gate_refuses_a_page_that_does_not_read_the_one_object(tmp_path, breaks):
    import shutil
    d = tmp_path / "rev"
    shutil.copytree(BC, d)
    rev = json.load(open(d / "review.json", encoding="utf-8"))
    man = json.load(open(d / "manifest.json", encoding="utf-8"))
    html = open(d / "index.html", encoding="utf-8").read()
    if breaks == "overlap_word":
        rev["comparator"]["overlap"]["relation"] = "OVERLAPPING"
    elif breaks == "parity_word":
        rev["reproduction"]["parity"]["parity_relation"]["relation"] = "OVERLAPPING"
    elif breaks == "manifest_word":
        man["comparator"]["overlap"]["relation"] = "OVERLAPPING"
    elif breaks == "no_block":
        html = html.replace("data-relation='DISJOINT'", "")
    else:
        rev["comparator"].pop("overlap_relation")
    json.dump(rev, open(d / "review.json", "w", encoding="utf-8"))
    json.dump(man, open(d / "manifest.json", "w", encoding="utf-8"))
    assert gate.check_overlap_relation_one_object(str(d), html), breaks


def test_PLANT_a_comparator_trial_that_is_one_of_our_NON_pooled_families_is_never_shared():
    # the ledger holds F9 (acronym XTRIAL, not pooled); the comparator names XTRIAL. Before V1.0.1's family/pool split
    # an acronym bound to ANY family counted as shared.
    rev = _review([("F3", "P3")])
    rev["trial_families"].append({"family_id": "F9", "aliases": {"report_ids": ["P9"], "registry_ids": [], "acronym": ["XTRIAL"]}})
    rev["comparator"]["comparator_trial_set"] = {"status": "MEASURED", "trials": ["XTRIAL"], "source_kind": "named prose"}
    rev["screening"] = {"records": [{"id": "P9", "decision": "exclude", "rule_id": "X3", "reason": "open-label"}]}
    YEARS["P9"] = 2012
    obj = _rel(rev)
    assert obj["shared_k"] == 0 and obj["relation"] == "DISJOINT"
    row = obj["inventory_comparison"]["rows"][0]
    assert row["status"] == "SCREENED_OUT" and row["family"] == "F9" and row["rule"] == "X3"
