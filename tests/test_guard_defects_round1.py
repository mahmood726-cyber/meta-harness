"""The four defects an independent codex review (lane R) found in the first guard landing.

Each test here FAILED before the fix. The probes are lane R's, not re-invented: it read 62 of 62
committed held documents, ran the guard on all 149 extracted table captions, enumerated the allowed
window set for all 38 configured topics, and ran 18 corruption limbs. Its verified claims stood
(97 result objects unchanged, both flags inert, no corruption probe ever passing) -- these are the
six that did not.

Keeping them as a file rather than folding them into the originals is deliberate: the original
tests passed while all four defects were live, so they are evidence about what a passing suite does
not prove.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import extract, pipeline  # noqa: E402


def _topic(slug):
    with open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8") as fh:
        return json.load(fh)["primary_outcome"]


# --- DEFECT 1: a declared RANGE collapsed to its upper endpoint -------------------------------

def test_a_declared_range_admits_both_of_its_endpoints():
    """'28-90 day or in-hospital' means 28 THROUGH 90, not 90.

    The regex read only "90 day" out of "28-90 day", so the allowed set was [90] and an explicitly
    permitted 28-day mortality result was REFUSED. A guard that deletes a legitimate row is worse
    than the mismatch it was built to catch, because it removes evidence instead of adding it.
    """
    po = _topic("balanced-crystalloids-vs-saline-mortality")
    assert po["timepoint"] == "28-90 day or in-hospital", po["timepoint"]
    for day in (28, 45, 90):
        why = extract.outcome_window_mismatch(po["timepoint"], po.get("keywords"),
                                              f"Overall {day}-day mortality did not differ")
        assert why == "", f"{day}-day is inside the declared range and was refused: {why}"


def test_a_window_outside_the_declared_range_is_still_refused():
    """The positive must survive the fix: widening the set must not disarm the guard."""
    po = _topic("balanced-crystalloids-vs-saline-mortality")
    why = extract.outcome_window_mismatch(po["timepoint"], po.get("keywords"),
                                          "Overall 180-day mortality did not differ")
    assert why, "180-day is outside '28-90 day or in-hospital' and must be refused"


def test_the_cap_window_guard_still_refuses_sixty_day():
    """The row this guard was built for: Meduri/ESCAPe's 60-day mortality in a 30-day outcome."""
    po = _topic("corticosteroids-cap-mortality")
    why = extract.outcome_window_mismatch(po["timepoint"], po.get("keywords"),
                                          "There was no significant difference in 60-day all-cause mortality")
    assert why and "60-day" in why, why


# --- DEFECT 2: a real results table refused ----------------------------------------------------

LIRAGLUTIDE_RESULTS_CAPTION = (
    "TABLE TABLE 1: Treatment effect (trial product estimand) on change from baseline to week 26 "
    "in HbA1c by baseline characteristics when liraglutide 1.8 mg versus placebo was added")


def test_a_treatment_effect_table_is_not_refused_for_saying_baseline_characteristics():
    """A real caption from cache/sglt2-primary-prevention-hf/ft_34132018.txt.

    It is a TREATMENT EFFECT table that happens to stratify BY baseline characteristics. The guard
    refused it because the caption contains the phrase. I claimed caption-keying avoided this false
    positive; I had tested "change from baseline" and never "by baseline characteristics".
    """
    assert extract.table_role_refusal(LIRAGLUTIDE_RESULTS_CAPTION) == ""


# --- DEFECT 3: real baseline tables admitted ---------------------------------------------------

@pytest.mark.parametrize("caption", [
    "TABLE Table 1: Participant Characteristics at Baseline. *",
    "TABLE Table 1: Characteristics of the Patients at Baseline",
    "TABLE Table 1. Baseline Characteristics of the Study Population",
    "TABLE Table 1: Demographics and clinical features of enrolled subjects",
])
def test_real_baseline_captions_from_the_corpus_are_refused(caption):
    """Captions lane R extracted from the committed held documents.

    My phrase list assumed a word order the corpus does not use: it matched "baseline demographic"
    and "baseline characteristic" but not "Characteristics ... at Baseline" or "Demographics and
    clinical features". A guard that matches only the phrasing I imagined protects nothing.
    """
    assert extract.table_role_refusal(caption), f"a baseline table was admitted: {caption!r}"


# --- DEFECT 4: included_ids widened the scope --------------------------------------------------

def test_included_ids_cannot_widen_the_scope_beyond_the_topics_records(tmp_path, monkeypatch):
    """`included_ids` was unioned into the allowed set, so it could admit anything.

    The production caller omits the argument, so this was latent -- but the documented contract is
    that a file is read only when its pmid belongs to THIS topic's records, and a parameter that
    can override that contract is the contract not existing.
    """
    monkeypatch.setattr(pipeline, "ROOT", str(tmp_path))
    monkeypatch.setattr(pipeline, "HELD_FULLTEXT_ENABLED", frozenset({"topic"}))
    cache = tmp_path / "cache" / "topic"
    cache.mkdir(parents=True)
    (cache / "ft_99999999.txt").write_text("OUTSIDE RECORDS", encoding="utf-8")
    records = {"records": [{"id": "28824029"}]}
    texts, digests = pipeline.held_fulltexts("topic", records, included_ids=["99999999"])
    assert "99999999" not in texts, "included_ids admitted a trial absent from the topic's records"
    assert "99999999" not in digests
