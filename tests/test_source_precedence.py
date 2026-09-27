"""The protocol's source hierarchy is a PRECEDENCE ORDER, not a prohibition (GLP-1 review, PIONEER 6)."""
import json
import os

from harness import fetch, pipeline, source_precedence as sp

ROOT = pipeline.ROOT
SLUG = "glp1-ra-mace-t2d"
PROTO = open(os.path.join(ROOT, "protocols", SLUG + ".md"), encoding="utf-8").read()
OLD = ("The abstract reports more gastrointestinal events leading to discontinuation with oral semaglutide but gives no "
       "harm count or harm effect with confidence interval; registry-only values do not meet this lane's GLP-1 "
       "level-1-abstract/level-2-FDA requirement.")


def test_the_protocol_hierarchy_is_parsed_as_an_order_with_one_pointer_only_level():
    lv = sp.parse(PROTO)
    assert [l["level"] for l in lv] == [1, 2, 3, 4, 5]
    assert [l["use"] for l in lv] == ["PERMITTED"] * 4 + ["POINTER_ONLY"]


def _rv(reason):
    return {"protocol": {"text": PROTO}, "outcomes": [{"name": "Gastrointestinal adverse events",
                                                       "declared_absent_trials": [{"id": "PMID 31185157", "reason": reason}]}]}


def test_a_refusal_treating_a_permitted_tier_as_disallowed_is_blocking():
    # PLANT: the served PIONEER 6 wording
    assert [p["kind"] for p in sp.problems(_rv(OLD))] == ["HIERARCHY_TREATED_AS_PROHIBITION"]
    assert [p["kind"] for p in sp.problems(_rv("regulatory-only values are not admissible here"))] == ["HIERARCHY_TREATED_AS_PROHIBITION"]


def test_the_protocols_own_pointer_only_rule_and_a_ladder_statement_are_not_flagged():
    assert sp.problems(_rv("a value found only in a meta-analysis is a pointer, never the number; level-5 requirement")) == []
    assert sp.problems(_rv("level 1 gives no count; level 2 not held; level 3 lists per-term counts that cannot be summed")) == []
    assert sp.problems({"protocol": {"text": "no hierarchy here"}, "outcomes": _rv(OLD)["outcomes"]}) == []


def test_the_built_glp1_review_has_no_hierarchy_prohibition_and_pioneer6_is_resolved_by_tier():
    config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    rv = pipeline.build_review_core(SLUG, config, fetch.ensure(config, ""), "test")
    assert sp.problems(rv) == []
    disc = next(o for o in rv["outcomes"] if o["name"] == "Adverse events leading to discontinuation")
    row = next(t for t in disc["trials"] if "31185157" in t["id"])
    assert (row["ai"], row["n1i"], row["ci"], row["n2i"]) == (184, 1591, 104, 1592)
    assert row["source_level"] == 3 and row["target_endpoint_class"] == "EXACT_TARGET"
    gi = next(o for o in rv["outcomes"] if o["name"] == "Gastrointestinal adverse events")
    a = next(x for x in gi["declared_absent_trials"] if "31185157" in x["id"])
    assert a["result_status"]["state"] == "REPORTED_UNRESOLVED"
