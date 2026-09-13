"""Trial<->report entity model: secondary/duplicate reports collapse to their parent (X-DEDUP)
before any count is promoted to a trial count."""
import harness.screen as S


def test_companion_report_collapsed_to_parent():
    cfg = {"include": {"intervention_any": ["x"], "comparator_any": ["y"], "population_any": ["z"]},
           "companion_reports": [{"pmid": "35749277", "parent": "TRANSFORM-1/2",
                                  "kind": "secondary factor-analysis of two already-counted RCTs"}]}
    rec = {"id": "35749277", "id_type": "pmid", "title": "Factor analysis of TRANSFORM",
           "abstract": "randomized", "pubtypes": ["Randomized Controlled Trial"]}
    out = S.run([rec], cfg)["decisions"][0]
    assert out["decision"] == "exclude" and out["rule_id"] == "X-DEDUP" and "TRANSFORM-1/2" in out["reason"]


def test_independent_trial_not_collapsed():
    cfg = {"include": {"intervention_any": ["x"], "comparator_any": ["y"], "population_any": ["z"]},
           "companion_reports": [{"pmid": "35749277", "parent": "P", "kind": "k"}]}
    rec = {"id": "99999999", "id_type": "pmid", "title": "An independent RCT of X vs Y",
           "abstract": "randomized", "pubtypes": ["Randomized Controlled Trial"]}
    out = S.run([rec], cfg)["decisions"][0]
    assert out["rule_id"] != "X-DEDUP"
