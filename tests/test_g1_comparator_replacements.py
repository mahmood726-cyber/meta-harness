"""PLANTS: comparator replacements (Mahmood 5 Oct, 'replace comparators') for dpp4, esketamine, melatonin, denosumab.
Each: a selection rule committed BEFORE the search (its SHA recorded in the selection), the pick made by the rule alone
(never the comparator being replaced), the swap through the normal path (topic + comparators.json, old record kept), the
old comparator retired in the denominator ledger with a reason and spans verbatim in its held source, and the new
comparator's trial set typed with spans verbatim in ITS held source."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
SEL = os.path.join(ROOT, "registry", "comparator_selection")

SWAPS = {  # slug: (rule sha prefix, new, old, retirement reason, n trials)
    "dpp4-mace-t2d": ("aa17b36ec", "31462224", "34754403", "NOT_ENUMERABLE_OPEN", 4),
    "esketamine-trd-madrs": ("530da166a", "37377288", "42490943", "COMPARATOR_ROW_CONTRADICTS_ITS_CITATION", 3),
    "melatonin-primary-insomnia-sol": ("d7594cc57", "35691474", "23691095", "COMPARATOR_POPULATION_BROADER_THAN_PROTOCOL", 2),
    "denosumab-vertebral-fracture": ("634e7b68d", "32492050", "36852077", "NOT_ENUMERABLE_OPEN", 2),
}


def _j(p):
    return json.load(open(p, encoding="utf-8"))


@pytest.mark.parametrize("slug", sorted(SWAPS))
def test_selection_is_by_the_preregistered_rule_and_never_the_replaced_comparator(slug):
    import g1_comparator_select as cs
    sha, new, old, _, _ = SWAPS[slug]
    sel = _j(os.path.join(SEL, slug + ".selection.json"))
    assert sel["rule_commit"].startswith(sha) and sel["result"] == "PICKED" and sel["pick"]["pmid"] == new
    rule = _j(os.path.join(SEL, slug + ".rule.json"))
    cands = _j(os.path.join(SEL, slug + ".candidates.json"))["candidates"]
    assert cs.select(rule, cands)[0]["pmid"] == new
    # the replaced comparator is never picked, even if it were made to pass every criterion
    forced = [dict(c, criteria={k: {"verdict": "PASS", "evidence": "x"} for k in c["criteria"]},
                   tie_breaks={"T1_ESTIMAND_MATCH": 9, "T2_MOST_RECENT": 999999, "T3_LARGEST_K": 999})
              if str(c["pmid"]) == old else c for c in cands]
    assert cs.select(rule, forced)[0]["pmid"] != old
    assert all(set(c["criteria"]) >= {r["id"] for r in rule["criteria"]} for c in cands)


@pytest.mark.parametrize("slug", sorted(SWAPS))
def test_swap_through_the_normal_path_keeps_the_old_record(slug):
    from harness import comparator_panel as cp
    _, new, old, reason, _ = SWAPS[slug]
    assert _j(os.path.join(ROOT, "topics", slug + ".json"))["comparator_pmid"] == new
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))
    assert c[0]["id"] == new and [r["id"] for r in c[0]["replaces"]] == [old]
    assert c[0]["replaces"][0]["retired"]["reason_code"] == reason
    cp.validate(c[0], ROOT)


@pytest.mark.parametrize("slug", sorted(SWAPS))
def test_old_comparator_retired_in_the_ledger_with_verbatim_spans(slug):
    import g1_denominator_ledger as dl
    _, new, old, reason, _ = SWAPS[slug]
    r = dl.retired_comparator(slug, new)
    assert r and r["retired_pmid"] == old and r["reason_code"] == reason and r["span"]["parts"]
    assert dl.retired_comparator(slug, old) is None
    led = {"removed": [{"slug": slug, "label": "x", "kind": "COMPARATOR_RETIRED",
                        "rule_id": "COMPARATOR_RETIRED:" + reason, "span": r["span"]}],
           "baseline": {"N": 1}, "removed_n": 1, "added_n": 0, "current": {"N": 0}}
    assert dl.problems(led) == []


@pytest.mark.parametrize("slug", sorted(SWAPS))
def test_new_comparator_trial_set_is_typed_and_verifiable(slug):
    import k_gap_table as kt
    _, new, old, _, n = SWAPS[slug]
    e = _j(os.path.join(ROOT, "registry", "comparator_enumerations", slug + ".json"))
    assert e["comparator_pmid"] == new and len(e["units"]) == n and all(u["pmid"].isdigit() for u in e["units"])
    us = kt.enumeration_units(slug, ["x"], new)
    assert len(us) == n and all(u["cited"][0]["pmid"] for u in us)
    assert kt.enumeration_units(slug, ["x"], old) == []
    a = _j(os.path.join(SEL, slug + ".adoption.json"))
    assert a["comparator_type"] == "COMPARATOR_WITH_PER_TRIAL_ROWS" and a["pooled_result"]["k"] == n
    src = os.path.join(ROOT, a["pooled_result"]["source"]["path"])
    assert kt.held_norm(None, next(iter(a["pooled_result"]["spans"].values()))) in kt.held_norm(src)
