"""Mahmood's review of the served glp1 page (98726cc1 / 6f14b03a, 19 Sep 2026), increment 3 of the revision list: the page
says "1 trial family" declared absent in four places and "3 eligible families not in the pool" in twelve. Two counts of
the same thing render from different sources: `identity.outcome_counts` counts the primary's `declared_absent_trials`
(ELIXA only), `grade.missing_family_count` counts the known-missing panel (FLOW, FREEDOM-CVO, ELIXA); FLOW and
FREEDOM-CVO were never in the screening ledger (they arrived by concept query), and ELIXA's absent row still says
OUTCOME_NOT_IN_SOURCE while its panel row says EXTRACTED_SOURCE_CONFLICT.

Requirement: one ledger (`identity.trial_family_ledger`) links every family to its eligibility, screening route,
analysis membership, held sources, unresolved adjudications and poolability; the primary's declared-absent rows are
reconciled from it (every eligible-not-pooled family present, states agreeing with the held facts); every count on the
page derives from the same object, so the two counts cannot disagree. Plant: on bf2af50d the first two tests fail.
"""
import json
import pathlib
import re

from harness import grade, identity, manuscript, page

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _review(slug):
    return json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def test_glp1_absent_count_and_missing_count_are_the_same_number():
    review = _review("glp1-ra-mace-t2d")
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    absent = identity.outcome_counts(primary)["absent"]["trials"]
    missing = grade.missing_family_count(review)
    assert absent == missing == 3, (absent, missing)
    ledger = review.get("trial_family_ledger")
    assert ledger, "the review object carries the ledger"
    not_pooled = [e for e in ledger["families"] if e["eligibility"] == "eligible" and not e["pooled_in"]]
    names = {n for e in not_pooled for n in [e["family"], *e["ids"]]}
    assert {"FLOW", "FREEDOM-CVO", "ELIXA"} <= names and len(not_pooled) == 3, not_pooled
    elixa = next(e for e in not_pooled if "ELIXA" in e["ids"] or e["family"] == "ELIXA")
    assert elixa["state"] == "EXTRACTED_SOURCE_CONFLICT" and elixa["unresolved_adjudications"]
    absent_states = {r.get("label") or r.get("id"): r.get("state") for r in primary["declared_absent_trials"]}
    assert absent_states.get("26630143") == "EXTRACTED_SOURCE_CONFLICT", absent_states


def test_rendered_surfaces_carry_one_count():
    review = _review("glp1-ra-mace-t2d")
    text = _plain(page.render_page(review)) + " " + _plain(manuscript.render(review))
    assert "1 trial family" not in text and "1 eligible trial" not in text, "the stale count survives"
    assert "3 trial families" in text
    assert "3 eligible families not in the pool" in text


def test_ledger_is_built_from_the_object_and_every_pooled_family_is_poolable():
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        ledger = identity.trial_family_ledger(review)
        primary = next((o for o in review["outcomes"] if o.get("primary")), None)
        if not primary:
            continue
        pooled = {identity._family_of(t) for t in primary.get("trials") or []}
        for entry in ledger["families"]:
            if entry["family"] in pooled:
                assert entry["state"] == "POOLABLE" and primary["name"] in entry["pooled_in"], (path.parent.name, entry)
        # every served object carries the ledger it was reconciled with, and the counts every surface prints are its counts
        stored = review.get("trial_family_ledger")
        assert stored, (path.parent.name, "review object carries no trial_family_ledger")
        absent = identity.outcome_counts(primary)["absent"]["trials"]
        assert absent == ledger["counts"]["eligible_not_pooled_primary"] == stored["counts"]["eligible_not_pooled_primary"], (
            path.parent.name, absent, ledger["counts"], stored["counts"])
        assert grade.missing_family_count(review) == absent, (path.parent.name, grade.missing_family_count(review), absent)
