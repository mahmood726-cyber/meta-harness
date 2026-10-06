"""Plant: a trial that reports the primary outcome but is not pooled keeps its disclosure when ANOTHER
trial pools. Before the fix the disclosure lived only in the nothing-pooled branch, so pooling DELIVER
silenced 34711976 and 37534453 on the dapagliflozin page (the STALE reason and the absence note vanished)."""
from harness import invalidation
from harness.pipeline import reported_not_pooled

SPEC = {"name": "worsening heart failure", "keywords": ["worsening heart failure"]}
INCLUDED = [{"id": "36027570"}, {"id": "34711976"}, {"id": "37534453"}, {"id": "NCT04475042"}]
RECS = {"36027570": {"abstract": "the primary outcome, worsening heart failure or cv death, HR 0.82"},
        "34711976": {"abstract": "Worsening heart failure events were fewer"},
        "37534453": {"abstract": "reduce risk of worsening heart failure"},
        "NCT04475042": {"abstract": ""}}


def test_pooled_trial_excluded_unpooled_reporters_kept():
    pooled = [{"id": "PMID 36027570", "family_report_id": "36027570"}]
    assert reported_not_pooled(SPEC, INCLUDED, RECS, pooled) == ["34711976", "37534453"]


def test_nothing_pooled_lists_every_reporter():
    assert reported_not_pooled(SPEC, INCLUDED, RECS, []) == ["36027570", "34711976", "37534453"]


def test_invalidation_fires_when_primary_is_pooled():
    core = {"outcomes": [{"primary": True, "result": {"present": True, "k": 1, "estimate": 0.82,
                                                      "reported_not_extracted": True,
                                                      "reported_by": ["34711976", "37534453"]}}]}
    out = invalidation.assess(core, {})
    assert "primary_reported_not_extracted" in repr(out)
