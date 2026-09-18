"""URGENT audit (18 Sep 2026), defect 4: the dependency checker compared stored stamps with themselves.
`claimgraph._scan_dependents.current_for` returned the object's own stored `input_set_version` -- written by the same
stamping pass as its `depends_on` -- so the two could never disagree. Measured on the served glp1 object (237e9094 /
75cc9a46): mutating a pooled trial's effect changed the outcome's recomputed input_set_version, yet `check()` reported
STALE_DEPENDENT for only 3 of 28 stamped objects (the three that carry no stamp of their own); the pooled result, the
GRADE object, the membership rows, the strands and the RoB-sensitivity points stayed silent.

Requirement: the current version is always recomputed from the outcome's rows as they stand; after a mutation of any
pooled row, every object that depends on that outcome's input set is reported stale. Plant: on 75cc9a46 the first test fails.
"""
import copy
import json
import pathlib

from harness import claimgraph as cg

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _review(slug):
    return json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _stamped_paths(obj, path=""):
    if isinstance(obj, dict):
        if (obj.get("depends_on") or {}).get("input_set_version"):
            yield path
        for k, v in obj.items():
            if k in {"protocol", "search", "screening", "limitations"}:
                continue
            yield from _stamped_paths(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _stamped_paths(v, f"{path}/{i}")


def test_mutating_a_pooled_effect_makes_every_primary_dependent_stale():
    review = _review("glp1-ra-mace-t2d")
    assert cg.check(review) == []
    mutated = copy.deepcopy(review)
    primary = next(o for o in mutated["outcomes"] if o.get("primary"))
    primary["trials"][0]["effect"] = 0.5
    assert cg.input_set_version(primary) != cg.input_set_version(next(o for o in review["outcomes"] if o.get("primary")))
    stale = {v["object_path"] for v in cg.check(mutated) if v["code"] == "STALE_DEPENDENT"}
    # the pooled result and the GRADE object are the two dependents a reader relies on most
    assert "/outcomes/0/result" in stale, stale
    assert "/grade" in stale, stale
    # every stamped object bound to the primary outcome's version is stale, not just the un-self-stamped three
    primary_version = cg.input_set_version(next(o for o in review["outcomes"] if o.get("primary")))
    bound = set()
    for path in _stamped_paths(review):
        node = review
        for part in path.split("/")[1:]:
            node = node[int(part)] if isinstance(node, list) else node[part]
        if node["depends_on"]["input_set_version"] == primary_version:
            bound.add(path)
    assert bound, "fixture assumption: the served object carries primary-bound stamps"
    assert bound <= stale, sorted(bound - stale)


def test_mutating_a_strand_member_makes_that_strand_stale_and_nothing_else():
    review = _review("iv-iron-hfref-hosp")
    strands = (review.get("strands") or {}).get("strands") or []
    assert strands and strands[0].get("members"), "fixture assumption: iv-iron carries a strand with members"
    mutated = copy.deepcopy(review)
    mutated["strands"]["strands"][0]["members"][0]["effect"] = 0.123
    stale = {v["object_path"] for v in cg.check(mutated) if v["code"] == "STALE_DEPENDENT"}
    assert "/strands/strands/0" in stale
    assert all(p.startswith("/strands/strands/0") for p in stale), stale


def test_unmutated_served_objects_report_no_stale_dependent():
    bad = []
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        if any(v["code"] == "STALE_DEPENDENT" for v in cg.check(review)):
            bad.append(path.parent.name)
    assert bad == []
