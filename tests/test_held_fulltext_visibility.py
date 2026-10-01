"""A committed held full text must reach POOL CONSTRUCTION, and only the right one.

The defect this pins. `consumer_consistency.fulltexts_by_id` globs cache/<slug>/ft_*.txt and reads
them; the pipeline took `fulltext_by_pmid` from records.json only, which `harness/fetch.py` fills
from a network fetch at acquisition time. A full text committed to the cache afterwards was read by
the consistency checker and was invisible to the code that builds the pool -- 58 of 62 committed
held documents across 18 topics, measured 2026-09-30.

Concretely: J-EMPHASIS-HF (PMID 28824029) publishes its ITT all-cause-mortality HR 1.77 (0.81-3.87)
in Table 3. The harness had recorded PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE and pooled a
reconstruction from arm counts instead. The span is now committed from the open-access J-STAGE PDF,
and the harvester finds it -- but nothing changed, because the pipeline never read the file.

Three required answers, each different, so a change that reads everything or reads nothing fails
whichever case it was written for.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import pipeline, source_hierarchy  # noqa: E402


@pytest.fixture
def opted_in(monkeypatch):
    """Held full texts are a PER-TOPIC OPT-IN, default off (pipeline.HELD_FULLTEXT_ENABLED).

    Enabling all 58 committed documents at once moved 4 of 51 outcomes in a single step and two
    of the first rows examined were extracted from the wrong part of their document. So each
    topic is enabled on its own. These tests enable the topic under test explicitly, and
    test_a_topic_that_has_not_opted_in_reads_nothing pins the default.
    """
    monkeypatch.setattr(pipeline, "HELD_FULLTEXT_ENABLED", frozenset({SLUG,
                                                                     "probiotics-aad-prevention",
                                                                     "tocilizumab-covid19-mortality"}))


SLUG = "spironolactone-hfref-mortality"
PMID = "28824029"


def _records(slug):
    with open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8") as fh:
        return json.load(fh)


def test_the_committed_held_fulltext_is_read_by_pool_construction(opted_in):
    """The positive plant: the file exists, so the loader must return it, with its digest."""
    texts, digests = pipeline.held_fulltexts(SLUG, _records(SLUG))
    assert PMID in texts, (
        "the committed held document cache/%s/ft_%s.txt is not reaching pool construction" % (SLUG, PMID))
    assert PMID in digests and len(digests[PMID]["sha256"]) == 64, digests.get(PMID)
    assert digests[PMID]["ref"] == f"cache/{SLUG}/ft_{PMID}.txt"


def test_the_published_ITT_hazard_ratio_is_the_candidate_that_comes_out(opted_in):
    """1.77 (0.81-3.87) -- the ITT primary analysis, named as such in Table 3."""
    texts, _ = pipeline.held_fulltexts(SLUG, _records(SLUG))
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    po = cfg["primary_outcome"]
    spec = {"name": po["name"], "keywords": list(po["keywords"]), "estimand": po.get("estimand")}
    got = source_hierarchy.effect_candidates_for_outcome(spec, texts[PMID])
    effects = sorted(round(float(c["effect"]), 4) for c in got if c.get("effect") is not None)
    assert 1.77 in effects, f"the published ITT mortality HR was not harvested; candidates: {effects}"


def test_table_4_on_treatment_1_36_is_never_the_candidate(opted_in):
    """The negative that matters clinically: Table 4 is the ALTERNATIVE analysis.

    The held excerpt contains the sentence 'the hazard ratio of death from any cause was lower than
    that of the primary analysis (1.36 vs. 1.77)'. 1.36 is the on-treatment figure and must never be
    selected for a declared ITT outcome. 1.36 also appears as the upper bound of the PRIMARY
    COMPOSITE's interval 0.85 (0.53, 1.36) in the same excerpt, so a loose match has two ways to
    pick it up.
    """
    texts, _ = pipeline.held_fulltexts(SLUG, _records(SLUG))
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    po = cfg["primary_outcome"]
    spec = {"name": po["name"], "keywords": list(po["keywords"]), "estimand": po.get("estimand")}
    got = source_hierarchy.effect_candidates_for_outcome(spec, texts[PMID])
    effects = [round(float(c["effect"]), 4) for c in got if c.get("effect") is not None]
    assert 1.36 not in effects, f"Table 4's on-treatment HR was harvested for an ITT outcome: {got}"
    assert 0.85 not in effects, f"the CV-death/HHF composite was harvested as mortality: {got}"


def test_a_fulltext_for_an_unrelated_trial_is_not_read(tmp_path, monkeypatch):
    """The negative plant on SCOPE: bytes beside the cache are not evidence about this topic.

    Without this, the loader would admit any ft_*.txt dropped into the directory -- including one
    for a trial that is not in this topic's records at all.
    """
    monkeypatch.setattr(pipeline, "ROOT", str(tmp_path))
    monkeypatch.setattr(pipeline, "HELD_FULLTEXT_ENABLED", frozenset({SLUG}))
    cache = tmp_path / "cache" / SLUG
    cache.mkdir(parents=True)
    (cache / "ft_28824029.txt").write_text("real trial, in the records", encoding="utf-8")
    (cache / "ft_99999999.txt").write_text("a trial this topic never screened", encoding="utf-8")
    records = {"records": [{"id": "28824029"}]}
    texts, digests = pipeline.held_fulltexts(SLUG, records)
    assert "28824029" in texts
    assert "99999999" not in texts, "a full text for a trial outside this topic's records was read"
    assert "99999999" not in digests


def test_the_recorded_network_fetch_keeps_precedence(tmp_path, monkeypatch):
    """records.json is what acquisition actually retrieved; a later file must not displace it.

    Preferring the committed file would hide a disagreement between the two rather than surface it.
    """
    monkeypatch.setattr(pipeline, "ROOT", str(tmp_path))
    monkeypatch.setattr(pipeline, "HELD_FULLTEXT_ENABLED", frozenset({SLUG}))
    cache = tmp_path / "cache" / SLUG
    cache.mkdir(parents=True)
    (cache / "ft_28824029.txt").write_text("LATER COMMITTED BYTES", encoding="utf-8")
    records = {"records": [{"id": "28824029"}],
               "fulltext_by_pmid": {"28824029": "WHAT ACQUISITION FETCHED"}}
    texts, _ = pipeline.held_fulltexts(SLUG, records)
    assert texts["28824029"] == "WHAT ACQUISITION FETCHED"


@pytest.mark.parametrize("slug", ["probiotics-aad-prevention", "tocilizumab-covid19-mortality"])
def test_other_topics_held_documents_also_reach_pool_construction(slug, opted_in):
    """This was never one trial's problem: 58 of 62 held documents were invisible."""
    texts, digests = pipeline.held_fulltexts(slug, _records(slug))
    on_disk = [n for n in os.listdir(os.path.join(ROOT, "cache", slug))
               if n.startswith("ft_") and n.endswith(".txt")]
    assert on_disk, f"{slug} has no committed held documents to test"
    assert digests, f"{slug} committed {len(on_disk)} held documents and none reached the pipeline"


def test_a_topic_that_has_not_opted_in_reads_nothing(tmp_path, monkeypatch):
    """The default must be OFF, and provably so.

    Without this the opt-in could be silently defaulted to on by a later edit and the corpus-wide
    aperture change would happen by accident -- which is exactly the failure the opt-in exists to
    prevent. An empty digests map matters as much as empty texts: nothing downstream may believe a
    held document was read when it was not.
    """
    monkeypatch.setattr(pipeline, "ROOT", str(tmp_path))
    monkeypatch.setattr(pipeline, "HELD_FULLTEXT_ENABLED", frozenset())
    cache = tmp_path / "cache" / SLUG
    cache.mkdir(parents=True)
    (cache / f"ft_{PMID}.txt").write_text("held bytes that must not be read", encoding="utf-8")
    texts, digests = pipeline.held_fulltexts(SLUG, {"records": [{"id": PMID}]})
    assert texts == {} and digests == {}
